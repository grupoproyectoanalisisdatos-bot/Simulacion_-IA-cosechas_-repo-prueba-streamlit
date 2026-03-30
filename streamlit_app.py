import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import subprocess
import time

# --- LOGICA DE INSTALACION FORZADA (Ejecución temprana) ---
def ensure_dependencies():
    """Fuerza la instalación y recarga del path si falta plotly."""
    try:
        import plotly
        return True
    except ImportError:
        # Intentar instalar usando el ejecutable actual de Python
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly", "pandas", "openpyxl"])
        # Forzar la actualización del path de búsqueda de módulos
        import site
        from importlib import reload
        reload(site)
        return False

# Ejecutar verificación antes de cualquier otra importación de plotly
PLOTLY_READY = ensure_dependencies()

# Ahora intentamos las importaciones normales
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_READY = True
except ImportError:
    PLOTLY_READY = False

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="IA Cosechas | Simulación Pro",
    page_icon="🌾",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_stdio=True)

# --- BARRA LATERAL: ESTADO Y SISTEMA ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/agriculture.png", width=80)
    st.title("Panel de Control")
    
    status_color = "green" if PLOTLY_READY else "red"
    st.markdown(f"**Motor Gráfico:** :{status_color}[{'Activo' if PLOTLY_READY else 'Inactivo (Modo Tabla)'}]")
    
    st.divider()
    st.subheader("🛠️ Info de Entorno")
    st.caption(f"Python: {sys.version.split()[0]}")
    if st.button("🔄 Reiniciar Diagnóstico"):
        st.cache_data.clear()
        st.rerun()

# --- CARGA DE DATOS INTELIGENTE ---
@st.cache_data
def get_data():
    files = {
        "Producción": "Datos para la Base de Datos - Produccion.csv",
        "Temperatura": "Datos para la Base de Datos - Temperatura.csv"
    }
    loaded = {}
    for key, path in files.items():
        if os.path.exists(path):
            try:
                loaded[key] = pd.read_csv(path)
            except:
                # Fallback por si el CSV tiene codificación extraña o es Excel mal nombrado
                try: loaded[key] = pd.read_excel(path)
                except: pass
    return loaded

# --- CUERPO PRINCIPAL ---
st.title("🌾 Análisis de Cosechas con IA")
st.subheader("Visualización de variables críticas y predicción")

datasets = get_data()

if not datasets:
    st.warning("⚠️ No se encontraron archivos de datos locales. Por favor, verifica que los archivos .csv estén en la raíz del repositorio.")
    st.info("Buscando: 'Datos para la Base de Datos - Produccion.csv'")
else:
    # --- MÉTRICAS RÁPIDAS ---
    if "Producción" in datasets:
        df_p = datasets["Producción"]
        m1, m2, m3 = st.columns(3)
        with m1:
            val = df_p.select_dtypes(include=[np.number]).iloc[:,0].sum()
            st.metric("Producción Total", f"{val:,.0f} kg")
        with m2:
            st.metric("Municipios", len(df_p))
        with m3:
            st.metric("Estado de Datos", "Sincronizado")

    # --- VISUALIZACIÓN ---
    st.divider()
    
    if PLOTLY_READY:
        tab1, tab2 = st.tabs(["📊 Gráficos de Producción", "🌡️ Análisis Climático"])
        
        with tab1:
            if "Producción" in datasets:
                df = datasets["Producción"]
                cols = df.columns.tolist()
                fig = px.bar(df, x=cols[0], y=df.select_dtypes(include=[np.number]).columns[0],
                             title="Rendimiento por Zona", color_discrete_sequence=['#2ecc71'])
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if "Temperatura" in datasets:
                df = datasets["Temperatura"]
                fig2 = px.line(df, title="Variación Térmica", template="plotly_white")
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("### 🔌 Error de librerías visuales")
        st.info("El sistema no pudo cargar Plotly. Mostrando datos crudos:")
        for name, df in datasets.items():
            st.write(f"**Datos de {name}:**")
            st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("Sistema de Monitoreo Agrícola - v3.5 (Build 2026)")
