# Configuración del Tema - AB Test Dashboard

Este documento explica la configuración del tema del dashboard y cómo personalizarlo.

## Configuración Actual

El tema del dashboard está configurado en `.streamlit/config.toml` con las siguientes características:

### Detección Automática del Tema del Sistema

El dashboard está configurado para **detectar automáticamente** el tema del sistema operativo (claro u oscuro) y ajustarse en consecuencia. Esto proporciona una experiencia de usuario más natural y consistente.

**Características:**
- ✅ Detección automática del tema del sistema
- ✅ Color primario: `#3CCFE7` (cyan/turquesa)
- ✅ Fuente: Sans serif
- ✅ Sin colores de fondo/texto forzados (permite la detección automática)

### Configuración del Servidor

```toml
[server]
headless = false
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### Estadísticas del Navegador

Las estadísticas de uso están deshabilitadas para mayor privacidad:

```toml
[browser]
gatherUsageStats = false
```

## Personalización del Tema

### Forzar un Tema Específico

Si deseas forzar un tema específico (claro u oscuro) independientemente del sistema, puedes editar `.streamlit/config.toml` y descomentar la línea:

```toml
[theme]
primaryColor = "#3CCFE7"
font = "sans serif"
base = "light"  # o "dark"
```

**Opciones disponibles:**
- `base = "light"` - Forzar tema claro
- `base = "dark"` - Forzar tema oscuro
- Sin especificar `base` - Detección automática (recomendado)

### Cambiar el Color Primario

Para cambiar el color primario del dashboard, modifica el valor de `primaryColor` en `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#TU_COLOR_HEX"
```

Ejemplos de colores:
- Azul: `#1f77b4`
- Verde: `#2ca02c`
- Rojo: `#d62728`
- Naranja: `#ff7f0e`

### Cambiar la Fuente

Para cambiar la fuente, modifica el valor de `font`:

```toml
[theme]
font = "sans serif"  # o "serif", "monospace"
```

## Notas Importantes

⚠️ **No definir colores de fondo/texto manualmente**: Para mantener la detección automática del tema del sistema, no debes definir `backgroundColor`, `secondaryBackgroundColor` ni `textColor` en la configuración. Esto permite que Streamlit use CSS para detectar el tema del sistema automáticamente.

## Aplicar Cambios

Después de modificar `.streamlit/config.toml`, necesitas reiniciar la aplicación Streamlit para que los cambios surtan efecto:

1. Detén la aplicación (Ctrl+C en la terminal)
2. Reinicia con `streamlit run app.py` o usando `iniciar_app.bat`

## Referencias

- [Documentación oficial de Streamlit - Theming](https://docs.streamlit.io/library/advanced-features/theming)
- [Configuración de Streamlit](https://docs.streamlit.io/library/advanced-features/configuration)
