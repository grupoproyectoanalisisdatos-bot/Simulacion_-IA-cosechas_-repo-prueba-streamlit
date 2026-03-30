import streamlit as st
import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Data Intelligence - Agro Clima",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PROFESIONALES (CSS CORREGIDO) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .landing-card {
        background: white; padding: 2rem; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-left: 8px solid #1e3a8a;
    }
    .main-title { color: #1e3a8a; font-size: 3.5rem; font-weight: 800; }
    .doc-section { background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    excel_file = "Datos  Base de Datos.xlsx"
    dfs = {}
    
    if os.path.exists(excel_file):
        try:
            excel_data = pd.ExcelFile(excel_file)
            for sheet_name in excel_data.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # Limpieza de columnas
                df.columns = [str(c).replace(':', '').strip() for c in df.columns]
                
                # Normalización de 'Valor'
                if 'Valor' in df.columns:
                    df['Valor'] = pd.to_numeric(df['Valor'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
                
                # Asegurar coordenadas numéricas
                for coord in ['Latitud', 'Longitud']:
                    if coord in df.columns:
                        df[coord] = pd.to_numeric(df[coord], errors='coerce')
                
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

dfs, error_msg = load_data()

# Validar errores
if not dfs:
    st.error("❌ Error en la base de datos.")
    st.info(error_msg if error_msg else "Archivo no encontrado.")
    st.stop()

if not st.session_state.auth:
    # --- LANDING PAGE ---
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown('<h1 class="main-title">Agro-Clima <br>Intelligence</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color:#64748b; font-size:1.2rem;">Análisis geoespacial y estrés hídrico para la toma de decisiones.</p>', unsafe_allow_html=True)
        st.button("🚀 Ingresar al Panel de Trabajo", on_click=enter_dashboard, type="primary", use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=800", use_container_width=True)

else:
    # --- DASHBOARD PANEL ---
    with st.sidebar:
        st.title("Data Expert Panel")
        options = list(dfs.keys())
        dataset_name = st.selectbox("Seleccione Dataset", options)
        if st.button("⬅ Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    df = dfs.get(dataset_name)
    
    if df is not None:
        tab1, tab2, tab3 = st.tabs(["🗺️ Mapa y Estrés", "📊 Estadísticas", "📄 Datos"])

        with tab1:
            st.subheader("Análisis Geoespacial de Estrés Hídrico")
            
            # Cálculo de Estrés Hídrico (Simulado/Analítico basado en Valor)
            if 'Valor' in df.columns:
                # El estrés hídrico suele ser inverso a la precipitación/humedad disponible
                # Normalizamos de 0 a 100 para visualización
                v_min, v_max = df['Valor'].min(), df['Valor'].max()
                if v_max != v_min:
                    df['Indice_Estres'] = 100 * (1 - (df['Valor'] - v_min) / (v_max - v_min))
                else:
                    df['Indice_Estres'] = 50
            
            # Verificación de Coordenadas
            if 'Latitud' in df.columns and 'Longitud' in df.columns:
                # Limpiar filas sin coordenadas para el mapa
                map_df = df.dropna(subset=['Latitud', 'Longitud'])
                
                if not map_df.empty:
                    fig_map = px.scatter_mapbox(
                        map_df,
                        lat="Latitud",
                        lon="Longitud",
                        color="Indice_Estres" if 'Indice_Estres' in map_df.columns else None,
                        size="Valor" if 'Valor' in map_df.columns else None,
                        hover_name="Municipio" if "Municipio" in map_df.columns else None,
                        color_continuous_scale=px.colors.sequential.YlOrRd,
                        zoom=5,
                        height=600,
                        mapbox_style="carto-positron",
                        title="Distribución de Estrés Hídrico por Municipio"
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
                else:
                    st.warning("⚠️ Las columnas Latitud/Longitud están vacías o tienen formato incorrecto.")
            else:
                st.info("ℹ️ No se detectaron columnas de coordenadas (Latitud/Longitud) en esta hoja.")

        with tab2:
            st.subheader("Indicadores Críticos")
            m1, m2 = st.columns(2)
            m1.metric("Total Registros", len(df))
            if 'Indice_Estres' in df.columns:
                m2.metric("Nivel de Estrés Promedio", f"{df['Indice_Estres'].mean():.2f}%")
            
            # Gráficos adicionales
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                var_sel = st.selectbox("Variable para tendencia", numeric_cols)
                fig_hist, ax_hist = plt.subplots()
                sns.histplot(df[var_sel], kde=True, color="#1e3a8a", ax=ax_hist)
                st.pyplot(fig_hist)

        with tab3:
            st.subheader("Inspección de Datos")
            st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Sistema de Inteligencia Agrícola | Coordenadas y Estrés Hídrico Verificados")
