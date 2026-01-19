# ✅ Métricas de Home Creadas

## 📋 Resumen

Se han creado exitosamente las métricas para **Home** (landing page) en el AB Test Dashboard.

## 🎯 Métricas Implementadas

### 1. HOME_NSR (Next Step Rate)
**Descripción:** Mide la tasa de usuarios que pasan del home al siguiente paso del flujo (flight).

**Funnel:**
```
home_dom_loaded → flight_dom_loaded_flight
```

**Código:**
```python
HOME_NSR = {'events': [
    ('home_dom_loaded', []),
    ('flight_dom_loaded_flight', [])
]}
```

### 2. HOME_WCR (Website Conversion Rate)
**Descripción:** Mide la conversión completa desde el home hasta la compra final (revenue).

**Funnel:**
```
home_dom_loaded → revenue_amount
```

**Código:**
```python
HOME_WCR = {'events': [
    ('home_dom_loaded', []),
    ('revenue_amount', [])
]}
```

## 📂 Estructura de Archivos Creados

```
ABTestDashboard/src/metrics/home/
├── __init__.py           ✅ Exporta HOME_NSR y HOME_WCR
├── home_metrics.py       ✅ Define las métricas
└── README.md            ✅ Documentación detallada
```

## 🔄 Integración Automática

Las métricas de home se cargarán **automáticamente** en el dashboard gracias al sistema de `metrics_loader.py` que:

1. **Escanea** todas las carpetas en `src/metrics/`
2. **Detecta** archivos `*_metrics.py`
3. **Valida** que las métricas sigan el formato correcto
4. **Carga** las métricas automáticamente sin necesidad de imports manuales

## 🎨 Características

✅ **Sin filtros adicionales**: Ambas métricas miden el comportamiento general del home  
✅ **Compatibilidad con filtros globales**: Device, Culture, etc. se aplican automáticamente  
✅ **Nomenclatura consistente**: Sigue el mismo patrón que las demás métricas  
✅ **Documentación completa**: Incluye README con ejemplos de uso  
✅ **Validación de linting**: Sin errores de código

## 🚀 Cómo Usar

Las métricas estarán disponibles automáticamente en el dashboard en la categoría **"home"**:

- **HOME_NSR**: Para medir la efectividad del home en llevar usuarios al siguiente paso
- **HOME_WCR**: Para medir la conversión completa desde el home hasta la compra

## 📊 Flujo de Conversión Completo

```
Home → Flight → Baggage → Seats → Extras → Passengers → Payment → Revenue
 ↓                                                                      ↑
 └─────────────────────────── HOME_WCR ───────────────────────────────┘
 └── HOME_NSR ──→
```

## 🔍 Eventos Utilizados

- `home_dom_loaded` - Evento que se dispara cuando el home/landing page se carga
- `flight_dom_loaded_flight` - Evento que se dispara cuando la página de selección de vuelos se carga
- `revenue_amount` - Evento que se dispara cuando se confirma el pago

## ✨ Próximos Pasos

Las métricas están listas para usar. El sistema las detectará automáticamente la próxima vez que se ejecute el dashboard.

Si necesitas **agregar más métricas** para home (por ejemplo, A2C o CR específicas), solo tienes que:

1. Agregar la nueva métrica en `home_metrics.py`
2. Exportarla en `__init__.py`
3. El sistema la cargará automáticamente

---

**Fecha de creación:** 13 de enero de 2026  
**Versión:** 1.0.0

