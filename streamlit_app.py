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
    .help-icon { color: #1e3a8a; cursor: help; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner="Conectando con Kaggle y descargando el dataset...")
def load_kaggle_data():
    """Descarga y limpia los datos de Kaggle con manejo de rutas robusto."""
    try:
        # Descarga el dataset usando kagglehub
        path = kagglehub.dataset_download("corzogac/magdalena-colombia-data")
        
        # Búsqueda recursiva de archivos CSV
        csv_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
        
        if not csv_files:
            return None
        
        # Cargar el primer CSV disponible
        df = pd.read_csv(csv_files[0])
        
        # Normalización de nombres de columnas (minúsculas, sin espacios, sin tildes básicas)
        df.columns = [c.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error técnico al procesar el dataset: {e}")
        return None

def main():
    # Inicialización del estado de la sesión para la navegación entre páginas
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'

    # --- LANDING PAGE ---
    if st.session_state.page == 'landing':
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<h1 class="main-title">Análisis Integrador: <br>Río Magdalena</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle">Plataforma avanzada para la exploración de datos socio-ambientales del departamento del Magdalena, Colombia.</p>', unsafe_allow_html=True)
            
            st.info("""
            **Propósito del Proyecto:**
            Este dashboard interactivo permite a los analistas visualizar distribuciones críticas, correlaciones entre variables 
            y tendencias geográficas de la cuenca. Diseñado para niveles de análisis integrador.
            """)
            
            # Actualizado: use_container_width -> width='stretch'
            if st.button("🚀 Ingresar al Panel de Trabajo", width='stretch'):
                st.session_state.page = 'dashboard'
                st.rerun()
        
        with col2:
            # Imagen temática del Río Magdalena
            st.image("https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&q=80&w=800", 
                     caption="Monitoreo de la Cuenca Hidrográfica", width='stretch')

    # --- DASHBOARD DE TRABAJO ---
    else:
        # Barra lateral de navegación y estado
        with st.sidebar:
            st.title("⚙️ Panel de Control")
            if st.button("⬅ Volver al Inicio"):
                st.session_state.page = 'landing'
                st.rerun()
            st.divider()
            st.markdown("### Estado del Sistema")
            st.success("Conectado a Kaggle")
            st.info("Nivel: Integrador Experto")
            st.divider()
            st.caption("Desarrollado para el curso de Análisis de Datos.")

        # Carga de datos
        df = load_kaggle_data()
        
        if df is not None:
            st.title("🧪 Laboratorio de Análisis de Datos")
            
            # Organización por pestañas profesionales
            tab_explora, tab_stats, tab_doc = st.tabs(["🔍 Exploración de Datos", "📊 Visualización Experta", "📖 Documentación"])

            with tab_explora:
                st.subheader("Vista Previa de los Datos Crudos")
                st.dataframe(df.head(20), width='stretch')
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Total Registros", df.shape[0])
                col_m2.metric("Total Columnas", df.shape[1])
                col_m3.metric("Valores Nulos", df.isna().sum().sum())
                
                st.divider()
                st.write("**Resumen Estadístico:**")
                st.write(df.describe())

            with tab_stats:
                # Configuración de estilo Seaborn
                sns.set_theme(style="whitegrid", palette="mako")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

                if len(numeric_cols) > 0:
                    # --- GRÁFICO 1: DISTRIBUCIÓN ---
                    st.markdown("### 1. Análisis de Distribución Univariada")
                    col_g1, col_t1 = st.columns([2, 1])
                    with col_g1:
                        sel_col = st.selectbox("Seleccione una variable para ver su distribución", numeric_cols, key="dist_sel")
                        fig, ax = plt.subplots(figsize=(10, 5))
                        sns.histplot(df[sel_col], kde=True, color="#1e3a8a", ax=ax)
                        ax.set_title(f"Distribución de {sel_col}")
                        st.pyplot(fig)
                    with col_t1:
                        st.markdown('<span class="help-icon">❓ Ayuda Contextual</span>', unsafe_allow_html=True)
                        st.write(f"""
                        **Interpretación:** El gráfico muestra cómo se reparten los valores de la variable `{sel_col}`. 
                        La línea KDE (Kernel Density Estimate) suaviza el histograma para identificar la forma de la distribución 
                        (Normal, Sesgada, Bimodal).
                        """)

                    st.divider()

                    # --- GRÁFICO 2: CORRELACIÓN ---
                    st.markdown("### 2. Matriz de Correlación de Pearson")
                    col_g2, col_t2 = st.columns([2, 1])
                    with col_g2:
                        fig2, ax2 = plt.subplots(figsize=(10, 8))
                        correlation_matrix = df[numeric_cols].corr()
                        sns.heatmap(correlation_matrix, annot=True, cmap="mako", fmt=".2f", ax=ax2)
                        st.pyplot(fig2)
                    with col_t2:
                        st.markdown('<span class="help-icon">❓ Ayuda Contextual</span>', unsafe_allow_html=True)
                        st.write("""
                        **Interpretación:** El Heatmap mide la relación lineal entre variables. 
                        - **1.0**: Correlación positiva perfecta.
                        - **-1.0**: Correlación negativa perfecta.
                        - **0**: Sin relación lineal.
                        Utilice esto para evitar la multicolinealidad en modelos.
                        """)

                    st.divider()

                    # --- GRÁFICO 3: RELACIÓN BIVARIADA ---
                    st.markdown("### 3. Gráfico de Dispersión con Regresión")
                    col_g3, col_t3 = st.columns([2, 1])
                    if len(numeric_cols) >= 2:
                        with col_g3:
                            cx, cy = st.columns(2)
                            var_x = cx.selectbox("Variable Eje X", numeric_cols, index=0)
                            var_y = cy.selectbox("Variable Eje Y", numeric_cols, index=1)
                            fig3, ax3 = plt.subplots(figsize=(10, 6))
                            sns.regplot(data=df, x=var_x, y=var_y, scatter_kws={'alpha':0.4}, line_kws={'color':'red'}, ax=ax3)
                            st.pyplot(fig3)
                        with col_t3:
                            st.markdown('<span class="help-icon">❓ Ayuda Contextual</span>', unsafe_allow_html=True)
                            st.write(f"""
                            **Interpretación:** Analiza la relación directa entre `{var_x}` y `{var_y}`. 
                            La línea roja representa la tendencia central (regresión lineal). La dispersión de los puntos 
                            indica la varianza del modelo.
                            """)
                else:
                    st.warning("El dataset no contiene suficientes columnas numéricas para el análisis estadístico.")

            with tab_doc:
                st.markdown("""
                ### Guía de Documentación Metodológica
                
                **1. Fuente de Datos:**
                Los datos son extraídos mediante la API de `kagglehub` del repositorio `corzogac/magdalena-colombia-data`.
                
                **2. Preparación de Datos:**
                - Se eliminan espacios en blanco en encabezados.
                - Se normalizan caracteres especiales y mayúsculas.
                - Se categorizan automáticamente las variables numéricas y de texto.
                
                **3. Estándares Visuales:**
                - Se utiliza la paleta de colores `mako` de Seaborn para una visualización profesional y accesible.
                - Se implementan `st.cache_data` para optimizar el rendimiento y evitar descargas repetitivas.
                
                **4. Requerimientos:**
                Asegúrese de tener instaladas las librerías listadas en `requirements.txt`.
                """)
        else:
            st.error("Error al cargar los datos. Por favor, verifica la conexión con Kaggle o los logs de la aplicación.")

if __name__ == "__main__":
    main()
