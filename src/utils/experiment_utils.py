"""
Módulo de utilidades para análisis de experimentos AB Test en Amplitude.

Este módulo contiene todas las funciones necesarias para:
- Obtener datos de experimentos desde la API de Amplitude
- Procesar datos de funnels por variantes
- Generar pipelines completos de análisis
"""

import os
import json
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from src.utils.amplitude_filters import (
    get_culture_digital_filter, get_culture_digital_filter_multiple,
    get_country_filter,
    get_device_type, get_device_type_multiple,
    get_flow_type_filter, get_flow_type_filter_multiple,
    get_bundle_filters, get_bundle_filters_multiple,
    get_trip_type_filter, get_trip_type_filter_multiple,
    get_pax_adult_count_filter,
    get_travel_group_filter, get_travel_group_filter_multiple
)
import sys
from io import StringIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import streamlit as st

# Variable global para almacenar logs
_logs = []

# Cache simple en memoria para requests a Amplitude (mejora velocidad)
_amplitude_cache = {}

def get_logs():
    """Obtiene y limpia los logs capturados"""
    global _logs
    logs = _logs.copy()
    _logs = []  # Limpiar logs después de obtenerlos
    return logs


def _generate_cache_key(*args, **kwargs):
    """
    Genera una clave única para el caché basada en los parámetros.
    
    Returns:
        str: Hash MD5 de los parámetros
    """
    # Convertir todos los parámetros a string y crear un hash
    key_str = json.dumps({
        'args': str(args),
        'kwargs': {k: str(v) for k, v in sorted(kwargs.items())}
    }, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def clear_amplitude_cache():
    """Limpia el caché de Amplitude"""
    global _amplitude_cache
    _amplitude_cache = {}
    return len(_amplitude_cache)


def get_credentials():
    """
    Obtiene las credenciales de Amplitude desde variables de entorno.
    Esta función debe ser llamada DESPUÉS de que load_dotenv() se haya ejecutado.
    
    Returns:
        tuple: (api_key, secret_key, management_api_key)
    """
    api_key = os.getenv('AMPLITUDE_API_KEY')
    secret_key = os.getenv('AMPLITUDE_SECRET_KEY')
    management_api_key = os.getenv('AMPLITUDE_MANAGEMENT_KEY')
    
    # Debug: Verificar que las credenciales se cargaron
    # También verificar variaciones comunes del nombre de la variable
    if not management_api_key:
        # Intentar con variaciones del nombre
        management_api_key = (
            os.getenv('AMPLITUDE_MANAGEMENT_KEY') or
            os.getenv('AMPLITUDE_MANAGEMENT_API_KEY') or
            os.getenv('AMPLITUDE_MGMT_KEY') or
            os.getenv('AMPLITUDE_MGMT_API_KEY')
        )
    
    return api_key, secret_key, management_api_key


def extract_median_time_from_response(response_json, variant_name="control"):
    """
    Extrae el tiempo mediano de conversión (medianTransTimes) de la respuesta de Amplitude.
    
    Args:
        response_json: Respuesta JSON de la API de Amplitude
        variant_name: Nombre de la variante (para logging)
        
    Returns:
        float: Tiempo mediano en segundos, o None si no está disponible
    """
    try:
        if 'data' not in response_json:
            return None
        
        data = response_json['data']
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
        elif isinstance(data, dict):
            first_item = data
        else:
            return None
        
        # Buscar medianTransTimes en la estructura
        # Según la documentación de Amplitude, puede estar en:
        # - data[0].medianTransTimes (array de tiempos por paso)
        # - data[0].dayFunnels.medianTransTimes
        # - data[0].medianTransTimes (directo)
        
        median_times = None
        
        # Intentar extraer de diferentes ubicaciones posibles
        if 'medianTransTimes' in first_item:
            median_times = first_item['medianTransTimes']
        elif 'dayFunnels' in first_item and isinstance(first_item['dayFunnels'], dict):
            if 'medianTransTimes' in first_item['dayFunnels']:
                median_times = first_item['dayFunnels']['medianTransTimes']
        
        if median_times is None:
            return None
        
        # medianTransTimes es un array donde cada elemento corresponde a un paso del funnel
        # El último elemento es el tiempo total de conversión (del primer al último paso)
        if isinstance(median_times, list) and len(median_times) > 0:
            # Tomar el último valor (tiempo total de conversión)
            total_time_ms = median_times[-1]
            # Convertir de milisegundos a segundos
            total_time_seconds = total_time_ms / 1000.0
            return total_time_seconds
        elif isinstance(median_times, (int, float)):
            # Si es un solo valor, asumir que está en milisegundos
            return median_times / 1000.0
        
        return None
    except Exception as e:
        print(f"[Warning] Error extrayendo tiempo mediano para {variant_name}: {e}")
        return None


def normalize_date_for_amplitude(date_input, default_time="00:00:00", is_end_date=False):
    """
    Normaliza una fecha para enviarla a la API de Amplitude con precisión horaria.
    
    Args:
        date_input: Puede ser:
            - str en formato ISO (YYYY-MM-DDTHH:mm:ss o YYYY-MM-DD)
            - datetime object
            - pd.Timestamp
            - None
        default_time: Hora por defecto si solo se proporciona la fecha (formato HH:mm:ss)
        is_end_date: Si es True y solo hay fecha, usa 23:59:59 en lugar de default_time
        
    Returns:
        str: Fecha formateada como YYYYMMDDHHmmss para la API de Amplitude
    """
    if date_input is None or pd.isna(date_input):
        return None
    
    # Convertir a datetime si es string
    if isinstance(date_input, str):
        # Intentar parsear diferentes formatos
        try:
            # Formato ISO completo con hora
            if 'T' in date_input or ' ' in date_input:
                dt = pd.to_datetime(date_input)
            else:
                # Solo fecha, agregar hora
                date_str = date_input.strip()
                if is_end_date:
                    time_str = "23:59:59"
                else:
                    time_str = default_time
                dt = pd.to_datetime(f"{date_str} {time_str}")
        except Exception:
            # Fallback: asumir formato YYYY-MM-DD
            date_str = date_input.strip()
            if is_end_date:
                time_str = "23:59:59"
            else:
                time_str = default_time
            dt = pd.to_datetime(f"{date_str} {time_str}")
    elif isinstance(date_input, (pd.Timestamp, datetime)):
        dt = pd.to_datetime(date_input)
        # Si no tiene hora (00:00:00), aplicar la hora por defecto según el tipo
        if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
            if is_end_date:
                dt = dt.replace(hour=23, minute=59, second=59)
            # Si es start_date y es 00:00:00, mantenerlo así (ya es el default)
    else:
        # Intentar convertir con pandas
        dt = pd.to_datetime(date_input)
        # Si después de la conversión no tiene hora, aplicar la hora por defecto
        if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
            if is_end_date:
                dt = dt.replace(hour=23, minute=59, second=59)
    
    # Formatear como YYYYMMDDHHmmss para la API de Amplitude
    return dt.strftime('%Y%m%d%H%M%S')

@st.cache_data(persist="disk", show_spinner=False, ttl=86400)
def get_funnel_data_experiment(api_key, secret_key, start_date, end_date, experiment_id, device, variant, culture, event_list, conversion_window=1800, event_filters_map=None, flow_type="ALL", bundle_profile="ALL", trip_type="ALL", pax_adult_count="ALL", travel_group="ALL", country=None, hidden_first_step=False, include_time_data=False):
	"""
	Obtiene datos de funnel desde la API de Amplitude para un experimento específico.
	OPTIMIZACIÓN: Incluye caché en memoria para evitar requests duplicadas.
	
	Args:
		api_key: API key de Amplitude
		secret_key: Secret key de Amplitude
		start_date: Fecha de inicio (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
		end_date: Fecha de fin (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
		experiment_id: ID del experimento en Amplitude
		device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
		variant: Nombre de la variante ('control' o 'treatment')
		culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
		event_list: Lista de eventos a analizar
		conversion_window: Ventana de tiempo de conversión en segundos (default: 1800 = 30 min)
		event_filters_map: Diccionario opcional que mapea eventos a sus filtros adicionales.
		                   Formato: {event_name: [filter1, filter2, ...]}
		flow_type: Tipo de flujo ('DB', 'PB', 'CK', o 'ALL')
		bundle_profile: Perfil de bundle ('ALL', 'Vuela Ligero', 'Smart', 'Full', 'Smart + Full')
		trip_type: Tipo de viaje ('ALL', 'Solo Ida (One Way)', 'Ida y Vuelta (Round Trip)')
		pax_adult_count: Cantidad de adultos ('ALL', '1 Adulto', '2 Adultos', '3 Adultos', '4+ Adultos')
		hidden_first_step: Si es True, aplica "Inmunidad Contextual": solo filtra Flow/Trip/Bundle en el paso 0 (ancla)
		
	Returns:
		dict: Respuesta JSON de la API de Amplitude con los datos del funnel
	"""
	# OPTIMIZACIÓN #2: Verificar caché antes de hacer request
	global _amplitude_cache
	cache_key = _generate_cache_key(
		start_date, end_date, experiment_id, device, variant, culture,
		event_list, conversion_window, event_filters_map, flow_type,
		bundle_profile, trip_type, pax_adult_count, travel_group, country, hidden_first_step
	)
	
	if cache_key in _amplitude_cache:
		# Retornar resultado cacheado (sin hacer request a Amplitude)
		return _amplitude_cache[cache_key]
	# ============================================================
	# COMPOSITE METRIC STRATEGY: EXTRAS_GENERAL_CR
	# ============================================================
	# Detectamos si esta es la métrica EXTRAS_GENERAL_CR que requiere
	# lógica OR (suma de 3 sub-métricas: Flexi, Pet, Priority)
	# Estructura esperada: extras_dom_loaded -> extra_selected (filtro) -> revenue_amount
	is_extras_general_cr = False
	if event_list and len(event_list) >= 3:
		# Extraer nombres de eventos (puede venir como lista de strings o lista de tuplas)
		first_event = event_list[0] if isinstance(event_list[0], str) else (event_list[0][0] if isinstance(event_list[0], tuple) else None)
		second_event = event_list[1] if isinstance(event_list[1], str) else (event_list[1][0] if isinstance(event_list[1], tuple) else None)
		third_event = event_list[2] if isinstance(event_list[2], str) else (event_list[2][0] if isinstance(event_list[2], tuple) else None)
		
		# Verificar estructura de EXTRAS_GENERAL_CR
		if (first_event == 'extras_dom_loaded' and 
		    second_event == 'extra_selected' and 
		    third_event == 'revenue_amount'):
			# Verificar que el filtro de extra_selected excluya airportCheckin
			# Primero intentar desde event_filters_map (formato desde app.py)
			second_event_filters = []
			if event_filters_map and 'extra_selected' in event_filters_map:
				second_event_filters = event_filters_map.get('extra_selected', [])
			# Si no está en event_filters_map, intentar desde event_list (formato tupla)
			elif isinstance(event_list[1], tuple) and len(event_list[1]) > 1:
				second_event_filters = event_list[1][1] if isinstance(event_list[1][1], list) else [event_list[1][1]]
			
			# Buscar filtro que excluya airportCheckin
			for filt in second_event_filters:
				if isinstance(filt, dict):
					if (filt.get('subprop_key') == 'type' and 
					    filt.get('subprop_op') == 'is not' and 
					    'airportCheckin' in filt.get('subprop_value', [])):
						is_extras_general_cr = True
						break
	
	# Si es EXTRAS_GENERAL_CR, usar estrategia de métrica compuesta
	if is_extras_general_cr:
		# Definir las 3 sub-métricas (Flexi, Pet, Priority)
		sub_metrics = [
			{
				'name': 'flexi',
				'event_list': [
					('extras_dom_loaded', []),
					('revenue_amount', [{
						'subprop_type': 'event',
						'subprop_key': 'flexi_smart_count',
						'subprop_op': 'greater',
						'subprop_value': [0]
					}])
				]
			},
			{
				'name': 'pet',
				'event_list': [
					('extras_dom_loaded', []),
					('revenue_amount', [{
						'subprop_type': 'event',
						'subprop_key': 'pet_in_cabin_count',
						'subprop_op': 'greater',
						'subprop_value': [0]
					}])
				]
			},
			{
				'name': 'priority',
				'event_list': [
					('extras_dom_loaded', []),
					('revenue_amount', [{
						'subprop_type': 'event',
						'subprop_key': 'priority_boarding_count',
						'subprop_op': 'greater',
						'subprop_value': [0]
					}])
				]
			}
		]
		
		# OPTIMIZACIÓN: Ejecutar las 3 sub-métricas en paralelo
		def fetch_sub_metric(sub_metric):
			"""Helper function para obtener una sub-métrica en paralelo"""
			sub_event_list = sub_metric['event_list']
			sub_event_filters_map = {}
			
			# Construir event_filters_map para esta sub-métrica
			for event_item in sub_event_list:
				if isinstance(event_item, tuple) and len(event_item) > 1:
					event_name = event_item[0]
					event_filters = event_item[1] if isinstance(event_item[1], list) else [event_item[1]]
					if event_filters:
						sub_event_filters_map[event_name] = event_filters
			
			# Llamar recursivamente a get_funnel_data_experiment para esta sub-métrica
			return get_funnel_data_experiment(
				api_key, secret_key, start_date, end_date, experiment_id,
				device, variant, culture, sub_event_list,
				conversion_window, sub_event_filters_map,
				flow_type, bundle_profile, trip_type, pax_adult_count, travel_group, country, hidden_first_step
			)
		
		# Ejecutar las 3 sub-métricas en paralelo usando ThreadPoolExecutor
		sub_results = []
		with ThreadPoolExecutor(max_workers=3) as executor:
			# Enviar todas las tareas en paralelo
			future_to_metric = {executor.submit(fetch_sub_metric, sub_metric): sub_metric for sub_metric in sub_metrics}
			
			# Recopilar resultados a medida que completan (mantener orden)
			sub_results_ordered = [None] * len(sub_metrics)
			for future in as_completed(future_to_metric):
				sub_metric = future_to_metric[future]
				try:
					sub_result = future.result()
					# Mantener el orden original de las sub-métricas
					metric_idx = sub_metrics.index(sub_metric)
					sub_results_ordered[metric_idx] = sub_result
				except Exception as e:
					# Si una sub-métrica falla, agregar error en lugar de fallar todo
					print(f"⚠️ Error obteniendo sub-métrica {sub_metric.get('name', 'unknown')}: {e}")
					metric_idx = sub_metrics.index(sub_metric)
					sub_results_ordered[metric_idx] = {'error': str(e)}
			
			# Filtrar None y usar resultados ordenados
			sub_results = [r for r in sub_results_ordered if r is not None]
		
		# Combinar resultados: sumar conversiones de las 3 sub-métricas
		# La estructura de respuesta de Amplitude: data[0] = {dayFunnels: {series: [[val1, val2], ...], xValues: [dates]}, events: [...]}
		combined_result = sub_results[0].copy() if sub_results else {}
		
		if 'data' in combined_result and sub_results and len(sub_results) > 0:
			from collections import defaultdict
			
			# Obtener la primera sub-métrica como base para estructura
			base_data = sub_results[0].get('data', [])
			if not base_data:
				return combined_result
			
			base_website = base_data[0] if isinstance(base_data, list) else base_data
			base_events = base_website.get('events', [])
			base_dates = base_website.get('dayFunnels', {}).get('xValues', [])
			
			# Inicializar estructura combinada
			combined_series = defaultdict(lambda: defaultdict(int))  # {date_index: {step_index: value}}
			
			# Procesar cada sub-métrica
			for sub_result in sub_results:
				sub_data = sub_result.get('data', [])
				if not sub_data:
					continue
				
				sub_website = sub_data[0] if isinstance(sub_data, list) else sub_data
				sub_series = sub_website.get('dayFunnels', {}).get('series', [])
				sub_dates = sub_website.get('dayFunnels', {}).get('xValues', [])
				
				# Sumar valores por fecha y step
				for date_idx, date_series in enumerate(sub_series):
					if date_idx < len(sub_dates):
						date_key = sub_dates[date_idx]
						# Buscar índice de fecha en base_dates
						if date_key in base_dates:
							base_date_idx = base_dates.index(date_key)
							for step_idx, step_value in enumerate(date_series):
								# Solo sumar el último step (conversión)
								if step_idx == len(date_series) - 1:
									combined_series[base_date_idx][step_idx] += step_value
								# Para el primer step (anchor), tomar el máximo (mismo denominador)
								elif step_idx == 0:
									combined_series[base_date_idx][step_idx] = max(
										combined_series[base_date_idx][step_idx],
										step_value
									)
			
			# Reconstruir estructura combinada
			combined_series_list = []
			for date_idx in range(len(base_dates)):
				date_series = []
				for step_idx in range(len(base_events)):
					value = combined_series[date_idx].get(step_idx, 0)
					date_series.append(value)
				combined_series_list.append(date_series)
			
			# Actualizar resultado combinado
			combined_website = base_website.copy()
			combined_website['dayFunnels']['series'] = combined_series_list
			combined_result['data'] = [combined_website]
		
		# OPTIMIZACIÓN #2: Guardar resultado compuesto en caché
		_amplitude_cache[cache_key] = combined_result
		
		return combined_result
	
	# Si no es EXTRAS_GENERAL_CR, continuar con el flujo normal
	url = 'https://amplitude.com/api/2/funnels'

	# Construir filtros base de segmentación (GLOBAL GHOST ANCHOR)
	# ESTRATEGIA GLOBAL GHOST ANCHOR: Todos los filtros globales (Device, Culture, Flow Type, etc.)
	# se aplican EXCLUSIVAMENTE al primer evento (índice 0). Los eventos siguientes (Steps/Goal)
	# solo reciben filtros técnicos específicos de la métrica para evitar "ceros" en conversiones.
	# Esto resuelve el problema sistémico donde revenue_amount y otros eventos finales no tienen
	# propiedades de segmentación, causando que los filtros fallen y devuelvan 0 conversiones.
	segmentation_filters = []

	# Manejo de filtros con soporte para listas (multiselect)
	# Si el valor es una lista, usar funciones _multiple; si es string, usar funciones individuales
	# Lista vacía o "ALL" significa "sin filtro" (todos los valores)
	
	# Culture filter
	if culture:
		if isinstance(culture, list):
			if len(culture) > 0:
				culture_filter = get_culture_digital_filter_multiple(culture)
				if culture_filter:  # Solo agregar si no está vacío
					segmentation_filters.append(culture_filter)
		else:
			if str(culture).upper() != "ALL":
				culture_filter = get_culture_digital_filter(culture)
				if culture_filter:  # Solo agregar si no está vacío (devuelve dict o "")
					segmentation_filters.append(culture_filter)
	
	# Device filter
	if device:
		if isinstance(device, list):
			if len(device) > 0:
				device_filter = get_device_type_multiple(device)
				if device_filter and isinstance(device_filter, dict):  # Solo agregar si es un dict válido
					segmentation_filters.append(device_filter)
		else:
			if str(device).upper() != "ALL":
				# Normalizar device a minúsculas porque get_device_type espera 'mobile' o 'desktop'
				device_normalized = str(device).lower().strip()
				device_filter = get_device_type(device_normalized)
				# get_device_type devuelve dict si encuentra, [] si no encuentra
				if device_filter and isinstance(device_filter, dict):  # Solo agregar si es un dict válido
					segmentation_filters.append(device_filter)
				elif device_filter == []:
					# Si devuelve lista vacía, el valor no es reconocido
					# Intentar con el valor original por si acaso
					device_filter_alt = get_device_type(device)
					if device_filter_alt and isinstance(device_filter_alt, dict):
						segmentation_filters.append(device_filter_alt)

	# Country filter (propiedad nativa de usuario en Amplitude)
	if country:
		country_filter = get_country_filter(country)
		if country_filter:
			segmentation_filters.append(country_filter)

	# ============================================================
	# CONSOLIDACIÓN: Construir lista unificada de filtros globales
	# ============================================================
	# NOTA: Estos filtros se aplicarán SOLO al evento 0 (Anchor) como parte
	# de la estrategia Global Ghost Anchor para evitar "ceros" en conversiones
	
	# PASO B: Construir filtros contextuales (Flow Type, Bundle Profile, Trip Type, Pax Adult Count)
	# Verificar primero si la métrica tiene filtros explícitos para evitar duplicados
	has_explicit_flow_type_filter = False
	has_explicit_trip_type_filter = False
	has_explicit_bundle_filter = False
	has_explicit_pax_filter = False
	
	# Revisar todos los eventos en event_filters_map para detectar filtros explícitos
	if event_filters_map:
		for event_name, filters in event_filters_map.items():
			if filters:
				filters_list = filters if isinstance(filters, list) else [filters]
				for filt in filters_list:
					if isinstance(filt, dict):
						subprop_key = filt.get('subprop_key')
						if subprop_key == 'flow_type':
							has_explicit_flow_type_filter = True
						elif subprop_key == 'trip_type':
							has_explicit_trip_type_filter = True
						elif subprop_key == 'bundle_profile' or 'bundle' in str(subprop_key).lower():
							has_explicit_bundle_filter = True
						elif subprop_key == 'pax_adult_count' or 'pax' in str(subprop_key).lower():
							has_explicit_pax_filter = True
	
	# ============================================================
	# CONSTRUCCIÓN DE EVENTOS: ESTRATEGIA GLOBAL GHOST ANCHOR
	# ============================================================
	# Evento 0 (Anchor): Filtros globales + filtros técnicos de métrica
	# Eventos > 0 (Steps/Goal): SOLO filtros técnicos de métrica
	# ============================================================
	event_filters_grouped = []
	for idx, event in enumerate(event_list):
		# PASO A: Iniciar lista de filtros para este evento
		event_filters = []
		
		# Extraer el nombre del evento (puede venir como tupla ('evento', [filtros]) o como string)
		if isinstance(event, tuple) and len(event) > 0:
			event_name = event[0]
		elif isinstance(event, str):
			event_name = event
		else:
			event_name = str(event)
		
		# PASO B: ESTRATEGIA GLOBAL GHOST ANCHOR
		# ============================================================
		# REGLA DE NEGOCIO: Aplicar filtros globales SOLO al Evento 0 (Anchor)
		# ============================================================
		# - Evento 0 (Anchor): Aplica TODOS los filtros globales (Device, Culture, Flow Type, etc.)
		#                     + filtros técnicos específicos de la métrica
		# - Eventos > 0 (Steps/Goal): IGNORA filtros globales, aplica SOLO filtros técnicos
		#                             de la métrica (definidos en event_filters_map)
		# ============================================================
		# Esto resuelve el problema de "ceros" en métricas de conversión donde revenue_amount
		# y otros eventos finales no tienen propiedades de segmentación.
		# ============================================================
		is_anchor_event = (idx == 0)
		is_strict_anchor = (idx == 0)
		
		# SOLO el evento 0 (Anchor) recibe filtros globales de segmentación
		# Los eventos siguientes (Steps/Goal) NO reciben filtros globales para evitar "ceros"
		if is_strict_anchor:
			# Device y Culture se aplican SOLO al evento ancla
			event_filters.extend(segmentation_filters)
		
		# PASO C: Construir filtros contextuales (Flow Type, Trip Type, Bundle, Travel Group)
		# Estos filtros ya están configurados para aplicarse solo al evento 0 (is_strict_anchor)
		# como parte de la estrategia Global Ghost Anchor
		
		# 1. TRAVEL GROUP: Solo aplicar en el primer paso
		if travel_group:
			if isinstance(travel_group, list):
				if len(travel_group) > 0 and is_strict_anchor:
					travel_group_filters = get_travel_group_filter_multiple(travel_group, event_name)
					if travel_group_filters:
						event_filters.extend(travel_group_filters)
			else:
				if str(travel_group).upper() != "ALL" and is_strict_anchor:
					travel_group_filters = get_travel_group_filter(travel_group, event_name)
					if travel_group_filters:
						event_filters.extend(travel_group_filters)
		
		# 2. PAX ADULT COUNT: Solo aplicar en el primer paso (compatibilidad hacia atrás)
		elif pax_adult_count and str(pax_adult_count).upper() != "ALL" and not has_explicit_pax_filter:
			if is_strict_anchor:
				pax_adult_count_filter = get_pax_adult_count_filter(pax_adult_count)
				if pax_adult_count_filter:
					event_filters.append(pax_adult_count_filter)
		
		# 3. TRIP TYPE: Solo aplicar en el primer paso
		if trip_type and not has_explicit_trip_type_filter:
			if isinstance(trip_type, list):
				if len(trip_type) > 0 and is_strict_anchor:
					trip_type_filter = get_trip_type_filter_multiple(trip_type)
					if trip_type_filter:
						event_filters.append(trip_type_filter)
			else:
				if str(trip_type).upper() != "ALL" and is_strict_anchor:
					trip_type_filter = get_trip_type_filter(trip_type)
					if trip_type_filter:
						event_filters.append(trip_type_filter)
		
		# 4. FLOW TYPE: Solo aplicar en el primer paso
		if flow_type and not has_explicit_flow_type_filter:
			if isinstance(flow_type, list):
				if len(flow_type) > 0 and is_strict_anchor:
					flow_type_filter = get_flow_type_filter_multiple(flow_type)
					if flow_type_filter:
						event_filters.append(flow_type_filter)
			else:
				if str(flow_type).upper() != "ALL" and is_strict_anchor:
					flow_type_filter = get_flow_type_filter(flow_type)
					if flow_type_filter:
						event_filters.append(flow_type_filter)
		
		# 5. BUNDLE PROFILE: Solo aplicar en el primer paso
		if bundle_profile and not has_explicit_bundle_filter:
			if isinstance(bundle_profile, list):
				if len(bundle_profile) > 0 and is_strict_anchor:
					bundle_filters = get_bundle_filters_multiple(bundle_profile)
					if bundle_filters:
						event_filters.extend(bundle_filters)
			else:
				if str(bundle_profile).upper() != "ALL" and is_strict_anchor:
					bundle_filters = get_bundle_filters(bundle_profile)
					if bundle_filters:
						event_filters.extend(bundle_filters)
		
		# PASO D: Agregar filtros técnicos específicos de la métrica si existen para este evento
		# Estos filtros se aplican a TODOS los eventos (0 y > 0) como parte de la lógica de negocio
		# de la métrica. Son filtros técnicos (ej: seats_count > 0) que validan condiciones específicas.
		if event_filters_map and event_name in event_filters_map:
			additional_filters = event_filters_map[event_name]
			if additional_filters:
				# Si additional_filters es una lista, extender
				if isinstance(additional_filters, list):
					event_filters.extend(additional_filters)
				else:
					# Si es un solo filtro, agregarlo
					event_filters.append(additional_filters)
		
		event_filters_grouped.append({
			"event_type": event_name,  # Usar el nombre extraído del evento
			"filters": event_filters,
			"group_by": []
		})


    
    
	segments = [
						{
							'group_type': 'User',
							'prop': f'gp:[Experiment] {experiment_id}',
							'prop_type': 'user',
							'op': 'is',
							'type': 'property',
							'values': [
								variant,
							],
						},
						# {
						# 	'group_type': 'User',
						# 	'prop': 'device_type',
						# 	'prop_type': 'user',
						# 	'op': 'is',
						# 	'type': 'property',
						# 	'values': get_device_type(device)
						# },
					],

	# Normalizar fechas con precisión horaria para la API de Amplitude
	start_date_formatted = normalize_date_for_amplitude(start_date, default_time="00:00:00", is_end_date=False)
	end_date_formatted = normalize_date_for_amplitude(end_date, default_time="00:00:00", is_end_date=True)
	
	params = {
		'e': [json.dumps(event) for event in event_filters_grouped],
		'start': start_date_formatted,
		'end': end_date_formatted,
		'cs': conversion_window,
		's': [json.dumps(segment) for segment in segments],
		
	}
	
	# Si se solicita tiempo de conversión, agregar parámetro view
	if include_time_data:
		params['view'] = 'time_to_convert'

	headers = {
		'Authorization': f'Basic {api_key}:{secret_key}'
	}
	
	# ============================================================
	# DEBUG: Instrumentación para auditoría de filtros
	# ============================================================
	# Verificar integridad de filtros antes de enviar
	debug_warnings = []
	
	# Verificar que los filtros de segmentación estén presentes en todos los eventos
	if segmentation_filters:
		for event_obj in event_filters_grouped:
			event_name = event_obj.get('event_type', 'unknown')
			event_filters = event_obj.get('filters', [])
			
			# Verificar que los filtros de segmentación estén presentes
			has_device_filter = any(
				f.get('subprop_key') == 'device_type' 
				for f in event_filters 
				if isinstance(f, dict)
			) if device and str(device).upper() != "ALL" else True
			
			has_culture_filter = any(
				f.get('subprop_key') == 'culture' 
				for f in event_filters 
				if isinstance(f, dict)
			) if culture and str(culture).upper() != "ALL" else True
			
			if device and str(device).upper() != "ALL" and not has_device_filter:
				debug_warnings.append(f"⚠️ Evento '{event_name}' NO tiene filtro de device (esperado: {device})")
			
			if culture and str(culture).upper() != "ALL" and not has_culture_filter:
				debug_warnings.append(f"⚠️ Evento '{event_name}' NO tiene filtro de culture (esperado: {culture})")
	
	# Mostrar debug SOLO si el modo debug está activo (encapsulado en expander)
	try:
		import streamlit as st
		# Solo mostrar debug si el modo debug está explícitamente activo
		debug_mode_active = (
			hasattr(st, 'session_state') and 
			st.session_state.get('debug_mode', False)
		)
		
		if debug_mode_active:
			# Mostrar un mensaje informativo antes del expander
			st.info(f"🔍 Modo Debug activo para variante: {variant}")
			debug_info = {
				'experiment_id': experiment_id,
				'variant': variant,
				'device': device,
				'culture': culture,
				'flow_type': flow_type,
				'bundle_profile': bundle_profile,
				'trip_type': trip_type,
				'pax_adult_count': pax_adult_count,
				'segmentation_filters_count': len(segmentation_filters),
				'segmentation_filters': segmentation_filters,
				'events_with_filters': [],
				'warnings': debug_warnings
			}
			
			# Analizar cada evento y sus filtros
			for event_obj in event_filters_grouped:
				event_name = event_obj.get('event_type', 'unknown')
				event_filters = event_obj.get('filters', [])
				
				# Identificar tipos de filtros presentes
				filter_types = []
				for f in event_filters:
					if isinstance(f, dict):
						filter_key = f.get('subprop_key', 'unknown')
						filter_types.append(filter_key)
				
				debug_info['events_with_filters'].append({
					'event': event_name,
					'total_filters': len(event_filters),
					'filter_types': filter_types,
					'filters': event_filters
				})
			
			# Encapsular TODO el debug en un expander que solo se muestra si debug_mode está activo
			with st.expander(f"🕵️ Ver Logs de Debug - Variant: {variant}", expanded=False):
				if debug_warnings:
					st.write("**⚠️ Advertencias:**")
					for warning in debug_warnings:
						st.warning(warning)
					st.write("---")
				
				st.write("**📊 Información de Debug:**")
				st.json(debug_info)
				
				st.write("**🔧 Event Filters Grouped (JSON):**")
				st.json(event_filters_grouped)
				
				st.write("**📤 Params enviados a Amplitude (primeros 1000 chars):**")
				params_str = json.dumps(params, indent=2)
				st.text(params_str[:1000] + ("..." if len(params_str) > 1000 else ""))
	except Exception:
		# Si streamlit no está disponible o hay error, continuar sin debug
		pass
	
	try:
		response = requests.get(url, headers=headers, params=params, auth=HTTPBasicAuth(api_key, secret_key))
		response.raise_for_status()  # Lanza excepción si el status code indica error
		
		response_json = response.json()
		
		# ============================================================
		# DIAGNÓSTICO: Inspección de estructura de respuesta para TTC
		# ============================================================
		print("\n" + "="*80)
		print("🔍 DIAGNÓSTICO: Estructura de respuesta de Amplitude")
		print("="*80)
		print(f"Keys del JSON raíz: {list(response_json.keys())}")
		
		if 'data' in response_json:
			data = response_json['data']
			if isinstance(data, list) and len(data) > 0:
				first_item = data[0]
				print(f"\nTipo de 'data': {type(data)}")
				print(f"Keys del primer elemento de 'data': {list(first_item.keys()) if isinstance(first_item, dict) else 'No es dict'}")
				
				if isinstance(first_item, dict):
					# Inspeccionar estructura de dayFunnels
					if 'dayFunnels' in first_item:
						day_funnels = first_item['dayFunnels']
						print(f"Keys de 'dayFunnels': {list(day_funnels.keys()) if isinstance(day_funnels, dict) else 'No es dict'}")
						
						# Buscar campos relacionados con tiempo
						if isinstance(day_funnels, dict):
							for key in day_funnels.keys():
								if any(time_word in key.lower() for time_word in ['time', 'interval', 'median', 'average', 'mean', 'duration']):
									print(f"  ⏱️  Campo relacionado con tiempo encontrado: '{key}' = {day_funnels[key]}")
					
					# Inspeccionar eventos
					if 'events' in first_item:
						events = first_item['events']
						print(f"\nTipo de 'events': {type(events)}")
						if isinstance(events, list) and len(events) > 0:
							print(f"Primer evento: {events[0]}")
							if isinstance(events[0], dict):
								print(f"  Keys del primer evento: {list(events[0].keys())}")
					
					# Buscar cualquier campo que contenga 'time', 'interval', 'median', etc.
					print(f"\n🔎 Búsqueda de campos relacionados con tiempo en el primer elemento:")
					def search_time_fields(obj, path=""):
						if isinstance(obj, dict):
							for key, value in obj.items():
								current_path = f"{path}.{key}" if path else key
								if any(time_word in key.lower() for time_word in ['time', 'interval', 'median', 'average', 'mean', 'duration', 'step']):
									print(f"  ⏱️  {current_path}: {value}")
								if isinstance(value, (dict, list)):
									search_time_fields(value, current_path)
						elif isinstance(obj, list):
							for i, item in enumerate(obj):
								search_time_fields(item, f"{path}[{i}]")
					
					search_time_fields(first_item)
			elif isinstance(data, dict):
				print(f"\nTipo de 'data': dict")
				print(f"Keys de 'data': {list(data.keys())}")
		
		print("="*80 + "\n")
		# ============================================================
		# FIN DIAGNÓSTICO
		# ============================================================
		
		# Verificar si la API devolvió un error
		if 'error' in response_json:
			error_msg = response_json.get('error', 'Error desconocido de Amplitude')
			error_details = response_json.get('errorDetails', '')
			raise ValueError(
				f"🚨 API Error de Amplitude: {error_msg}\n"
				f"Detalles: {error_details}\n"
				f"Payload enviado: {json.dumps(params, indent=2)}"
			)
		
		# Verificar si la respuesta tiene estructura esperada
		if 'data' not in response_json and 'error' not in response_json:
			raise ValueError(
				f"🚨 Respuesta inesperada de Amplitude. Claves disponibles: {list(response_json.keys())}\n"
				f"Payload enviado: {json.dumps(params, indent=2)}\n"
				f"Response (primeros 500 caracteres): {str(response_json)[:500]}"
			)
		
		# OPTIMIZACIÓN #2: Guardar en caché antes de retornar
		_amplitude_cache[cache_key] = response_json
		
		return response_json
		
	except requests.exceptions.HTTPError as e:
		# Error HTTP (4xx, 5xx)
		error_msg = f"🚨 HTTP Error {response.status_code} de Amplitude"
		try:
			error_response = response.json()
			if 'error' in error_response:
				error_msg += f": {error_response['error']}"
		except:
			error_msg += f": {response.text[:500]}"
		raise ValueError(
			f"{error_msg}\n"
			f"Payload enviado: {json.dumps(params, indent=2)}"
		)
	except requests.exceptions.RequestException as e:
		# Error de conexión, timeout, etc.
		raise ValueError(
			f"🚨 Error de conexión con Amplitude: {str(e)}\n"
			f"Payload enviado: {json.dumps(params, indent=2)}"
		)


def get_variant_funnel(variant):
    """
    Procesa los datos de una variante y genera un DataFrame con datos diarios.
    
    Args:
        variant: Diccionario con datos de la variante que incluye:
            - Data: Datos de la API de Amplitude
            - ExperimentID: ID del experimento
            - Culture: Cultura filtrada
            - Device: Dispositivo filtrado
            - Variant: Nombre de la variante
            
    Returns:
        pd.DataFrame: DataFrame con columnas:
            - Date: Fecha del evento
            - ExperimentID: ID del experimento
            - Funnel Stage: Paso del funnel
            - Culture: Cultura
            - Device: Dispositivo
            - Variant: Variante
            - Event Count: Cantidad de eventos
    """
    
    df = pd.DataFrame({
        'Date': [],
        'ExperimentID': [],
        'Culture': [],
        'Device': [],
        'Variant': [],
        'Event Count': []
    })

    variant_data = variant.get('Data', {})
    
    # Si variant_data está vacío o no existe, verificar si hay un error en la respuesta
    if not variant_data:
        error_info = variant.get('error', 'Error desconocido')
        error_details = variant.get('errorDetails', '')
        experiment_id = variant.get('ExperimentID', 'N/A')
        variant_name = variant.get('Variant', 'N/A')
        raise ValueError(
            f"🚨 No se recibieron datos de Amplitude para la variante '{variant_name}' del experimento '{experiment_id}'\n"
            f"Error: {error_info}\n"
            f"Detalles: {error_details}"
        )
    
    # Verificar si existe la clave 'data'
    if 'data' not in variant_data:
        # Si hay un error en la respuesta, exponerlo
        if 'error' in variant_data:
            error_msg = variant_data.get('error', 'Error desconocido de Amplitude')
            error_details = variant_data.get('errorDetails', '')
            experiment_id = variant.get('ExperimentID', 'N/A')
            variant_name = variant.get('Variant', 'N/A')
            raise ValueError(
                f"🚨 API Error de Amplitude para la variante '{variant_name}' del experimento '{experiment_id}':\n"
                f"Error: {error_msg}\n"
                f"Detalles: {error_details}\n"
                f"Keys disponibles en la respuesta: {list(variant_data.keys())}"
            )
        else:
            raise KeyError(
                f"No existe la clave 'data' en variant_data. Keys disponibles: {list(variant_data.keys())}\n"
                f"Variant: {variant.get('Variant', 'N/A')}, ExperimentID: {variant.get('ExperimentID', 'N/A')}"
            )
    
    
    # Normalizar estructura: puede venir lista o dict
    if isinstance(variant_data['data'], list):
        websites = variant_data['data']
    elif isinstance(variant_data['data'], dict):
        websites = [variant_data['data']]
    else:
        return df

    for website_funnel in websites:
        funnel_website_conversion_data = website_funnel['dayFunnels']['series']
        funnel_stages = website_funnel['events']
        dates = website_funnel['dayFunnels']['xValues']

        for date, data in zip(dates, funnel_website_conversion_data):
            for funnel_stage, value in zip(funnel_stages, data):
                # Si el paso viene como dict de Amplitude, tomar el nombre
                if isinstance(funnel_stage, dict):
                    stage_name = funnel_stage.get('event_type', str(funnel_stage))
                else:
                    stage_name = funnel_stage
                
                new_row = {
                    'Date': pd.to_datetime(date),
                    'ExperimentID': variant['ExperimentID'],
                    'Funnel Stage': stage_name,
                    'Culture': variant['Culture'],
                    'Device': variant['Device'],
                    'Variant': variant['Variant'],
                    'Event Count': int(value)
                }

                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df


def get_variant_funnel_cum(variant, actual_start_date=None, actual_end_date=None):
    """
    Procesa los datos de una variante y genera un DataFrame con datos acumulados.
    
    Args:   
        variant: Diccionario con datos de la variante que incluye:
            - Data: Datos de la API de Amplitude
            - ExperimentID: ID del experimento
            - Culture: Cultura filtrada
            - Device: Dispositivo filtrado
            - Variant: Nombre de la variante
        actual_start_date: Fecha de inicio exacta usada en la query (con hora)
        actual_end_date: Fecha de fin exacta usada en la query (con hora)
            
    Returns:
        pd.DataFrame: DataFrame con columnas:
            - Start Date: Fecha de inicio del período
            - End Date: Fecha de fin del período
            - ExperimentID: ID del experimento
            - Culture: Cultura
            - Device: Dispositivo
            - Variant: Variante
            - Funnel Stage: Paso del funnel
            - Event Count: Cantidad acumulada de eventos
    """
    
    df = pd.DataFrame({
        'Start Date': [],
        'End Date': [],
        'ExperimentID': [],
        'Culture': [],
        'Device': [],
        'Variant': [],
        'Funnel Stage': [],
        'Event Count': []
    })

    variant_data = variant.get('Data', {})
    
    # Si variant_data está vacío o no existe, verificar si hay un error en la respuesta
    if not variant_data:
        error_info = variant.get('error', 'Error desconocido')
        error_details = variant.get('errorDetails', '')
        experiment_id = variant.get('ExperimentID', 'N/A')
        variant_name = variant.get('Variant', 'N/A')
        raise ValueError(
            f"🚨 No se recibieron datos de Amplitude para la variante '{variant_name}' del experimento '{experiment_id}'\n"
            f"Error: {error_info}\n"
            f"Detalles: {error_details}"
        )
    
    # Verificar si existe la clave 'data'
    if 'data' not in variant_data:
        # Si hay un error en la respuesta, exponerlo
        if 'error' in variant_data:
            error_msg = variant_data.get('error', 'Error desconocido de Amplitude')
            error_details = variant_data.get('errorDetails', '')
            experiment_id = variant.get('ExperimentID', 'N/A')
            variant_name = variant.get('Variant', 'N/A')
            raise ValueError(
                f"🚨 API Error de Amplitude para la variante '{variant_name}' del experimento '{experiment_id}':\n"
                f"Error: {error_msg}\n"
                f"Detalles: {error_details}\n"
                f"Keys disponibles en la respuesta: {list(variant_data.keys())}"
            )
        else:
            raise KeyError(
                f"No existe la clave 'data' en variant_data. Keys disponibles: {list(variant_data.keys())}\n"
                f"Variant: {variant.get('Variant', 'N/A')}, ExperimentID: {variant.get('ExperimentID', 'N/A')}"
            )
    
    
    # Normalizar estructura: puede venir lista o dict
    if isinstance(variant_data['data'], list):
        websites = variant_data['data']
    elif isinstance(variant_data['data'], dict):
        websites = [variant_data['data']]
    else:
        return df

    for website_funnel in websites:
        # Usar las fechas exactas de la query en lugar de x_values
        if actual_start_date is not None:
            # Convertir a datetime si es string
            if isinstance(actual_start_date, str):
                start_date_filter = pd.to_datetime(actual_start_date)
            else:
                start_date_filter = pd.to_datetime(actual_start_date)
        else:
            # Fallback: usar x_values si no se proporciona actual_start_date
            day_funnels = website_funnel.get('dayFunnels', {})
            x_values = day_funnels.get('xValues', [])
            start_date_filter = pd.to_datetime(x_values[0]) if x_values else None
        
        if actual_end_date is not None:
            # Convertir a datetime si es string
            if isinstance(actual_end_date, str):
                end_date_filter = pd.to_datetime(actual_end_date)
            else:
                end_date_filter = pd.to_datetime(actual_end_date)
        else:
            # Fallback: usar x_values si no se proporciona actual_end_date
            day_funnels = website_funnel.get('dayFunnels', {})
            x_values = day_funnels.get('xValues', [])
            end_date_filter = pd.to_datetime(x_values[-1]) if x_values else None

        # Pasos del funnel y acumulados
        funnel_stages = website_funnel.get('events', [])
        cumulative_raw = website_funnel.get('cumulativeRaw', [])

        # Validaciones mínimas
        if not cumulative_raw or not funnel_stages:
            continue

        # Alinear cada paso con su acumulado
        for funnel_stage, value in zip(funnel_stages, cumulative_raw):
            # Si el paso viene como dict de Amplitude, tomar el nombre
            if isinstance(funnel_stage, dict):
                stage_name = funnel_stage.get('event_type', str(funnel_stage))
            else:
                stage_name = funnel_stage

            new_row = {
                'Start Date': start_date_filter,
                'End Date': end_date_filter,
                'ExperimentID': variant['ExperimentID'],
                'Culture': variant['Culture'],
                'Device': variant['Device'],
                'Variant': variant['Variant'],
                'Funnel Stage': stage_name,
                'Event Count': int(value)
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    return df


def get_control_treatment_raw_data(
    start_date, 
    end_date, 
    experiment_id, 
    device, 
    culture, 
    event_list,
    conversion_window=1800,
    flow_type="ALL",
    bundle_profile="ALL",
    trip_type="ALL",
    pax_adult_count="ALL",
    travel_group="ALL",
    country=None,
    hidden_first_step=False
):
    """
    Obtiene los datos raw de control y treatment para un experimento.
    
    Args:
        start_date: Fecha de inicio (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        end_date: Fecha de fin (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de tiempo de conversión en segundos (default: 1800 = 30 min)
        flow_type: Tipo de flujo ('DB', 'PB', 'CK', o 'ALL')
        bundle_profile: Perfil de bundle ('ALL', 'Vuela Ligero', 'Smart', 'Full', 'Smart + Full')
        trip_type: Tipo de viaje ('ALL', 'Solo Ida (One Way)', 'Ida y Vuelta (Round Trip)')
        pax_adult_count: Cantidad de adultos ('ALL', '1 Adulto', '2 Adultos', '3 Adultos', '4+ Adultos')
        
    Returns:
        tuple: (control_data, treatment_data) donde cada uno es un diccionario con:
            - Data: Respuesta de la API
            - ExperimentID: ID del experimento
            - Culture: Cultura filtrada
            - Device: Dispositivo filtrado
            - Variant: Nombre de la variante
    """
    # Obtener credenciales
    api_key, secret_key, _ = get_credentials()
    
    
    control_response = get_funnel_data_experiment(
        api_key,
        secret_key,
        start_date,
        end_date,
        experiment_id,
        device,
        "control",
        culture,
        event_list,
        conversion_window,
        None,
        flow_type,
        bundle_profile,
        trip_type,
        pax_adult_count,
        travel_group,
        country,
        hidden_first_step
    )
    
    
    treatment_response = get_funnel_data_experiment(
        api_key,
        secret_key,
        start_date,
        end_date,
        experiment_id,
        device,
        "treatment",
        culture,
        event_list,
        conversion_window,
        None,
        flow_type,
        bundle_profile,
        trip_type,
        pax_adult_count,
        travel_group,
        country,
        hidden_first_step
    )
    
    
    control = {
        'Data': control_response,
        'ExperimentID': experiment_id,
        'Culture': culture,
        'Device': device,
        'Variant': 'control'
    }
    
    treatment = {
        'Data': treatment_response,
        'ExperimentID': experiment_id,
        'Culture': culture,
        'Device': device,
        'Variant': 'treatment'
    }
    
    
    return control, treatment


@st.cache_data(persist="disk", show_spinner=False, ttl=86400)
def final_pipeline(start_date, end_date, experiment_id, device, culture, event_list, conversion_window=1800, event_filters_map=None, flow_type="ALL", bundle_profile="ALL", trip_type="ALL", pax_adult_count="ALL", travel_group="ALL", country=None, hidden_first_step=False, active_variants=None):
    """
    Pipeline completo para análisis de experimentos AB Test.
    Si se pasa active_variants, solo se solicitan datos a la API para esas variantes (evita variantes fantasma).

    Args:
        start_date, end_date, experiment_id, device, culture, event_list: parámetros del análisis
        conversion_window: Ventana de conversión en segundos (default: 1800)
        event_filters_map: Diccionario opcional que mapea eventos a sus filtros adicionales.
        flow_type, bundle_profile, trip_type, pax_adult_count, travel_group: filtros
        country: Filtro de país (propiedad nativa Amplitude)
        hidden_first_step: Si es True, aplica "Inmunidad Contextual" en el paso 0 (ancla)
        active_variants: Opcional. Tuple o lista de variantes a incluir; si es None, se usan todas.

    Returns:
        pd.DataFrame: DataFrame combinado con datos de las variantes (activas o todas)
    """
    all_variants_data = get_all_variants_raw_data(
        start_date,
        end_date,
        experiment_id,
        device,
        culture,
        event_list,
        conversion_window,
        event_filters_map,
        flow_type,
        bundle_profile,
        trip_type,
        pax_adult_count,
        travel_group=travel_group,
        country=country,
        hidden_first_step=hidden_first_step,
        active_variants=active_variants,
    )

    # Procesar cada variante
    all_dataframes = []
    for variant_data in all_variants_data:
        df_variant = get_variant_funnel(variant_data)
        all_dataframes.append(df_variant)

    # Combinar todos los DataFrames
    if all_dataframes:
        df_final = pd.concat(all_dataframes, axis=0, ignore_index=True)
    else:
        df_final = pd.DataFrame()

    return df_final


def get_variant_volumes_overall(
    experiment_id,
    start_date,
    end_date,
    event_list,
    conversion_window=1800,
    event_filters_map=None,
    flow_type="ALL",
    bundle_profile="ALL",
    trip_type="ALL",
    pax_adult_count="ALL",
    travel_group="ALL",
    country=None,
    hidden_first_step=False,
):
    """
    Obtiene el volumen total (primer paso del funnel) por variante en la vista general (sin segmentar).
    Se usa para filtrar variantes fantasma (rollback) antes de hacer las llamadas segmentadas a la API.

    Args:
        experiment_id: ID del experimento en Amplitude
        start_date: Fecha de inicio
        end_date: Fecha de fin
        event_list: Lista de eventos (típicamente solo el primer evento / ancla para minimizar coste)
        conversion_window, event_filters_map, flow_type, bundle_profile, trip_type,
        pax_adult_count, travel_group, country, hidden_first_step: mismos que get_funnel_data_experiment

    Returns:
        dict: Mapeo variant_name -> total count (suma del primer paso del funnel en todos los días)
    """
    variants = get_experiment_variants(experiment_id)
    api_key, secret_key, _ = get_credentials()

    def _volume_for_variant(variant):
        try:
            resp = get_funnel_data_experiment(
                api_key,
                secret_key,
                start_date,
                end_date,
                experiment_id,
                "All",
                variant,
                "All",
                event_list,
                conversion_window,
                event_filters_map,
                flow_type,
                bundle_profile,
                trip_type,
                pax_adult_count,
                travel_group,
                country=country,
                hidden_first_step=hidden_first_step,
            )
            if not resp or "data" not in resp:
                return variant, 0
            data_list = resp.get("data") or []
            if not data_list:
                return variant, 0
            first_group = data_list[0] if isinstance(data_list[0], dict) else {}
            day_funnels = first_group.get("dayFunnels") or {}
            series = day_funnels.get("series") or []
            total = 0
            for day_row in series:
                if isinstance(day_row, (list, tuple)) and len(day_row) > 0:
                    total += int(day_row[0]) if day_row[0] is not None else 0
            return variant, total
        except Exception:
            return variant, 0

    volumes = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_v = {executor.submit(_volume_for_variant, v): v for v in variants}
        for future in as_completed(future_to_v):
            v, count = future.result()
            volumes[v] = count
    return volumes


def filter_active_variants(
    variant_names,
    volumes,
    min_sessions=50,
    min_pct_of_control=0.01,
):
    """
    Filtra la lista de variantes para quedarse solo con las "activas" (suficiente tráfico).
    Elimina variantes fantasma típicas de rollbacks (variant-2, variant-4 con ~0 sesiones).

    Args:
        variant_names: Lista de nombres de variantes (orden típico: control, variant-1, ...)
        volumes: dict variant_name -> total sesiones (primer paso del funnel)
        min_sessions: Mínimo de sesiones para considerar una variante activa
        min_pct_of_control: Mínimo ratio respecto al control (ej. 0.01 = 1%)

    Returns:
        list: Subconjunto de variant_names que son activas. Control siempre se incluye.
    """
    if not variant_names:
        return []
    control_volume = volumes.get("control", 0) or volumes.get(variant_names[0], 0)
    active = []
    for v in variant_names:
        vol = volumes.get(v, 0) or 0
        if v == "control" or v == variant_names[0]:
            active.append(v)
            continue
        if vol < min_sessions:
            continue
        if control_volume > 0 and (vol / control_volume) < min_pct_of_control:
            continue
        active.append(v)
    return active


def get_experiments_list():
    """
    Obtiene la lista de todos los experimentos disponibles en Amplitude.
    
    Returns:
        pd.DataFrame: DataFrame con la información de todos los experimentos
        
    Raises:
        ValueError: Si las credenciales no están disponibles o la respuesta es inválida
        requests.RequestException: Si hay un error en la petición HTTP
    """
    # Obtener credenciales
    _, _, management_api_key = get_credentials()
    
    # Verificar que la management API key esté disponible
    if not management_api_key:
        raise ValueError(
            "AMPLITUDE_MANAGEMENT_KEY no está configurada. "
            "Por favor, verifica tus variables de entorno."
        )
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {management_api_key}',
    }

    params = {
        'limit': '1000',
    }

    try:
        response = requests.get(
            'https://experiment.amplitude.com/api/1/experiments', 
            params=params, 
            headers=headers,
            timeout=30
        )
        
        # Verificar el status code
        response.raise_for_status()
        
        # Verificar que la respuesta no esté vacía
        if not response.text or not response.text.strip():
            raise ValueError(
                f"La respuesta de la API está vacía. "
                f"Status code: {response.status_code}"
            )
        
        # Intentar parsear el JSON
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error al parsear la respuesta JSON: {str(e)}\n"
                f"Status code: {response.status_code}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        # Verificar que la respuesta tenga la estructura esperada
        if 'experiments' not in data:
            raise ValueError(
                f"La respuesta no contiene la clave 'experiments'. "
                f"Claves disponibles: {list(data.keys())}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        return pd.DataFrame(data['experiments'])
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error al realizar la petición a la API de Amplitude: {str(e)}\n"
            f"URL: https://experiment.amplitude.com/api/1/experiments"
        )


def get_experiment_variants(experiment_id):
    """
    Obtiene las variantes de un experimento específico.
    
    Args:
        experiment_id (str): ID del experimento
        
    Returns:
        list: Lista de nombres de variantes del experimento CON GUIONES
    """
    # Obtener credenciales
    _, _, management_api_key = get_credentials()
    
    if not management_api_key:
        raise ValueError(
            "AMPLITUDE_MANAGEMENT_KEY no está configurada. "
            "Por favor, verifica tus variables de entorno."
        )
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {management_api_key}',
    }

    params = {
        'limit': '1000',
    }

    try:
        response = requests.get(
            'https://experiment.amplitude.com/api/1/experiments', 
            params=params, 
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        if not response.text or not response.text.strip():
            raise ValueError(
                f"La respuesta de la API está vacía. "
                f"Status code: {response.status_code}"
            )
        
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error al parsear la respuesta JSON: {str(e)}\n"
                f"Status code: {response.status_code}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        if 'experiments' not in data:
            raise ValueError(
                f"La respuesta no contiene la clave 'experiments'. "
                f"Claves disponibles: {list(data.keys())}"
            )
        
        experiments = data['experiments']
        
        # Buscar el experimento específico
        for exp in experiments:
            if exp.get('key') == experiment_id:
                variants = exp.get('variants', [])
                variant_names = []
                
                
                for variant in variants:
                    if isinstance(variant, dict):
                        name = variant.get('name', variant.get('key', str(variant)))
                    else:
                        name = str(variant)
                    
                    # SIMPLE: Reemplazar espacios por guiones
                    processed_name = name.replace(' ', '-')
                    variant_names.append(processed_name)
                
                return variant_names
        
        # Si no se encuentra el experimento, retornar variantes por defecto
        return ['control', 'treatment']
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error al realizar la petición a la API de Amplitude: {str(e)}"
        )


def get_experiment_variants_original(experiment_id):
    """
    Obtiene las variantes originales (sin procesar) de un experimento específico.
    
    Args:
        experiment_id (str): ID del experimento
        
    Returns:
        list: Lista de nombres originales de variantes del experimento
    """
    # Obtener credenciales
    _, _, management_api_key = get_credentials()
    
    if not management_api_key:
        raise ValueError(
            "AMPLITUDE_MANAGEMENT_KEY no está configurada. "
            "Por favor, verifica tus variables de entorno."
        )
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {management_api_key}',
    }

    params = {
        'limit': '1000',
    }

    try:
        response = requests.get(
            'https://experiment.amplitude.com/api/1/experiments', 
            params=params, 
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        if not response.text or not response.text.strip():
            raise ValueError(
                f"La respuesta de la API está vacía. "
                f"Status code: {response.status_code}"
            )
        
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error al parsear la respuesta JSON: {str(e)}\n"
                f"Status code: {response.status_code}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        if 'experiments' not in data:
            raise ValueError(
                f"La respuesta no contiene la clave 'experiments'. "
                f"Claves disponibles: {list(data.keys())}"
            )
        
        experiments = data['experiments']
        
        # Buscar el experimento específico
        for exp in experiments:
            if exp.get('key') == experiment_id:
                variants = exp.get('variants', [])
                variant_names = []
                
                
                for variant in variants:
                    if isinstance(variant, dict):
                        # Extraer el nombre original de la variante (sin procesar)
                        name = variant.get('name', variant.get('key', str(variant)))
                        variant_names.append(name)
                    else:
                        # Usar el nombre original (sin procesar)
                        variant_names.append(str(variant))
                
                return variant_names
        
        # Si no se encuentra el experimento, retornar variantes por defecto
        return ['control', 'treatment']
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error al realizar la petición a la API de Amplitude: {str(e)}"
        )


@st.cache_data(persist="disk", show_spinner=False, ttl=86400)
def get_all_variants_raw_data(
    start_date,
    end_date,
    experiment_id,
    device,
    culture,
    event_list,
    conversion_window=1800,
    event_filters_map=None,
    flow_type="ALL",
    bundle_profile="ALL",
    trip_type="ALL",
    pax_adult_count="ALL",
    travel_group="ALL",
    country=None,
    hidden_first_step=False,
    include_time_data=False,
    active_variants=None,
):
    """
    Obtiene los datos raw de las variantes activas de un experimento.
    Si se pasa active_variants (tuple o lista), solo se consulta la API para esas variantes;
    así se evitan llamadas para variantes fantasma (rollback).

    Args:
        start_date: Fecha de inicio (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        end_date: Fecha de fin (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        event_filters_map: Diccionario opcional que mapea eventos a sus filtros adicionales.
        flow_type, bundle_profile, trip_type, pax_adult_count, travel_group: filtros
        country: Filtro de país (propiedad nativa Amplitude)
        hidden_first_step: Si es True, aplica "Inmunidad Contextual" en el paso 0
        include_time_data: Si se incluyen datos de tiempo de conversión
        active_variants: Opcional. Tuple o lista de nombres de variantes a consultar.
                         Si es None, se consultan todas las variantes del experimento.

    Returns:
        list: Lista de diccionarios con datos de cada variante (solo variantes activas si se pasó active_variants)
    """
    if active_variants is not None:
        variants = list(active_variants)
    else:
        variants = get_experiment_variants(experiment_id)
    
    
    # Obtener credenciales
    api_key, secret_key, _ = get_credentials()
    
    # OPTIMIZACIÓN #1: Paralelización de requests con ThreadPoolExecutor
    # Hacer todas las requests a Amplitude en paralelo en lugar de secuencial
    # Esto reduce el tiempo de espera de N×5seg a ~5seg (donde N es el número de variantes)
    
    def fetch_variant_data(variant):
        """Helper function para hacer request de una variante en paralelo"""
        variant_response = get_funnel_data_experiment(
            api_key,
            secret_key,
            start_date,
            end_date,
            experiment_id,
            device,
            variant,
            culture,
            event_list,
            conversion_window,
            event_filters_map,
            flow_type,
            bundle_profile,
            trip_type,
            pax_adult_count,
            travel_group,
            country,
            hidden_first_step,
            include_time_data
        )
        
        return {
            'Data': variant_response,
            'ExperimentID': experiment_id,
            'Culture': culture,
            'Device': device,
            'Variant': variant
        }
    
    # Ejecutar requests en paralelo usando ThreadPoolExecutor
    # max_workers=2: Limitar concurrencia para no superar límite de Amplitude (5 concurrent) en desgloses por segmento
    all_variants_data = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Crear futures para cada variante
        future_to_variant = {executor.submit(fetch_variant_data, variant): variant for variant in variants}
        
        # Recopilar resultados a medida que completan
        for future in as_completed(future_to_variant):
            variant = future_to_variant[future]
            try:
                variant_data = future.result()
                all_variants_data.append(variant_data)
            except Exception as e:
                # Si una variante falla, agregar error en lugar de fallar todo
                print(f"⚠️ Error obteniendo datos para variante {variant}: {e}")
                # Agregar datos vacíos para no romper el análisis
                all_variants_data.append({
                    'Data': {'error': str(e)},
                    'ExperimentID': experiment_id,
                    'Culture': culture,
                    'Device': device,
                    'Variant': variant
                })
    
    return all_variants_data


@st.cache_data(persist="disk", show_spinner=False, ttl=86400)
def final_pipeline_cumulative(start_date, end_date, experiment_id, device, culture, event_list, conversion_window=1800, event_filters_map=None, flow_type="ALL", bundle_profile="ALL", trip_type="ALL", pax_adult_count="ALL", travel_group="ALL", country=None, hidden_first_step=False, active_variants=None):
    """
    Pipeline completo para análisis de experimentos AB Test con datos acumulados.
    Si se pasa active_variants, solo se solicitan datos a la API para esas variantes.

    Args:
        start_date, end_date, experiment_id, device, culture, event_list: parámetros del análisis
        conversion_window, event_filters_map, flow_type, bundle_profile, trip_type,
        pax_adult_count, travel_group, country, hidden_first_step: igual que final_pipeline
        active_variants: Opcional. Tuple o lista de variantes a incluir; si es None, se usan todas.

    Returns:
        pd.DataFrame: DataFrame combinado con datos acumulados de las variantes (activas o todas)
    """
    all_variants_data = get_all_variants_raw_data(
        start_date,
        end_date,
        experiment_id,
        device,
        culture,
        event_list,
        conversion_window,
        event_filters_map,
        flow_type,
        bundle_profile,
        trip_type,
        pax_adult_count,
        travel_group,
        country=country,
        hidden_first_step=hidden_first_step,
        active_variants=active_variants,
    )

    # Procesar cada variante con datos acumulados
    all_dataframes = []
    for variant_data in all_variants_data:
        # Pasar las fechas exactas a get_variant_funnel_cum
        df_variant = get_variant_funnel_cum(variant_data, actual_start_date=start_date, actual_end_date=end_date)
        all_dataframes.append(df_variant)

    # Combinar todos los DataFrames
    if all_dataframes:
        df_final = pd.concat(all_dataframes, axis=0, ignore_index=True)
    else:
        df_final = pd.DataFrame()

    return df_final

