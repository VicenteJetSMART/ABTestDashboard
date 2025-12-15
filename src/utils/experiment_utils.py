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
from src.utils.amplitude_filters import get_culture_digital_filter, get_device_type, get_flow_type_filter, get_bundle_filters, get_trip_type_filter, get_pax_adult_count_filter, get_travel_group_filter
import sys
from io import StringIO

# Variable global para almacenar logs
_logs = []

def get_logs():
    """Obtiene y limpia los logs capturados"""
    global _logs
    logs = _logs.copy()
    _logs = []  # Limpiar logs después de obtenerlos
    return logs


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

def get_funnel_data_experiment(api_key, secret_key, start_date, end_date, experiment_id, device, variant, culture, event_list, conversion_window=1800, event_filters_map=None, flow_type="ALL", bundle_profile="ALL", trip_type="ALL", pax_adult_count="ALL", travel_group="ALL", hidden_first_step=False):
	"""
	Obtiene datos de funnel desde la API de Amplitude para un experimento específico.
	
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
	url = 'https://amplitude.com/api/2/funnels'

	# Construir filtros base de segmentación (siempre se aplican a todos los eventos)
	# Estos son filtros globales que se aplican a todos los eventos del funnel
	# CRÍTICO: Estos filtros DEBEN estar presentes en TODOS los eventos para mantener el cohorte
	segmentation_filters = []

	# Comparación case-insensitive para evitar problemas con "ALL", "All", "all"
	# CRÍTICO: Normalizar valores a minúsculas antes de pasarlos a las funciones de filtros
	# porque get_device_type espera 'mobile' o 'desktop' en minúsculas
	if culture and str(culture).upper() != "ALL":
		culture_filter = get_culture_digital_filter(culture)
		if culture_filter:  # Solo agregar si no está vacío (devuelve dict o "")
			segmentation_filters.append(culture_filter)

	if device and str(device).upper() != "ALL":
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

	# ============================================================
	# CONSOLIDACIÓN: Construir lista unificada de TODOS los filtros globales
	# ============================================================
	# CRÍTICO: Todos los filtros globales deben aplicarse a TODOS los eventos
	# para garantizar la integridad del cohorte en todo el funnel
	
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
	# CONSTRUCCIÓN DE EVENTOS: Aplicar TODOS los filtros a TODOS los eventos
	# CON MAPEO DE PROPIEDADES SEGÚN EL TIPO DE EVENTO
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
		
		# PASO B: Agregar SIEMPRE los filtros de segmentación (Device, Culture)
		# Estos filtros garantizan que el cohorte sea consistente en todo el funnel
		event_filters.extend(segmentation_filters)
		
		# PASO C: Construir filtros contextuales con "Inmunidad Contextual" para Ghost Anchors
		# EXCEPCIÓN: revenue_amount (y payment_confirmation_loaded) tienen propiedades rotas/vacías para flow_type y bundle_profile.
		# - flow_type: Propiedad rota/vacía (siempre da 0 al filtrar)
		# - bundle_profile: No tiene bundle_smart_count ni bundle_full_count (solo strings de nombres)
		# El filtrado estricto en el inicio del funnel (Step 1) garantiza la integridad del cohorte.
		
		# Detectar si el evento actual es revenue_amount o payment_confirmation_loaded (propiedades flow_type y bundle_profile rotas)
		is_payment_confirmation = event_name and ('revenue_amount' in str(event_name).lower() or 'payment_confirmation_loaded' in str(event_name).lower())
		
		# ============================================================
		# INMUNIDAD CONTEXTUAL: Regla de exclusión de filtros para Ghost Anchors
		# ============================================================
		# Si hay un Ghost Anchor activo (hidden_first_step == True):
		# - Paso 0 (Ancla): APLICAR TODOS los filtros (Strict Mode) - aquí filtramos el cohorte
		# - Pasos Intermedios (idx > 0): SKIP filtros Flow/Trip/Bundle (confiamos en el filtro del Paso 0)
		# - Paso Final (payment_confirmation_loaded): Mantener lógica especial existente
		# ============================================================
		should_skip_context = False
		if hidden_first_step and idx > 0:
			# Si tenemos un ancla fantasma activa y NO es el primer evento (el ancla), relajamos los filtros
			should_skip_context = True
		
		# Flow Type: Agregar según reglas de Inmunidad Contextual
		if flow_type and str(flow_type).upper() != "ALL" and not has_explicit_flow_type_filter and not is_payment_confirmation and not should_skip_context:
			flow_type_filter = get_flow_type_filter(flow_type)
			if flow_type_filter:
				event_filters.append(flow_type_filter)
		
		# Trip Type: Agregar según reglas de Inmunidad Contextual
		if trip_type and str(trip_type).upper() != "ALL" and not has_explicit_trip_type_filter and not should_skip_context:
			trip_type_filter = get_trip_type_filter(trip_type)
			if trip_type_filter:
				event_filters.append(trip_type_filter)
		
		# Bundle Profile: Agregar según reglas de Inmunidad Contextual
		if bundle_profile and str(bundle_profile).upper() != "ALL" and not has_explicit_bundle_filter and not is_payment_confirmation and not should_skip_context:
			bundle_filters = get_bundle_filters(bundle_profile)
			if bundle_filters:
				event_filters.extend(bundle_filters)
		
		# Travel Group: Agregar según reglas de Inmunidad Contextual
		# CRÍTICO: Verificar si debemos saltar contexto (para eventos intermedios ciegos como extra_selected)
		# La única excepción es revenue_amount (y payment_confirmation_loaded) que siempre acepta pax counts.
		if travel_group and str(travel_group).upper() != "ALL":
			# Aplicar filtro SI: (No estamos en modo skip) O (Es el evento de pago/revenue)
			if not should_skip_context or is_payment_confirmation:
				travel_group_filters = get_travel_group_filter(travel_group, event_name)
				if travel_group_filters:
					event_filters.extend(travel_group_filters)
		# Pax Adult Count: Agregar SIEMPRE si travel_group no está disponible (compatibilidad hacia atrás)
		# También protegido por should_skip_context
		elif pax_adult_count and str(pax_adult_count).upper() != "ALL" and not has_explicit_pax_filter:
			if not should_skip_context or is_payment_confirmation:
				pax_adult_count_filter = get_pax_adult_count_filter(pax_adult_count)
				if pax_adult_count_filter:
					event_filters.append(pax_adult_count_filter)
		
		# PASO D: Agregar filtros específicos de la métrica si existen para este evento
		# Estos filtros se agregan DESPUÉS de los globales, permitiendo que la métrica
		# tenga filtros adicionales específicos sin perder los filtros globales
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
	
	# Mostrar debug si hay advertencias o si está en modo debug
	try:
		import streamlit as st
		show_debug = (
			len(debug_warnings) > 0 or 
			(hasattr(st, 'session_state') and st.session_state.get('debug_mode', False))
		)
		
		if show_debug:
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
			
			# Mostrar debug
			with st.expander(f"🕵️ DEBUG PAYLOAD - Variant: {variant}", expanded=(len(debug_warnings) > 0)):
				if debug_warnings:
					for warning in debug_warnings:
						st.warning(warning)
				st.json(debug_info)
				st.write("**Event Filters Grouped (JSON):**")
				st.json(event_filters_grouped)
				st.write("**Params enviados a Amplitude (primeros 1000 chars):**")
				params_str = json.dumps(params, indent=2)
				st.text(params_str[:1000] + ("..." if len(params_str) > 1000 else ""))
	except Exception:
		# Si streamlit no está disponible o hay error, continuar sin debug
		pass
	
	try:
		response = requests.get(url, headers=headers, params=params, auth=HTTPBasicAuth(api_key, secret_key))
		response.raise_for_status()  # Lanza excepción si el status code indica error
		
		response_json = response.json()
		
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


def final_pipeline(start_date, end_date, experiment_id, device, culture, event_list, conversion_window=1800, event_filters_map=None, flow_type="ALL", bundle_profile="ALL", trip_type="ALL", pax_adult_count="ALL", travel_group="ALL", hidden_first_step=False):
    """
    Pipeline completo para análisis de experimentos AB Test.
    
    Args:
        start_date: Fecha de inicio (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        end_date: Fecha de fin (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        event_filters_map: Diccionario opcional que mapea eventos a sus filtros adicionales.
                           Formato: {event_name: [filter1, filter2, ...]}
        flow_type: Tipo de flujo ('DB', 'PB', 'CK', o 'ALL')
        bundle_profile: Perfil de bundle ('ALL', 'Vuela Ligero', 'Smart', 'Full', 'Smart + Full')
        trip_type: Tipo de viaje ('ALL', 'Solo Ida (One Way)', 'Ida y Vuelta (Round Trip)')
        pax_adult_count: Cantidad de adultos ('ALL', '1 Adulto', '2 Adultos', '3 Adultos', '4+ Adultos')
        hidden_first_step: Si es True, aplica "Inmunidad Contextual": solo filtra Flow/Trip/Bundle en el paso 0 (ancla)
        
    Returns:
        pd.DataFrame: DataFrame combinado con datos de todas las variantes
    """
    # Obtener datos de todas las variantes
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
        pax_adult_count
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
    hidden_first_step=False
):
    """
    Obtiene los datos raw de todas las variantes de un experimento.
    
    Args:
        start_date: Fecha de inicio (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        end_date: Fecha de fin (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        event_filters_map: Diccionario opcional que mapea eventos a sus filtros adicionales.
                           Formato: {event_name: [filter1, filter2, ...]}
        flow_type: Tipo de flujo ('DB', 'PB', 'CK', o 'ALL')
        bundle_profile: Perfil de bundle ('ALL', 'Vuela Ligero', 'Smart', 'Full', 'Smart + Full')
        trip_type: Tipo de viaje ('ALL', 'Solo Ida (One Way)', 'Ida y Vuelta (Round Trip)')
        pax_adult_count: Cantidad de adultos ('ALL', '1 Adulto', '2 Adultos', '3 Adultos', '4+ Adultos')
        hidden_first_step: Si es True, aplica "Inmunidad Contextual": solo filtra Flow/Trip/Bundle en el paso 0 (ancla)
        
    Returns:
        list: Lista de diccionarios con datos de cada variante
    """
    # Obtener las variantes del experimento
    variants = get_experiment_variants(experiment_id)
    
    
    # Obtener credenciales
    api_key, secret_key, _ = get_credentials()
    
    all_variants_data = []
    
    # Obtener datos para cada variante
    for variant in variants:
        
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
            hidden_first_step
        )
        
        variant_data = {
            'Data': variant_response,
            'ExperimentID': experiment_id,
            'Culture': culture,
            'Device': device,
            'Variant': variant
        }
        
        all_variants_data.append(variant_data)
    
    
    return all_variants_data


def final_pipeline_cumulative(start_date, end_date, experiment_id, device, culture, event_list, conversion_window=1800, event_filters_map=None, flow_type="ALL", bundle_profile="ALL", trip_type="ALL", pax_adult_count="ALL", travel_group="ALL", hidden_first_step=False):
    """
    Pipeline completo para análisis de experimentos AB Test con datos acumulados.
    
    Args:
        start_date: Fecha de inicio (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        end_date: Fecha de fin (puede ser str YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, ISO, o datetime)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        event_filters_map: Diccionario opcional que mapea eventos a sus filtros adicionales.
                           Formato: {event_name: [filter1, filter2, ...]}
        flow_type: Tipo de flujo ('DB', 'PB', 'CK', o 'ALL')
        bundle_profile: Perfil de bundle ('ALL', 'Vuela Ligero', 'Smart', 'Full', 'Smart + Full')
        trip_type: Tipo de viaje ('ALL', 'Solo Ida (One Way)', 'Ida y Vuelta (Round Trip)')
        pax_adult_count: Cantidad de adultos ('ALL', '1 Adulto', '2 Adultos', '3 Adultos', '4+ Adultos')
        hidden_first_step: Si es True, aplica "Inmunidad Contextual": solo filtra Flow/Trip/Bundle en el paso 0 (ancla)
        
    Returns:
        pd.DataFrame: DataFrame combinado con datos acumulados de todas las variantes
    """
    # Obtener datos de todas las variantes
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
        hidden_first_step
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

