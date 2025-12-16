"""
Módulo para cargar automáticamente métricas desde las carpetas de metrics/.

Este módulo escanea las carpetas en metrics/ y detecta automáticamente
todas las métricas definidas en archivos *_metrics.py, organizándolas
por carpeta y generando información para mostrar en el dashboard.
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple
import inspect
import time


def is_valid_metric(obj: Any) -> bool:
    """
    Verifica si un objeto es una métrica válida.
    
    Una métrica válida debe ser un diccionario con la estructura:
    {'events': [('evento', [filtros]), ...]}
    
    Args:
        obj: Objeto a verificar
        
    Returns:
        bool: True si es una métrica válida, False en caso contrario
    """
    if not isinstance(obj, dict):
        return False
    
    if 'events' not in obj:
        return False
    
    events = obj['events']
    if not isinstance(events, list) or len(events) < 2:
        return False
    
    # Verificar que cada evento sea una tupla ('evento', [filtros])
    for event_item in events:
        if isinstance(event_item, tuple):
            if len(event_item) < 1:
                return False
            # El primer elemento debe ser un string (nombre del evento)
            if not isinstance(event_item[0], str):
                return False
            # El segundo elemento (si existe) debe ser una lista de filtros
            if len(event_item) >= 2 and not isinstance(event_item[1], list):
                return False
        elif isinstance(event_item, str):
            # Formato antiguo: solo string, también es válido
            pass
        else:
            return False
    
    return True


def get_event_name(event_item: Any) -> str:
    """
    Extrae el nombre del evento de un item (puede ser tupla o string).
    
    Args:
        event_item: Item del evento (tupla o string)
        
    Returns:
        str: Nombre del evento
    """
    if isinstance(event_item, tuple) and len(event_item) > 0:
        return event_item[0]
    elif isinstance(event_item, str):
        return event_item
    return "-"


def get_event_filters(event_item: Any) -> List[Any]:
    """
    Extrae los filtros de un item de evento.
    
    Args:
        event_item: Item del evento (tupla o string)
        
    Returns:
        List: Lista de filtros (puede estar vacía)
    """
    if isinstance(event_item, tuple) and len(event_item) >= 2:
        filters_list = event_item[1]
        if isinstance(filters_list, list):
            return filters_list
    return []


def load_metrics_from_file(file_path: Path, category: str) -> Dict[str, Dict]:
    """
    Carga todas las métricas válidas desde un archivo de métricas.
    
    Args:
        file_path: Ruta al archivo de métricas
        category: Categoría/carpeta de la métrica (ej: 'baggage', 'seats')
        
    Returns:
        Dict: Diccionario con {nombre_metric: config_metric}
    """
    metrics = {}
    
    try:
        # Limpiar caché de módulos relacionados con este archivo
        # Buscar y eliminar módulos cacheados que coincidan con el patrón
        module_pattern = f"metrics_{category}_{file_path.stem}"
        modules_to_remove = [
            name for name in sys.modules.keys() 
            if name.startswith(module_pattern) or name == f"src.metrics.{category}.{file_path.stem}"
        ]
        for module_name in modules_to_remove:
            del sys.modules[module_name]
        
        # Generar un nombre único para el módulo para evitar caché
        module_name = f"metrics_{category}_{file_path.stem}_{int(time.time() * 1000000)}"
        
        # Cargar el módulo dinámicamente
        spec = importlib.util.spec_from_file_location(
            module_name,
            file_path
        )
        if spec is None or spec.loader is None:
            return metrics
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Buscar todas las variables que sean métricas válidas
        for name, obj in inspect.getmembers(module):
            # Ignorar imports, funciones, clases, etc.
            if name.startswith('_'):
                continue
            
            # Verificar si es una métrica válida
            if is_valid_metric(obj):
                # Usar el nombre de la variable directamente (nomenclatura abreviada)
                # Ejemplo: SEATS_WCR, BAGGAGE_NSR, etc.
                display_name = name
                
                metrics[display_name] = obj
        
    except Exception as e:
        print(f"Error cargando métricas desde {file_path}: {e}")
    
    return metrics


def generate_display_name(var_name: str, emoji: str = '') -> str:
    """
    Genera un nombre de display legible a partir del nombre de variable.
    Maneja la nueva nomenclatura estándar: [STEP]_[TYPE], [STEP]_DB_[TYPE], etc.
    
    Args:
        var_name: Nombre de la variable (ej: 'SEATS_WCR', 'BAGGAGE_DB_NSR')
        emoji: Emoji para la categoría (opcional, por defecto vacío)
        
    Returns:
        str: Nombre de display (ej: 'Website Conversion Rate Seats')
    """
    # Mapeo de tipos de métricas
    metric_type_map = {
        'WCR': 'Website Conversion Rate',
        'NSR': 'Next Step Rate',
        'A2C': 'Add to Cart',
        'CR': 'Cr',
        'SELECTION_RATE': 'Selection Rate',
        'CONTINUE_RATE': 'Continue Rate',
    }
    
    # Mapeo de steps/categorías
    step_map = {
        'SEATS': 'Seats',
        'BAGGAGE': 'Baggage',
        'PAYMENT': 'Payment',
        'PASSENGERS': 'Passengers',
        'FLIGHT': 'Flight',
        'EXTRAS': 'Extras',
        'CABIN_BAG': 'Cabin Bag',
        'CHECKED_BAG': 'Checked Bag',
        'OUTBOUND_SEAT': 'Outbound Seat',
        'INBOUND_SEAT': 'Inbound Seat',
        'OUTBOUND_FLIGHT': 'Outbound Flight',
        'INBOUND_FLIGHT': 'Inbound Flight',
        'PRIORITY_BOARDING': 'Priority Boarding',
        'PET': 'Pet',
        'INSURANCE': 'Insurance',
        'FLEXI': 'Flexi',
        'EXTRAS_GENERAL': 'Extras General',
        'DISCOUNT_CLUB': 'Discount Club',
        'ANCILLARY_MODAL': 'Ancillary Modal',
        'AIRPORT_CHECKIN': 'Airport Checkin',
    }
    
    # Mapeo de modificadores
    modifier_map = {
        'DB': 'DB',
        'VUELA_LIGERO': 'Vuela Ligero',
        'WITH_SELECTION': 'With Selection',
        'WITH_BUNDLE': 'With Bundle',
    }
    
    name_parts = var_name.split('_')
    
    # Detectar el tipo de métrica (último elemento o penúltimo si hay DB)
    metric_type = None
    step = None
    modifiers = []
    db_modifier = None
    
    # Casos especiales primero
    if var_name == 'PAYMENT_TO_REVENUE':
        base_name = 'Payment To Revenue'
        if emoji:
            return f"{emoji} {base_name}"
        return base_name
    
    # Buscar tipo de métrica (WCR, NSR, A2C, CR) al final
    if len(name_parts) >= 2:
        # Verificar si el último es un tipo de métrica
        last_part = name_parts[-1]
        if last_part in metric_type_map:
            metric_type = metric_type_map[last_part]
            # El penúltimo podría ser DB
            if len(name_parts) >= 3 and name_parts[-2] == 'DB':
                db_modifier = 'DB'
                # El step está antes de DB
                remaining = name_parts[:-2]
            else:
                remaining = name_parts[:-1]
        # Verificar si hay SELECTION_RATE o CONTINUE_RATE (dos partes)
        elif len(name_parts) >= 2 and f"{name_parts[-2]}_{name_parts[-1]}" in metric_type_map:
            metric_type = metric_type_map[f"{name_parts[-2]}_{name_parts[-1]}"]
            remaining = name_parts[:-2]
        else:
            # No hay tipo de métrica al final, podría ser un nombre especial
            remaining = name_parts
    
    # Identificar el step y modificadores
    step_candidates = []
    used_indices = set()
    
    # Primero buscar steps (combinaciones de dos partes primero para mayor especificidad)
    for i, part in enumerate(remaining):
        if i in used_indices:
            continue
        # Verificar combinaciones de dos partes primero (más específicas)
        if i < len(remaining) - 1:
            two_part = f"{part}_{remaining[i+1]}"
            if two_part in step_map:
                step_candidates.append((i, step_map[two_part], 2))
                used_indices.add(i)
                used_indices.add(i + 1)
        # Verificar si es un step completo de una parte
        if i not in used_indices and part in step_map:
            step_candidates.append((i, step_map[part], 1))
            used_indices.add(i)
    
    # Tomar el step más largo (más específico)
    if step_candidates:
        # Ordenar por longitud del nombre (más específico primero)
        step_candidates.sort(key=lambda x: len(x[1]), reverse=True)
        best_step = step_candidates[0]
        step = best_step[1]
        step_start_idx = best_step[0]
        step_length = best_step[2]
        step_end_idx = step_start_idx + step_length
        
        # Procesar partes antes del step (modificadores)
        for i in range(step_start_idx):
            if i in used_indices:
                continue
            part = remaining[i]
            # Verificar combinaciones de dos partes para modificadores
            if i < len(remaining) - 1:
                two_part = f"{part}_{remaining[i+1]}"
                if two_part in modifier_map:
                    modifiers.append(modifier_map[two_part])
                    used_indices.add(i)
                    used_indices.add(i + 1)
                    continue
            if part in modifier_map:
                modifiers.append(modifier_map[part])
                used_indices.add(i)
            elif part == 'DB':
                db_modifier = 'DB'
                used_indices.add(i)
        
        # Procesar partes después del step (modificadores adicionales)
        i = step_end_idx
        while i < len(remaining):
            if i in used_indices:
                i += 1
                continue
            part = remaining[i]
            # Verificar combinaciones de dos partes para modificadores
            if i < len(remaining) - 1:
                two_part = f"{part}_{remaining[i+1]}"
                if two_part in modifier_map:
                    modifiers.append(modifier_map[two_part])
                    used_indices.add(i)
                    used_indices.add(i + 1)
                    i += 2
                    continue
            if part in modifier_map:
                modifiers.append(modifier_map[part])
                used_indices.add(i)
            elif part == 'DB':
                db_modifier = 'DB'
                used_indices.add(i)
            i += 1
    else:
        # No se encontró step conocido, usar todas las partes como step
        step = ' '.join(word.capitalize() for word in remaining)
    
    # Construir el nombre final
    # Formato: [Tipo de Métrica] [Step] [Modificadores]
    name_parts_final = []
    
    # Agregar tipo de métrica primero
    if metric_type:
        name_parts_final.append(metric_type)
    
    # Agregar step
    if step:
        name_parts_final.append(step)
    
    # Agregar DB si existe (después del step)
    if db_modifier:
        name_parts_final.append(db_modifier)
    
    # Agregar otros modificadores al final
    if modifiers:
        name_parts_final.extend(modifiers)
    
    # Si no se construyó nada, usar fallback
    if not name_parts_final:
        base_name = ' '.join(word.capitalize() for word in name_parts)
    else:
        base_name = ' '.join(name_parts_final)
    
    # Agregar emoji al inicio solo si se proporciona
    if emoji:
        return f"{emoji} {base_name}"
    return base_name


def load_all_metrics(metrics_root: Path = None) -> Dict[str, Dict[str, Dict]]:
    """
    Carga todas las métricas desde todas las carpetas de metrics/.
    
    Args:
        metrics_root: Ruta raíz de la carpeta metrics/ (por defecto: relativa a este archivo)
        
    Returns:
        Dict: Diccionario organizado por categoría:
        {
            'baggage': {
                'NSR Baggage': {'events': [...]},
                ...
            },
            'seats': {...},
            ...
        }
    """
    if metrics_root is None:
        # Obtener la ruta del directorio actual (utils/)
        current_dir = Path(__file__).resolve().parent
        # Subir un nivel y entrar a metrics/
        metrics_root = current_dir.parent / 'metrics'
    else:
        metrics_root = Path(metrics_root)
    
    if not metrics_root.exists():
        return {}
    
    all_metrics = {}
    
    # Escanear cada subcarpeta en metrics/
    for category_dir in metrics_root.iterdir():
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        
        # Buscar archivos *_metrics.py en esta carpeta
        metrics_files = list(category_dir.glob('*_metrics.py'))
        
        if not metrics_files:
            continue
        
        category_metrics = {}
        
        # Cargar métricas de cada archivo
        for metrics_file in metrics_files:
            file_metrics = load_metrics_from_file(metrics_file, category)
            category_metrics.update(file_metrics)
        
        if category_metrics:
            all_metrics[category] = category_metrics
    
    return all_metrics


def get_metrics_info(metrics_dict: Dict[str, Dict]) -> List[Dict[str, str]]:
    """
    Genera información de display para las métricas.
    
    Args:
        metrics_dict: Diccionario de métricas {display_name: config}
        
    Returns:
        List[Dict]: Lista de diccionarios con información para mostrar
    """
    info_list = []
    
    for display_name, metric_config in metrics_dict.items():
        events = metric_config.get('events', [])
        
        if not events:
            continue
        
        # Extraer información de eventos
        initial_event = get_event_name(events[0]) if events else "-"
        final_event = get_event_name(events[-1]) if len(events) > 1 else "-"
        
        # Extraer información de filtros
        filters_info = []
        for event_item in events:
            event_filters = get_event_filters(event_item)
            if event_filters:
                # Intentar obtener descripción del filtro
                filter_descriptions = []
                for filt in event_filters:
                    if callable(filt):
                        # Si es una función, intentar obtener su nombre
                        filter_descriptions.append(filt.__name__ if hasattr(filt, '__name__') else 'custom')
                    else:
                        filter_descriptions.append(str(filt))
                
                if filter_descriptions:
                    filters_info.append(', '.join(filter_descriptions))
        
        # Construir descripción de filtros
        if filters_info:
            # Si todos los eventos tienen los mismos filtros, simplificar
            if len(set(filters_info)) == 1:
                filters_desc = filters_info[0]
            else:
                unique_filters = ', '.join(set(filters_info))
                filters_desc = f"Variados ({unique_filters})"
        else:
            filters_desc = "Ninguno"
        
        info_list.append({
            'Métrica': display_name,
            'Evento Inicial': initial_event,
            'Evento Final': final_event,
            'Filtros': filters_desc
        })
    
    return info_list


def get_all_metrics_flat(metrics_by_category: Dict[str, Dict[str, Dict]] = None) -> Dict[str, Dict]:
    """
    Obtiene todas las métricas en un diccionario plano (sin categorías).
    
    Args:
        metrics_by_category: Diccionario organizado por categoría (si None, carga automáticamente)
        
    Returns:
        Dict: Diccionario plano {display_name: config}
    """
    if metrics_by_category is None:
        metrics_by_category = load_all_metrics()
    
    flat_metrics = {}
    for category_metrics in metrics_by_category.values():
        flat_metrics.update(category_metrics)
    
    return flat_metrics

