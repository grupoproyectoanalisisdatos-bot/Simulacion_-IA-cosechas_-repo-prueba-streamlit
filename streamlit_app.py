import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
import numpy as np
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Agro-Clima Intelligence Pro",
    page_icon="🚜",
    layout="wide"
)

# --- ESTILOS PROFESIONALES (CSS) ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #15803d;
        color: white !important;
        font-weight: 800;
        font-size: 1rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background-color: #1e3a8a;
        transform: translateY(-2px);
    }
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 6px solid #15803d;
        margin-bottom: 1rem;
    }
    .no-data-msg {
        padding: 20px;
        background-color: #fef2f2;
        border: 1px solid #fee2e2;
        border-radius: 10px;
        color: #991b1b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA Y PROCESAMIENTO DE DATOS ---
@st.cache_data
def load_data():
    files = {
        "prod": "Datos para la Base de Datos - Produccion.csv",
        "temp": "Datos para la Base de Datos - Temperatura.csv",
        "prec": "Datos para la Base de Datos - Precipitacion.csv",
        "brillo": "Datos para la Base de Datos - Brillo Solar.csv"
    }
    
    data = {}
    found_any = False
    for key, path in files.items():
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df.columns = [str(c).strip() for c in df.columns]
                if 'Fecha' in df.columns:
                    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
                if 'Año' in df.columns:
                    df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
                data[key] = df
                found_any = True
            except Exception as e:
                st.error(f"Error al leer {path}: {e}")
        else:
            data[key] = None
    return data, found_any

datasets, hay_datos = load_data()

# --- INTERFAZ PRINCIPAL ---
st.title("🚜 Panel de Decisiones Agro-Climáticas")
st.markdown("---")

if not hay_datos:
    st.warning("📡 **Estado del Sistema:** Esperando conexión con base de datos CSV.")
    st.info("Para activar el panel, asegúrate de que los archivos `.csv` estén en el repositorio raíz de GitHub.")
    
    # Simulación de estructura si no hay datos para que la UI no se vea vacía
    st.markdown("""
        <div class="no-data-msg">
            <b>Nota:</b> El motor de análisis está listo. Una vez detectados los archivos de Producción y Clima, 
            se habilitarán automáticamente los mapas de calor y gráficos de rendimiento.
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- LÓGICA SI HAY DATOS ---
df_prod = datasets.get("prod")
df_temp = datasets.get("temp")

if df_prod is not None:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
        st.header("📍 Filtros de Análisis")
        col_mun = 'Municipio' if 'Municipio' in df_prod.columns else df_prod.columns[0]
        municipios = sorted(df_prod[col_mun].dropna().unique())
        mun_sel = st.selectbox("Seleccione Municipio", municipios)
        st.divider()
        st.info("💡 Tip: El cruce de datos permite predecir el impacto térmico en la cosecha.")

    # --- MÉTRICAS ---
    data_mun = df_prod[df_prod[col_mun] == mun_sel]
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rend = data_mun['Rendimiento'].mean() if 'Rendimiento' in data_mun.columns else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Rendimiento Promedio", f"{rend:.2f} T/Ha")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        area = data_mun['Area Sembrada'].sum() if 'Area Sembrada' in data_mun.columns else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Área Sembrada", f"{area:,.0f} Ha")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        cosecha_col = 'Area Cosechada' if 'Area Cosechada' in data_mun.columns else None
        efi = (data_mun[cosecha_col].sum() / area * 100) if cosecha_col and area > 0 else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Eficiencia de Cosecha", f"{efi:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        temp_val = "N/D"
        if df_temp is not None:
            col_t_mun = 'Municipio:' if 'Municipio:' in df_temp.columns else 'Municipio'
            if col_t_mun in df_temp.columns:
                val = df_temp[df_temp[col_t_mun] == mun_sel]['Valor:'].mean() if 'Valor:' in df_temp.columns else None
                if val is not None and not np.isnan(val): temp_val = f"{val:.1f} °C"
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Temp. Promedio", temp_val)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- MAPA Y ACCIONES ---
    st.divider()
    c_map, c_action = st.columns([2, 1])

    with c_map:
        st.subheader("🗺️ Geo-localización de Lotes")
        if df_temp is not None and 'Latitud:' in df_temp.columns:
            col_t_mun = 'Municipio:' if 'Municipio:' in df_temp.columns else 'Municipio'
            df_map = df_temp[df_temp[col_t_mun] == mun_sel].copy()
            
            def normalize_coord(x):
                try:
                    s = str(x).replace(".", "").replace("-", "")
                    if len(s) < 2: return 0.0
                    return float(s[0] + "." + s[1:6])
                except: return 0.0

            df_map['lat'] = df_map['Latitud:'].apply(normalize_coord)
            df_map['lon'] = df_map['Longitud:'].apply(lambda x: -normalize_coord(x))
            df_map = df_map[(df_map['lat'] != 0) & (df_map['lon'] != 0)]
            
            if not df_map.empty:
                st.map(df_map[['lat', 'lon']], zoom=10)
            else:
                st.info("Sin coordenadas GPS válidas para mapeo.")
        else:
            st.warning("No hay coordenadas disponibles.")

    with c_action:
        st.subheader("🎯 Recomendaciones")
        if rend < 1.0:
            st.error("🚨 Alerta de Bajo Rendimiento detectada.")
        else:
            st.success("🌱 Zona con potencial de alta productividad.")
        st.write("---")
        st.button("📄 Generar Reporte PDF")
        st.button("🔔 Alertar Equipo Técnico")

    # --- GRÁFICO ---
    st.divider()
    st.subheader("📈 Tendencias Históricas")
    if PLOTLY_AVAILABLE and 'Año' in data_mun.columns:
        plot_data = data_mun.groupby(['Año', 'Producto'])['Rendimiento'].mean().reset_index()
        fig = px.line(plot_data, x='Año', y='Rendimiento', color='Producto', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Gráficos interactivos se habilitarán al cargar datos históricos.")

st.markdown("---")
st.caption("Agro-Clima Intelligence Pro - Modo Standby / Listo para Datos")
