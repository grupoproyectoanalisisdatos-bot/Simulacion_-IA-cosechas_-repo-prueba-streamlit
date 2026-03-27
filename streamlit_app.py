import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import kagglehub
import os
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
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner="Accediendo a Kaggle y procesando archivos...")
def load_data_from_kaggle():
    """Descarga el dataset y busca archivos CSV de forma recursiva."""
    try:
        # Descarga la última versión
        download_path = kagglehub.dataset_download("corzogac/magdalena-colombia-data")
        
        # Búsqueda profunda de archivos CSV (Kaggle a veces crea subcarpetas con hashes)
        files_found = []
        for root, dirs, files in os.walk(download_path):
            for file in files:
                if file.endswith(".csv"):
                    files_found.append(os.path.join(root, file))
        
        if not files_found:
            return None
        
        # Cargamos el archivo más grande (generalmente es el dataset principal)
        # O el primero si solo hay uno
        target_file = max(files_found, key=os.path.getsize)
        
        # Intentar leer con detección de errores de codificación
        try:
            df = pd.read_csv(target_file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(target_file, encoding='latin-1')
            
        # Limpieza técnica de nombres de columnas
        df.columns = [c.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error crítico en la carga: {e}")
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
            
            st.info("**Expertise Nivel Integrador:** Este panel procesa datos reales de Kaggle para realizar análisis de correlación y regresión científica.")
            
            # Nota: use_container_width=True es ahora width='stretch'
            if st.button("🚀 Ingresar al Panel de Trabajo", width='stretch'):
                st.session_state.page = 'dashboard'
                st.rerun()
        
        with col2:
            st.image("https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&q=80&w=800", 
                     caption="Cuenca del Río Magdalena", width='stretch')

    # --- DASHBOARD PRINCIPAL ---
    else:
        with st.sidebar:
            st.title("📊 Navegación")
            if st.button("⬅ Volver al Inicio"):
                st.session_state.page = 'landing'
                st.rerun()
            st.divider()
            st.write("**Entorno:** Streamlit Cloud")
            st.write("**Librería Gráfica:** Seaborn")
            st.success("Dataset Vinculado")

        df = load_data_from_kaggle()
        
        if df is not None:
            tab_data, tab_viz, tab_docs = st.tabs(["🔍 Datos", "📈 Análisis Gráfico", "📖 Documentación"])

            with tab_data:
                st.subheader("Exploración Inicial del Dataset")
                st.dataframe(df.head(20), width='stretch')
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Filas", df.shape[0])
                c2.metric("Columnas", df.shape[1])
                c3.metric("Nulos", df.isna().sum().sum())

            with tab_viz:
                sns.set_theme(style="darkgrid")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

                if numeric_cols:
                    # Gráfico 1: Histograma
                    st.markdown("### 1. Distribución de Frecuencias")
                    g1_col, t1_col = st.columns([2, 1])
                    with g1_col:
                        var_sel = st.selectbox("Seleccione Variable", numeric_cols, key="s1")
                        fig1, ax1 = plt.subplots(figsize=(10, 5))
                        sns.histplot(df[var_sel], kde=True, color="#1e3a8a", ax=ax1)
                        st.pyplot(fig1)
                    with t1_col:
                        st.markdown('<div class="help-card">💡 <b>Ayuda:</b> El histograma con KDE permite identificar si la variable tiene una distribución Gaussiana (Normal) o si existen sesgos importantes que requieran normalización.</div>', unsafe_allow_html=True)

                    st.divider()

                    # Gráfico 2: Heatmap
                    st.markdown("### 2. Matriz de Correlación (Pearson)")
                    g2_col, t2_col = st.columns([2, 1])
                    with g2_col:
                        fig2, ax2 = plt.subplots(figsize=(10, 8))
                        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="YlGnBu", ax=ax2)
                        st.pyplot(fig2)
                    with t2_col:
                        st.markdown('<div class="help-card">💡 <b>Ayuda:</b> Valores cercanos a 1 indican una relación directa fuerte. Útil para entender qué variables influyen sobre otras en el ecosistema del Magdalena.</div>', unsafe_allow_html=True)
                else:
                    st.warning("No se detectaron columnas numéricas suficientes.")

            with tab_docs:
                st.markdown("""
                ### Documentación del Proyecto
                - **Librerías**: `seaborn`, `pandas`, `kagglehub`.
                - **Dataset**: `magdalena-colombia-data`.
                - **Método**: La aplicación descarga el dataset en tiempo real y busca el archivo `.csv` más relevante de forma recursiva para evitar errores de ruta.
                """)
        else:
            st.error("Lo sentimos, el dataset no pudo ser leído. Verifique los logs de la consola en Streamlit Cloud.")

if __name__ == "__main__":
    main()
