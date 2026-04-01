import streamlit as st
import pandas as pd
import numpy as np
import os

# --- PRE-FLIGHT CHECK: IMPORTACIÓN DE LIBRERÍAS ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    st.error("⚠️ Error Crítico: La librería 'plotly' no está instalada.")
    st.info("Por favor, asegúrate de que tu archivo 'requirements.txt' contenga la palabra: plotly")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Data Intelligence - Agro Analítica",
    page_icon="📊",
    layout="wide"
)

# --- FUNCIÓN DE LIMPIEZA DE COLUMNAS (Solución al DuplicateError: 'anio') ---
def clean_dataframe_columns(df):
    """
    Detecta columnas duplicadas y las renombra (ej. 'anio', 'anio' -> 'anio', 'anio_1')
    Esto evita el DuplicateError reportado en los logs.
    """
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols == dup] = [f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    # Eliminar columnas totalmente vacías
    df = df.dropna(how='all', axis=1)
    return df

# --- CARGA DE DATOS RESILIENTE ---
@st.cache_data(ttl=600)
def load_data():
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            excel_data = pd.ExcelFile(excel_file)
            dfs = {}
            for sheet in excel_data.sheet_names:
                raw_df = pd.read_excel(excel_file, sheet_name=sheet)
                # Aplicar desinfección de columnas inmediatamente
                dfs[sheet] = clean_dataframe_columns(raw_df)
            return dfs, None
        except Exception as e:
            return None, f"Error al procesar el Excel: {e}"
    return None, f"Archivo '{excel_file}' no encontrado en el repositorio."

# --- INTERFAZ DE USUARIO ---
st.title("📊 Inteligencia de Datos Agrícolas")
st.markdown("Solución avanzada para el análisis de relaciones clima-cosecha.")

dfs, error = load_data()

if error:
    st.error(error)
    st.info("Sugerencia: Verifica que el nombre del archivo Excel sea exactamente 'Datos  Base de Datos.xlsx'.")
else:
    # Sidebar: Selección de Hoja
    with st.sidebar:
        st.header("⚙️ Configuración")
        selected_sheet = st.selectbox("Seleccionar Tabla", list(dfs.keys()))
        df = dfs[selected_sheet]
        st.success(f"Columnas procesadas correctamente.")

    # Identificación de Columnas Especiales
    # Se identifican para excluirlas de análisis estadísticos pero usarlas en mapas
    geo_cols = [c for c in df.columns if any(x in c.lower() for x in ['latitud', 'longitud', 'lat', 'lon'])]
    num_cols_analysis = [c for c in df.select_dtypes(include=[np.number]).columns.tolist() if c not in geo_cols]

    # Tabs de Análisis
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Análisis de Relaciones", "🌍 Mapa Geográfico", "📊 Distribución", "📄 Datos Crudos"])

    with tab1:
        st.subheader("Investigación de Factores Críticos")
        
        if len(num_cols_analysis) >= 2:
            col_ctrl1, col_ctrl2 = st.columns(2)
            with col_ctrl1:
                var_x = st.selectbox("Variable Causa (X)", num_cols_analysis, index=0)
            with col_ctrl2:
                var_y = st.selectbox("Variable Efecto (Y)", num_cols_analysis, index=len(num_cols_analysis)-1)

            # Gráfico de Dispersión con Regresión
            fig_rel = px.scatter(
                df, x=var_x, y=var_y, 
                trendline="ols", 
                title=f"Correlación: {var_x} vs {var_y}",
                template="plotly_white",
                color_discrete_sequence=["#1e3a8a"]
            )
            st.plotly_chart(fig_rel, use_container_width=True)
            
            st.info("💡 **Análisis de Experto:** Las coordenadas geográficas han sido excluidas de este análisis correlacional para evitar sesgos, tratándolas exclusivamente como datos de ubicación.")
        else:
            st.warning("La tabla seleccionada no tiene suficientes variables numéricas (excluyendo coordenadas) para este análisis.")

    with tab2:
        st.subheader("Visualización Espacial de Datos")
        
        # Verificar si existen columnas de coordenadas
        lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
        lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)
        
        if lat_col and lon_col:
            st.markdown("Uso correcto de coordenadas para georreferenciación:")
            map_var = st.selectbox("Variable a visualizar en mapa", num_cols_analysis)
            
            # Limpiar datos para el mapa
            map_df = df.dropna(subset=[lat_col, lon_col, map_var])
            
            fig_map = px.scatter_mapbox(
                map_df, lat=lat_col, lon=lon_col, 
                color=map_var, size=map_var,
                color_continuous_scale=px.colors.cyclical.IceFire,
                size_max=15, zoom=6,
                mapbox_style="carto-positron",
                title=f"Distribución Geográfica de {map_var}"
            )
            fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No se detectaron columnas de Latitud/Longitud en esta hoja para generar el mapa.")

    with tab3:
        st.subheader("Diagnóstico de Variabilidad")
        if num_cols_analysis:
            target_var = st.selectbox("Seleccionar Variable para Histograma", num_cols_analysis)
            fig_hist = px.histogram(
                df, x=target_var, 
                marginal="box", 
                title=f"Distribución y Outliers de {target_var}",
                color_discrete_sequence=["#15803d"]
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    with tab4:
        st.subheader("Explorador de Registros")
        st.dataframe(df, use_container_width=True)

st.divider()
st.caption("Fix: Geo-Aware Data Processing Enabled | Plotly Rendering Engine v2.1")
