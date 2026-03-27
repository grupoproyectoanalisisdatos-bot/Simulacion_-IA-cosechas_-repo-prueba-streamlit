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
        # Descarga la última versión del dataset
        download_path = kagglehub.dataset_download("corzogac/magdalena-colombia-data")
        
        # Búsqueda profunda de archivos CSV en todas las subcarpetas
        files_found = []
        for root, dirs, files in os.walk(download_path):
            for file in files:
                if file.endswith(".csv"):
                    full_path = os.path.join(root, file)
                    files_found.append(full_path)
        
        if not files_found:
            # Si no hay CSV, intentamos listar qué archivos existen para depuración
            st.warning(f"No se encontraron archivos CSV en la ruta: {download_path}")
            return None
        
        # Seleccionamos el archivo con mayor tamaño (usualmente es el dataset principal)
        target_file = max(files_found, key=os.path.getsize)
        
        # Intentar leer con detección de errores de codificación (Colombian data often uses latin-1)
        try:
            df = pd.read_csv(target_file, encoding='utf-8')
        except (UnicodeDecodeError, Exception):
            df = pd.read_csv(target_file, encoding='latin-1')
            
        # Limpieza técnica de nombres de columnas: minúsculas, sin espacios, sin tildes
        df.columns = [
            str(c).lower().replace(' ', '_')
            .replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            .strip() for c in df.columns
        ]
        return df
    except Exception as e:
        st.error(f"Error crítico en la carga del dataset: {e}")
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
            
        # Intentar cargar los datos
        df = load_data_from_kaggle()
        
        if df is not None:
            st.sidebar.success("Dataset Vinculado Correctamente")
            tab_data, tab_viz, tab_docs = st.tabs(["🔍 Exploración de Datos", "📈 Análisis Gráfico", "📖 Documentación"])

            with tab_data:
                st.subheader("Visualización del Dataset Principal")
                st.dataframe(df.head(20), width='stretch')
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total de Registros", f"{df.shape[0]:,}")
                c2.metric("Columnas Detectadas", df.shape[1])
                c3.metric("Datos Faltantes", df.isna().sum().sum())
                
                st.divider()
                st.write("**Estadística Descriptiva Automática:**")
                st.write(df.describe())

            with tab_viz:
                sns.set_theme(style="darkgrid")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

                if numeric_cols:
                    # Gráfico 1: Histograma
                    st.markdown("### 1. Distribución y Densidad de Probabilidad")
                    g1_col, t1_col = st.columns([2, 1])
                    with g1_col:
                        var_sel = st.selectbox("Seleccione la variable a analizar", numeric_cols, key="s1")
                        fig1, ax1 = plt.subplots(figsize=(10, 5))
                        sns.histplot(df[var_sel], kde=True, color="#1e3a8a", ax=ax1)
                        ax1.set_title(f"Distribución: {var_sel}")
                        st.pyplot(fig1)
                    with t1_col:
                        st.markdown(f"""
                        <div class="help-card">
                        💡 <b>Análisis de {var_sel}:</b><br>
                        Este gráfico combina un histograma con un KDE (Kernel Density Estimate). 
                        Permite observar si los datos están sesgados o si presentan una distribución normal.
                        </div>
                        """, unsafe_allow_html=True)

                    st.divider()

                    # Gráfico 2: Heatmap de Correlación
                    st.markdown("### 2. Matriz de Correlación (Coeficiente de Pearson)")
                    g2_col, t2_col = st.columns([2, 1])
                    with g2_col:
                        fig2, ax2 = plt.subplots(figsize=(10, 8))
                        corr_matrix = df[numeric_cols].corr()
                        sns.heatmap(corr_matrix, annot=True, cmap="YlGnBu", fmt=".2f", ax=ax2)
                        st.pyplot(fig2)
                    with t2_col:
                        st.markdown("""
                        <div class="help-card">
                        💡 <b>Interpretación:</b><br>
                        Identifica relaciones lineales. Un valor cercano a <b>1.0</b> indica una relación proporcional directa fuerte, 
                        mientras que valores cercanos a <b>0</b> sugieren independencia estadística.
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("El dataset no contiene suficientes variables numéricas para el análisis gráfico.")

            with tab_docs:
                st.markdown("""
                ### Ficha Técnica del Proyecto
                - **Librerías Nucleares**: `seaborn` (Visualización), `pandas` (Estructura), `kagglehub` (Ingesta).
                - **Fuente de Datos**: Repositorio `corzogac/magdalena-colombia-data`.
                - **Procesamiento**: El sistema implementa una búsqueda recursiva de archivos para asegurar la carga incluso tras actualizaciones del dataset en origen.
                """)
        else:
            # Si df es None, mostramos un error más explicativo
            st.error("⚠️ El sistema no pudo procesar los datos.")
            st.info("Sugerencia: Revisa los logs de la consola en 'Manage App' para verificar si la descarga de Kaggle fue bloqueada o si el archivo está en un formato no soportado.")

if __name__ == "__main__":
    main()
