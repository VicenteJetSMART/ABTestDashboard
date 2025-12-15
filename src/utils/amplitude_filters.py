# Funciones para obtener los filtros de Amplitude
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

def get_travel_group_filter(travel_group):
    """
    Obtiene los filtros de Amplitude para Travel Group (Grupo de Viaje).
    
    Args:
        travel_group: Tipo de grupo de viaje ('ALL', 'Viajero Solo', 'Pareja', 'Grupo', 'Familia (con Niño)', 'Familia (con Infante)')
        
    Returns:
        list: Lista de filtros de Amplitude para el grupo de viaje, o lista vacía si es 'ALL'
    """
    if travel_group == "ALL":
        return []
    
    filters = []
    
    # Mapeo de Travel Group a filtros de Amplitude
    if travel_group == "Viajero Solo":
        # 1 adulto, sin niños, sin infantes
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_adult_count",
            "subprop_op": "is",
            "subprop_value": [1]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_children_count",
            "subprop_op": "is",
            "subprop_value": [0]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_infant_count",
            "subprop_op": "is",
            "subprop_value": [0]
        })
    elif travel_group == "Pareja":
        # 2 adultos, sin niños, sin infantes
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_adult_count",
            "subprop_op": "is",
            "subprop_value": [2]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_children_count",
            "subprop_op": "is",
            "subprop_value": [0]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_infant_count",
            "subprop_op": "is",
            "subprop_value": [0]
        })
    elif travel_group == "Grupo":
        # 3+ adultos, sin niños, sin infantes
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_adult_count",
            "subprop_op": "greater_or_equal",
            "subprop_value": [3]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_children_count",
            "subprop_op": "is",
            "subprop_value": [0]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_infant_count",
            "subprop_op": "is",
            "subprop_value": [0]
        })
    elif travel_group == "Familia (con Niño)":
        # Al menos 1 adulto y al menos 1 niño, sin infantes
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_adult_count",
            "subprop_op": "greater_or_equal",
            "subprop_value": [1]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_children_count",
            "subprop_op": "greater_or_equal",
            "subprop_value": [1]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_infant_count",
            "subprop_op": "is",
            "subprop_value": [0]
        })
    elif travel_group == "Familia (con Infante)":
        # Al menos 1 adulto y al menos 1 infante
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_adult_count",
            "subprop_op": "greater_or_equal",
            "subprop_value": [1]
        })
        filters.append({
            "subprop_type": "event",
            "subprop_key": "pax_infant_count",
            "subprop_op": "greater_or_equal",
            "subprop_value": [1]
        })
    
    return filters

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

