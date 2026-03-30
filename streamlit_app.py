import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import subprocess
import time

# --- LÓGICA DE INSTALACIÓN FORZADA ---
def ensure_dependencies():
    """Intenta importar plotly, si falla lo instala y recarga el entorno."""
    try:
        import plotly.express as px
        return True
    except ImportError:
        try:
            # Comando de instalación silenciosa
            subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly", "pandas", "openpyxl"])
            import site
            from importlib import reload
            reload(site)
            return True
        except Exception as e:
            return False

# Ejecutar verificación de dependencias
PLOTLY_READY = ensure_dependencies()

# Importaciones tras validación
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    PLOTLY_READY = False

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="IA Cosechas | Simulación Pro",
    page_icon="🌾",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS (Corrección de unsafe_allow_html) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL: ESTADO Y SISTEMA ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/agriculture.png", width=80)
    st.title("Panel de Control")
    
    if PLOTLY_READY:
        st.success("✅ Motor Gráfico: Activo")
    else:
        st.error("❌ Motor Gráfico: Fallido")
    
    st.divider()
    st.subheader("🛠️ Info de Entorno")
    st.caption(f"Python: {sys.version.split()[0]}")
    
    if st.button("🔄 Forzar Reinstalación"):
        st.cache_data.clear()
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "plotly"])
        st.rerun()

# --- CARGA DE DATOS ---
@st.cache_data
def get_data():
    # Nombres exactos detectados en los logs
    files = {
        "Producción": "Datos para la Base de Datos - Produccion.csv",
        "Temperatura": "Datos para la Base de Datos - Temperatura.csv"
    }
    loaded = {}
    for key, path in files.items():
        if os.path.exists(path):
            try:
                # Intento de lectura robusta
                loaded[key] = pd.read_csv(path, encoding='utf-8')
            except:
                try: loaded[key] = pd.read_csv(path, encoding='latin1')
                except: pass
    return loaded

# --- CUERPO PRINCIPAL ---
st.title("🌾 Análisis de Cosechas con IA")
st.subheader("Simulación y Visualización de Datos Agrícolas")

datasets = get_data()

if not datasets:
    st.warning("⚠️ No se encontraron los archivos CSV en la raíz del repositorio.")
    st.info("Asegúrate de que los archivos 'Datos para la Base de Datos - Produccion.csv' estén presentes.")
else:
    # --- MÉTRICAS ---
    if "Producción" in datasets:
        df_p = datasets["Producción"]
        m1, m2, m3 = st.columns(3)
        with m1:
            # Tomar la primera columna numérica que encuentre para el total
            num_cols = df_p.select_dtypes(include=[np.number]).columns
            if len(num_cols) > 0:
                val = df_p[num_cols[0]].sum()
                st.metric("Producción Total", f"{val:,.0f} kg")
        with m2:
            st.metric("Registros", len(df_p))
        with m3:
            st.metric("Estado", "En Línea")

    st.divider()
    
    # --- VISUALIZACIÓN CONDICIONAL ---
    if PLOTLY_READY:
        tab1, tab2 = st.tabs(["📊 Gráficos de Producción", "🌡️ Análisis Climático"])
        
        with tab1:
            if "Producción" in datasets:
                df = datasets["Producción"]
                cols = df.columns.tolist()
                # Gráfico simple de barras
                fig = px.histogram(df, x=cols[0], y=df.select_dtypes(include=[np.number]).columns[0],
                                 title="Distribución de Producción", color_discrete_sequence=['#2ecc71'])
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if "Temperatura" in datasets:
                df = datasets["Temperatura"]
                st.line_chart(df.select_dtypes(include=[np.number]))
    else:
        st.warning("### 💡 Modo de compatibilidad activado")
        st.info("Mostrando tablas de datos (Plotly no disponible temporalmente).")
        for name, df in datasets.items():
            st.write(f"**Vista previa: {name}**")
            st.dataframe(df.head(20), use_container_width=True)

st.markdown("---")
st.caption("Sistema de Monitoreo Agrícola | Generado para contingencia de infraestructura")
