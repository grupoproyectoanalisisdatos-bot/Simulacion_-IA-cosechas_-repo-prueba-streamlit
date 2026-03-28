import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Data Intelligence - Agro Clima",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PROFESIONALES (CSS) ---
st.markdown("""
    <style>
    /* Estilo General */
    .main { background-color: #f4f7f9; }
    .stApp { background-image: linear-gradient(0deg, #f4f7f9 0%, #ffffff 100%); }
    
    /* Landing Page */
    .landing-card {
        background: white; padding: 2rem; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-left: 8px solid #1e3a8a;
    }
    .main-title { color: #1e3a8a; font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; }
    .sub-title { color: #64748b; font-size: 1.2rem; margin-bottom: 2rem; }
    
    /* Ayuda e Iconos */
    .help-icon { color: #3b82f6; cursor: help; font-size: 0.9rem; margin-left: 5px; }
    .doc-section { background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS (ACTUALIZADO PARA EXCEL) ---
@st.cache_data
def load_data():
    # El archivo en el repositorio es un .xlsx
    excel_file = "Datos  Base de Datos.xlsx"
    dfs = {}
    
    if os.path.exists(excel_file):
        try:
            # Cargamos todas las hojas del Excel
            excel_data = pd.ExcelFile(excel_file)
            for sheet_name in excel_data.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Limpieza de columnas (quitar espacios y caracteres extraños)
                df.columns = [c.replace(':', '').strip() for c in df.columns]
                
                # Normalización de la columna 'Valor' si existe
                if 'Valor' in df.columns:
                    df['Valor'] = pd.to_numeric(df['Valor'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
                
                dfs[sheet_name] = df
            return dfs, None
        except Exception as e:
            return {}, f"Error al procesar el Excel: {e}"
    else:
        return {}, f"No se encontró el archivo: {excel_file}"

# --- LÓGICA DE NAVEGACIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def enter_dashboard():
    st.session_state.auth = True

# --- RENDERIZADO ---
dfs, error_msg = load_data()

# Validar errores de carga
if not dfs:
    st.error(f"❌ Error en la base de datos.")
    st.info(error_msg if error_msg else "El repositorio no contiene datos válidos.")
    st.stop()

if not st.session_state.auth:
    # --- LANDING PAGE ---
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown('<h1 class="main-title">Agro-Clima <br>Intelligence</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Plataforma avanzada de análisis predictivo y descriptivo para el sector agrícola.</p>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="landing-card">
                <h3>Sobre el Dataset</h3>
                <p>Análisis integrado de variables climáticas y de producción extraídas de la base de datos oficial.</p>
                <ul>
                    <li>Lectura automatizada de hojas de Excel</li>
                    <li>Normalización de métricas municipales</li>
                    <li>Visualización estadística en tiempo real</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        st.button("🚀 Ingresar al Panel de Trabajo", on_click=enter_dashboard, type="primary", use_container_width=True)

    with col2:
        st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80", 
                 caption="Tecnología Aplicada al Campo", use_container_width=True)

else:
    # --- DASHBOARD PANEL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2610/2610098.png", width=100)
        st.title("Data Expert Panel")
        
        # Selección segura del dataset basado en las hojas del Excel
        options = list(dfs.keys())
        dataset_name = st.selectbox("Seleccione Dataset (Hoja)", options)
        
        if st.button("⬅ Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Acceso seguro al DataFrame
    df = dfs.get(dataset_name)
    
    if df is not None:
        tab1, tab2, tab3 = st.tabs(["📊 Visualización Crítica", "📄 Exploración de Datos", "📖 Documentación Técnica"])

        with tab1:
            st.subheader(f"Análisis Avanzado: {dataset_name}")
            
            # Métricas principales
            m1, m2, m3 = st.columns(3)
            m1.metric("Registros Totales", f"{len(df):,}")
            m2.metric("Municipios", len(df['Municipio'].unique()) if 'Municipio' in df.columns else "N/A")
            
            if 'Valor' in df.columns:
                val_mean = df['Valor'].mean()
                m3.metric("Promedio General", f"{val_mean:.2f}" if not np.isnan(val_mean) else "N/A")

            st.divider()

            # Identificar columnas numéricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            if numeric_cols:
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"**Distribución de Frecuencia**", unsafe_allow_html=True)
                    var_sel = st.selectbox("Seleccione Variable", numeric_cols, key="v1")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.histplot(df[var_sel].dropna(), kde=True, color="#1e3a8a", ax=ax)
                    ax.set_title(f"Histograma de {var_sel}")
                    st.pyplot(fig)

                with col_b:
                    st.markdown(f"**Análisis Geográfico (Top 10)**", unsafe_allow_html=True)
                    if 'Municipio' in df.columns:
                        top_10 = df.groupby('Municipio')[var_sel].mean().sort_values(ascending=False).head(10)
                        fig2, ax2 = plt.subplots(figsize=(10, 6))
                        sns.barplot(x=top_10.values, y=top_10.index, palette="viridis", ax=ax2)
                        ax2.set_title(f"Media de {var_sel} por Municipio")
                        st.pyplot(fig2)

        with tab2:
            st.subheader("Inspección de Datos")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar CSV", df.to_csv(index=False), f"{dataset_name}.csv", "text/csv")

        with tab3:
            st.markdown(f"""
            <div class="doc-section">
                <h3>📖 Documentación del Dataset</h3>
                <p>Fuente: <i>Datos  Base de Datos.xlsx</i></p>
                <p>Hoja actual: <b>{dataset_name}</b></p>
                <hr>
                <h4>Ajustes Realizados:</h4>
                <ul>
                    <li>Conversión automática de tipos de datos.</li>
                    <li>Soporte para múltiples hojas de cálculo.</li>
                    <li>Manejo de errores para archivos inexistentes.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Panel de Inteligencia de Datos v2.2 | Basado en Repositorio GitHub")
