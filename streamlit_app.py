
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    /* Estilo para los botones: Inscripción siempre visible y colores temáticos */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #15803d; /* Verde Agro */
        color: white !important;
        font-weight: 800;
        font-size: 1rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    div.stButton > button:hover {
        background-color: #1e3a8a; /* Azul Clima al pasar el mouse */
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    div.stButton > button p {
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.2 !important;
    }

    /* Tarjetas de Métricas */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 6px solid #15803d;
        margin-bottom: 1rem;
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
    for key, path in files.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Limpieza básica de columnas
            df.columns = [c.strip() for c in df.columns]
            data[key] = df
    return data

datasets = load_data()

# --- VALIDACIÓN DE DATOS ---
if not datasets.get("prod") is not None:
    st.error("⚠️ No se encontraron los archivos CSV en el directorio raíz.")
    st.stop()

df_prod = datasets["prod"]
df_temp = datasets.get("temp")

# --- INTERFAZ PRINCIPAL ---
st.title("🚜 Panel de Decisiones Agro-Climáticas")
st.markdown("---")

# Sidebar para filtros de acción
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.header("📍 Filtros de Análisis")
    municipios = sorted(df_prod['Municipio'].unique())
    mun_sel = st.selectbox("Seleccione Municipio", municipios)
    
    st.divider()
    st.markdown("### 💡 Acción Experta")
    st.info("El cruce de coordenadas permite identificar microrregiones con estrés térmico.")

# --- MÉTRICAS DE DESEMPEÑO ---
data_mun = df_prod[df_prod['Municipio'] == mun_sel]

col1, col2, col3, col4 = st.columns(4)

with col1:
    rend_medio = data_mun['Rendimiento'].mean()
    st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Rendimiento Promedio", f"{rend_medio:.2f} T/Ha")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    area_tot = data_mun['Area Sembrada'].sum()
    st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Área Sembrada", f"{area_tot:,.0f} Ha")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    # Cálculo de eficiencia (Cosechado / Sembrado)
    eficiencia = (data_mun['Area Cosechada'].sum() / area_tot * 100) if area_tot > 0 else 0
    st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Eficiencia de Cosecha", f"{eficiencia:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    # Ejemplo de temperatura si existe el dataset
    temp_val = "N/D"
    if df_temp is not None and 'Municipio:' in df_temp.columns:
        temp_val = f"{df_temp[df_temp['Municipio:'] == mun_sel]['Valor:'].mean():.1f} °C"
    st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Temp. Promedio", temp_val)
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAPA Y ACCIONES RECOMENDADAS ---
st.divider()
c_map, c_action = st.columns([2, 1])

with c_map:
    st.subheader("🗺️ Geo-localización de Lotes")
    if df_temp is not None and 'Latitud:' in df_temp.columns:
        # Normalización de coordenadas para el mapa de Streamlit
        # (Ajuste basado en el formato detectado en tus archivos)
        df_map = df_temp[df_temp['Municipio:'] == mun_sel].copy()
        
        def normalize_coord(x):
            try:
                # Convierte el formato "62.983..." a decimal "6.298..."
                s = str(x).replace(".", "")
                return float(s[0] + "." + s[1:6])
            except: return 0.0

        df_map['lat'] = df_map['Latitud:'].apply(normalize_coord)
        df_map['lon'] = df_map['Longitud:'].apply(lambda x: -normalize_coord(abs(x)))
        
        st.map(df_map[['lat', 'lon']], zoom=10)
    else:
        st.warning("No hay coordenadas GPS procesables para este municipio.")

with c_action:
    st.subheader("🎯 Acciones Sugeridas")
    if rend_medio < 1.0:
        st.error("🚨 **Alerta de Rendimiento:** La producción está por debajo del umbral crítico. Se recomienda auditoría de suelos.")
    else:
        st.success("🌱 **Zona de Alta Productividad:** Condiciones óptimas detectadas. Apta para programas de tecnificación.")
    
    st.write("---")
    st.button("📄 Exportar Hoja de Ruta para Campo")
    st.button("🔔 Notificar a Técnicos de Zona")

# --- GRÁFICO EVOLUTIVO ---
st.divider()
st.subheader("📈 Evolución de Rendimiento por Producto")
fig = px.line(data_mun, x='Año', y='Rendimiento', color='Producto',
              markers=True, title="Histórico de Rendimiento (T/Ha)",
              color_discrete_sequence=['#15803d', '#1e3a8a'])
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Agro-Clima Intelligence Pro - Sistema de Soporte a Decisiones")
