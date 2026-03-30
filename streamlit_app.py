import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# --- DIAGNÓSTICO DE DEPENDENCIAS ---
def check_dependencies():
    deps = ["plotly", "pandas", "openpyxl", "numpy"]
    status = {}
    for lib in deps:
        try:
            __import__(lib)
            status[lib] = "✅ Instalada"
        except ImportError:
            status[lib] = "❌ No encontrada"
    return status

# --- INTENTO DE IMPORTACIÓN DE PLOTLY ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Agro-Clima Pro - Dashboard",
    page_icon="🚜",
    layout="wide"
)

# --- ESTILOS ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ESTADO DEL SISTEMA ---
with st.sidebar:
    st.title("⚙️ Configuración")
    if st.button("🔍 Diagnosticar Sistema"):
        st.write("### Estado de Librerías")
        st.json(check_dependencies())
        st.write(f"Versión Python: {sys.version.split()[0]}")

# --- FUNCIÓN DE CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Diccionario de archivos basado en tus logs
    files = {
        "Producción": ["Datos para la Base de Datos - Produccion.csv", "Datos para la Base de Datos - Produccion.xlsx"],
        "Clima": ["Datos para la Base de Datos - Temperatura.csv", "Datos para la Base de Datos - Temperatura.xlsx"]
    }
    
    loaded_data = {}
    for key, paths in files.items():
        for path in paths:
            if os.path.exists(path):
                try:
                    if path.endswith('.csv'):
                        loaded_data[key] = pd.read_csv(path)
                    else:
                        loaded_data[key] = pd.read_excel(path)
                    break
                except Exception as e:
                    st.error(f"Error cargando {path}: {e}")
    return loaded_data

# --- CUERPO PRINCIPAL ---
st.title("🚜 Dashboard Agro-Climático")

if not PLOTLY_AVAILABLE:
    st.warning("⚠️ **Librería de gráficos (Plotly) no detectada.**")
    st.info("Para solucionar esto, asegúrate de que tu archivo `requirements.txt` tenga una línea que diga simplemente: `plotly`")
    
    # Versión simplificada sin Plotly para que la app no falle
    st.subheader("Vista Previa de Datos (Modo Texto)")
    data = load_data()
    if data:
        for name, df in data.items():
            st.write(f"**Base de datos: {name}**")
            st.dataframe(df.head(5))
    else:
        st.info("Sube tus archivos .csv o .xlsx al repositorio para comenzar.")
    st.stop()

# --- SI PLOTLY ESTÁ DISPONIBLE, MOSTRAR DASHBOARD COMPLETO ---
data = load_data()

if data:
    st.success("✅ Datos cargados correctamente")
    col1, col2 = st.columns(2)
    
    if "Producción" in data:
        df_p = data["Producción"]
        with col1:
            st.subheader("Rendimiento por Municipio")
            # Asumiendo columnas detectadas en logs: 'Municipio', 'Rendimiento'
            fig = px.bar(df_p, x='Municipio', y='Rendimiento', color='Rendimiento',
                         title="Rendimiento Agrícola", color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
            
    if "Clima" in data:
        df_c = data["Clima"]
        with col2:
            st.subheader("Tendencia de Temperatura")
            # Asumiendo columna 'Temperatura'
            temp_col = 'Temperatura' if 'Temperatura' in df_c.columns else df_c.select_dtypes(include=[np.number]).columns[0]
            fig2 = px.line(df_c, y=temp_col, title="Variación Térmica", line_shape='spline')
            st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Esperando archivos de datos en la raíz del proyecto...")
    st.image("https://images.unsplash.com/photo-1495107336214-b292163974c0?q=80&w=1000", caption="Análisis de Cosechas Inteligente")

st.markdown("---")
st.caption("v2.6 - Sistema de Diagnóstico de Dependencias Integrado")
