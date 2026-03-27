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

# Estilos personalizados (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; }
    .subtitle { color: #64748b; font-size: 1.2rem; margin-bottom: 2rem; }
    .card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; white-space: pre-wrap; background-color: #f1f5f9; 
        border-radius: 5px 5px 0 0; gap: 1px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
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
    # Inicialización del estado de la sesión para navegación
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'

    # --- LANDING PAGE ---
    if st.session_state.page == 'landing':
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<h1 class="main-title">Análisis Integrador: <br>Río Magdalena</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle">Exploración avanzada de datos socio-ambientales y geográficos de la cuenca principal de Colombia.</p>', unsafe_allow_html=True)
            
            st.info("""
            **Sobre este Dataset:**
            Este conjunto de datos integra variables críticas sobre el departamento del Magdalena. 
            Permite realizar análisis de correlación, distribución de recursos y tendencias temporales.
            """)
            
            if st.button("🚀 Ingresar al Panel de Trabajo", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
        
        with col2:
            # Imagen representativa (Placeholder profesional)
            st.image("https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&q=80&w=800", 
                     caption="Cuenca del Río Magdalena - Análisis de Datos", use_container_width=True)

    # --- DASHBOARD ---
    else:
        # Sidebar de navegación
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
            st.title("Panel de Control")
            if st.button("⬅ Volver al Inicio"):
                st.session_state.page = 'landing'
                st.rerun()
            st.divider()
            st.write("**Nivel:** Integrador Experto")
            st.write("**Dataset:** Magdalena-Colombia")

        df = load_kaggle_data()
        
        if df is not None:
            st.title("🧪 Laboratorio de Análisis de Datos")
            
            # Pestañas de Trabajo
            tab_explora, tab_stats, tab_doc = st.tabs(["🔍 Exploración Raw", "📊 Gráficos Expertos", "📖 Documentación"])

            with tab_explora:
                st.subheader("Vista Previa del Dataset")
                st.dataframe(df.head(15), use_container_width=True)
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Total Registros", df.shape[0])
                col_m2.metric("Columnas", df.shape[1])
                col_m3.metric("Valores Nulos", df.isna().sum().sum())

            with tab_stats:
                # Configuración Global de Seaborn
                sns.set_theme(style="whitegrid")
                palette = sns.color_palette("viridis")

                # --- GRÁFICO 1: DISTRIBUCIÓN ---
                st.markdown("### 1. Análisis de Distribución Univariada")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                col_g1, col_t1 = st.columns([2, 1])
                with col_g1:
                    sel_col = st.selectbox("Selecciona variable para analizar distribución", numeric_cols)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    sns.histplot(df[sel_col], kde=True, color="#1e3a8a", ax=ax)
                    st.pyplot(fig)
                with col_t1:
                    st.help("El histograma con KDE (Kernel Density Estimate) permite visualizar la forma de la distribución, detectar sesgos (skewness) y valores atípicos.")
                    st.write(f"**Análisis:** La variable `{sel_col}` presenta una media de `{df[sel_col].mean():.2f}`. Observa si la curva se asemeja a una normal o si tiene múltiples modas.")

                st.divider()

                # --- GRÁFICO 2: CORRELACIÓN (HEATMAP) ---
                st.markdown("### 2. Matriz de Correlación de Pearson")
                col_g2, col_t2 = st.columns([2, 1])
                with col_g2:
                    fig2, ax2 = plt.subplots(figsize=(10, 8))
                    corr = df[numeric_cols].corr()
                    sns.heatmap(corr, annot=True, cmap="YlGnBu", fmt=".2f", ax=ax2)
                    st.pyplot(fig2)
                with col_t2:
                    st.help("El mapa de calor muestra la fuerza de la relación lineal entre variables (de -1 a 1).")
                    st.write("**Interpretación:** Valores cercanos a 1 indican una correlación positiva fuerte. Útil para la selección de variables en modelos predictivos.")

                st.divider()

                # --- GRÁFICO 3: RELACIÓN (REGRESIÓN) ---
                st.markdown("### 3. Análisis de Regresión y Dispersión")
                col_g3, col_t3 = st.columns([2, 1])
                if len(numeric_cols) >= 2:
                    with col_g3:
                        c1, c2 = st.columns(2)
                        v1 = c1.selectbox("Variable X", numeric_cols, index=0)
                        v2 = c2.selectbox("Variable Y", numeric_cols, index=1)
                        fig3, ax3 = plt.subplots()
                        sns.regplot(data=df, x=v1, y=v2, scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax3)
                        st.pyplot(fig3)
                    with col_t3:
                        st.help("El gráfico de dispersión con línea de regresión ayuda a identificar tendencias y la heterocedasticidad de los datos.")
                        st.write(f"**Análisis de Tendencia:** Visualiza cómo varía `{v2}` ante cambios en `{v1}`.")

            with tab_doc:
                st.markdown("""
                ### Guía Metodológica
                1. **Carga de Datos:** Se utiliza la librería `kagglehub` para garantizar la fuente original.
                2. **Limpieza:** Se normalizan los encabezados para evitar errores de sintaxis en Python.
                3. **Visualización:** Se emplea `Seaborn` por su capacidad de realizar agregaciones estadísticas automáticas.
                
                ### Requerimientos de Software
                - Python 3.9+
                - Streamlit (Interfaz)
                - Seaborn & Matplotlib (Gráficos)
                - Pandas (Manipulación de datos)
                """)

        else:
            st.error("No se pudieron cargar los datos. Por favor revisa la configuración del API de Kaggle.")

if __name__ == "__main__":
    main()
