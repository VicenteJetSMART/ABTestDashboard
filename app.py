import os
import sys
import re
import time
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
import pandas as pd
import requests

from src.utils.experiment_utils import (
    get_experiments_list,
    final_pipeline,
    final_pipeline_cumulative,
    get_control_treatment_raw_data,
    get_variant_funnel,
    get_variant_funnel_cum,
    get_experiment_variants,
    clear_amplitude_cache
)

PROJECT_ROOT = Path(__file__).resolve().parent

# ==============================================================================
# MAPEO DE GHOST ANCHORS (Configuración Explícita)
# Define qué evento de contexto (_loaded) se inyecta según el evento inicial.
# Key: Evento Inicial de la métrica (Hijo)
# Value: Evento Ancla a inyectar (Padre/Contexto)
# ==============================================================================
EVENT_ANCHOR_MAP = {
    # Extras (Flexi, Checkin, Embarque, etc.)
    'extra_selected': 'extras_dom_loaded',  # CORREGIDO: Plural 'extras'

    # Maletas / Ancillaries (Modal o Selección directa)
    'modal_ancillary_clicked': 'baggage_dom_loaded',
    'baggage_selected': 'baggage_dom_loaded',
    'cabin_bag_selected': 'baggage_dom_loaded',
    'checked_bag_selected': 'baggage_dom_loaded',

    # Vuelos (Selección de itinerario)
    'dc_modal_dom_loaded': 'flight_dom_loaded_flight',
    'inbound_flight_selected_flight': 'flight_dom_loaded_flight',
    'outbound_flight_selected_flight': 'flight_dom_loaded_flight',

    # Asientos (Selección en mapa)
    'inbound_seat_selected': 'seatmap_dom_loaded',
    'outbound_seat_selected': 'seatmap_dom_loaded'
}

# Lista completa de eventos disponibles en Amplitude
AVAILABLE_EVENTS = [
    "homepage_dom_loaded", 
    "everymundo_landing_dom_loaded",
    "flight_dom_loaded_flight",
    "search_clicked_home",
    "outbound_flight_selected_flight",
    "baggage_dom_loaded",
    "itinerary_dom_loaded",
    "seatmap_dom_loaded",
    "continue_clicked_baggage",
    "inbound_flight_selected_flight",
    "extras_dom_loaded",
    "continue_clicked_seat",
    "continue_clicked_extras",
    "continue_clicked_flight",
    "dc_modal_dom_loaded",
    "check_in_clicked",
    "passengers_dom_loaded",
    "checkin_passengers_dom_loaded",
    "click_header_button",
    "search_clicked_flight",
    "extra_selected",
    "payment_dom_loaded",
    "click_searchbox_header",
    "continue_clicked_checkin",
    "checkin_additional_info_dom_loaded",
    "payment_selected",
    "modal_ancillary_clicked",
    "force_select_baggage",
    "continue_clicked_passengers",
    "boarding_card_downloaded",
    "edit_booking_clicked", 
    "payment_clicked",
    "open_breakdown_mobile",
    "login_dom_loaded",
    "monthly_view_clicked",
    "user_login",
    "payment_confirmation_loaded",
    "revenue_amount",
    "click_toggle_taxes",
    "outbound_bundle_selected",
    "carousel_banner_clicked",
    "outbound_seat_selected",
    "inbound_bundle_selected",
    "continue_gender_passengers",
    "inbound_seat_selected",
    "modal_skip_direct_payment_clicked",
    "flight_dom_loaded_EXP_283",
    "filter_direct_cnx_loaded",
    "click_checkbox_miles_aa",
    "flightstatus_dom_loaded",
    "cyd_dom_loaded",
    "click_aadvantage_passengers",
    "header_my_booking_clicked",
    "installments_selected",
    "click_destinations_card",
    "user_register",
    "cyd_options_loaded",
    "force_select_extras",
    "click_thrid_parties",
    "ancillary_clicked",
    "destinos_landing_dom_loaded",
    "be_login_rut_verified",
    "payment_card_country_clicked",
    "landing_entretencion_dom_loaded",
    "error_404_dom_loaded",
    "chatbot_widget_clicked",
    "click_widgets_home",
    "error_500_dom_loaded",
    "user_logout",
    "ancillary_clicked_custom",
    "click_flightstatus_search",
    "quick_booking_dom_loaded",
    "promo_homepage_dom_loaded",
    "quick_booking_click",
    "jgo_homepage_dom_loaded",
    "click_btn_landing_entretencion",
    "edit_outbound_bundle",
    "click_taxes_toggle",
    "seo_landing_dom_loaded",
    "grant_full_consent",
    "autofill_toggle_clicked",
    "dc_membership_type_clicked",
    "count_AA_Passengers",
    "click_see_all_destinations",
    "cart_search_click",
    "click_btn_cambios_y_devoluciones",
    "seats_info_clicked",
    "header_destination_clicked",
    "buscador_smart_dom_loaded",
    "cart_header_click",
    "portal_login",
    "blog_dom_loaded",
    "millas_aa_acumular_dom_loaded",
    "button_back_clicked",
    "edit_inbound_bundle",
    "continue_clicked_payment",
    "grupos_dom_loaded",
    "header_flight_info_clicked",
    "header_benefits_clicked",
    "toggle_switch_AR",
    "continue_without_seats_clicked",
    "cart_search_remove",
    "jgo_search_dom_loaded",
    "go_to_pay_clicked",
    "alianza_aa_dom_loaded",
    "dc_membership_creation_continue_clicked",
    "click_cotiza_aqui_grupos",
    "autofill_pax_clicked",
    "reservas_en_grupo_dom_loaded",
    "flight_filter_clicked",
    "jgo_search_results_loaded",
    "millas_aa_canjear_dom_loaded",
    "jgo_plans_dom_loaded",
    "insufficient_miles_modal_loaded",
    "jgo_click_subscribe",
    "jgo_baggage_dom_loaded",
    "jgo_plan_selected",
    "vuelasmart_dom_loaded",
    "jgo_payment_redemption_loaded",
    "jgo_faq_clicked",
    "jgo_payment_redemption_clicked",
    "jgo_register_email_dom_loaded",
    "cotizar_sin_millas_clicked",
    "jgo_payment_redemption_confirmation",
    "vuelasmart_form_submit",
    "force_select_flights",
    "jgo_baggage_continue_clicked",
    "jgo_verify_email",
    "jgo_payment_register_loaded",
    "jgo_register_info_dom_loaded",
    "click_insurance_postbooking",
    "jgo_payment_register_confirmation",
    "new_lim_dom_loaded",
    "jgo_payment_register_clicked",
    "elige_otro_vuelo_clicked",
    "form_equipaje_dom_loaded",
    "group_rm_payment_confirmation",
    "form_equipaje_submit",
    "smu_landing_dom_loaded",
    "click_corporate_header_btn",
    "aadvantage_dom_loaded",
    "clicks_carousel_btn_home",
    "EXP_179_dom_loaded",
    "clicks_login_type"
]


def ensure_sys_path() -> None:
    # Asegura que el proyecto raíz esté en sys.path para importar módulos locales
    root_str = str(PROJECT_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


@st.cache_resource(show_spinner=False)
def load_env() -> tuple[bool, str]:
    """
    Carga las variables de entorno desde el archivo .env
    
    Returns:
        tuple: (success, message) - Indica si se cargó correctamente y un mensaje informativo
    """
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return False, "python-dotenv no está instalado. Instálalo con: pip install python-dotenv"
    
    # Intentar cargar desde múltiples ubicaciones posibles
    env_paths = [
        PROJECT_ROOT / ".env",  # Raíz del proyecto
        Path(__file__).resolve().parent / ".env",  # Carpeta raíz (donde está app.py)
    ]
    
    env_loaded = False
    loaded_path = None
    
    for env_path in env_paths:
        if env_path.exists():
            result = load_dotenv(dotenv_path=env_path, override=True)
            if result:
                env_loaded = True
                loaded_path = env_path
                break
        else:
            # También intentar sin especificar path (busca automáticamente)
            result = load_dotenv(dotenv_path=env_path, override=True)
            if result:
                env_loaded = True
                loaded_path = env_path
                break
    
    # Verificar que las variables críticas estén disponibles
    required_vars = ['AMPLITUDE_API_KEY', 'AMPLITUDE_SECRET_KEY', 'AMPLITUDE_MANAGEMENT_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        message = (
            f"⚠️ Variables de entorno faltantes: {', '.join(missing_vars)}\n\n"
            f"📁 Archivo .env buscado en:\n"
            f"   - {PROJECT_ROOT / '.env'}\n"
            f"   - {Path(__file__).resolve().parent / '.env'}\n\n"
            f"💡 Crea un archivo .env en una de estas ubicaciones con:\n"
            f"   AMPLITUDE_API_KEY=tu_api_key\n"
            f"   AMPLITUDE_SECRET_KEY=tu_secret_key\n"
            f"   AMPLITUDE_MANAGEMENT_KEY=tu_management_key"
        )
        return False, message
    
    if env_loaded and loaded_path:
        return True, f"✅ Variables cargadas desde: {loaded_path}"
    else:
        # Intentar carga automática (sin path específico)
        load_dotenv(override=True)
        # Verificar nuevamente
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if not missing_vars:
            return True, "✅ Variables cargadas (ubicación automática)"
        else:
            return False, (
                f"⚠️ No se encontró archivo .env en las ubicaciones esperadas.\n\n"
                f"📁 Crea un archivo .env en: {PROJECT_ROOT / '.env'}\n\n"
                f"💡 Con el siguiente contenido:\n"
                f"   AMPLITUDE_API_KEY=tu_api_key\n"
                f"   AMPLITUDE_SECRET_KEY=tu_secret_key\n"
                f"   AMPLITUDE_MANAGEMENT_KEY=tu_management_key"
            )


def safe_unique_from_column(series):
    """
    Extrae valores únicos de una serie de pandas que puede contener listas o strings.
    
    Args:
        series: Serie de pandas que puede contener strings, listas, o ambos
        
    Returns:
        list: Lista de valores únicos (strings)
    """
    unique_values = set()
    
    for value in series.dropna():
        if isinstance(value, list):
            # Si es una lista, agregar cada elemento
            for item in value:
                if item and str(item).strip().upper() not in ['ALL', 'N/A', '']:
                    unique_values.add(str(item).strip())
        else:
            # Si es un string u otro tipo, convertir a string
            value_str = str(value).strip()
            if value_str and value_str.upper() not in ['ALL', 'N/A', '']:
                unique_values.add(value_str)
    
    return sorted(list(unique_values))


def run_ui():
    st.set_page_config(
        page_title="AB Test Dashboard",
        layout="wide",
        page_icon="📊"
    )

    # Header principal
    st.title("📊 AB Test Dashboard - Amplitude")
    st.markdown("---")

    # Cargar funciones de experiment_utils
    ensure_sys_path()
    env_success, env_message = load_env()

    # Estado de sesión para persistir vistas e inputs entre reruns
    if "show_experiments" not in st.session_state:
        st.session_state["show_experiments"] = False
    if "selected_exp" not in st.session_state:
        st.session_state["selected_exp"] = None

    # Sidebar con configuración básica
    with st.sidebar:
        # ============================================================
        # SECCIÓN DE CONFIGURACIÓN DE ANÁLISIS
        # ============================================================
        st.subheader("🔍 Configuración de Análisis")
        
        # Hardcodear use_cumulative = True (toggle eliminado)
        use_cumulative = True
        
        # Cargar experimentos para la sidebar
        with st.spinner("Cargando experimentos..."):
            try:
                df_exp_sidebar = get_experiments_list()
                
                columns_to_show = ['name', 'key', 'state', 'startDate', 'endDate', 'createdAt', 'variants']
                available_columns = [col for col in columns_to_show if col in df_exp_sidebar.columns]
                df_exp_filtered_sidebar = df_exp_sidebar[available_columns].copy()
                
                date_columns = ['startDate', 'endDate', 'createdAt']
                for col in date_columns:
                    if col in df_exp_filtered_sidebar.columns:
                        df_exp_filtered_sidebar[col] = pd.to_datetime(df_exp_filtered_sidebar[col], errors='coerce')
                        df_exp_filtered_sidebar[col] = df_exp_filtered_sidebar[col].dt.strftime('%Y-%m-%d')
                
                # Procesar columna variants
                if 'variants' in df_exp_filtered_sidebar.columns:
                    def process_variants(variant_obj):
                        if variant_obj is None:
                            return "N/A"
                        try:
                            if isinstance(variant_obj, float) and pd.isna(variant_obj):
                                return "N/A"
                            if isinstance(variant_obj, list):
                                if not variant_obj:
                                    return "N/A"
                                names = []
                                for v in variant_obj:
                                    if isinstance(v, dict):
                                        names.append(v.get('name', v.get('key', str(v))))
                                    else:
                                        names.append(str(v))
                                return ", ".join(names)
                            elif isinstance(variant_obj, dict):
                                return variant_obj.get('name', variant_obj.get('key', str(variant_obj)))
                            return str(variant_obj)
                        except Exception:
                            return str(variant_obj)
                    
                    df_exp_filtered_sidebar['variants'] = df_exp_filtered_sidebar['variants'].apply(process_variants)
                
                # Selector de experimento
                if len(df_exp_filtered_sidebar) > 0:
                    experiment_options_sidebar = []
                    for idx, row in df_exp_filtered_sidebar.iterrows():
                        exp_name = row.get('name', f"Experiment {idx}")
                        exp_key = row.get('key', '')
                        exp_state = row.get('state', '')
                        display_name = f"{exp_name} ({exp_key}) - {exp_state}"
                        experiment_options_sidebar.append((display_name, idx))
                    
                    selected_exp_display_sidebar = st.selectbox(
                        "📊 Selecciona un experimento:",
                        options=[opt[0] for opt in experiment_options_sidebar],
                        help="Elige un experimento de la lista para configurar su análisis",
                        key="selected_exp_sidebar"
                    )
                    
                    # Obtener el índice del experimento seleccionado
                    try:
                        selected_exp_idx_sidebar = next(opt[1] for opt in experiment_options_sidebar if opt[0] == selected_exp_display_sidebar)
                        selected_row_sidebar = df_exp_filtered_sidebar.iloc[selected_exp_idx_sidebar]
                        selected_row_original_sidebar = df_exp_sidebar.iloc[selected_exp_idx_sidebar]
                    except StopIteration:
                        selected_exp_idx_sidebar = experiment_options_sidebar[0][1]
                        selected_row_sidebar = df_exp_filtered_sidebar.iloc[selected_exp_idx_sidebar]
                        selected_row_original_sidebar = df_exp_sidebar.iloc[selected_exp_idx_sidebar]
                    
                    # Guardar en session_state inmediatamente
                    st.session_state['selected_row_sidebar'] = selected_row_sidebar
                    st.session_state['selected_row_original_sidebar'] = selected_row_original_sidebar
                    
                    st.divider()
                    
                    # ============================================================
                    # FILTROS PRINCIPALES (Visibles directamente)
                    # ============================================================
                    st.subheader("🎯 Filtros Principales")
                    
                    device_quick = st.multiselect(
                        "📱 Device",
                        options=["desktop", "mobile"],
                        default=[],
                        key="device_quick",
                        help="Tipo de dispositivo a analizar. Deja vacío para ver todos."
                    )
                    culture_quick = st.multiselect(
                        "🌍 Culture",
                        options=["CL", "AR", "PE", "CO", "INTER"],
                        default=[],
                        key="culture_quick",
                        help="Cultura/país a analizar. INTER incluye: BR, UY, PY, EC, US, DO. Deja vacío para ver todos."
                    )
                    flow_type_quick = st.multiselect(
                        "🔄 Tipo de Flujo",
                        options=["DB", "PB", "CK"],
                        default=[],
                        key="flow_type_quick",
                        help="Tipo de flujo a analizar. Deja vacío para ver todos."
                    )
                    # Mapeo de Ventana de Conversión a Segundos (Amplitude requiere int)
                    conversion_window_options_quick = {
                        "5 minutos": 300,
                        "15 minutos": 900,
                        "30 minutos": 1800,
                        "1 hora": 3600,
                        "1 día": 86400
                    }
                    conversion_window_label_quick = st.selectbox(
                        "⏱️ Ventana de Conversión",
                        options=list(conversion_window_options_quick.keys()),
                        index=2,
                        key="conversion_window_quick",  # El widget guarda el string en session_state
                        help="Tiempo máximo para considerar una conversión válida"
                    )
                    # Convertir el string seleccionado a segundos (entero) y guardar en session_state
                    conversion_window_seconds = conversion_window_options_quick.get(conversion_window_label_quick, 1800)
                    st.session_state['conversion_window_seconds'] = conversion_window_seconds  # Guardar el entero
                    
                    st.divider()
                    
                    # ============================================================
                    # FILTROS AVANZADOS (En expander)
                    # ============================================================
                    with st.expander("⚙️ Filtros Avanzados", expanded=False):
                        bundle_profile_quick = st.multiselect(
                            "✈️ Perfil de Vuelo",
                            options=["Vuela Ligero", "Smart", "Full", "Smart + Full"],
                            default=[],
                            key="bundle_profile_quick",
                            help="Perfil de bundle del usuario. Deja vacío para ver todos."
                        )
                        trip_type_quick = st.multiselect(
                            "✈️ Tipo de Viaje",
                            options=["Solo Ida (One Way)", "Ida y Vuelta (Round Trip)"],
                            default=[],
                            key="trip_type_quick",
                            help="Tipo de viaje a analizar. Deja vacío para ver todos."
                        )
                        travel_group_quick = st.multiselect(
                            "👥 Grupo de Viaje",
                            options=["Viajero Solo", "Pareja", "Grupo", "Familia (con Menores)"],
                            default=[],
                            key="travel_group_quick",
                            help="Tipo de grupo de viaje. Deja vacío para ver todos."
                        )
                    
                    st.divider()
                    
                    # Cargar métricas
                    PREDEFINED_METRICS_QUICK = {}
                    try:
                        from src.utils.metrics_loader import (
                            load_all_metrics,
                            get_all_metrics_flat,
                            get_metrics_info
                        )
                        
                        metrics_by_category = load_all_metrics()
                        PREDEFINED_METRICS_QUICK = get_all_metrics_flat(metrics_by_category)
                        
                        # Aplicar Ghost Anchors
                        for metric_name, metric_def in PREDEFINED_METRICS_QUICK.items():
                            if isinstance(metric_def, dict) and 'events' in metric_def:
                                events_list = metric_def.get('events', [])
                                if len(events_list) > 0:
                                    first_event = events_list[0]
                                    first_event_name = first_event[0] if isinstance(first_event, tuple) else first_event
                                    if first_event_name in EVENT_ANCHOR_MAP:
                                        anchor_event = EVENT_ANCHOR_MAP[first_event_name]
                                        if first_event_name != anchor_event:
                                            anchor_tuple = (anchor_event, [])
                                            events_list.insert(0, anchor_tuple)
                                            metric_def['hidden_first_step'] = True
                    except Exception as e:
                        st.warning(f"⚠️ Error cargando métricas: {e}")
                    
                    # Selector de métricas
                    st.subheader("📊 Métricas")
                    if PREDEFINED_METRICS_QUICK:
                        selected_metrics_quick = st.multiselect(
                            "Selecciona Métricas:",
                            options=list(PREDEFINED_METRICS_QUICK.keys()),
                            default=[],
                            key="metrics_quick_sidebar",
                            help="Métricas completas predefinidas"
                        )
                    else:
                        selected_metrics_quick = []
                    
                    # Eventos individuales eliminados - asumir lista vacía
                    selected_events_raw_quick = []
                    
                    # Procesar métricas seleccionadas
                    metrics_to_process_sidebar = []
                    if selected_metrics_quick or selected_events_raw_quick:
                        # Procesar métricas predefinidas
                        for metric_name in selected_metrics_quick:
                            if metric_name in PREDEFINED_METRICS_QUICK:
                                metric_config = PREDEFINED_METRICS_QUICK[metric_name]
                                metric_events = []
                                metric_filters_map = {}
                                
                                if isinstance(metric_config, dict) and 'events' in metric_config:
                                    events_list = metric_config['events']
                                    if events_list:
                                        first_item = events_list[0]
                                        
                                        if isinstance(first_item, tuple) and len(first_item) >= 2:
                                            for event_tuple in events_list:
                                                if isinstance(event_tuple, tuple) and len(event_tuple) >= 2:
                                                    event_name = event_tuple[0]
                                                    event_filters = event_tuple[1] if isinstance(event_tuple[1], list) else []
                                                    metric_events.append(event_name)
                                                    if event_filters:
                                                        metric_filters_map[event_name] = event_filters
                                        elif isinstance(first_item, tuple) and len(first_item) == 1:
                                            for event_tuple in events_list:
                                                if isinstance(event_tuple, tuple) and len(event_tuple) > 0:
                                                    metric_events.append(event_tuple[0])
                                        elif isinstance(first_item, str):
                                            metric_events = events_list
                                            metric_filters = metric_config.get('filters', [])
                                            if metric_filters:
                                                filters_list = metric_filters if isinstance(metric_filters, list) else [metric_filters]
                                                for event in metric_events:
                                                    metric_filters_map[event] = filters_list.copy()
                                
                                elif isinstance(metric_config, list):
                                    metric_events = metric_config
                                
                                if metric_events:
                                    hidden_first_step = False
                                    if isinstance(metric_config, dict):
                                        hidden_first_step = metric_config.get('hidden_first_step', False)
                                    
                                    metrics_to_process_sidebar.append({
                                        'name': metric_name,
                                        'events': metric_events,
                                        'filters': metric_filters_map,
                                        'hidden_first_step': hidden_first_step
                                    })
                        
                        # Agregar eventos individuales
                        if selected_events_raw_quick:
                            metrics_to_process_sidebar.append({
                                'name': 'Eventos Individuales',
                                'events': selected_events_raw_quick,
                                'filters': {}
                            })
                    
                    # Guardar métricas procesadas y datos del experimento en session_state para usar en el área principal
                    # NOTA: No guardamos device_quick, culture_quick, etc. aquí porque los widgets ya manejan su propio estado
                    st.session_state['metrics_to_process_sidebar'] = metrics_to_process_sidebar
                    st.session_state['PREDEFINED_METRICS_QUICK'] = PREDEFINED_METRICS_QUICK
                    st.session_state['selected_row_sidebar'] = selected_row_sidebar
                    st.session_state['selected_row_original_sidebar'] = selected_row_original_sidebar
                    # use_cumulative se guarda porque no tiene widget con key en la sidebar actual
                    st.session_state['use_cumulative'] = use_cumulative
                    
                    st.divider()
                    
                    # ============================================================
                    # BOTÓN DE EJECUCIÓN
                    # ============================================================
                    btn_run_quick = st.button(
                        "🚀 Ejecutar Análisis",
                        use_container_width=True,
                        type="primary",
                        key="btn_run_quick_sidebar",
                        disabled=len(metrics_to_process_sidebar) == 0
                    )
                    
                    # Guardar en session_state cuando se presiona el botón
                    if btn_run_quick and metrics_to_process_sidebar:
                        st.session_state['run_analysis'] = True
                    
                else:
                    st.warning("No hay experimentos disponibles")
                    selected_exp_idx_sidebar = None
                    selected_row_sidebar = None
                    selected_row_original_sidebar = None
                    btn_run_quick = False
                    selected_metrics_quick = []
                    selected_events_raw_quick = []
                    
            except Exception as e:
                st.error(f"❌ Error cargando experimentos: {e}")
                selected_exp_idx_sidebar = None
                selected_row_sidebar = None
                selected_row_original_sidebar = None
                btn_run_quick = False
                selected_metrics_quick = []
                selected_events_raw_quick = []
        
        st.divider()
        
        # ============================================================
        # SECCIÓN DE OPTIMIZACIÓN
        # ============================================================
        st.subheader("🚀 Optimización")
        if st.button("🗑️ Limpiar Caché de Amplitude", key="clear_cache_sidebar"):
            clear_amplitude_cache()
            st.success("✅ Caché limpiado exitosamente")
            st.info("El caché acelera las consultas repetidas. Límpialo si los datos parecen desactualizados.")
        
        st.divider()
        
        # ============================================================
        # SECCIÓN DE INFORMACIÓN
        # ============================================================
        st.subheader("ℹ️ Información")
        st.info("""
        **AB Test Dashboard**
        Herramienta para analizar experimentos de Amplitude con datos de Jetsmart.
        Configura los parámetros arriba y ejecuta el análisis.
        """)

    # Tabs principales
    tab_experiments, tab_statistical, tab_help = st.tabs(["📋 Experimentos", "📊 Análisis Estadístico", "❓ Ayuda"])

    with tab_experiments:
                # Mostrar información de métricas disponibles y botón de ejecutar si hay experimento seleccionado
                if st.session_state.get('selected_row_sidebar') is not None:
                    selected_row_sidebar = st.session_state['selected_row_sidebar']
                    PREDEFINED_METRICS_QUICK = st.session_state.get('PREDEFINED_METRICS_QUICK', {})
                    metrics_to_process_sidebar = st.session_state.get('metrics_to_process_sidebar', [])
                    
                    # Mostrar detalles del experimento seleccionado
                    st.markdown("### 📋 Experimento Seleccionado")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Nombre:** {selected_row_sidebar.get('name', 'N/A')}")
                        st.write(f"**Key:** {selected_row_sidebar.get('key', 'N/A')}")
                        st.write(f"**Estado:** {selected_row_sidebar.get('state', 'N/A')}")
                    with col2:
                        st.write(f"**Fecha Inicio:** {selected_row_sidebar.get('startDate', 'N/A')}")
                        end_date_display = selected_row_sidebar.get('endDate', 'N/A')
                        if pd.isna(end_date_display) or end_date_display in ['None', 'nan', '']:
                            end_date_display = f"{pd.Timestamp.now().strftime('%Y-%m-%d')} (Hoy)"
                        st.write(f"**Fecha Fin:** {end_date_display}")
                        st.write(f"**Variantes:** {selected_row_sidebar.get('variants', 'N/A')}")
                    
                    st.markdown("---")
                    
                    # Mostrar tabla de métricas disponibles
                    if PREDEFINED_METRICS_QUICK:
                        try:
                            from src.utils.metrics_loader import get_metrics_info
                            metrics_info_quick = get_metrics_info(PREDEFINED_METRICS_QUICK)
                            
                            if metrics_info_quick:
                                with st.expander("📚 Ver Métricas Disponibles", expanded=False):
                                    df_metrics_quick = pd.DataFrame(metrics_info_quick)
                                    st.dataframe(
                                        df_metrics_quick,
                                        use_container_width=True,
                                        hide_index=True
                                    )
                        except Exception as e:
                            st.warning(f"⚠️ Error mostrando métricas: {e}")
                    
                    st.markdown("---")
                    
                    # Botón de ejecutar ahora está en la sidebar
                    # Verificar si se presionó desde la sidebar
                    btn_run_quick = st.session_state.get('run_analysis', False)
                    
                    if btn_run_quick and metrics_to_process_sidebar:
                        st.session_state['run_analysis'] = True
                        st.session_state['metrics_to_process'] = metrics_to_process_sidebar
                        st.session_state['selected_row_original'] = st.session_state['selected_row_original_sidebar']
                        st.session_state['selected_row'] = selected_row_sidebar
                
                # Ejecutar análisis si se presionó el botón
                if st.session_state.get('run_analysis', False) and st.session_state.get('metrics_to_process'):
                    metrics_to_process = st.session_state['metrics_to_process']
                    selected_row_original = st.session_state['selected_row_original']
                    selected_row = st.session_state['selected_row']
                    # Leer valores directamente de los widgets (que ya están en session_state automáticamente)
                    # Los multiselect devuelven listas. Si está vacía, significa "ALL" (todos)
                    device_quick = st.session_state.get('device_quick', [])
                    culture_quick_raw = st.session_state.get('culture_quick', [])
                    # Expandir INTER a la lista de países
                    def expand_inter_culture(value):
                        """Expande 'INTER' en la lista de culture a los países que representa.
                        INTER incluye: BR, UY, PY, EC, US, DO
                        """
                        if value is None:
                            return value
                        if isinstance(value, list):
                            expanded = []
                            for item in value:
                                if item == 'INTER':
                                    expanded.extend(['BR', 'UY', 'PY', 'EC', 'US', 'DO'])
                                else:
                                    expanded.append(item)
                            return expanded if expanded else value
                        if isinstance(value, str) and value == 'INTER':
                            return ['BR', 'UY', 'PY', 'EC', 'US', 'DO']
                        return value
                    culture_quick = expand_inter_culture(culture_quick_raw)
                    flow_type_quick = st.session_state.get('flow_type_quick', [])
                    bundle_profile_quick = st.session_state.get('bundle_profile_quick', [])
                    trip_type_quick = st.session_state.get('trip_type_quick', [])
                    travel_group_quick = st.session_state.get('travel_group_quick', [])
                    
                    # Obtener ventana de conversión (ya convertida a segundos en la sidebar)
                    # El widget guarda el string en 'conversion_window_quick', pero guardamos el entero en 'conversion_window_seconds'
                    conversion_window_quick = st.session_state.get('conversion_window_seconds', 1800)
                    # Fallback: si no existe el valor convertido, convertir desde el string
                    if conversion_window_quick == 1800 and 'conversion_window_quick' in st.session_state:
                        conversion_window_label = st.session_state.get('conversion_window_quick')
                        if isinstance(conversion_window_label, str):
                            conversion_window_map = {
                                "5 minutos": 300,
                                "15 minutos": 900,
                                "30 minutos": 1800,
                                "1 hora": 3600,
                                "1 día": 86400
                            }
                            conversion_window_quick = conversion_window_map.get(conversion_window_label, 1800)
                    
                    use_cumulative = st.session_state.get('use_cumulative', True)
                    
                    # Ejecutar análisis
                    if metrics_to_process:
                        with st.spinner("Ejecutando análisis..."):
                            try:
                                # Obtener fechas del experimento con precisión horaria desde el DataFrame original
                                start_date_raw = selected_row_original.get('startDate', None)
                                end_date_raw = selected_row_original.get('endDate', None)
                                
                                # Normalizar start_date: preservar hora completa si está disponible
                                if start_date_raw is None or pd.isna(start_date_raw) or str(start_date_raw) in ['None', 'nan', '']:
                                    start_date_quick = '2024-01-01 00:00:00'
                                else:
                                    # Intentar parsear la fecha manteniendo la hora si está presente
                                    try:
                                        start_dt = pd.to_datetime(start_date_raw)
                                        # Si tiene hora, mantenerla; si no, usar 00:00:00
                                        if start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0:
                                            start_date_quick = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                                        else:
                                            start_date_quick = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                                    except Exception:
                                        # Fallback: asumir formato YYYY-MM-DD y agregar hora
                                        start_date_quick = f"{str(start_date_raw).strip()} 00:00:00"
                                
                                # Normalizar end_date: preservar hora completa si está disponible
                                if end_date_raw is None or pd.isna(end_date_raw) or str(end_date_raw) in ['None', 'nan', '']:
                                    # Si no hay fecha de fin, usar fecha de hoy con hora 23:59:59
                                    end_date_quick = pd.Timestamp.now().strftime('%Y-%m-%d 23:59:59')
                                else:
                                    # Intentar parsear la fecha manteniendo la hora si está presente
                                    try:
                                        end_dt = pd.to_datetime(end_date_raw)
                                        # Si tiene hora, mantenerla; si no, usar 23:59:59 para cubrir el día completo
                                        if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                                            end_date_quick = end_dt.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
                                        else:
                                            end_date_quick = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                                    except Exception:
                                        # Fallback: asumir formato YYYY-MM-DD y agregar hora 23:59:59
                                        end_date_quick = f"{str(end_date_raw).strip()} 23:59:59"
                                
                                experiment_id_quick = selected_row.get('key', '')
                                
                                # Obtener variantes del experimento para mostrar información
                                experiment_variants = get_experiment_variants(experiment_id_quick)
                                
                                # Diccionario para almacenar resultados por métrica
                                metrics_results = {}
                                
                                # Procesar cada métrica por separado
                                progress_bar = st.progress(0)
                                total_metrics = len(metrics_to_process)
                                
                                for idx, metric_info in enumerate(metrics_to_process):
                                    metric_name = metric_info['name']
                                    metric_events = metric_info['events']
                                    metric_filters = metric_info['filters']
                                    
                                    # Actualizar progreso
                                    progress_bar.progress((idx + 1) / total_metrics)
                                    
                                    # Ejecutar pipeline para esta métrica
                                    pipeline_kwargs = {
                                        'start_date': start_date_quick,
                                        'end_date': end_date_quick,
                                        'experiment_id': experiment_id_quick,
                                        'device': device_quick,
                                        'culture': culture_quick,
                                        'event_list': metric_events,
                                        'conversion_window': conversion_window_quick,
                                        'flow_type': flow_type_quick,
                                        'bundle_profile': bundle_profile_quick,
                                        'trip_type': trip_type_quick,
                                        'travel_group': travel_group_quick
                                    }
                                    
                                    # Agregar event_filters_map solo si existe y no está vacío
                                    if metric_filters:
                                        pipeline_kwargs['event_filters_map'] = metric_filters
                                    
                                    # Agregar hidden_first_step si la métrica lo tiene
                                    if metric_info.get('hidden_first_step', False):
                                        pipeline_kwargs['hidden_first_step'] = True
                                    
                                    try:
                                        if use_cumulative:
                                            df_metric = final_pipeline_cumulative(**pipeline_kwargs)
                                        else:
                                            df_metric = final_pipeline(**pipeline_kwargs)
                                        
                                        # Guardar resultado de esta métrica
                                        metrics_results[metric_name] = df_metric
                                    except Exception as e:
                                        st.warning(f"⚠️ Error procesando métrica '{metric_name}': {e}")
                                        metrics_results[metric_name] = pd.DataFrame()
                                
                                progress_bar.empty()
                                
                                # Guardar todos los resultados en session_state
                                # El nombre de la métrica ya es el display name (viene de PREDEFINED_METRICS_QUICK)
                                st.session_state['metrics_results'] = metrics_results
                                st.session_state['analysis_experiment_id'] = experiment_id_quick
                                st.session_state['analysis_experiment_name'] = selected_row.get('name', experiment_id_quick)
                                
                                # Guardar parámetros originales para el desglose
                                # Normalizar valores para consistencia: listas vacías = "ALL"
                                def normalize_filter_value(value):
                                    """Normaliza valores de filtro para consistencia.
                                    Si es una lista vacía o None, retorna "ALL".
                                    Si es una lista con elementos, retorna la lista.
                                    Si es un string "ALL", retorna "ALL".
                                    """
                                    if value is None:
                                        return "ALL"
                                    if isinstance(value, list):
                                        if len(value) == 0:
                                            return "ALL"
                                        return value
                                    value_str = str(value).strip()
                                    if value_str.upper() == "ALL":
                                        return "ALL"
                                    return value
                                
                                st.session_state['analysis_params'] = {
                                    'start_date': start_date_quick,
                                    'end_date': end_date_quick,
                                    'experiment_id': experiment_id_quick,
                                    'device': normalize_filter_value(device_quick),
                                    'culture': normalize_filter_value(culture_quick),
                                    'flow_type': normalize_filter_value(flow_type_quick),
                                    'bundle_profile': normalize_filter_value(bundle_profile_quick),
                                    'trip_type': normalize_filter_value(trip_type_quick),
                                    'travel_group': normalize_filter_value(travel_group_quick),
                                    'conversion_window': conversion_window_quick,
                                    'use_cumulative': use_cumulative
                                }
                                
                                # Guardar lista de métricas procesadas
                                st.session_state['analysis_metrics'] = metrics_to_process
                                
                                # Mostrar resumen de resultados
                                st.success(f"✅ Análisis completado: {len(metrics_results)} métrica(s) procesada(s)")
                                
                                # Información sobre variantes detectadas
                                if experiment_variants:
                                    st.info(f"**Variantes detectadas:** {', '.join(experiment_variants)}")
                                
                                # ============================================
                                # TABLA 1: RESUMEN EJECUTIVO (1 fila por métrica)
                                # ============================================
                                st.markdown("### 📊 Resumen Ejecutivo")
                                summary_data = []
                                for metric_name, df_metric in metrics_results.items():
                                    if not df_metric.empty:
                                        summary_data.append({
                                            'Métrica': metric_name,
                                            'Registros': len(df_metric),
                                            'Variantes': df_metric['Variant'].nunique() if 'Variant' in df_metric.columns else 0,
                                            'Etapas': df_metric['Funnel Stage'].nunique() if 'Funnel Stage' in df_metric.columns else 0,
                                            'Total Eventos': f"{df_metric['Event Count'].sum():,.0f}" if 'Event Count' in df_metric.columns else "0"
                                        })
                                
                                if summary_data:
                                    df_metric_summary = pd.DataFrame(summary_data)
                                    st.dataframe(df_metric_summary, use_container_width=True, hide_index=True)
                                
                                # ============================================
                                # TABLA 2: DETALLE DE DATOS (Todas las filas)
                                # ============================================
                                st.markdown("### 📋 Detalle de Datos")
                                
                                # Combinar todos los DataFrames de métricas en uno solo
                                all_detailed_data = []
                                
                                # Preparar fechas formateadas
                                try:
                                    if ' ' in start_date_quick or 'T' in start_date_quick:
                                        start_dt = pd.to_datetime(start_date_quick)
                                        start_date_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                                    else:
                                        start_dt = pd.to_datetime(start_date_quick)
                                        start_date_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                                    
                                    if ' ' in end_date_quick or 'T' in end_date_quick:
                                        end_dt = pd.to_datetime(end_date_quick)
                                        end_date_formatted = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                                    else:
                                        end_dt = pd.to_datetime(end_date_quick)
                                        end_dt = end_dt.replace(hour=23, minute=59, second=59)
                                        end_date_formatted = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                                except Exception:
                                    start_date_formatted = start_date_quick
                                    end_date_formatted = end_date_quick
                                
                                # Procesar cada métrica y agregar columnas de contexto
                                for metric_name, df_metric in metrics_results.items():
                                    if not df_metric.empty:
                                        df_metric_copy = df_metric.copy()
                                        
                                        # Agregar columna de métrica
                                        df_metric_copy['Métrica'] = metric_name
                                        
                                        # Agregar columnas de filtro de contexto
                                        # Convertir listas a strings para mostrar en el DataFrame
                                        def format_filter_value(value):
                                            """Convierte valores de filtro a string para mostrar en DataFrame"""
                                            if isinstance(value, list):
                                                if len(value) == 0:
                                                    return "ALL"
                                                return ", ".join(str(v) for v in value)
                                            return str(value) if value else "ALL"
                                        
                                        df_metric_copy['Flow Type'] = format_filter_value(flow_type_quick)
                                        df_metric_copy['Trip Type'] = format_filter_value(trip_type_quick)
                                        df_metric_copy['Flight Profile'] = format_filter_value(bundle_profile_quick)
                                        df_metric_copy['Travel Group'] = format_filter_value(travel_group_quick)
                                        
                                        # Formatear fechas como strings si existen
                                        if use_cumulative:
                                            # Para datos acumulados: Start Date y End Date
                                            if 'Start Date' in df_metric_copy.columns:
                                                df_metric_copy['Start Date'] = pd.to_datetime(df_metric_copy['Start Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
                                            else:
                                                # Si no existe, agregar desde las variables
                                                df_metric_copy['Start Date'] = start_date_formatted
                                            
                                            if 'End Date' in df_metric_copy.columns:
                                                df_metric_copy['End Date'] = pd.to_datetime(df_metric_copy['End Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
                                            else:
                                                df_metric_copy['End Date'] = end_date_formatted
                                        else:
                                            # Para datos diarios: Date
                                            if 'Date' in df_metric_copy.columns:
                                                df_metric_copy['Date'] = pd.to_datetime(df_metric_copy['Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
                                            else:
                                                # Si no existe Date, agregar Start Date y End Date
                                                df_metric_copy['Start Date'] = start_date_formatted
                                                df_metric_copy['End Date'] = end_date_formatted
                                        
                                        # Asegurar que ExperimentID, Culture y Device estén presentes
                                        if 'ExperimentID' not in df_metric_copy.columns:
                                            df_metric_copy['ExperimentID'] = experiment_id_quick
                                        if 'Culture' not in df_metric_copy.columns:
                                            df_metric_copy['Culture'] = culture_quick
                                        if 'Device' not in df_metric_copy.columns:
                                            df_metric_copy['Device'] = device_quick
                                        
                                        all_detailed_data.append(df_metric_copy)
                                
                                # Combinar todos los DataFrames
                                if all_detailed_data:
                                    df_detailed = pd.concat(all_detailed_data, axis=0, ignore_index=True)
                                    
                                    # Reordenar columnas para mejor visualización
                                    preferred_order = [
                                        'Métrica', 'Start Date', 'End Date', 'Date',
                                        'ExperimentID', 'Culture', 'Device',
                                        'Flow Type', 'Trip Type', 'Flight Profile', 'Travel Group',
                                        'Variant', 'Funnel Stage', 'Event Count'
                                    ]
                                    
                                    # Obtener columnas existentes en el orden preferido
                                    existing_columns = [col for col in preferred_order if col in df_detailed.columns]
                                    # Agregar cualquier columna adicional que no esté en la lista
                                    remaining_columns = [col for col in df_detailed.columns if col not in existing_columns]
                                    final_column_order = existing_columns + remaining_columns
                                    
                                    df_detailed = df_detailed[final_column_order]
                                    st.dataframe(df_detailed, use_container_width=True, hide_index=True)
                                    
                                    # Botón de descarga para tabla detallada
                                    col1, col2, col3 = st.columns([1, 1, 1])
                                    with col2:
                                        excel_buffer_detailed = BytesIO()
                                        df_detailed.to_excel(excel_buffer_detailed, index=False, engine='openpyxl')
                                        excel_buffer_detailed.seek(0)
                                        st.download_button(
                                            label="📥 Descargar Tabla Detallada (Excel)",
                                            data=excel_buffer_detailed.getvalue(),
                                            file_name=f"ab_test_detailed_{experiment_id_quick}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            use_container_width=True
                                        )
                                else:
                                    st.warning("⚠️ No hay datos detallados disponibles para mostrar")
                                
                                # Resetear el flag de ejecución después de procesar
                                st.session_state['run_analysis'] = False
                                
                            except Exception as e:
                                st.error(f"❌ Error ejecutando análisis: {e}")
                                st.exception(e)
                                # Resetear el flag incluso si hay error
                                st.session_state['run_analysis'] = False
                    else:
                        # Si no hay métricas seleccionadas, mostrar mensaje
                        if st.session_state.get('run_analysis', False):
                            st.warning("⚠️ Por favor selecciona al menos una métrica o evento en la barra lateral")
                st.session_state['run_analysis'] = False

    with tab_statistical:
        st.subheader("📊 Análisis Estadístico A/B/N")
        st.caption("Análisis estadístico completo con p-values, lift, P2BB y significancia")
        
        # Verificar si hay datos disponibles (nuevo formato con múltiples métricas o formato antiguo)
        has_metrics_results = 'metrics_results' in st.session_state and st.session_state['metrics_results']
        has_single_df = 'analysis_df' in st.session_state and st.session_state['analysis_df'] is not None and not st.session_state['analysis_df'].empty
        
        if not has_metrics_results and not has_single_df:
            st.info("""
            ℹ️ **No hay datos disponibles para análisis estadístico**
            
            Para usar esta funcionalidad:
            1. Ve a la pestaña **📋 Experimentos**
            2. Selecciona un experimento y ejecuta un análisis
            3. Los resultados estarán disponibles aquí para análisis estadístico
            """)
        else:
            experiment_id_stat = st.session_state.get('analysis_experiment_id', 'N/A')
            experiment_name_stat = st.session_state.get('analysis_experiment_name', 'N/A')
            
            # Determinar qué métrica(s) analizar
            if has_metrics_results:
                # Nuevo formato: múltiples métricas - mostrar todas de una vez
                metrics_results = st.session_state['metrics_results']
                # HARDENING: Materializar available_metrics como lista explícita
                available_metrics = list([(name, df) for name, df in metrics_results.items() if df is not None and not df.empty])
                
                if not available_metrics:
                    st.warning("⚠️ No hay métricas con datos disponibles para análisis")
                else:
                    # Mostrar información del experimento
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, #1B365D 0%, #4A6489 100%); 
                                border: 2px solid #3CCFE7; 
                                border-radius: 12px; 
                                padding: 20px; 
                                margin: 20px 0; 
                                text-align: center;">
                        <h3 style="color: white; margin: 0; font-size: 1.3em;">
                            {experiment_name_stat} ({experiment_id_stat})
                        </h3>
                        <p style="color: #E0E0E0; margin: 10px 0 0 0;">
                            Total de métricas analizadas: <strong>{len(available_metrics)}</strong>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Importar funciones de análisis estadístico
                    from src.utils.statistical_analysis import (
                        prepare_variants_from_dataframe,
                        calculate_ab_test,
                        calculate_chi_square_test,
                        create_metric_card,
                        create_multivariant_card
                    )
                    
                    # Función auxiliar para ordenar variantes: control primero, luego variant-1, variant-2, etc.
                    def sort_variants_correctly(variants_list, experiment_id):
                        """Ordena las variantes: control primero, luego variant-1, variant-2, etc."""
                        try:
                            # Obtener el orden oficial de variantes del experimento
                            ordered_variants = get_experiment_variants(experiment_id)
                            # Crear diccionario para mapear orden
                            variant_order = {name: idx for idx, name in enumerate(ordered_variants)}
                            
                            # Ordenar según el orden del experimento
                            def get_sort_key(variant):
                                name = variant.get('name', '')
                                # Si la variante está en la lista del experimento, usar su índice
                                if name in variant_order:
                                    return variant_order[name]
                                # Si no está, intentar ordenar por nombre (control primero, luego variant-1, variant-2)
                                name_lower = name.lower()
                                if name_lower == 'control':
                                    return -1  # Control siempre primero
                                elif name_lower.startswith('variant-'):
                                    try:
                                        # Extraer número: variant-1 -> 1, variant-2 -> 2, etc.
                                        num_str = name_lower.replace('variant-', '').split('-')[0]
                                        variant_num = int(re.match(r'^(\d+)', num_str).group(1))
                                        return variant_num  # variant-1 = 1, variant-2 = 2, etc.
                                    except (ValueError, AttributeError):
                                        return 999
                                return 9999  # Otros al final
                            
                            return sorted(variants_list, key=get_sort_key)
                        except Exception:
                            # Si falla, intentar ordenamiento simple por nombre
                            def get_simple_sort_key(variant):
                                name = variant.get('name', '').lower()
                                if name == 'control':
                                    return (0, '')
                                elif name.startswith('variant-'):
                                    try:
                                        num_str = name.replace('variant-', '').split('-')[0]
                                        variant_num = int(re.match(r'^(\d+)', num_str).group(1))
                                        return (1, variant_num)
                                    except (ValueError, AttributeError):
                                        return (2, name)
                                return (2, name)
                            return sorted(variants_list, key=get_simple_sort_key)
                    
                    # Procesar cada métrica y mostrar en su propio recuadro
                    for metric_key, df_analysis in available_metrics:
                        # El nombre de la métrica ya es el display name
                        metric_display_name = metric_key
                        
                        # Análisis estadístico para esta métrica
                        if 'Funnel Stage' in df_analysis.columns:
                            # Obtener etapas únicas del funnel
                            available_stages = df_analysis['Funnel Stage'].unique().tolist()
                            
                            # Obtener el orden correcto de eventos desde la configuración de la métrica
                            # Cargar métricas automáticamente para buscar la configuración
                            metric_config = None
                            try:
                                from src.utils.metrics_loader import get_all_metrics_flat
                                all_metrics = get_all_metrics_flat()
                                metric_config = all_metrics.get(metric_display_name)
                            except Exception:
                                # Si no se pueden cargar, continuar sin configuración
                                pass
                            
                            # Determinar initial_stage y final_stage según el orden de eventos en la métrica
                            if metric_config and 'events' in metric_config and len(metric_config['events']) >= 2:
                                # Verificar si esta métrica tiene hidden_first_step (Ghost Anchor)
                                hidden_first_step = metric_config.get('hidden_first_step', False)
                                
                                # Extraer nombres de eventos (pueden ser tuplas o strings)
                                event_names = []
                                for event_item in metric_config['events']:
                                    if isinstance(event_item, tuple) and len(event_item) > 0:
                                        event_names.append(event_item[0])
                                    elif isinstance(event_item, str):
                                        event_names.append(event_item)
                                
                                # Si hidden_first_step == True, filtrar el stage del evento ancla de available_stages
                                # y usar el segundo evento como initial_stage
                                if hidden_first_step and len(event_names) >= 2:
                                    # Identificar el stage del evento ancla (primer evento)
                                    anchor_event_name = event_names[0]
                                    
                                    # Función auxiliar para normalizar nombres de eventos (definida más abajo)
                                    def normalize_event_name_for_filter(name):
                                        """Normaliza el nombre del evento para comparación"""
                                        name = name.replace('[Amplitude]', '').strip()
                                        if name.startswith('ce:'):
                                            name = name[3:].strip()
                                            if name.startswith('('):
                                                end_paren = name.find(')')
                                                if end_paren != -1:
                                                    name = name[end_paren + 1:].strip()
                                        return name.lower().strip()
                                    
                                    # Filtrar el stage del evento ancla de available_stages
                                    normalized_anchor = normalize_event_name_for_filter(anchor_event_name)
                                    available_stages_filtered = [
                                        stage for stage in available_stages
                                        if normalize_event_name_for_filter(stage) != normalized_anchor
                                    ]
                                    
                                    # Si no quedan stages después de filtrar, usar todos (fallback)
                                    if not available_stages_filtered:
                                        available_stages_filtered = available_stages
                                    
                                    # Usar el segundo evento (índice 1) como initial_stage
                                    # El último evento sigue siendo final_stage
                                    event_names_for_stages = event_names[1:]  # Recortar el primer evento
                                    available_stages = available_stages_filtered  # Actualizar available_stages
                                else:
                                    event_names_for_stages = event_names
                                
                                # Usar el orden de eventos de la métrica
                                # Para WCR: conversión = revenue_amount / baggage_dom_loaded
                                # En prepare_variants_from_dataframe:
                                #   - initial_stage → n (denominador) = baggage_dom_loaded
                                #   - final_stage → x (numerador) = revenue_amount
                                # Conversión = x/n = final_stage / initial_stage
                                
                                # Función auxiliar para normalizar nombres de eventos
                                def normalize_event_name(name):
                                    """Normaliza el nombre del evento removiendo prefijos y espacios"""
                                    # Remover prefijos comunes como [Amplitude]
                                    name = name.replace('[Amplitude]', '').strip()
                                    # Manejar custom events con prefijo ce:
                                    if name.startswith('ce:'):
                                        name = name[3:].strip()  # Remover 'ce:'
                                        # Remover paréntesis si existen: 'ce:(NEW) evento' -> 'evento'
                                        if name.startswith('('):
                                            end_paren = name.find(')')
                                            if end_paren != -1:
                                                name = name[end_paren + 1:].strip()
                                    # Convertir a minúsculas y normalizar espacios
                                    return name.lower().strip()
                                
                                # Función auxiliar para extraer palabra clave del evento
                                def get_event_keyword(name):
                                    """Extrae la palabra clave principal del nombre del evento"""
                                    # Remover prefijos
                                    name = name.replace('[Amplitude]', '').strip()
                                    # Manejar custom events
                                    if name.startswith('ce:'):
                                        name = name[3:].strip()
                                        if name.startswith('('):
                                            end_paren = name.find(')')
                                            if end_paren != -1:
                                                name = name[end_paren + 1:].strip()
                                    # Convertir a minúsculas
                                    name = name.lower()
                                    # Si tiene guiones bajos, tomar la primera parte (más significativa)
                                    if '_' in name:
                                        parts = name.split('_')
                                        # Para revenue_amount, tomar 'revenue'
                                        # Para baggage_dom_loaded, tomar 'baggage'
                                        return parts[0] if len(parts) > 0 else name
                                    # Si no tiene guiones bajos, devolver el nombre completo
                                    return name
                                
                                # Función auxiliar para buscar stage por evento
                                def find_stage_by_event(event_name, available_stages, exclude_stage=None):
                                    """Busca un stage que coincida con el nombre del evento"""
                                    # Normalizar el evento
                                    normalized_event = normalize_event_name(event_name)
                                    keyword_event = get_event_keyword(event_name)
                                    
                                    # 1. Coincidencia exacta
                                    for stage in available_stages:
                                        if stage == event_name and stage != exclude_stage:
                                            return stage
                                    
                                    # 2. Coincidencia normalizada exacta
                                    for stage in available_stages:
                                        if stage != exclude_stage:
                                            normalized_stage = normalize_event_name(stage)
                                            if normalized_event == normalized_stage:
                                                return stage
                                    
                                    # 3. Coincidencia por palabra clave
                                    for stage in available_stages:
                                        if stage != exclude_stage:
                                            keyword_stage = get_event_keyword(stage)
                                            if keyword_event == keyword_stage and keyword_event:
                                                return stage
                                    
                                    # 4. Coincidencia parcial (el evento contiene el stage o viceversa)
                                    for stage in available_stages:
                                        if stage != exclude_stage:
                                            normalized_stage = normalize_event_name(stage)
                                            keyword_stage = get_event_keyword(stage)
                                            if (normalized_event in normalized_stage or normalized_stage in normalized_event or
                                                keyword_event in keyword_stage or keyword_stage in keyword_event):
                                                return stage
                                    
                                    return None
                                
                                # Buscar el primer evento (initial_stage) - debe ser el denominador
                                # Si hidden_first_step, usar el segundo evento (event_names_for_stages[0])
                                initial_stage = find_stage_by_event(event_names_for_stages[0], available_stages)
                                
                                # Buscar el último evento (final_stage) - debe ser el numerador
                                # Excluir initial_stage para asegurar que sean diferentes
                                final_stage = find_stage_by_event(event_names_for_stages[-1], available_stages, exclude_stage=initial_stage)
                                
                                # Si aún no se encuentran, usar FALLBACK INTELIGENTE que respeta el orden de la métrica
                                # NO usar orden alfabético porque puede invertir los eventos
                                if not initial_stage or not final_stage:
                                    # FALLBACK: Buscar por coincidencia parcial más agresiva
                                    # Intentar encontrar stages que contengan palabras clave de los eventos
                                    
                                    if not initial_stage:
                                        # Buscar stage que mejor coincida con el primer evento
                                        first_event_lower = event_names_for_stages[0].lower()
                                        best_match = None
                                        best_score = 0
                                        
                                        for stage in available_stages:
                                            stage_lower = stage.lower()
                                            # Calcular score de coincidencia (palabras en común)
                                            first_words = set(first_event_lower.replace('_', ' ').split())
                                            stage_words = set(stage_lower.replace('_', ' ').split())
                                            common_words = first_words.intersection(stage_words)
                                            score = len(common_words)
                                            
                                            if score > best_score:
                                                best_score = score
                                                best_match = stage
                                        
                                        # Si encontramos alguna coincidencia, usarla; si no, usar el primer stage disponible
                                        initial_stage = best_match if best_match else available_stages[0]
                                    
                                    if not final_stage:
                                        # Buscar stage que mejor coincida con el último evento (excluyendo initial_stage)
                                        last_event_lower = event_names_for_stages[-1].lower()
                                        best_match = None
                                        best_score = 0
                                        
                                        for stage in available_stages:
                                            if stage == initial_stage:
                                                continue
                                            
                                            stage_lower = stage.lower()
                                            # Calcular score de coincidencia (palabras en común)
                                            last_words = set(last_event_lower.replace('_', ' ').split())
                                            stage_words = set(stage_lower.replace('_', ' ').split())
                                            common_words = last_words.intersection(stage_words)
                                            score = len(common_words)
                                            
                                            if score > best_score:
                                                best_score = score
                                                best_match = stage
                                        
                                        # Si encontramos alguna coincidencia, usarla
                                        if best_match:
                                            final_stage = best_match
                                        else:
                                            # Buscar cualquier stage diferente al initial_stage
                                            for stage in available_stages:
                                                if stage != initial_stage:
                                                    final_stage = stage
                                                    break
                                            
                                            # Si no hay otro stage, hay un problema
                                            if not final_stage:
                                                if len(available_stages) > 1:
                                                    # Tomar el último disponible
                                                    final_stage = available_stages[-1]
                                                else:
                                                    # Solo hay un stage disponible - no podemos hacer análisis
                                                    initial_stage = None
                                                    final_stage = None
                                    
                                    # Verificación final: asegurar que sean diferentes
                                    if initial_stage and final_stage and initial_stage == final_stage and len(available_stages) > 1:
                                        # Si son iguales pero hay más stages, buscar otro stage
                                        for stage in available_stages:
                                            if stage != initial_stage:
                                                final_stage = stage
                                                break
                            else:
                                # Fallback: usar orden alfabético inteligente (ignorando prefijos)
                                # Normalizar nombres para ordenar (remover [Amplitude] y otros prefijos)
                                def normalize_for_sorting(name):
                                    """Normaliza el nombre para ordenamiento, removiendo prefijos"""
                                    # Remover prefijos comunes
                                    name = name.replace('[Amplitude]', '').strip()
                                    # Convertir a minúsculas y remover espacios
                                    name = name.lower().strip()
                                    # Priorizar eventos que empiezan con ciertas palabras clave
                                    # (baggage, seatmap, etc. suelen ser eventos iniciales)
                                    priority_keywords = ['baggage', 'seatmap', 'checkout', 'payment']
                                    for keyword in priority_keywords:
                                        if name.startswith(keyword):
                                            return f"0_{name}"  # Prioridad alta (viene primero)
                                    return f"1_{name}"  # Prioridad normal
                                
                                # Ordenar por nombre normalizado, pero mantener los nombres originales
                                sorted_stages = sorted(available_stages, key=normalize_for_sorting)
                                initial_stage = sorted_stages[0]
                                final_stage = sorted_stages[-1] if len(sorted_stages) > 1 else sorted_stages[0]
                            
                            # Verificar que tenemos stages válidos y diferentes
                            if initial_stage and final_stage and initial_stage != final_stage:
                                    # Si hidden_first_step == True, filtrar el DataFrame para excluir el stage del evento ancla
                                    df_analysis_filtered = df_analysis.copy()
                                    if metric_config and metric_config.get('hidden_first_step', False):
                                        # Obtener el nombre del evento ancla (primer evento)
                                        anchor_event_name = None
                                        if 'events' in metric_config and metric_config['events']:
                                            first_event = metric_config['events'][0]
                                            anchor_event_name = first_event[0] if isinstance(first_event, tuple) else first_event
                                        
                                        if anchor_event_name:
                                            # Función auxiliar para normalizar nombres de eventos
                                            def normalize_event_name_for_filter(name):
                                                """Normaliza el nombre del evento para comparación"""
                                                name = name.replace('[Amplitude]', '').strip()
                                                if name.startswith('ce:'):
                                                    name = name[3:].strip()
                                                    if name.startswith('('):
                                                        end_paren = name.find(')')
                                                        if end_paren != -1:
                                                            name = name[end_paren + 1:].strip()
                                                return name.lower().strip()
                                            
                                            # Filtrar filas que corresponden al stage del evento ancla
                                            normalized_anchor = normalize_event_name_for_filter(anchor_event_name)
                                            df_analysis_filtered = df_analysis_filtered[
                                                df_analysis_filtered['Funnel Stage'].apply(
                                                    lambda stage: normalize_event_name_for_filter(stage) != normalized_anchor
                                                )
                                            ]
                                    
                                    # Preparar variantes usando el DataFrame filtrado
                                    variants = prepare_variants_from_dataframe(
                                        df_analysis_filtered,
                                        initial_stage=initial_stage,
                                        final_stage=final_stage
                                    )
                                    
                                    # Ordenar variantes correctamente: control primero, luego variant-1, variant-2, etc.
                                    variants = sort_variants_correctly(variants, experiment_id_stat)
                                    
                                    if len(variants) >= 2:
                                        # Análisis según número de variantes
                                        if len(variants) == 2:
                                            # Análisis A/B simple
                                            control = variants[0]
                                            treatment = variants[1]
                                            
                                            results = calculate_ab_test(
                                                control['n'], control['x'],
                                                treatment['n'], treatment['x']
                                            )
                                            
                                            # Crear estructura de datos para la tarjeta
                                            comparison_data = {
                                                'baseline': control,
                                                'treatment': treatment
                                            }
                                            
                                            # Mostrar tarjeta de métrica: Header = Experimento, Sub-header = Métrica
                                            create_metric_card(
                                                metric_name=metric_display_name,
                                                data=comparison_data,
                                                results=results,
                                                experiment_name=experiment_name_stat,
                                                metric_subtitle=metric_display_name
                                            )
                                            
                                            
                                        else:
                                            # Análisis multivariante - usar diseño de tabla
                                            # Test Chi-cuadrado global
                                            chi_square_result = calculate_chi_square_test(variants)
                                            
                                            # Mostrar tarjeta multivariante: Header = Experimento, Sub-header = Métrica
                                            create_multivariant_card(
                                                metric_name=metric_display_name,
                                                variants=variants,
                                                experiment_name=experiment_name_stat,
                                                metric_subtitle=metric_display_name,
                                                chi_square_result=chi_square_result
                                            )
                                            
                                    else:
                                        st.warning(f"⚠️ Se necesitan al menos 2 variantes para el análisis estadístico de '{metric_display_name}'. Se encontraron {len(variants)} variantes.")
                            else:
                                # Construir mensaje de error más informativo
                                error_msg = f"⚠️ **No se pudieron encontrar etapas diferentes** para la métrica '{metric_display_name}'\n\n"
                                
                                if metric_config and 'events' in metric_config:
                                    event_names = []
                                    for event_item in metric_config['events']:
                                        if isinstance(event_item, tuple) and len(event_item) > 0:
                                            event_names.append(event_item[0])
                                        elif isinstance(event_item, str):
                                            event_names.append(event_item)
                                    
                                    if event_names:
                                        error_msg += f"**Eventos esperados:**\n"
                                        error_msg += f"- Inicial: `{event_names[0]}`\n"
                                        error_msg += f"- Final: `{event_names[-1]}`\n\n"
                                
                                error_msg += f"**Etapas disponibles en los datos:** {', '.join(f'`{s}`' for s in available_stages)}\n\n"
                                
                                if initial_stage and final_stage:
                                    error_msg += f"**Etapas detectadas:** Inicial=`{initial_stage}`, Final=`{final_stage}` (son iguales)\n\n"
                                elif not initial_stage or not final_stage:
                                    error_msg += f"**Problema:** No se pudo encontrar una coincidencia para los eventos de la métrica en los datos disponibles.\n\n"
                                
                                error_msg += "💡 **Sugerencias:**\n"
                                error_msg += "- Verifica que los eventos de la métrica coincidan con los nombres en los datos\n"
                                error_msg += "- Asegúrate de que haya al menos 2 etapas diferentes en el funnel\n"
                                error_msg += "- Revisa que los custom events (ce:) estén correctamente formateados"
                                
                                st.warning(error_msg)
                        else:
                            # Si no hay Funnel Stage, hacer análisis simple por variante
                            st.info(f"ℹ️ No se detectó columna 'Funnel Stage' para '{metric_display_name}'. Realizando análisis simple por variante.")
                            
                            variants = prepare_variants_from_dataframe(df_analysis)
                            
                            # Ordenar variantes correctamente: control primero, luego variant-1, variant-2, etc.
                            variants = sort_variants_correctly(variants, experiment_id_stat)
                            
                            if len(variants) >= 2:
                                # Análisis
                                if len(variants) == 2:
                                    control = variants[0]
                                    treatment = variants[1]
                                    
                                    results = calculate_ab_test(
                                        control['n'], control['x'],
                                        treatment['n'], treatment['x']
                                    )
                                    
                                    comparison_data = {
                                        'baseline': control,
                                        'treatment': treatment
                                    }
                                    
                                    # Mostrar tarjeta de métrica: Header = Experimento, Sub-header = Métrica
                                    create_metric_card(
                                        metric_name=metric_display_name,
                                        data=comparison_data,
                                        results=results,
                                        experiment_name=experiment_name_stat,
                                        metric_subtitle=metric_display_name
                                    )
                                    
                                else:
                                    # Multivariante - usar diseño de tabla
                                    chi_square_result = calculate_chi_square_test(variants)
                                    
                                    # Mostrar tarjeta multivariante: Header = Experimento, Sub-header = Métrica
                                    create_multivariant_card(
                                        metric_name=metric_display_name,
                                        variants=variants,
                                        experiment_name=experiment_name_stat,
                                        metric_subtitle=metric_display_name,
                                        chi_square_result=chi_square_result
                                    )
                                    
                            else:
                                st.warning(f"⚠️ Se necesitan al menos 2 variantes para el análisis estadístico de '{metric_display_name}'")
                    
                    # ============================================
                    # LABORATORIO DE SEGMENTACIÓN V2
                    # ============================================
                    st.markdown("---")
                    st.markdown("### Segmentación")
                    st.caption("Desglosa los resultados por diferentes dimensiones para encontrar insights ocultos")
                    
                    # Selector de desglose
                    breakdown_options = ['Ninguno', 'Device', 'Culture', 'Flow Type', 'Trip Type', 'Flight Profile', 'Travel Group']
                    breakdown_selected = st.radio(
                        "🔍 Desglosar resultados por:",
                        options=breakdown_options,
                        horizontal=True,
                        index=0,
                        key=f"breakdown_selector_{experiment_id_stat}"
                    )
                    
                    # Toggle de modo debug (oculto por ahora)
                    # if breakdown_selected != 'Ninguno':
                    #     debug_mode = st.checkbox(
                    #         "🕵️ Modo Debug (mostrar payloads de API)",
                    #         value=st.session_state.get('debug_mode', False),
                    #         key=f"debug_mode_{experiment_id_stat}",
                    #         help="Activa la visualización de los payloads enviados a Amplitude para debugging"
                    #     )
                    #     st.session_state['debug_mode'] = debug_mode
                    
                    # Si se selecciona un desglose, calcular estadísticas por segmento
                    if breakdown_selected != 'Ninguno':
                        # Obtener parámetros originales guardados
                        if 'analysis_params' not in st.session_state or 'analysis_metrics' not in st.session_state:
                            st.warning("⚠️ No se encontraron parámetros del análisis original. Por favor, ejecuta un análisis primero.")
                        else:
                            original_params = st.session_state['analysis_params']
                            original_metrics = st.session_state['analysis_metrics']
                            use_cumulative_breakdown = original_params.get('use_cumulative', True)
                            
                            # Definir valores únicos para cada tipo de desglose (deben coincidir con los valores de los selectores)
                            breakdown_values_map = {
                                'Device': ['desktop', 'mobile'],  # Valores exactos de los selectores (minúsculas, sin 'ALL')
                                'Culture': ['CL', 'AR', 'PE', 'CO', 'BR', 'UY', 'PY', 'EC', 'US', 'DO'],  # Valores exactos de los selectores (sin 'ALL')
                                'Flow Type': ['DB', 'PB', 'CK'],  # Valores exactos de los selectores (sin 'ALL')
                                'Trip Type': ['Solo Ida (One Way)', 'Ida y Vuelta (Round Trip)'],  # Valores exactos de los selectores (sin 'ALL')
                                'Flight Profile': ['Vuela Ligero', 'Smart', 'Full', 'Smart + Full'],  # Valores exactos de los selectores (sin 'ALL')
                                'Travel Group': ['Viajero Solo', 'Pareja', 'Grupo', 'Familia (con Menores)']  # Valores exactos de los selectores (sin 'ALL')
                            }
                            
                            # Mapeo de desglose a parámetro de la función
                            param_mapping = {
                                'Device': 'device',
                                'Culture': 'culture',
                                'Flow Type': 'flow_type',
                                'Trip Type': 'trip_type',
                                'Flight Profile': 'bundle_profile',
                                'Travel Group': 'travel_group'
                            }
                            
                            breakdown_param = param_mapping.get(breakdown_selected)
                            
                            if breakdown_param:
                                # Obtener valores únicos disponibles dinámicamente desde los datos del experimento
                                segment_values = []
                                
                                if breakdown_selected == 'Culture':
                                    # Obtener culturas reales presentes en los datos del experimento
                                    all_cultures = set()
                                    
                                    # Método 1: Intentar obtener de los datos procesados (si tienen culturas específicas)
                                    for metric_key, df_analysis in available_metrics:
                                        if 'Culture' in df_analysis.columns:
                                            # CORREGIDO: Usar función segura que maneja listas y strings
                                            # Las columnas pueden contener listas ['CL', 'PE'] debido a multiselect
                                            cultures_in_data = safe_unique_from_column(df_analysis['Culture'])
                                            for culture in cultures_in_data:
                                                all_cultures.add(culture)
                                    
                                    # Método 2: Si no encontramos culturas específicas (porque el análisis fue con 'ALL'),
                                    # hacer una consulta rápida para obtener las culturas disponibles
                                    if not all_cultures:
                                        try:
                                            # Hacer una consulta rápida con 'ALL' para obtener las culturas reales
                                            # Usar la primera métrica como referencia
                                            if original_metrics:
                                                first_metric = original_metrics[0]
                                                test_params = {
                                                    'start_date': original_params['start_date'],
                                                    'end_date': original_params['end_date'],
                                                    'experiment_id': original_params['experiment_id'],
                                                    'device': 'ALL' if original_params.get('device') == 'ALL' else original_params.get('device', 'ALL'),
                                                    'culture': 'ALL',  # Consultar con ALL para obtener todas las culturas
                                                    'event_list': first_metric['events'][:1] if first_metric['events'] else ['homepage_dom_loaded'],  # Solo un evento para ser rápido
                                                    'conversion_window': original_params['conversion_window'],
                                                    'flow_type': original_params.get('flow_type', 'ALL'),
                                                    'bundle_profile': original_params.get('bundle_profile', 'ALL'),
                                                    'trip_type': original_params.get('trip_type', 'ALL'),
                                                    'travel_group': original_params.get('travel_group', 'ALL')
                                                }
                                                
                                                # Hacer consulta rápida
                                                if use_cumulative_breakdown:
                                                    test_df = final_pipeline_cumulative(**test_params)
                                                else:
                                                    test_df = final_pipeline(**test_params)
                                                
                                                # Extraer culturas de la respuesta
                                                if not test_df.empty and 'Culture' in test_df.columns:
                                                    # CORREGIDO: Usar función segura que maneja listas y strings
                                                    cultures_from_query = safe_unique_from_column(test_df['Culture'])
                                                    for culture in cultures_from_query:
                                                        all_cultures.add(culture)
                                        except Exception:
                                            # Si falla la consulta, continuar con el fallback
                                            pass
                                    
                                    if all_cultures:
                                        # HARDENING: Materializar all_cultures como lista antes de usarlo
                                        all_cultures = sorted(list(all_cultures))  # Convertir set a lista ordenada
                                        
                                        # Agrupar países INTER (BR, UY, PY, EC, US, DO) bajo "INTER"
                                        inter_countries = {'BR', 'UY', 'PY', 'EC', 'US', 'DO'}
                                        main_countries = {'CL', 'AR', 'PE', 'CO'}
                                        segment_values = []
                                        
                                        # Agregar países principales si existen
                                        for country in ['CL', 'AR', 'PE', 'CO']:
                                            if country in all_cultures:
                                                segment_values.append(country)
                                        
                                        # Si existe al menos un país INTER, agregar "INTER"
                                        if any(country in all_cultures for country in inter_countries):
                                            segment_values.append('INTER')
                                        
                                        # HARDENING: Materializar segment_values como lista explícita
                                        segment_values = list(segment_values)
                                    else:
                                        # Fallback: usar la lista del selector agrupando INTER
                                        segment_values = ["CL", "AR", "PE", "CO", "INTER"]
                                else:
                                    # Para otros desgloses, usar la lista predefinida
                                    # HARDENING: Crear copia explícita para evitar referencias volátiles
                                    segment_values = list(breakdown_values_map.get(breakdown_selected, []))
                                
                                if not segment_values:
                                    st.warning(f"⚠️ No se encontraron valores para desglosar por '{breakdown_selected}'")
                                else:
                                    # HARDENING: Materializar segment_values como lista explícita, ordenada y sin duplicados
                                    # Esto asegura que no sea un generador, set, o referencia volátil
                                    segment_values = sorted(list(set(segment_values))) if segment_values else []
                                    
                                    # Pre-calcular segmentos disponibles (copia materializada, no referencia)
                                    available_segments = list(segment_values)  # Copia explícita para evitar mutaciones
                                    
                                    # Control global de visualización
                                    show_cards = st.toggle(
                                        "🔍 Ver Detalle en Tarjetas",
                                        value=False,
                                        key=f"show_cards_{breakdown_selected}_{experiment_id_stat}",
                                        help="Activa la visualización detallada en tarjetas. Por defecto se muestran tablas resumen."
                                    )
                                    
                                    # Multiselect global para seleccionar segmentos (solo visible cuando show_cards está ON)
                                    selected_segments_view = []
                                    if show_cards:
                                        selected_segments_view = st.multiselect(
                                            "Selecciona Segmentos a Visualizar",
                                            options=available_segments,
                                            default=available_segments,  # Por defecto todos los segmentos
                                            key=f"selected_segments_{breakdown_selected}_{experiment_id_stat}",
                                            help="Selecciona los segmentos que deseas visualizar en detalle"
                                        )
                                    
                                    # Determinar qué segmentos procesar según el modo
                                    # Si show_cards está ON y hay segmentos seleccionados, solo procesar los seleccionados (para optimizar)
                                    # Si show_cards está OFF, procesar todos los segmentos (para las tablas)
                                    # HARDENING: Materializar segments_to_process como lista explícita antes del bucle
                                    if show_cards and selected_segments_view:
                                        segments_to_process = sorted(list(selected_segments_view))  # Materializar y ordenar
                                    else:
                                        segments_to_process = list(available_segments)  # Asegurar copia materializada
                                    
                                    # Verificación de integridad antes del procesamiento
                                    # Solo procesar si hay segmentos disponibles
                                    if len(segments_to_process) > 0:
                                        # Procesar cada métrica con desglose
                                        for metric_info in original_metrics:
                                            metric_display_name = metric_info['name']
                                            metric_events = metric_info['events']
                                            metric_filters = metric_info.get('filters', {})
                                            
                                            # Mostrar título de la métrica
                                            st.markdown(f"#### 📊 Desglose por {breakdown_selected} - {metric_display_name}")
                                            
                                            # Importar funciones de renderizado
                                            from src.utils.statistical_analysis import (
                                                create_multivariant_card,
                                                calculate_single_comparison
                                            )
                                            
                                            # OPTIMIZACIÓN #3: Paralelización de desgloses
                                            # Función helper para procesar un segmento individual (ejecutada en paralelo)
                                            def process_segment(segment_value):
                                                """Procesa un segmento individual y retorna los datos para renderizar"""
                                                try:
                                                    # Función auxiliar para normalizar y obtener valores seguros
                                                    def get_safe_param(param_name, default_value):
                                                        value = original_params.get(param_name, default_value)
                                                        if value is None:
                                                            return default_value
                                                        if isinstance(value, str):
                                                            value_str = value.strip()
                                                            if value_str.upper() == "ALL":
                                                                return "ALL"
                                                        return value
                                                    
                                                    # Construir parámetros de query
                                                    query_params = {
                                                        'start_date': original_params.get('start_date'),
                                                        'end_date': original_params.get('end_date'),
                                                        'experiment_id': original_params.get('experiment_id'),
                                                        'event_list': metric_events,
                                                        'device': get_safe_param('device', 'ALL'),
                                                        'culture': get_safe_param('culture', 'ALL'),
                                                        'flow_type': get_safe_param('flow_type', 'ALL'),
                                                        'bundle_profile': get_safe_param('bundle_profile', 'ALL'),
                                                        'trip_type': get_safe_param('trip_type', 'ALL'),
                                                        'travel_group': get_safe_param('travel_group', 'ALL'),
                                                        'conversion_window': original_params.get('conversion_window', 1800),
                                                        'event_filters_map': metric_filters if metric_filters else None
                                                    }
                                                    
                                                    if metric_info.get('hidden_first_step', False):
                                                        query_params['hidden_first_step'] = True
                                                    
                                                    # Validar parámetros obligatorios
                                                    required_params = ['start_date', 'end_date', 'experiment_id', 'event_list']
                                                    missing_params = [p for p in required_params if query_params.get(p) is None]
                                                    if missing_params:
                                                        return {'error': f"Parámetros faltantes: {missing_params}", 'segment': segment_value}
                                                    
                                                    # Sobrescribir parámetro del segmento
                                                    if breakdown_selected == 'Device':
                                                        query_params['device'] = segment_value
                                                    elif breakdown_selected == 'Culture':
                                                        # Si el segment es "INTER", agrupar los países INTER
                                                        if segment_value == 'INTER':
                                                            query_params['culture'] = ['BR', 'UY', 'PY', 'EC', 'US', 'DO']
                                                        else:
                                                            query_params['culture'] = segment_value
                                                    elif breakdown_selected == 'Flow Type':
                                                        query_params['flow_type'] = segment_value
                                                    elif breakdown_selected == 'Trip Type':
                                                        query_params['trip_type'] = segment_value
                                                    elif breakdown_selected == 'Flight Profile':
                                                        query_params['bundle_profile'] = segment_value
                                                    elif breakdown_selected == 'Travel Group':
                                                        query_params['travel_group'] = segment_value
                                                    
                                                    # Remover event_filters_map si es None
                                                    call_params = query_params.copy()
                                                    if call_params.get('event_filters_map') is None:
                                                        call_params.pop('event_filters_map', None)
                                                    
                                                    # Hacer llamada API con retry y backoff
                                                    max_retries = 3
                                                    attempt = 0
                                                    df_segment = None
                                                    
                                                    while attempt < max_retries:
                                                        try:
                                                            # Intentar obtener datos
                                                            if use_cumulative_breakdown:
                                                                df_segment = final_pipeline_cumulative(**call_params)
                                                            else:
                                                                df_segment = final_pipeline(**call_params)
                                                            
                                                            # Validar si la respuesta es útil (no vacía)
                                                            if df_segment is not None and not df_segment.empty:
                                                                break  # ¡Éxito! Salimos del bucle de reintentos
                                                            
                                                            # Si llegamos aquí, el DataFrame está vacío
                                                            attempt += 1
                                                            if attempt < max_retries:
                                                                time.sleep(0.5)  # Esperamos medio segundo antes de reintentar
                                                            else:
                                                                return {'error': 'DataFrame vacío después de múltiples intentos', 'segment': segment_value}
                                                        
                                                        except Exception as api_error:
                                                            # Si hay un error en la llamada API, reintentar
                                                            attempt += 1
                                                            if attempt < max_retries:
                                                                time.sleep(0.5)  # Esperamos medio segundo antes de reintentar
                                                            else:
                                                                return {'error': f'Error en API después de {max_retries} intentos: {str(api_error)}', 'segment': segment_value}
                                                    
                                                    # Verificación final de seguridad
                                                    if df_segment is None or df_segment.empty:
                                                        return {'error': 'DataFrame vacío', 'segment': segment_value}
                                                    
                                                    # Determinar initial_stage y final_stage (mismo código que antes)
                                                    initial_stage = None
                                                    final_stage = None
                                                    
                                                    if 'Funnel Stage' in df_segment.columns:
                                                        available_stages = df_segment['Funnel Stage'].unique().tolist()
                                                        
                                                        metric_config = None
                                                        try:
                                                            from src.utils.metrics_loader import get_all_metrics_flat
                                                            all_metrics = get_all_metrics_flat()
                                                            metric_config = all_metrics.get(metric_display_name)
                                                        except Exception:
                                                            pass
                                                        
                                                        if metric_config and 'events' in metric_config and len(metric_config['events']) >= 2:
                                                            hidden_first_step = metric_config.get('hidden_first_step', False)
                                                            event_names = []
                                                            for event_item in metric_config['events']:
                                                                if isinstance(event_item, tuple) and len(event_item) > 0:
                                                                    event_names.append(event_item[0])
                                                                elif isinstance(event_item, str):
                                                                    event_names.append(event_item)
                                                            
                                                            if hidden_first_step and len(event_names) >= 2:
                                                                anchor_event_name = event_names[0]
                                                                def normalize_event_name_simple(name):
                                                                    name = name.replace('[Amplitude]', '').strip()
                                                                    if name.startswith('ce:'):
                                                                        name = name[3:].strip()
                                                                        if name.startswith('('):
                                                                            end_paren = name.find(')')
                                                                            if end_paren != -1:
                                                                                name = name[end_paren + 1:].strip()
                                                                    return name.lower().strip()
                                                                normalized_anchor = normalize_event_name_simple(anchor_event_name)
                                                                available_stages = [s for s in available_stages if normalize_event_name_simple(s) != normalized_anchor]
                                                                if not available_stages:
                                                                    available_stages = df_segment['Funnel Stage'].unique().tolist()
                                                                event_names = event_names[1:]
                                                                
                                                            def normalize_event_name_simple(name):
                                                                name = name.replace('[Amplitude]', '').strip()
                                                                if name.startswith('ce:'):
                                                                    name = name[3:].strip()
                                                                    if name.startswith('('):
                                                                        end_paren = name.find(')')
                                                                        if end_paren != -1:
                                                                            name = name[end_paren + 1:].strip()
                                                                return name.lower().strip()
                                                            
                                                            def find_stage_robust(event_name, stages, exclude_stage=None):
                                                                normalized_event = normalize_event_name_simple(event_name)
                                                                for stage in stages:
                                                                    if stage == event_name and stage != exclude_stage:
                                                                        return stage
                                                                for stage in stages:
                                                                    if stage != exclude_stage:
                                                                        normalized_stage = normalize_event_name_simple(stage)
                                                                        if normalized_event == normalized_stage:
                                                                            return stage
                                                                for stage in stages:
                                                                    if stage != exclude_stage:
                                                                        normalized_stage = normalize_event_name_simple(stage)
                                                                        if (normalized_event in normalized_stage or normalized_stage in normalized_event):
                                                                            return stage
                                                                return None
                                                            
                                                            initial_stage = find_stage_robust(event_names[0], available_stages) if event_names else None
                                                            final_stage = find_stage_robust(event_names[-1], available_stages, exclude_stage=initial_stage) if len(event_names) > 1 else None
                                                        
                                                            # Fallback inteligente
                                                            if not initial_stage or not final_stage:
                                                                if not initial_stage and event_names:
                                                                    first_event_lower = event_names[0].lower()
                                                                    best_match = None
                                                                    best_score = 0
                                                                    for stage in available_stages:
                                                                        stage_lower = stage.lower()
                                                                        first_words = set(first_event_lower.replace('_', ' ').split())
                                                                        stage_words = set(stage_lower.replace('_', ' ').split())
                                                                        common_words = first_words.intersection(stage_words)
                                                                        score = len(common_words)
                                                                        if score > best_score:
                                                                            best_score = score
                                                                            best_match = stage
                                                                    initial_stage = best_match if best_match else (available_stages[0] if available_stages else None)
                                                                
                                                                if not final_stage and event_names:
                                                                    last_event_lower = event_names[-1].lower()
                                                                    best_match = None
                                                                    best_score = 0
                                                                    for stage in available_stages:
                                                                        if stage == initial_stage:
                                                                            continue
                                                                        stage_lower = stage.lower()
                                                                        last_words = set(last_event_lower.replace('_', ' ').split())
                                                                        stage_words = set(stage_lower.replace('_', ' ').split())
                                                                        common_words = last_words.intersection(stage_words)
                                                                        score = len(common_words)
                                                                        if score > best_score:
                                                                            best_score = score
                                                                            best_match = stage
                                                                    if best_match:
                                                                        final_stage = best_match
                                                                    else:
                                                                        for stage in available_stages:
                                                                            if stage != initial_stage:
                                                                                final_stage = stage
                                                                                break
                                                    
                                                    if not initial_stage or not final_stage or initial_stage == final_stage:
                                                        return {'error': 'No se encontraron stages válidos', 'segment': segment_value}
                                                    
                                                    # Filtrar DataFrame si hidden_first_step
                                                    df_segment_filtered = df_segment.copy()
                                                    if metric_config and metric_config.get('hidden_first_step', False):
                                                        anchor_event_name = None
                                                        if 'events' in metric_config and metric_config['events']:
                                                            first_event = metric_config['events'][0]
                                                            anchor_event_name = first_event[0] if isinstance(first_event, tuple) else first_event
                                                        if anchor_event_name:
                                                            def normalize_event_name_for_filter_segment(name):
                                                                name = name.replace('[Amplitude]', '').strip()
                                                                if name.startswith('ce:'):
                                                                    name = name[3:].strip()
                                                                    if name.startswith('('):
                                                                        end_paren = name.find(')')
                                                                        if end_paren != -1:
                                                                            name = name[end_paren + 1:].strip()
                                                                return name.lower().strip()
                                                            normalized_anchor = normalize_event_name_for_filter_segment(anchor_event_name)
                                                            df_segment_filtered = df_segment_filtered[
                                                                df_segment_filtered['Funnel Stage'].apply(
                                                                    lambda stage: normalize_event_name_for_filter_segment(stage) != normalized_anchor
                                                                )
                                                            ]
                                                    
                                                    # Preparar variantes
                                                    from src.utils.statistical_analysis import prepare_variants_from_dataframe
                                                    variants_segment = prepare_variants_from_dataframe(
                                                        df_segment_filtered,
                                                        initial_stage=initial_stage,
                                                        final_stage=final_stage
                                                    )
                                                    
                                                    variants_segment = [v for v in variants_segment if v.get('n', 0) > 0]
                                                    
                                                    if len(variants_segment) < 1:
                                                        return {'error': 'No hay variantes válidas', 'segment': segment_value}
                                                    
                                                    # Ordenar variantes
                                                    variants_segment = sort_variants_correctly(variants_segment, experiment_id_stat)
                                                    
                                                    return {
                                                        'segment': segment_value,
                                                        'variants': variants_segment,
                                                        'metric_subtitle': f"{metric_display_name} - {segment_value}"
                                                    }
                                                except Exception as e:
                                                    return {'error': str(e), 'segment': segment_value}
                                            
                                            # OPTIMIZACIÓN #3: Ejecutar todos los segmentos en paralelo
                                            # Usar segments_to_process en lugar de segment_values para optimizar cuando show_cards está ON
                                            breakdown_progress = st.progress(0)
                                            total_segments = len(segments_to_process)
                                            segment_results = []
                                            
                                            with ThreadPoolExecutor(max_workers=10) as executor:
                                                # Enviar todas las tareas en paralelo
                                                future_to_segment = {executor.submit(process_segment, segment_value): segment_value for segment_value in segments_to_process}
                                                
                                                # Recopilar resultados a medida que completan
                                                completed = 0
                                                for future in as_completed(future_to_segment):
                                                    completed += 1
                                                    breakdown_progress.progress(completed / total_segments)
                                                    
                                                    result = future.result()
                                                    if 'error' not in result:
                                                        segment_results.append(result)
                                            
                                            breakdown_progress.empty()
                                            
                                            # HARDENING: Materializar segment_results completamente antes de ordenar
                                            segment_results = list(segment_results)  # Asegurar que sea una lista materializada
                                            
                                            # Verificación de integridad: asegurar que tenemos resultados para todos los segmentos esperados
                                            segments_processed = {r.get('segment') for r in segment_results if 'error' not in r}
                                            segments_expected = set(segments_to_process)
                                            missing_segments = segments_expected - segments_processed
                                            if missing_segments and not show_cards:  # Solo mostrar warning en modo tabla
                                                st.warning(f"⚠️ Algunos segmentos no retornaron datos: {sorted(missing_segments)}")
                                            
                                            # Ordenar resultados según el tipo de desglose
                                            if breakdown_selected == 'Device':
                                                # Orden personalizado para Device: desktop, mobile
                                                device_order = {'desktop': 0, 'mobile': 1}
                                                segment_results.sort(key=lambda x: device_order.get(x.get('segment', ''), 999))
                                            elif breakdown_selected == 'Culture':
                                                # Orden personalizado para Culture: CL, AR, PE, CO, luego INTER
                                                culture_order = {
                                                    'CL': 0,
                                                    'AR': 1,
                                                    'PE': 2,
                                                    'CO': 3,
                                                    'INTER': 4
                                                }
                                                segment_results.sort(key=lambda x: culture_order.get(x.get('segment', ''), 999))
                                            elif breakdown_selected == 'Flow Type':
                                                # Orden personalizado para Flow Type: DB, PB, CK
                                                flow_type_order = {'DB': 0, 'PB': 1, 'CK': 2}
                                                segment_results.sort(key=lambda x: flow_type_order.get(x.get('segment', ''), 999))
                                            elif breakdown_selected == 'Trip Type':
                                                # Orden personalizado para Trip Type: Solo Ida (One Way), Ida y Vuelta (Round Trip)
                                                trip_type_order = {
                                                    'Solo Ida (One Way)': 0,
                                                    'Ida y Vuelta (Round Trip)': 1
                                                }
                                                segment_results.sort(key=lambda x: trip_type_order.get(x.get('segment', ''), 999))
                                            elif breakdown_selected == 'Flight Profile':
                                                # Orden personalizado para Flight Profile: Vuela Ligero, Smart, Full, Smart + Full
                                                flight_profile_order = {
                                                    'Vuela Ligero': 0,
                                                    'Smart': 1,
                                                    'Full': 2,
                                                    'Smart + Full': 3
                                                }
                                                segment_results.sort(key=lambda x: flight_profile_order.get(x.get('segment', ''), 999))
                                            elif breakdown_selected == 'Travel Group':
                                                # Orden personalizado para Travel Group: Viajero Solo, Pareja, Grupo, Familia (con Menores)
                                                travel_group_order = {
                                                    'Viajero Solo': 0,
                                                    'Pareja': 1,
                                                    'Grupo': 2,
                                                    'Familia (con Menores)': 3
                                                }
                                                segment_results.sort(key=lambda x: travel_group_order.get(x.get('segment', ''), 999))
                                            else:
                                                # Para otros desgloses, mantener el orden original (breakdown_values_map)
                                                # Los resultados ya vienen en el orden correcto de segment_values
                                                pass
                                            
                                            # Renderizar resultados según el modo seleccionado
                                            if not show_cards:
                                                # Modo Tabla (por defecto): Mostrar tablas resumen
                                                # Modo Tabla: Acumular datos y mostrar DataFrame
                                                data_rows = []
                                                
                                                for result in segment_results:
                                                    try:
                                                        variants = result['variants']
                                                        segment_value = result['segment']
                                                        
                                                        if len(variants) < 1:
                                                            continue
                                                        
                                                        # Baseline (control) es la primera variante
                                                        baseline = variants[0]
                                                        
                                                        # Calcular CR del control
                                                        cr_control = (baseline['x'] / baseline['n']) * 100 if baseline['n'] > 0 else 0
                                                        
                                                        # Iterar sobre todas las variantes (excluyendo el control, índice 0)
                                                        if len(variants) > 1:
                                                            # Bucle interno: una fila por cada variante comparada contra el control
                                                            for i in range(1, len(variants)):
                                                                variant = variants[i]
                                                                variant_name = variant.get('name', f'Variant-{i}')
                                                                
                                                                comparison = calculate_single_comparison(baseline, variant)
                                                                
                                                                cr_variant = (variant['x'] / variant['n']) * 100 if variant['n'] > 0 else 0
                                                                p_value = comparison['p_value']
                                                                is_significant = comparison['significant']
                                                                
                                                                data_rows.append({
                                                                    "Segmento": segment_value,
                                                                    "Variante": variant_name,
                                                                    "Sesiones (Ctrl)": baseline['n'],
                                                                    "Sesiones (Var)": variant['n'],
                                                                    "CR Control": cr_control,
                                                                    "CR Variant": cr_variant,
                                                                    "Lift (%)": comparison['relative_lift'],  # Ya está en porcentaje
                                                                    "P-Value": p_value,
                                                                    "Sig.": "✅" if is_significant else "-"
                                                                })
                                                        else:
                                                            # Solo hay control, mostrar solo datos del control
                                                            data_rows.append({
                                                                "Segmento": segment_value,
                                                                "Variante": "N/A",
                                                                "Sesiones (Ctrl)": baseline['n'],
                                                                "Sesiones (Var)": 0,
                                                                "CR Control": cr_control,
                                                                "CR Variant": 0.0,
                                                                "Lift (%)": 0.0,
                                                                "P-Value": 1.0,
                                                                "Sig.": "-"
                                                            })
                                                        
                                                    except Exception as e:
                                                        # Manejar errores silenciosamente
                                                        continue
                                                
                                                # Renderizar tabla resumen si hay datos
                                                if len(data_rows) > 0:
                                                    # HARDENING: Crear DataFrame con reset_index para evitar problemas de índices duplicados
                                                    df_segmentation = pd.DataFrame(data_rows).reset_index(drop=True)
                                                    
                                                    # Verificación de integridad: asegurar que el DataFrame tiene el número esperado de filas
                                                    expected_min_rows = len(segments_to_process)  # Mínimo una fila por segmento
                                                    if len(df_segmentation) < expected_min_rows:
                                                        st.warning(f"⚠️ La tabla muestra {len(df_segmentation)} filas, pero se esperaban al menos {expected_min_rows} segmentos procesados.")
                                                    
                                                    st.dataframe(
                                                        df_segmentation,
                                                        use_container_width=True,
                                                        hide_index=True,
                                                        column_config={
                                                            "Segmento": st.column_config.TextColumn(
                                                                "Segmento",
                                                                help="Segmento de análisis (país, dispositivo, etc.)"
                                                            ),
                                                            "Variante": st.column_config.TextColumn(
                                                                "Variante",
                                                                help="Nombre de la variante comparada contra el control"
                                                            ),
                                                            "CR Control": st.column_config.NumberColumn(
                                                                "CR Control (%)",
                                                                format="%.2f%%",
                                                                help="Tasa de conversión del grupo control"
                                                            ),
                                                            "CR Variant": st.column_config.NumberColumn(
                                                                "CR Variant (%)",
                                                                format="%.2f%%",
                                                                help="Tasa de conversión de la variante"
                                                            ),
                                                            "Lift (%)": st.column_config.NumberColumn(
                                                                "Lift (%)",
                                                                format="%.2f%%",
                                                                help="Diferencia relativa entre variante y control"
                                                            ),
                                                            "P-Value": st.column_config.NumberColumn(
                                                                "P-Value",
                                                                format="%.5f",
                                                                help="Valor p del test estadístico (significativo si < 0.05)"
                                                            ),
                                                            "Sesiones (Ctrl)": st.column_config.NumberColumn(
                                                                "Sesiones (Ctrl)",
                                                                format="%d",
                                                                help="Número de sesiones en el grupo control"
                                                            ),
                                                            "Sesiones (Var)": st.column_config.NumberColumn(
                                                                "Sesiones (Var)",
                                                                format="%d",
                                                                help="Número de sesiones en la variante"
                                                            ),
                                                        }
                                                    )
                                                else:
                                                    # Si no se encontraron datos, mostrar mensaje informativo
                                                    st.info(f"ℹ️ No se encontraron segmentos válidos para desglosar por '{breakdown_selected}' en la métrica '{metric_display_name}'.")
                                            
                                            elif show_cards:
                                                # Modo Tarjetas: Renderizar tarjetas detalladas solo para segmentos seleccionados
                                                if selected_segments_view:
                                                    # Los resultados ya están filtrados porque solo procesamos los segmentos seleccionados
                                                    for result in segment_results:
                                                        try:
                                                            # Renderizar tarjeta unificada con todas las variantes
                                                            create_multivariant_card(
                                                                metric_name=metric_display_name,
                                                                variants=result['variants'],
                                                                experiment_name=experiment_name_stat,
                                                                metric_subtitle=result['metric_subtitle'],
                                                                chi_square_result=None
                                                            )
                                                            
                                                        except Exception as e:
                                                            # Manejar errores silenciosamente
                                                            continue
                                                    
                                                    # Si no se renderizó ninguna tarjeta, mostrar mensaje informativo
                                                    if len(segment_results) == 0:
                                                        st.info(f"ℹ️ No se encontraron segmentos válidos para desglosar por '{breakdown_selected}' en la métrica '{metric_display_name}'.")
                                                else:
                                                    # Si no hay segmentos seleccionados, mostrar mensaje
                                                    st.info("ℹ️ Por favor, selecciona al menos un segmento para visualizar en detalle.")
                                    
                                    # Cerrar el bucle de métricas
                                    else:
                                        # Si no hay segmentos disponibles, mostrar warning
                                        st.warning(f"⚠️ No hay segmentos disponibles para procesar en '{breakdown_selected}'. Por favor, verifica los parámetros del análisis.")

    with tab_help:
        st.subheader("❓ Guía de Uso")
        st.markdown("""
        ### 🎯 Cómo usar el AB Test Dashboard
        1. **Configuración:** Ajusta los parámetros en la barra lateral  
        2. **Selección de Eventos:** Elige los eventos que quieres analizar  
        3. **Ejecución:** Haz clic en "Ejecutar Análisis" para obtener resultados

        ### 📊 Tipos de Análisis
        - **Diario:** Datos día por día  
        - **Acumulado:** Valores totales del período

        ### 🔧 Parámetros
        - **Device:** Tipo de dispositivo (ALL, desktop, mobile)  
        - **Culture:** País/región (ALL, CL, AR, PE, CO, BR, UY, PY, EC, US, DO)  
        - **Ventana de Conversión:** Tiempo máximo para una conversión válida  

        ### 📋 Eventos Disponibles
        Incluye todos los eventos de tracking de Jetsmart (`*_dom_loaded`, `*_clicked`, etc.)

        ### 🔑 Credenciales
        Las credenciales de Amplitude se leen desde el archivo `.env`:
        ```
        AMPLITUDE_API_KEY=tu_api_key
        AMPLITUDE_SECRET_KEY=tu_secret_key
        AMPLITUDE_MANAGEMENT_KEY=tu_management_key
        ```

        ### ➕ Cómo Agregar Nuevas Métricas

        Para agregar nuevas métricas al dashboard, sigue estos pasos:

        #### 1. Crear archivo de métricas
        Crea un archivo `[step]_metrics/[step]_metrics.py` siguiendo el formato de `baggage_metrics.py`:

        ```python
        # filtros amplitude
        from src.utils.amplitude_filters import (
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

        **📌 Formato de Métricas:**
        - **Todas las métricas** deben usar el formato `{'events': [...]}`
        - **SIEMPRE usa tuplas** `('evento', [filtros])`
        - **El segundo elemento es siempre una lista** de filtros: `[filtro1, filtro2, ...]`
        - **Si no hay filtros**, usa lista vacía: `[]`
        - **Puedes agregar tantos eventos como necesites** (2, 3, 4, 5+ eventos)
        - **Cada evento puede tener sus propios filtros** independientemente de los demás
        - **Los eventos se procesan en orden** como un funnel secuencial

        #### 2. ¡Listo! 🎉
        **Ya no necesitas modificar `app.py`**. El sistema detecta automáticamente todas las métricas desde las carpetas de `metrics/`.
        
        Las métricas se cargan automáticamente y aparecerán en el dashboard con:
        - ✅ Nombres descriptivos generados automáticamente
        - ✅ Información de eventos y filtros
        - ✅ Organización por categoría (baggage, seats, payment, etc.)
        
        **El sistema detecta automáticamente:**
        - Archivos `*_metrics.py` en cualquier subcarpeta de `metrics/`
        - Variables en mayúsculas que sean métricas válidas
        - Genera nombres de display con emojis según la categoría
        - Organiza y muestra toda la información automáticamente

        #### 📚 Documentación Completa
        Para más detalles, consulta:
        - `streamlit/METRICS_GUIDE.md` - Guía completa
        - `streamlit/EXAMPLE_SEATS_METRICS.py` - Ejemplo práctico
        """)


if __name__ == "__main__":
    run_ui()
