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

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    files = {
        "Temperatura": "Datos para la Base de Datos - Temperatura.csv",
        "Precipitación": "Datos para la Base de Datos - Precipitacion.csv",
        "Brillo Solar": "Datos para la Base de Datos - Brillo Solar.csv",
        "Producción": "Datos para la Base de Datos - Produccion.csv"
    }
    dfs = {}
    files_not_found = []
    
    for key, path in files.items():
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                # Limpieza de columnas (quitar los dos puntos ":")
                df.columns = [c.replace(':', '').strip() for c in df.columns]
                
                # Convertir 'Valor' a numérico si existe (manejo de puntos/comas)
                if 'Valor' in df.columns:
                    df['Valor'] = pd.to_numeric(df['Valor'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
                
                dfs[key] = df
            except Exception as e:
                st.error(f"Error al procesar {key}: {e}")
        else:
            files_not_found.append(path)
            
    return dfs, files_not_found

# --- LÓGICA DE NAVEGACIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def enter_dashboard():
    st.session_state.auth = True

# --- RENDERIZADO ---
dfs, missing = load_data()

# Validar si no hay datos cargados en absoluto
if not dfs:
    st.error("❌ No se encontraron archivos de datos.")
    st.info(f"Asegúrate de subir los archivos al repositorio: {', '.join(missing)}")
    st.stop()

if not st.session_state.auth:
    # --- LANDING PAGE ---
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown('<h1 class="main-title">Agro-Clima <br>Intelligence</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Plataforma avanzada de análisis predictivo y descriptivo para el sector agrícola y monitoreo climático regional.</p>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="landing-card">
                <h3>Sobre el Dataset</h3>
                <p>Este sistema integra variables de <b>Temperatura, Precipitación y Brillo Solar</b> junto con métricas de <b>Producción Agrícola</b> para identificar patrones de rendimiento y riesgo climático.</p>
                <ul>
                    <li>Análisis por Municipio</li>
                    <li>Correlación Clima-Cosecha</li>
                    <li>Distribuciones Estadísticas</li>
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
        
        # Selección segura del dataset
        options = list(dfs.keys())
        dataset_name = st.selectbox("Seleccione Dataset", options)
        
        if st.button("⬅ Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    # Acceso seguro al DataFrame
    df = dfs.get(dataset_name)
    
    if df is not None:
        # Tabs de navegación profesional
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

            # Gráficos con Seaborn
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            if numeric_cols:
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"**Distribución de Frecuencia** <span title='Muestra la densidad de los datos.' class='help-icon'>❓</span>", unsafe_allow_html=True)
                    var_sel = st.selectbox("Seleccione Variable", numeric_cols, key="v1")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.histplot(df[var_sel].dropna(), kde=True, color="#1e3a8a", ax=ax)
                    ax.set_title(f"Histograma de {var_sel}")
                    st.pyplot(fig)
                    st.info(f"ℹ️ **Explicación:** Identifica el sesgo de {var_sel} y detecta valores atípicos.")

                with col_b:
                    st.markdown(f"**Comportamiento por Municipio** <span title='Comparativa de medias.' class='help-icon'>❓</span>", unsafe_allow_html=True)
                    if 'Municipio' in df.columns:
                        top_10 = df.groupby('Municipio')[var_sel].mean().sort_values(ascending=False).head(10)
                        fig2, ax2 = plt.subplots(figsize=(10, 6))
                        sns.barplot(x=top_10.values, y=top_10.index, palette="viridis", ax=ax2)
                        ax2.set_title(f"Top 10 Municipios ({var_sel})")
                        st.pyplot(fig2)
                        st.info("ℹ️ **Explicación:** Muestra municipios con promedios más altos para la variable.")

                st.divider()

                if dataset_name == "Producción":
                    st.markdown(f"**Análisis de Rendimiento (Área vs Producción)** <span title='Correlación.' class='help-icon'>❓</span>", unsafe_allow_html=True)
                    fig3, ax3 = plt.subplots(figsize=(12, 5))
                    # Asegurar que no haya nulos para el gráfico de regresión
                    df_plot = df[['Area Sembrada', 'Produccion']].dropna()
                    sns.regplot(data=df_plot, x='Area Sembrada', y='Produccion', scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax3)
                    st.pyplot(fig3)
                    st.info("ℹ️ **Explicación:** La línea roja indica la tendencia central del rendimiento.")

        with tab2:
            st.subheader("Raw Data Inspection")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar este conjunto de datos", df.to_csv(index=False), f"{dataset_name}.csv", "text/csv")

        with tab3:
            st.markdown(f"""
            <div class="doc-section">
                <h3>📖 Documentación: {dataset_name}</h3>
                <p>Este dataset contiene información recolectada de estaciones regionales y reportes municipales.</p>
                <hr>
                <h4>Metodología de Análisis:</h4>
                <ul>
                    <li><b>Tratamiento de Datos:</b> Se han limpiado caracteres especiales en cabeceras y normalizado formatos numéricos.</li>
                    <li><b>Validación:</b> Los cálculos omiten automáticamente valores nulos (NaN).</li>
                    <li><b>Herramientas:</b> Visualizaciones optimizadas con Seaborn para entornos científicos.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Panel de Inteligencia de Datos v2.1 | Desarrollado por Expert Data Analyst")
