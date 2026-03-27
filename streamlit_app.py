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
    .error-box { background-color: #fee2e2; border: 1px solid #ef4444; padding: 15px; border-radius: 8px; color: #b91c1c; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner="Accediendo a Kaggle y procesando archivos...")
def load_data_from_kaggle():
    """Descarga el dataset y busca archivos CSV de forma recursiva con diagnóstico."""
    try:
        # Descarga la última versión del dataset
        # El dataset corzogac/magdalena-colombia-data parece descargarse como una carpeta
        download_path = kagglehub.dataset_download("corzogac/magdalena-colombia-data")
        
        # Búsqueda profunda de archivos CSV en todas las subcarpetas
        files_found = []
        all_detected_files = [] # Para diagnóstico
        
        for root, dirs, files in os.walk(download_path):
            for file in files:
                full_path = os.path.join(root, file)
                all_detected_files.append(file)
                if file.lower().endswith(".csv"):
                    files_found.append(full_path)
        
        if not files_found:
            # Si no hay CSV, informamos qué se encontró para ayudar al usuario
            st.session_state['debug_files'] = all_detected_files
            st.session_state['debug_path'] = download_path
            return None
        
        # Seleccionamos el archivo con mayor tamaño (usualmente el dataset principal)
        target_file = max(files_found, key=os.path.getsize)
        
        # Intentar leer con detección de errores de codificación
        try:
            # Primero intentamos con separador automático (coma o punto y coma)
            df = pd.read_csv(target_file, sep=None, engine='python', encoding='utf-8')
        except Exception:
            try:
                df = pd.read_csv(target_file, sep=None, engine='python', encoding='latin-1')
            except Exception as e:
                st.error(f"No se pudo decodificar el archivo CSV: {e}")
                return None
            
        # Limpieza técnica de nombres de columnas
        df.columns = [
            str(c).lower().replace(' ', '_')
            .replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            .strip() for c in df.columns
        ]
        return df
    except Exception as e:
        st.error(f"Error crítico en la comunicación con Kaggle: {e}")
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
            
            st.info("**Nivel Integrador:** Este panel utiliza inteligencia de datos para monitorear la cuenca más importante de Colombia.")
            
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
            st.write("**Servidor:** Streamlit Cloud")
            st.write("**Estado:** Ejecutando diagnóstico")
            
        # Intentar cargar los datos
        df = load_data_from_kaggle()
        
        if df is not None:
            st.sidebar.success("✅ Dataset Vinculado")
            tab_data, tab_viz, tab_docs = st.tabs(["🔍 Exploración de Datos", "📈 Análisis Gráfico", "📖 Documentación"])

            with tab_data:
                st.subheader("Vista Previa del Dataset")
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
                    st.markdown("### 1. Distribución de Frecuencia")
                    g1_col, t1_col = st.columns([2, 1])
                    with g1_col:
                        var_sel = st.selectbox("Seleccione Variable", numeric_cols, key="s1")
                        fig1, ax1 = plt.subplots(figsize=(10, 5))
                        sns.histplot(df[var_sel], kde=True, color="#1e3a8a", ax=ax1)
                        ax1.set_title(f"Distribución de {var_sel}")
                        st.pyplot(fig1)
                    with t1_col:
                        st.markdown(f'<div class="help-card">💡 <b>Análisis:</b> La curva KDE muestra la densidad de los datos. Útil para detectar valores atípicos en la cuenca del Magdalena.</div>', unsafe_allow_html=True)

                    st.divider()

                    st.markdown("### 2. Correlaciones Detectadas")
                    g2_col, t2_col = st.columns([2, 1])
                    with g2_col:
                        fig2, ax2 = plt.subplots(figsize=(10, 8))
                        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="mako", fmt=".2f", ax=ax2)
                        st.pyplot(fig2)
                    with t2_col:
                        st.markdown('<div class="help-card">💡 <b>Interpretación:</b> Colores más claros indican una correlación positiva alta entre factores ambientales o socioeconómicos.</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay suficientes datos numéricos para procesar gráficos.")

            with tab_docs:
                st.markdown("""
                ### Ficha Metodológica
                - **Ingesta**: Automatizada vía `kagglehub`.
                - **Limpieza**: Normalización de cabeceras y manejo de encoding Latin-1/UTF-8.
                - **Despliegue**: Optimizado para Streamlit Cloud 1.30+.
                """)
        else:
            # SECCIÓN DE DIAGNÓSTICO SI FALLA LA CARGA
            st.markdown('<div class="error-box">⚠️ Error de Lectura: No se detectaron archivos CSV válidos.</div>', unsafe_allow_html=True)
            
            with st.expander("🛠 Ver Diagnóstico Técnico"):
                if 'debug_path' in st.session_state:
                    st.write(f"**Ruta de descarga:** `{st.session_state['debug_path']}`")
                if 'debug_files' in st.session_state:
                    st.write("**Archivos encontrados en la carpeta:**")
                    st.write(st.session_state['debug_files'])
                else:
                    st.write("No se pudo listar ningún archivo. Es posible que la descarga fallara silenciosamente.")
            
            st.info("Sugerencia: Si ves archivos con extensión `.zip` o `.archive` en el diagnóstico, avísame para implementar un descompresor automático.")

if __name__ == "__main__":
    main()
