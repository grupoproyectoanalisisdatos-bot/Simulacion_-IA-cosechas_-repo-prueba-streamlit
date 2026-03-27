import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import kagglehub
import os
import zipfile
import glob

# Configuración de página con el nuevo estándar de Streamlit
st.set_page_config(
    page_title="Data Analytics - Cuenca del Magdalena",
    page_icon="🌊",
    layout="wide"
)

# Estilos CSS profesionales
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; }
    .subtitle { color: #64748b; font-size: 1.2rem; margin-bottom: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; background-color: #f1f5f9; 
        border-radius: 5px 5px 0 0; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
    .help-card { background-color: #e2e8f0; padding: 15px; border-radius: 8px; border-left: 5px solid #1e3a8a; }
    .error-box { background-color: #fee2e2; border: 1px solid #ef4444; padding: 15px; border-radius: 8px; color: #b91c1c; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner="Accediendo a Kaggle y procesando archivos...")
def load_data_from_kaggle():
    """Descarga el dataset, descomprime si es necesario y busca archivos CSV."""
    try:
        # Descarga la última versión del dataset
        download_path = kagglehub.dataset_download("corzogac/magdalena-colombia-data")
        
        # 1. VERIFICACIÓN Y DESCOMPRESIÓN MANUAL
        # Si la ruta es un archivo o contiene archivos .archive/.zip, intentamos extraer
        for root, dirs, files in os.walk(download_path):
            for file in files:
                if file.endswith(".zip") or file.endswith(".archive"):
                    archive_path = os.path.join(root, file)
                    try:
                        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                            # Extraemos en la misma carpeta de descarga
                            zip_ref.extractall(download_path)
                    except Exception:
                        pass # Si no es un zip válido, continuamos

        # 2. BÚSQUEDA PROFUNDA DE CSV
        files_found = []
        all_detected_files = []
        
        for root, dirs, files in os.walk(download_path):
            for file in files:
                full_path = os.path.join(root, file)
                all_detected_files.append(file)
                if file.lower().endswith(".csv"):
                    files_found.append(full_path)
        
        if not files_found:
            st.session_state['debug_files'] = all_detected_files
            st.session_state['debug_path'] = download_path
            return None
        
        # Seleccionamos el archivo con mayor tamaño (usualmente el dataset principal)
        target_file = max(files_found, key=os.path.getsize)
        
        # 3. CARGA DE DATOS
        try:
            # Intento con detección automática de separador
            df = pd.read_csv(target_file, sep=None, engine='python', encoding='utf-8')
        except Exception:
            try:
                df = pd.read_csv(target_file, sep=None, engine='python', encoding='latin-1')
            except Exception as e:
                st.error(f"Error de decodificación: {e}")
                return None
            
        # Limpieza de nombres de columnas
        df.columns = [
            str(c).lower().replace(' ', '_')
            .replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            .strip() for c in df.columns
        ]
        return df
    except Exception as e:
        st.error(f"Error crítico de conexión: {e}")
        return None

def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'

    # --- LANDING PAGE ---
    if st.session_state.page == 'landing':
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<h1 class="main-title">Análisis Integrador: <br>Río Magdalena</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle">Exploración de datos socio-ambientales y recursos del departamento del Magdalena.</p>', unsafe_allow_html=True)
            
            st.info("**Nivel Integrador:** Herramienta de inteligencia de datos para el monitoreo hidrológico y social.")
            
            if st.button("🚀 Ingresar al Panel de Trabajo", width='stretch'):
                st.session_state.page = 'dashboard'
                st.rerun()
        
        with col2:
            st.image("https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&q=80&w=800", 
                     caption="Vista del Río Magdalena", width='stretch')

    # --- DASHBOARD PRINCIPAL ---
    else:
        with st.sidebar:
            st.title("📊 Navegación")
            if st.button("⬅ Volver al Inicio"):
                st.session_state.page = 'landing'
                st.rerun()
            st.divider()
            st.write("**Entorno:** Streamlit Cloud")
            st.write("**Estado:** Análisis en tiempo real")
            
        # Carga de datos
        df = load_data_from_kaggle()
        
        if df is not None:
            st.sidebar.success("✅ Dataset Vinculado")
            tab_data, tab_viz, tab_docs = st.tabs(["🔍 Exploración", "📈 Gráficos", "📖 Info"])

            with tab_data:
                st.subheader("Datos de la Cuenca")
                st.dataframe(df.head(20), width='stretch')
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Registros", f"{df.shape[0]:,}")
                c2.metric("Variables", df.shape[1])
                c3.metric("Datos Nulos", df.isna().sum().sum())
                
                st.divider()
                st.write("**Resumen Estadístico:**")
                st.write(df.describe())

            with tab_viz:
                sns.set_theme(style="darkgrid")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

                if numeric_cols:
                    st.markdown("### 1. Distribución de Variables")
                    g1_col, t1_col = st.columns([2, 1])
                    with g1_col:
                        var_sel = st.selectbox("Seleccione Métrica", numeric_cols, key="s1")
                        fig1, ax1 = plt.subplots(figsize=(10, 5))
                        sns.histplot(df[var_sel], kde=True, color="#1e3a8a", ax=ax1)
                        st.pyplot(fig1)
                    with t1_col:
                        st.markdown('<div class="help-card">💡 <b>Nota:</b> El histograma muestra la frecuencia de los datos recolectados.</div>', unsafe_allow_html=True)

                    st.divider()

                    st.markdown("### 2. Matriz de Correlación")
                    g2_col, t2_col = st.columns([2, 1])
                    with g2_col:
                        fig2, ax2 = plt.subplots(figsize=(10, 8))
                        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="mako", fmt=".2f", ax=ax2)
                        st.pyplot(fig2)
                    with t2_col:
                        st.markdown('<div class="help-card">💡 <b>Nota:</b> Identifica la relación entre diferentes factores de la cuenca.</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay suficientes datos numéricos.")

            with tab_docs:
                st.markdown("### Ficha Técnica\nDataset descargado y procesado automáticamente desde Kaggle.")
        else:
            # DIAGNÓSTICO
            st.markdown('<div class="error-box">⚠️ Error: No se detectaron archivos CSV.</div>', unsafe_allow_html=True)
            with st.expander("🛠 Detalles del Servidor"):
                if 'debug_path' in st.session_state:
                    st.write(f"Ruta: `{st.session_state['debug_path']}`")
                if 'debug_files' in st.session_state:
                    st.write("Archivos detectados:", st.session_state['debug_files'])

if __name__ == "__main__":
    main()
