import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import subprocess

# --- AUTO-INSTALACIÓN DE DEPENDENCIAS ---
def install_requirements():
    try:
        import plotly
        import openpyxl
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly", "pandas", "openpyxl"])
            return True
        except:
            return False

READY = install_requirements()

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="IA Cosechas - Verificador", layout="wide")

# CORRECCIÓN CRÍTICA: El parámetro es unsafe_allow_html (no unsafe_allow_stdio)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌾 Verificador de Datos e IA de Cosechas")

# --- SECCIÓN 1: EXPLORADOR DE ARCHIVOS (Para verificar el repositorio) ---
with st.expander("🔍 Verificar Archivos en el Repositorio", expanded=True):
    current_files = os.listdir(".")
    st.write("Archivos detectados en la raíz del proyecto:")
    
    # Buscamos coincidencias con tus archivos
    target_files = ["Produccion", "Temperatura"]
    found_files = {}
    
    cols = st.columns(len(current_files) // 5 + 1)
    for i, file in enumerate(sorted(current_files)):
        with cols[i % len(cols)]:
            if "csv" in file.lower():
                st.code(f"📄 {file}")
                if "produccion" in file.lower(): found_files["Producción"] = file
                if "temperatura" in file.lower(): found_files["Temperatura"] = file
            else:
                st.text(f"📁 {file}")

# --- SECCIÓN 2: CARGA DE DATOS ---
st.divider()

def load_data(file_name):
    if not file_name: return None
    try:
        # Intento de carga con diferentes encodings por si es CSV de Excel
        return pd.read_csv(file_name, encoding='utf-8')
    except:
        try:
            return pd.read_csv(file_name, encoding='latin1', sep=None, engine='python')
        except Exception as e:
            st.error(f"Error cargando {file_name}: {e}")
            return None

# Intentar cargar si se encontraron
data_p = load_data(found_files.get("Producción"))
data_t = load_data(found_files.get("Temperatura"))

if data_p is not None:
    st.success(f"✅ Datos de Producción cargados: {found_files['Producción']}")
    
    m1, m2 = st.columns(2)
    with m1:
        st.dataframe(data_p.head(10), use_container_width=True)
    with m2:
        if READY:
            import plotly.express as px
            # Intentar gráfico con las primeras dos columnas
            cols = data_p.columns
            num_cols = data_p.select_dtypes(include=[np.number]).columns
            if len(num_cols) > 0:
                fig = px.bar(data_p, x=cols[0], y=num_cols[0], title="Vista Rápida de Producción")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Gráficos no disponibles (Instalando Plotly...)")

if data_t is not None:
    st.success(f"✅ Datos de Temperatura cargados: {found_files['Temperatura']}")
    st.line_chart(data_t.select_dtypes(include=[np.number]))

if not found_files:
    st.error("❌ No se detectaron archivos que contengan 'Produccion' o 'Temperatura' en el nombre.")
    st.info("Revisa la lista de archivos en el expansor de arriba para verificar los nombres exactos.")

st.markdown("---")
st.caption("Herramienta de diagnóstico de despliegue v1.2")
