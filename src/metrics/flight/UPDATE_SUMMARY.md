# ✅ Actualización de Métricas de Flight

## 📋 Cambios Realizados

Se han actualizado las métricas del módulo **Flight** según los nuevos requerimientos, simplificando y enfocando las métricas en las acciones principales.

---

## 🗑️ Métricas Eliminadas

Las siguientes métricas fueron **removidas** del módulo:

### Selection Rate
- ❌ `OUTBOUND_FLIGHT_SELECTION` - Tasa de selección de vuelo de ida
- ❌ `INBOUND_FLIGHT_SELECTION` - Tasa de selección de vuelo de regreso  
- ❌ `COMPLETE_FLIGHT_SELECTION` - Tasa de selección completa (ida + regreso)
- ❌ `FLIGHT_CONTINUE_RATE` - Tasa de click en continuar

### A2C (Add to Cart) - Versiones Antiguas
- ❌ `OUTBOUND_FLIGHT_A2C` - Add to Cart vuelo de ida
- ❌ `INBOUND_FLIGHT_A2C` - Add to Cart vuelo de regreso
- ❌ `DISCOUNT_CLUB_A2C` - Add to Cart Discount Club

### CR (Conversion Rate) - Versiones Antiguas
- ❌ `OUTBOUND_FLIGHT_CR` - CR vuelo de ida
- ❌ `INBOUND_FLIGHT_CR` - CR vuelo de regreso
- ❌ `DISCOUNT_CLUB_CR` - CR Discount Club

**Total eliminadas:** 10 métricas

---

## ✅ Métricas Actuales

### 1️⃣ **FLIGHTS_NSR** (Next Step Rate)
**Descripción:** Tasa de usuarios que pasan de flight a baggage

**Funnel:**
```
flight_dom_loaded_flight → baggage_dom_loaded
```

**Código:**
```python
FLIGHTS_NSR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('baggage_dom_loaded', [])
]}
```

---

### 2️⃣ **FLIGHTS_WCR** (Website Conversion Rate)
**Descripción:** Conversión desde flight hasta revenue

**Funnel:**
```
flight_dom_loaded_flight → revenue_amount
```

**Código:**
```python
FLIGHTS_WCR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('revenue_amount', [])
]}
```

---

### 3️⃣ **FLIGHTS_A2C** (Add to Cart - Flights) ⭐ NUEVO
**Descripción:** Tasa de selección de vuelos usando custom event

**Funnel:**
```
flight_dom_loaded_flight → ce:flight_selected
```

**Código:**
```python
FLIGHTS_A2C = {'events': [
    ('flight_dom_loaded_flight', []),
    ('ce:flight_selected', [])
]}
```

**Custom Event:** `ce:flight_selected` - Evento que se dispara cuando un usuario selecciona un vuelo

---

### 4️⃣ **BUNDLES_A2C** (Add to Cart - Bundles) ⭐ NUEVO
**Descripción:** Tasa de selección de bundles usando custom event

**Funnel:**
```
flight_dom_loaded_flight → ce:bundle_a2c
```

**Código:**
```python
BUNDLES_A2C = {'events': [
    ('flight_dom_loaded_flight', []),
    ('ce:bundle_a2c', [])
]}
```

**Custom Event:** `ce:bundle_a2c` - Evento que se dispara cuando un usuario selecciona un bundle

---

### 5️⃣ **BUNDLES_CR** (Conversion Rate - Bundles) ⭐ NUEVO
**Descripción:** Conversión desde la carga de flight hasta confirmación de pago con bundle

**Funnel:**
```
flight_dom_loaded_flight → ce:payment_confirmation_with_any_bundle
```

**Código:**
```python
BUNDLES_CR = {'events': [
    ('flight_dom_loaded_flight', []),
    ('ce:payment_confirmation_with_any_bundle', [])
]}
```

**Custom Event:** `ce:payment_confirmation_with_any_bundle` - Evento que se dispara cuando se confirma un pago que incluye un bundle

---

## 📊 Resumen de Métricas

| # | Métrica | Tipo | Status |
|---|---------|------|--------|
| 1 | FLIGHTS_NSR | NSR | ✅ Mantenida |
| 2 | FLIGHTS_WCR | WCR | ✅ Mantenida |
| 3 | FLIGHTS_A2C | A2C | ⭐ Nueva (custom event) |
| 4 | BUNDLES_A2C | A2C | ⭐ Nueva (custom event) |
| 5 | BUNDLES_CR | CR | ⭐ Nueva |

**Total métricas actuales:** 5 (vs 12 anteriores)  
**Reducción:** 58% menos métricas (más enfocado y simple)

---

## 🎯 Eventos Utilizados

### Eventos Estándar
- `flight_dom_loaded_flight` - Página de vuelos cargada
- `baggage_dom_loaded` - Siguiente paso (equipaje)  
- `revenue_amount` - Conversión final

### Custom Events (prefijo `ce:`)
- `ce:flight_selected` - Vuelo seleccionado
- `ce:bundle_a2c` - Bundle agregado al carrito
- `ce:payment_confirmation_with_any_bundle` - Confirmación de pago con bundle

---

## 📁 Archivos Modificados

```
ABTestDashboard/src/metrics/flight/
├── flight_metrics.py          ✅ Actualizado (5 métricas)
├── __init__.py                ✅ Actualizado (exports)
└── README.md                  ✅ Actualizado (documentación)
```

---

## 🔄 Integración Automática

Las métricas actualizadas se cargarán **automáticamente** en el dashboard gracias al sistema de `metrics_loader.py`. Las métricas antiguas ya no estarán disponibles y serán reemplazadas por las nuevas.

---

## ✨ Mejoras

1. ✅ **Más simple:** De 12 a 5 métricas enfocadas
2. ✅ **Uso de custom events:** Mayor precisión con `ce:flight_selected` y `ce:bundle_a2c`
3. ✅ **Métricas de bundles:** Nueva funcionalidad específica para bundles
4. ✅ **Mejor nomenclatura:** FLIGHTS_NSR en lugar de FLIGHT_NSR
5. ✅ **Documentación actualizada:** README completo con ejemplos

---

**Fecha de actualización:** 13 de enero de 2026  
**Versión:** 2.0.0  
**Estado:** ✅ Completado - Sin errores de linting

