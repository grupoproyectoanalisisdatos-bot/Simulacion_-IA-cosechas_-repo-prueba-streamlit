import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import subprocess

# --- FUNCIÓN DE INSTALACIÓN DINÁMICA (Último recurso) ---
def try_install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except:
        return False

# --- GESTIÓN DE DEPENDENCIAS ---
PLOTLY_AVAILABLE = False
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    # Intentar instalarlo si falla (solo funciona en algunos entornos)
    if try_install("plotly"):
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            PLOTLY_AVAILABLE = True
        except:
            PLOTLY_AVAILABLE = False

# --- CONFIGURACIÓN UI ---
st.set_page_config(page_title="IA Cosechas - Simulación", layout="wide")

# --- BARRA LATERAL DE DIAGNÓSTICO ---
with st.sidebar:
    st.header("🔍 Diagnóstico")
    st.write(f"**Plotly cargado:** {'✅' if PLOTLY_AVAILABLE else '❌'}")
    if st.button("Ver paquetes instalados"):
        try:
            import pkg_resources
            installed_packages = [f"{d.project_name}=={d.version}" for d in pkg_resources.working_set]
            st.write(sorted(installed_packages))
        except:
            st.write("No se pudo obtener la lista de paquetes.")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Buscamos archivos comunes reportados en tus logs
    search_files = [
        "Datos para la Base de Datos - Produccion.csv",
        "Datos para la Base de Datos - Produccion.xlsx",
        "Datos para la Base de Datos - Temperatura.csv",
        "Datos para la Base de Datos - Temperatura.xlsx"
    ]
    
    found_data = {}
    for f in search_files:
        if os.path.exists(f):
            name = "Producción" if "Produccion" in f else "Clima"
            try:
                if f.endswith('.csv'):
                    found_data[name] = pd.read_csv(f)
                else:
                    found_data[name] = pd.read_excel(f)
            except Exception as e:
                st.error(f"Error al leer {f}: {e}")
    return found_data

# --- VISTA PRINCIPAL ---
st.title("🌾 Simulación de Cosechas con IA")

data = load_data()

if PLOTLY_AVAILABLE:
    # --- DASHBOARD CON GRÁFICOS ---
    if data:
        col1, col2 = st.columns(2)
        
        if "Producción" in data:
            with col1:
                st.subheader("Análisis de Producción")
                df = data["Producción"]
                # Intentamos usar columnas típicas
                target_col = df.select_dtypes(include=[np.number]).columns[0]
                label_col = 'Municipio' if 'Municipio' in df.columns else df.columns[0]
                fig = px.bar(df, x=label_col, y=target_col, color=target_col, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                
        if "Clima" in data:
            with col2:
                st.subheader("Variables Climáticas")
                df = data["Clima"]
                temp_col = df.select_dtypes(include=[np.number]).columns[0]
                fig2 = px.line(df, y=temp_col, title="Tendencia Histórica", markers=True)
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sube archivos de datos (.csv o .xlsx) al repositorio para visualizar el análisis.")
        st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1000", caption="Preparado para el análisis")

else:
    # --- MODO DE EMERGENCIA (SIN PLOTLY) ---
    st.error("### 🚨 Error de Dependencia")
    st.warning("La librería `plotly` no está disponible en este servidor.")
    st.info("Mostrando datos en formato tabla para no interrumpir el trabajo:")
    
    if data:
        for k, v in data.items():
            st.write(f"**Tabla: {k}**")
            st.dataframe(v.head(20))
    else:
        st.write("No hay datos disponibles para mostrar.")

st.markdown("---")
st.caption("Módulo de Análisis v3.0 - Resiliente a errores de librería")
