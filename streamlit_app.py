import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import kagglehub
import os
import glob

# Configuración inicial de la página
st.set_page_config(
    page_title="Data Analytics - Cuenca del Magdalena",
    page_icon="🌊",
    layout="wide"
)

# Estilos personalizados (CSS) para nivel profesional
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
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner="Accediendo a la base de datos de Kaggle...")
def load_kaggle_data():
    """Descarga y limpia los datos de Kaggle."""
    try:
        path = kagglehub.dataset_download("corzogac/magdalena-colombia-data")
        csv_files = glob.glob(os.path.join(path, "*.csv"))
        if not csv_files: return None
        df = pd.read_csv(csv_files[0])
        # Limpieza estándar de nombres de columnas
        df.columns = [c.lower().replace(' ', '_').strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error en la conexión con Kaggle: {e}")
        return None

def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'

    # --- LANDING PAGE ---
    if st.session_state.page == 'landing':
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<h1 class="main-title">Análisis Integrador: <br>Río Magdalena</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle">Exploración avanzada de datos socio-ambientales de la cuenca principal de Colombia.</p>', unsafe_allow_html=True)
            st.info("**Expertise:** Este panel integra análisis estadístico descriptivo y multivariado para la toma de decisiones basada en datos.")
            if st.button("🚀 Ingresar al Panel de Trabajo", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
        with col2:
            st.image("https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&q=80&w=800", 
                     caption="Monitoreo Cuenca del Magdalena", use_container_width=True)

    # --- DASHBOARD ---
    else:
        with st.sidebar:
            st.title("⚙️ Configuración")
            if st.button("⬅ Volver al Inicio"):
                st.session_state.page = 'landing'
                st.rerun()
            st.divider()
            st.markdown("**Status:** 🟢 Sistema Activo")
            st.markdown("**Nivel:** Integrador Experto")

        df = load_kaggle_data()
        
        if df is not None:
            tab_explora, tab_stats, tab_doc = st.tabs(["🔍 Exploración", "📊 Visualización Experta", "📖 Documentación"])

            with tab_explora:
                st.subheader("Estructura de Datos")
                st.dataframe(df.head(10), use_container_width=True)
                st.write("**Resumen Estadístico:**", df.describe())

            with tab_stats:
                sns.set_theme(style="whitegrid")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

                # Gráfico 1
                st.markdown("### 1. Distribución de Variables")
                col_g1, col_t1 = st.columns([2, 1])
                with col_g1:
                    sel_col = st.selectbox("Seleccione variable", numeric_cols)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.histplot(df[sel_col], kde=True, color="#1e3a8a", ax=ax)
                    st.pyplot(fig)
                with col_t1:
                    st.help("El KDE ayuda a visualizar la densidad de probabilidad de la variable.")
                    st.write("Analiza si los datos siguen una distribución normal o presentan asimetría.")

                st.divider()

                # Gráfico 2
                st.markdown("### 2. Correlaciones (Heatmap)")
                col_g2, col_t2 = st.columns([2, 1])
                with col_g2:
                    fig2, ax2 = plt.subplots(figsize=(8, 6))
                    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="mako", ax=ax2)
                    st.pyplot(fig2)
                with col_t2:
                    st.help("Muestra la fuerza de asociación entre variables numéricas.")
                    st.write("Identifica variables con alta colinealidad para evitar redundancias en modelos.")

            with tab_doc:
                st.markdown("""
                ### Documentación Técnica
                - **Librerías:** Seaborn, Pandas, Kagglehub.
                - **Dataset:** Magdalena-Colombia.
                - **Método:** Análisis exploratorio automatizado.
                """)
        else:
            st.warning("Cargando dataset... Asegúrate de tener conexión a internet.")

if __name__ == "__main__":
    main()
