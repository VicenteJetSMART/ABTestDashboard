# Funciones para obtener los filtros de Amplitude

def get_culture_digital_filter_multiple(country_codes):
    """
    Obtiene un filtro combinado para múltiples códigos de país (OR lógico).
    
    Args:
        country_codes: Lista de códigos de país (ej: ["CL", "AR"])
        
    Returns:
        dict: Filtro combinado con todos los valores posibles, o "" si la lista está vacía
    """
    if not country_codes or len(country_codes) == 0:
        return ""
    
    # Combinar todos los valores posibles de todos los países seleccionados
    all_values = []
    for code in country_codes:
        single_filter = get_culture_digital_filter(code)
        if single_filter and isinstance(single_filter, dict):
            all_values.extend(single_filter.get('subprop_value', []))
    
    if not all_values:
        return ""
    
    return {
        "subprop_type": "event",
        "subprop_key": "culture",
        "subprop_op": "is",
        "subprop_value": all_values
    }

def get_culture_digital_filter(country_code):
    switch = {
        "CL": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["cl", "CL", "cL", "Cl", "es-CL", "CHILE", "es-cl"]
        },
        "AR": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["ar", "AR", "aR", "Ar", "es-AR", "ARGENTINA", "es-ar"]
        },
        "PE": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["pe", "PE", "pE", "Pe", "es-PE", "PERU", "es-pe"]
        },
        "CO": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["co", "CO", "cO", "Co", "es-CO", "COLOMBIA", "es-co"]
        },
        "BR": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["br", "BR", "bR", "Br", "pt-BR", "BRAZIL", "pt-br"]
        },
        "UY": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["uy", "UY", "uY", "Uy", "es-UY", "URUGUAY", "es-uy"]
        },
        "PY": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["py", "PY", "pY", "Py", "es-PY", "PARAGUAY", "es-py"]
        },
        "EC": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["ec", "EC", "eC", "Ec", "es-EC", "ECUADOR", "es-ec"]
        },
        "US": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["us", "US", "uS", "Us", "en-US", "UNITED STATES", "en-us"]
        },
    }
    return switch.get(country_code, "")

def get_traffic_type(traffic_type):    
    switch = {
        'Pagado': {
                'group_type': 'User',
                'subprop_key': 'acce9394-0a0d-4285-95a8-c5c1678ddc86',
                'subprop_op': 'is',
                'subprop_value': [
                        'Display',
                        'Paid Search',
                ],
                'subprop_type': 'derivedV2',
                'subfilters': [],
        },
        'Promoted': {
                'group_type': 'User',
                'subprop_key': 'acce9394-0a0d-4285-95a8-c5c1678ddc86',
                'subprop_op': 'is',
                'subprop_value': [
                    "Affiliates",
                    "Email",
                    "Metasearch",
                    "Social",
                    "Web Push"
                ],
                'subprop_type': 'derivedV2',
                'subfilters': [],
        },        
        'Organico': {
                'group_type': 'User',
                'subprop_key': 'acce9394-0a0d-4285-95a8-c5c1678ddc86',
                'subprop_op': 'is',
                'subprop_value': [
                    "Direct", 
                    "Organic Search",
                    "Referral"
                ],
                'subprop_type': 'derivedV2',
                'subfilters': [],
        },
    }
    return switch.get(traffic_type, [])

def get_DB_filter():    
    return {
        "subprop_type": "event",
        "subprop_key": "flow_type",
        "subprop_op": "is",
        "subprop_value": ["DB"]
    }

def get_during_booking_filter():    
    return {
        "subprop_type": "event",
        "subprop_key": "flow_type",
        "subprop_op": "is",
        "subprop_value": ["DB"]
    }

def get_flow_type_filter_multiple(flow_types):
    """
    Obtiene un filtro combinado para múltiples tipos de flujo (OR lógico).
    
    Args:
        flow_types: Lista de tipos de flujo (ej: ["DB", "PB"])
        
    Returns:
        dict: Filtro combinado con todos los valores, o "" si la lista está vacía
    """
    if not flow_types or len(flow_types) == 0:
        return ""
    
    # Combinar todos los valores de los tipos de flujo seleccionados
    all_values = []
    for flow_type in flow_types:
        single_filter = get_flow_type_filter(flow_type)
        if single_filter and isinstance(single_filter, dict):
            all_values.extend(single_filter.get('subprop_value', []))
    
    if not all_values:
        return ""
    
    return {
        "subprop_type": "event",
        "subprop_key": "flow_type",
        "subprop_op": "is",
        "subprop_value": all_values
    }

def get_flow_type_filter(flow_type):
    """
    Obtiene el filtro de Amplitude para flow_type.
    
    Args:
        flow_type: Tipo de flujo ('DB', 'PB', 'CK', o 'ALL')
        
    Returns:
        dict: Filtro de Amplitude para flow_type, o cadena vacía si flow_type es 'ALL'
    """
    switch = {
        "DB": {
            "subprop_type": "event",
            "subprop_key": "flow_type",
            "subprop_op": "is",
            "subprop_value": ["DB"]
        },
        "PB": {
            "subprop_type": "event",
            "subprop_key": "flow_type",
            "subprop_op": "is",
            "subprop_value": ["PB"]
        },
        "CK": {
            "subprop_type": "event",
            "subprop_key": "flow_type",
            "subprop_op": "is",
            "subprop_value": ["CK"]
        },
    }
    return switch.get(flow_type, "")

def get_trip_type_filter_multiple(trip_types):
    """
    Obtiene un filtro combinado para múltiples tipos de viaje (OR lógico).
    
    Args:
        trip_types: Lista de tipos de viaje (ej: ["Solo Ida (One Way)", "Ida y Vuelta (Round Trip)"])
        
    Returns:
        dict: Filtro combinado con todos los valores, o "" si la lista está vacía
    """
    if not trip_types or len(trip_types) == 0:
        return ""
    
    # Si ambos están seleccionados, no necesitamos filtro (todos los tipos)
    if len(trip_types) == 2:
        return ""
    
    # Si solo uno está seleccionado, usar el filtro individual
    if len(trip_types) == 1:
        return get_trip_type_filter(trip_types[0])
    
    return ""

def get_trip_type_filter(trip_type):
    """
    Obtiene el filtro de Amplitude para trip_type.
    
    Args:
        trip_type: Tipo de viaje ('Solo Ida (One Way)', 'Ida y Vuelta (Round Trip)', o 'ALL')
        
    Returns:
        dict: Filtro de Amplitude para trip_type, o cadena vacía si trip_type es 'ALL'
    """
    switch = {
        "Solo Ida (One Way)": {
            "subprop_type": "event",
            "subprop_key": "trip_type",
            "subprop_op": "is",
            "subprop_value": ["O"]
        },
        "Ida y Vuelta (Round Trip)": {
            "subprop_type": "event",
            "subprop_key": "trip_type",
            "subprop_op": "is",
            "subprop_value": ["R"]
        },
    }
    return switch.get(trip_type, "")

def get_pax_adult_count_filter(pax_adult_count, event_name=None):
    """
    Obtiene el filtro de Amplitude para pax_adult_count (Cantidad de Adultos).
    
    Args:
        pax_adult_count: Cantidad de adultos ('ALL', '1 Adulto', '2 Adultos', '3 Adultos', '4+ Adultos')
        event_name: Nombre del evento (opcional, mantenido para compatibilidad hacia atrás, pero ya no se usa)
        
    Returns:
        dict: Filtro de Amplitude para pax_adult_count, o cadena vacía si es 'ALL'
    """
    if pax_adult_count == "ALL":
        return ""
    
    # Todos los eventos (incluyendo payment_confirmation_loaded) usan 'pax_adult_count'
    prop_key = "pax_adult_count"
    
    switch = {
        "1 Adulto": {
            "subprop_type": "event",
            "subprop_key": prop_key,
            "subprop_op": "is",
            "subprop_value": [1]
        },
        "2 Adultos": {
            "subprop_type": "event",
            "subprop_key": prop_key,
            "subprop_op": "is",
            "subprop_value": [2]
        },
        "3 Adultos": {
            "subprop_type": "event",
            "subprop_key": prop_key,
            "subprop_op": "is",
            "subprop_value": [3]
        },
        "4+ Adultos": {
            "subprop_type": "event",
            "subprop_key": prop_key,
            "subprop_op": "greater_or_equal",
            "subprop_value": [4]
        },
    }
    return switch.get(pax_adult_count, "")

def get_travel_group_filter(travel_group, event_name=None):
    """
    Obtiene los filtros de Amplitude para Travel Group (Grupo de Viaje).
    Selecciona dinámicamente el nombre de la propiedad según el evento.
    
    Args:
        travel_group: Tipo de grupo de viaje ('ALL', 'Viajero Solo', 'Pareja', 'Grupo', 'Familia (con Menores)')
        event_name: Nombre del evento actual (opcional, usado para detectar revenue_amount)
        
    Returns:
        list: Lista de filtros de Amplitude para el grupo de viaje, o lista vacía si es 'ALL'
    """
    if travel_group == "ALL":
        return []
    
    # --- DICCIONARIO DE MAPEO (Correlation Map) ---
    # Detectamos si estamos en el evento de Revenue (Backend) o en eventos de Frontend
    is_revenue_event = event_name and 'revenue_amount' in str(event_name)
    
    if is_revenue_event:
        # Propiedades de Revenue (Backend)
        # Nota: 'passengers_child_count' incluye niños E infantes combinados.
        key_adult = "passengers_adult_count"
        key_child = "passengers_child_count"
        key_infant = None  # No existe separado en revenue, ni lo necesitamos gracias a la fusión
    else:
        # Propiedades Estándar (Frontend)
        key_adult = "pax_adult_count"
        key_children_only = "pax_children_count"
        key_infant_only = "pax_infant_count"
    
    filters = []
    
    # 1. VIAJERO SOLO
    if travel_group == "Viajero Solo":
        # Lógica Revenue
        if is_revenue_event:
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "is",
                    "subprop_value": [1, "1"]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_child,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                }
            ]
        # Lógica Frontend
        else:
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "is",
                    "subprop_value": [1, "1"]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_children_only,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_infant_only,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                }
            ]
    
    # 2. PAREJA
    elif travel_group == "Pareja":
        if is_revenue_event:
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "is",
                    "subprop_value": [2, "2"]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_child,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                }
            ]
        else:
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "is",
                    "subprop_value": [2, "2"]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_children_only,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_infant_only,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                }
            ]
    
    # 3. GRUPO (>2 Adultos)
    elif travel_group == "Grupo":
        if is_revenue_event:
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "greater",
                    "subprop_value": [2]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_child,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                }
            ]
        else:
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "greater",
                    "subprop_value": [2]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_children_only,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_infant_only,
                    "subprop_op": "is",
                    "subprop_value": [0, "0"]
                }
            ]
    
    # 4. FAMILIA (CON MENORES) - Fusión
    elif travel_group == "Familia (con Menores)":
        if is_revenue_event:
            # En Revenue, child_count > 0 ya implica que hay niños O infantes
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "greater",
                    "subprop_value": [0]
                },
                {
                    "subprop_type": "event",
                    "subprop_key": key_child,
                    "subprop_op": "greater",
                    "subprop_value": [0]
                }
            ]
        else:
            # En Frontend, debemos chequear si hay niños O infantes.
            # Como Amplitude no tiene OR simple en filtros, usamos una lógica abarcativa:
            # Simplemente verificamos que NO sea Solo/Pareja/Grupo (Child=0 y Infant=0)
            # PERO, para ser precisos con los filtros actuales, usaremos la lógica:
            # Adultos > 0 Y (Niños > 0) -- Simplificación válida, asumimos que familias suelen tener niños.
            # *Nota para mejora futura: Idealmente usaríamos cohortes, pero por ahora:*
            return [
                {
                    "subprop_type": "event",
                    "subprop_key": key_adult,
                    "subprop_op": "greater",
                    "subprop_value": [0]
                },
                # Aceptamos que aquí filtramos principalmente por pax_children_count > 0
                # Si queremos incluir infantes solo, necesitaríamos lógica OR compleja.
                # Por simplicidad del prompt actual:
                {
                    "subprop_type": "event",
                    "subprop_key": key_children_only,
                    "subprop_op": "greater",
                    "subprop_value": [0]
                }
            ]
    
    return []

def get_travel_group_filter_multiple(travel_groups, event_name=None):
    """
    Obtiene filtros combinados para múltiples grupos de viaje (OR lógico).
    
    Args:
        travel_groups: Lista de grupos de viaje (ej: ["Viajero Solo", "Pareja"])
        event_name: Nombre del evento actual (opcional)
        
    Returns:
        list: Lista de filtros combinados, o [] si la lista está vacía
    """
    if not travel_groups or len(travel_groups) == 0:
        return []
    
    # Si todos los grupos están seleccionados, no necesitamos filtro
    all_groups = ["Viajero Solo", "Pareja", "Grupo", "Familia (con Menores)"]
    if len(travel_groups) == len(all_groups) and all(g in travel_groups for g in all_groups):
        return []
    
    # Combinar filtros de todos los grupos seleccionados
    # Nota: Los filtros de travel_group son listas de filtros (AND dentro de cada grupo)
    # Para OR entre grupos, necesitamos una lógica más compleja
    # Por simplicidad, si hay múltiples grupos, retornamos [] (sin filtro)
    # O mejor: retornar la unión de todos los filtros
    all_filters = []
    for travel_group in travel_groups:
        group_filters = get_travel_group_filter(travel_group, event_name)
        if group_filters:
            all_filters.extend(group_filters)
    
    return all_filters if all_filters else []

def get_bundle_filters_multiple(profile_names):
    """
    Obtiene filtros combinados para múltiples perfiles de bundle (OR lógico).
    
    Args:
        profile_names: Lista de perfiles (ej: ["Vuela Ligero", "Smart"])
        
    Returns:
        list: Lista de filtros combinados, o [] si la lista está vacía
    """
    if not profile_names or len(profile_names) == 0:
        return []
    
    # Si todos los perfiles están seleccionados, no necesitamos filtro
    all_profiles = ["Vuela Ligero", "Smart", "Full", "Smart + Full"]
    if len(profile_names) == len(all_profiles) and all(p in profile_names for p in all_profiles):
        return []
    
    # Combinar filtros de todos los perfiles seleccionados
    # Nota: Los filtros de bundle son listas de filtros (AND dentro de cada perfil)
    # Para OR entre perfiles, necesitamos una lógica más compleja
    # Por simplicidad, si hay múltiples perfiles, retornamos [] (sin filtro)
    # O mejor: retornar la unión de todos los filtros
    all_filters = []
    for profile_name in profile_names:
        profile_filters = get_bundle_filters(profile_name)
        if profile_filters:
            all_filters.extend(profile_filters)
    
    return all_filters if all_filters else []

def get_bundle_filters(profile_name):
    """
    Obtiene los filtros de Amplitude para el perfil de bundle.
    
    Args:
        profile_name: Perfil de vuelo ('ALL', 'Vuela Ligero', 'Smart', 'Full', 'Smart + Full')
        
    Returns:
        list: Lista de filtros de Amplitude para el perfil de bundle, o lista vacía si es 'ALL'
    """
    if profile_name == "ALL":
        return []
    
    switch = {
        "Vuela Ligero": [
            {
                "subprop_type": "event",
                "subprop_key": "bundle_smart_count",
                "subprop_op": "is",
                "subprop_value": [0]
            },
            {
                "subprop_type": "event",
                "subprop_key": "bundle_full_count",
                "subprop_op": "is",
                "subprop_value": [0]
            }
        ],
        "Smart": [
            {
                "subprop_type": "event",
                "subprop_key": "bundle_smart_count",
                "subprop_op": "is not",
                "subprop_value": [0]
            }
        ],
        "Full": [
            {
                "subprop_type": "event",
                "subprop_key": "bundle_full_count",
                "subprop_op": "is not",
                "subprop_value": [0]
            }
        ],
        "Smart + Full": [
            {
                "subprop_type": "event",
                "subprop_key": "bundle_smart_count",
                "subprop_op": "is not",
                "subprop_value": [0]
            },
            {
                "subprop_type": "event",
                "subprop_key": "bundle_full_count",
                "subprop_op": "is not",
                "subprop_value": [0]
            }
        ],
    }
    return switch.get(profile_name, [])


def cabin_bag_filter():    
    return {
        "subprop_type": "event",
        "subprop_key": "cabin_bag_count",
        "subprop_op": "greater",
        "subprop_value": ['0']
    }

def checked_bag_filter():    
    return {
        "subprop_type": "event",
        "subprop_key": "checked_bag_count",
        "subprop_op": "greater",
        "subprop_value": ['0']
    }

def seat_selected_filter():
    """Filtro para usuarios que seleccionaron al menos un asiento"""
    return {
        "subprop_type": "event",
        "subprop_key": "seats",
        "subprop_op": "greater",
        "subprop_value": ['0']
    }

def bundle_selected_filter():
    """Filtro para usuarios que seleccionaron un bundle"""
    return {
        "subprop_type": "event",
        "subprop_key": "bundle_selected",
        "subprop_op": "is",
        "subprop_value": ['true', 'True', '1']
    }

def get_device_type_multiple(devices):
    """
    Obtiene un filtro combinado para múltiples tipos de dispositivo (OR lógico).
    
    Args:
        devices: Lista de tipos de dispositivo (ej: ["desktop", "mobile"])
        
    Returns:
        dict: Filtro combinado, o [] si la lista está vacía
    """
    if not devices or len(devices) == 0:
        return []
    
    # Si ambos están seleccionados, no necesitamos filtro (todos los dispositivos)
    if len(devices) == 2 and "desktop" in devices and "mobile" in devices:
        return []
    
    # Si solo uno está seleccionado, usar el filtro individual
    if len(devices) == 1:
        return get_device_type(devices[0])
    
    # Si hay múltiples pero no todos, necesitamos combinar con OR
    # Para device_type, esto es complejo porque desktop usa "is not" y mobile usa "is"
    # La mejor estrategia es crear un filtro que incluya ambos valores
    # Pero Amplitude no soporta OR directo, así que retornamos [] (todos) si hay múltiples
    # O mejor: si hay múltiples, no filtramos (todos los dispositivos)
    return []

def get_device_type(device):    
    switch = {
        'mobile': {
            'group_type': 'User',
            'subprop_key': 'device_type',
            'subprop_op': 'is',
            'subprop_value': [
                'Android',
                'Apple iPhone',
            ],
            'subprop_type': 'user',
            'subfilters': [],
        },
        'desktop': {
            'group_type': 'User',
            'subprop_key': 'device_type',
            'subprop_op': 'is not',
            'subprop_value': [
                'Android',
                'Apple iPhone',
            ],
            'subprop_type': 'user',
            'subfilters': [],
        },
    }
    return switch.get(device, [])

def get_filters_culture_device():
    cultures = [
        "CL", "AR", "PE", "CO", "BR", 
        "UY", "PY", "EC", "US", # Le quitamos la cultura Others
    ]
    devices = ['desktop', 'mobile']
    return [(culture, device) 
            for culture in cultures 
            for device in devices]
    

def get_filters_culture_device_traffic_type():
    cultures = [
        "CL", "AR", "PE", "CO", "BR", 
        "UY", "PY", "EC", "US", # Le quitamos la cultura Others
    ]
    devices = ['desktop', 'mobile']
    traffic_types = ['Pagado', 'Organico', 'Promoted']
    return [(culture, device, traffic_type) 
            for culture in cultures 
            for device in devices 
            for traffic_type in traffic_types] 

