# 📊 Guía para Agregar Nuevas Métricas - AB Test Dashboard

Esta guía explica cómo agregar nuevas métricas de manera fácil y organizada al AB Test Dashboard de Streamlit.

## 🏗️ Estructura de Carpetas por Step del Flujo de Compra

Las métricas están organizadas por carpetas según el step del flujo de compra:

```
📁 home/                # Métricas de home/landing
📁 flight_metrics/      # Métricas de vuelos
📁 baggage_metrics/     # Métricas de equipaje
📁 seats_metrics/       # Métricas de asientos
📁 extras_metrics/      # Métricas de extras
📁 passengers_metrics/  # Métricas de pasajeros
📁 payment_metrics/     # Métricas de pagos
```

## 📋 Estructura de Archivos por Carpeta

Cada carpeta de métricas debe contener:

```
📁 [step]_metrics/
├── 📄 [step]_metrics.py      # Definiciones de métricas (OBLIGATORIO)
├── 📄 [step]_utils.py        # Funciones de API (opcional)
├── 📄 amplitude_filters.py   # Filtros específicos (opcional)
├── 📄 README.md             # Documentación específica (opcional)
└── 📄 pruebas_metricas_[step].ipynb  # Notebook de pruebas (opcional)
```

## 🎯 Cómo Agregar una Nueva Métrica

### Paso 1: Crear/Actualizar el archivo `[step]_metrics.py`

Este archivo debe contener las definiciones de métricas siguiendo **exactamente** el formato de `baggage_metrics.py`:

```python
# filtros amplitude
from utils.amplitude_filters import (
    cabin_bag_filter,
    checked_bag_filter,
    get_DB_filter
)

# Next Step Rate [Step] - General (sin filtros adicionales)
NSR_[STEP] = {'events': [
    ('evento_inicial', []),
    ('evento_final', [])
]}

# Website Conversion Rate from [Step] - General (sin filtros adicionales)
WCR_[STEP] = {'events': [
    ('evento_inicial', []),
    ('revenue_amount', [])
]}

# [Step] A2C con filtros específicos aplicados a ambos eventos
[STEP]_A2C = {'events': [
    ('evento_inicial', [filtro_especifico()]),
    ('evento_final', [filtro_especifico()])
]}

# Métrica con filtros diferentes por evento
METRIC_CUSTOM = {'events': [
    ('evento_inicial', [get_DB_filter()]),  # Primer evento con filtro DB
    ('evento_final', [])  # Segundo evento sin filtros - lista vacía
]}
```

**IMPORTANTE:** 
- **SIEMPRE usa el formato de diccionario** `{'events': [...]}`
- **SIEMPRE usa tuplas** `('evento', [filtros])` donde el primer elemento es el nombre del evento
- **El segundo elemento es siempre una lista** de filtros: `[filtro1, filtro2, ...]`
- **Si no hay filtros**, usa lista vacía: `[]`
- **Puedes agregar tantos eventos como necesites** (2, 3, 4, 5+ eventos)
- **Cada evento puede tener sus propios filtros** independientemente de los demás
- **Los eventos se procesan en orden** como un funnel secuencial
- Sigue la nomenclatura exacta: `NSR_[STEP]`, `WCR_[STEP]`, `[STEP]_A2C`

### Paso 2: Actualizar `streamlit/app.py`

Agregar la importación de las nuevas métricas en la sección correspondiente:

```python
# Importar métricas de [step]
try:
    from [step]_metrics.[step]_metrics import (
        NSR_[STEP],
        WCR_[STEP],
        [NUEVA_METRICA]
    )
    
    # Agregar al diccionario de métricas predefinidas
    PREDEFINED_METRICS_QUICK = {
        "NSR [Step] (Next Step Rate)": NSR_[STEP],
        "WCR [Step] (Website Conversion Rate)": WCR_[STEP],
        "Nueva Métrica": [NUEVA_METRICA],
        # ... otras métricas existentes
    }
```

### Paso 3: Actualizar la documentación de métricas

En la sección "📚 Ver Métricas Disponibles", agregar información sobre la nueva métrica:

```python
metrics_info_quick = [
    # ... métricas existentes
    {
        "Métrica": "Nueva Métrica",
        "Evento Inicial": [NUEVA_METRICA][0] if isinstance([NUEVA_METRICA], list) else [NUEVA_METRICA].get('events', [])[0],
        "Evento Final": [NUEVA_METRICA][1] if isinstance([NUEVA_METRICA], list) else [NUEVA_METRICA].get('events', [])[1] if len([NUEVA_METRICA].get('events', [])) > 1 else "-",
        "Filtros": "DB + filtros_específicos"
    }
]
```

## 📝 Formato de Métricas - **NUEVO FORMATO OBLIGATORIO**

### Formato Estándar: Diccionario con Tuplas de Eventos y Lista de Filtros

**Todas las métricas deben usar este formato**, donde cada evento tiene sus propios filtros específicos:

```python
METRIC_NAME = {'events': [
    ('evento_1', [filtro_1, filtro_2, ..., filtro_m]),
    ('evento_2', [filtro_1, filtro_2, ..., filtro_m]),
    ('evento_3', [filtro_1, filtro_2, ..., filtro_m]),
    # ... puedes agregar tantos eventos como necesites
    ('evento_n', [filtro_1, filtro_2, ..., filtro_m]),
]}
```

### Estructura de la Tupla

Cada elemento en la lista `events` es una **tupla** donde:
- **Primer elemento**: Nombre del evento (string)
- **Segundo elemento**: Lista de filtros para ese evento `[filtro1, filtro2, ...]`
  - Si no hay filtros, usar lista vacía: `[]`

### Número de Eventos

**Puedes agregar tantos eventos como necesites** en una métrica. No hay límite:
- **2 eventos**: Funnel básico (evento inicial → evento final)
- **3+ eventos**: Funnel completo con múltiples etapas intermedias

### Ejemplos

#### Métrica sin filtros (todos los eventos sin filtros adicionales)
```python
# Next Step Rate [Step] - General
NSR_[STEP] = {'events': [
    ('evento_inicial', []),
    ('evento_final', [])
]}
```

#### Métrica con filtros aplicados a todos los eventos
```python
# [Step] A2C con filtros específicos aplicados a ambos eventos
[STEP]_A2C = {'events': [
    ('evento_inicial', [filtro_especifico()]),
    ('evento_final', [filtro_especifico()])
]}
```

#### Métrica con filtros diferentes por evento
```python
# Ejemplo: primer evento sin filtros, segundo con filtro DB
METRIC_EXAMPLE = {'events': [
    ('baggage_dom_loaded', []),  # Sin filtros - lista vacía
    ('seatmap_dom_loaded', [get_DB_filter()])  # Con filtro - lista con filtros
]}
```

#### Métrica con múltiples filtros por evento
```python
# Ejemplo: evento con múltiples filtros
METRIC_COMPLEX = {'events': [
    ('evento_inicial', [get_DB_filter(), cabin_bag_filter()]),
    ('evento_final', [get_DB_filter()])
]}
```

#### Métrica con múltiples eventos (funnel completo)
```python
# Ejemplo: funnel completo con 4 eventos
METRIC_FUNNEL_COMPLETE = {'events': [
    ('homepage_dom_loaded', []),  # Paso 1: Landing
    ('flight_dom_loaded', []),  # Paso 2: Selección de vuelo
    ('baggage_dom_loaded', [get_DB_filter()]),  # Paso 3: Equipaje (con filtro DB)
    ('seatmap_dom_loaded', []),  # Paso 4: Asientos
    ('payment_dom_loaded', []),  # Paso 5: Pago
    ('revenue_amount', [])  # Paso 6: Conversión final
]}

# Ejemplo: funnel con filtros diferentes en cada etapa
METRIC_FUNNEL_FILTERED = {'events': [
    ('baggage_dom_loaded', []),  # Sin filtros
    ('seatmap_dom_loaded', [cabin_bag_filter()]),  # Con filtro de cabina
    ('extras_dom_loaded', [checked_bag_filter()]),  # Con filtro de documentado
    ('payment_dom_loaded', [])  # Sin filtros
]}
```

**⚠️ IMPORTANTE:** 
- **SIEMPRE usa el formato de diccionario** `{'events': [...]}`
- **SIEMPRE usa tuplas** `('evento', [filtros])`
- **El segundo elemento es siempre una lista** de filtros: `[filtro1, filtro2, ...]`
- **Si no hay filtros**, usa lista vacía: `[]`
- **Los filtros se aplican individualmente** a cada evento según se especifique en su lista
- **Este formato permite máxima flexibilidad** para aplicar filtros diferentes a diferentes eventos

## 🔧 Filtros Disponibles

### Filtros Básicos (en `amplitude_filters.py`)
- `get_culture_digital_filter(country_code)` - Filtro por cultura/país
- `get_device_type(device)` - Filtro por tipo de dispositivo
- `get_traffic_type(traffic_type)` - Filtro por tipo de tráfico
- `get_DB_filter()` - Filtro para flujo DB (Direct Booking)

### Filtros Específicos
- `cabin_bag_filter()` - Filtro para equipaje de cabina
- `checked_bag_filter()` - Filtro para equipaje facturado

### Crear Nuevos Filtros
```python
def nuevo_filtro():
    return {
        "subprop_type": "event",
        "subprop_key": "propiedad",
        "subprop_op": "is",  # o "is not", "greater", etc.
        "subprop_value": ["valor1", "valor2"]
    }
```

## 🎨 Convenciones de Nomenclatura

### Métricas
- **NSR_[STEP]**: Next Step Rate (tasa de siguiente paso)
- **WCR_[STEP]**: Website Conversion Rate (tasa de conversión del sitio)
- **A2C_[STEP]**: Action to Conversion (acción a conversión)
- **[STEP]_[TIPO]**: Métricas específicas del step

### Eventos
- Eventos estándar: `evento_dom_loaded`, `evento_clicked`
- Custom Events: `ce:(NEW) evento_especifico`
- Eventos de conversión: `revenue_amount`, `payment_confirmation_loaded`

## 📊 Ejemplo Completo: Agregar Métrica de Seats

### 1. Crear `seats_metrics/seats_metrics.py`
```python
# filtros amplitude
from utils.amplitude_filters import (
    cabin_bag_filter,
    checked_bag_filter,
    get_DB_filter
)

# Next Step Rate Seats - General (sin filtros adicionales)
NSR_SEATS = {'events': [
    ('seatmap_dom_loaded', []),
    ('continue_clicked_seat', [])
]}

# Website Conversion Rate from Seats - General (sin filtros adicionales)
WCR_SEATS = {'events': [
    ('seatmap_dom_loaded', []),
    ('revenue_amount', [])
]}

# Seat Selection A2C con filtro de equipaje de cabina
SEAT_SELECTION_A2C = {'events': [
    ('seatmap_dom_loaded', [cabin_bag_filter()]),
    ('continue_clicked_seat', [cabin_bag_filter()])
]}

# Ejemplo: Métrica con filtros diferentes por evento
SEAT_CUSTOM = {'events': [
    ('seatmap_dom_loaded', [get_DB_filter()]),  # Primer evento con filtro DB
    ('continue_clicked_seat', [])  # Segundo evento sin filtros - lista vacía
]}
```

### 2. Actualizar `streamlit/app.py`
```python
# Importar métricas de seats
try:
    from seats_metrics.seats_metrics import (
        NSR_SEATS,
        WCR_SEATS,
        SEAT_SELECTION_A2C
    )
    
    # Agregar al diccionario
    PREDEFINED_METRICS_QUICK.update({
        "NSR Seats (Next Step Rate)": NSR_SEATS,
        "WCR Seats (Website Conversion Rate)": WCR_SEATS,
        "Seat Selection A2C": SEAT_SELECTION_A2C
    })
```

### 3. Actualizar documentación
```python
# Función auxiliar para extraer nombre de evento de tupla
def get_event_name(event_item):
    if isinstance(event_item, tuple) and len(event_item) > 0:
        return event_item[0]
    elif isinstance(event_item, str):
        return event_item
    return "-"

# Función auxiliar para obtener número de filtros
def get_filters_count(event_item):
    if isinstance(event_item, tuple) and len(event_item) >= 2:
        filters_list = event_item[1]
        if isinstance(filters_list, list):
            return len(filters_list)
    return 0

metrics_info_quick.extend([
    {
        "Métrica": "NSR Seats",
        "Evento Inicial": get_event_name(NSR_SEATS.get('events', [])[0]),
        "Evento Final": get_event_name(NSR_SEATS.get('events', [])[1]) if len(NSR_SEATS.get('events', [])) > 1 else "-",
        "Filtros": "Ninguno"
    },
    {
        "Métrica": "WCR Seats",
        "Evento Inicial": get_event_name(WCR_SEATS.get('events', [])[0]),
        "Evento Final": get_event_name(WCR_SEATS.get('events', [])[1]) if len(WCR_SEATS.get('events', [])) > 1 else "-",
        "Filtros": "Ninguno"
    },
    {
        "Métrica": "Seat Selection A2C",
        "Evento Inicial": get_event_name(SEAT_SELECTION_A2C.get('events', [])[0]),
        "Evento Final": get_event_name(SEAT_SELECTION_A2C.get('events', [])[1]) if len(SEAT_SELECTION_A2C.get('events', [])) > 1 else "-",
        "Filtros": "cabin_bag (ambos eventos)"
    }
])
```

## ✅ Checklist para Agregar Nueva Métrica

- [ ] Crear/actualizar `[step]_metrics.py` con la nueva métrica
- [ ] Importar la métrica en `streamlit/app.py`
- [ ] Agregar al diccionario `PREDEFINED_METRICS_QUICK`
- [ ] Actualizar `metrics_info_quick` con la documentación
- [ ] Probar la métrica en la interfaz de Streamlit
- [ ] Verificar que los eventos existen en `AVAILABLE_EVENTS`
- [ ] Documentar filtros específicos si los hay

## 🚀 Tips y Mejores Prácticas

1. **Usa emojis descriptivos** en los nombres de métricas para mejor UX
2. **Mantén nombres consistentes** con las convenciones existentes
3. **Documenta filtros complejos** en comentarios
4. **Prueba métricas** antes de agregarlas al dashboard
5. **Usa eventos existentes** de `AVAILABLE_EVENTS` cuando sea posible
6. **Agrupa métricas relacionadas** en la misma carpeta
7. **Mantén la estructura** de archivos consistente

## 🔍 Debugging

Si una métrica no aparece en el dashboard:

1. Verifica que la importación sea correcta
2. Confirma que el archivo `[step]_metrics.py` existe
3. Revisa que la métrica esté en `PREDEFINED_METRICS_QUICK`
4. Verifica que los eventos estén en `AVAILABLE_EVENTS`
5. Revisa los logs de Streamlit para errores de importación

## 📞 Soporte

Para dudas sobre esta guía o problemas al agregar métricas, revisa:
- `EXPERIMENT_UTILS_DOCUMENTATION.md` - Documentación técnica completa
- `FASTAPI_CONVERSION_PLAN.md` - Plan de migración a FastAPI
- Los notebooks de pruebas en cada carpeta de métricas
