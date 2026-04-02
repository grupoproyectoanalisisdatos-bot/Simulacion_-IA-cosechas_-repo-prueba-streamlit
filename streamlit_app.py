import streamlit as st
import pandas as pd
import numpy as np
import os

# --- PRE-FLIGHT CHECK ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    st.error("⚠️ Librería 'plotly' no detectada.")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Agro-Analítica Pro", layout="wide")

# --- LIMPIEZA DE DATOS PROFUNDA (Solución a DuplicateError y Tipos Mixtos) ---
def clean_data(df):
    # 1. Unicidad de columnas (Evita el error 'Valor:' duplicado)
    new_cols = []
    counts = {}
    for col in df.columns:
        name = str(col).strip().replace(':', '')
        if name in counts:
            counts[name] += 1
            new_cols.append(f"{name}_{counts[name]}")
        else:
            counts[name] = 0
            new_cols.append(name)
    df.columns = new_cols

    # 2. Identificación y conversión de FECHAS
    for col in df.columns:
        if any(x in col.lower() for x in ['fecha', 'date', 'anio', 'año', 'mes', 'periodo']):
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 3. Normalización Numérica (Asegura que el 'Valor' sea procesable)
    for col in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df.dropna(how='all', axis=1)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    file_path = "Datos  Base de Datos.xlsx"
    if os.path.exists(file_path):
        try:
            excel = pd.ExcelFile(file_path, engine='openpyxl')
            return {sheet: clean_data(pd.read_excel(file_path, sheet_name=sheet)) for sheet in excel.sheet_names}, None
        except Exception as e:
            return None, str(e)
    return None, "Archivo no encontrado."

data_dict, error = load_data()

if error:
    st.error(f"Error: {error}")
elif data_dict:
    with st.sidebar:
        sheet = st.selectbox("Seleccionar Hoja", list(data_dict.keys()))
        df = data_dict[sheet]

    # SEPARACIÓN LÓGICA DE VARIABLES
    # Las coordenadas NO se usan para análisis de regresión
    geo_keywords = ['lat', 'lon', 'latitud', 'longitud']
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if not any(k in c.lower() for k in geo_keywords)]

    tabs = st.tabs(["📈 Tendencia Temporal", "🌍 Georeferenciación", "📊 Distribución"])

    with tabs[0]:
        st.subheader("Análisis de Evolución Temporal")
        if date_cols and num_cols:
            col1, col2 = st.columns(2)
            time_col = col1.selectbox("Eje de Tiempo", date_cols)
            val_col = col2.selectbox("Indicador (Temperatura/Valor)", num_cols)

            # Relacionar FECHA con VALOR correctamente
            plot_df = df.dropna(subset=[time_col, val_col]).sort_values(time_col)
            
            fig = px.line(plot_df, x=time_col, y=val_col, 
                         title=f"Comportamiento de {val_col} a través del tiempo",
                         markers=True, line_shape="spline",
                         color_discrete_sequence=['#2E7D32'])
            
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("Este gráfico relaciona cronológicamente los datos, permitiendo identificar patrones estacionales o tendencias de calentamiento/enfriamiento.")
        else:
            st.warning("No se detectaron columnas de fecha y valor numérico simultáneamente.")

    with tabs[1]:
        st.subheader("Mapa de Calor Productivo")
        lat = next((c for c in df.columns if 'lat' in c.lower()), None)
        lon = next((c for c in df.columns if 'lon' in c.lower()), None)
        
        if lat and lon and num_cols:
            m_val = st.selectbox("Variable para Mapa", num_cols, key="map_val")
            map_df = df.dropna(subset=[lat, lon, m_val])
            fig_map = px.scatter_mapbox(map_df, lat=lat, lon=lon, color=m_val, size=m_val,
                                       color_continuous_scale="Viridis", zoom=5,
                                       mapbox_style="carto-positron", height=600)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Datos de georeferenciación no disponibles en esta tabla.")

    with tabs[2]:
        st.subheader("Análisis de Variabilidad (Outliers)")
        if num_cols:
            dist_val = st.selectbox("Variable", num_cols, key="dist_val")
            fig_dist = px.histogram(df, x=dist_val, marginal="box", color_discrete_sequence=['#1565C0'])
            st.plotly_chart(fig_dist, use_container_width=True)

st.divider()
st.caption("Estructura de Analítica Avanzada v4.0 | Enfoque en Relación Temporal")
