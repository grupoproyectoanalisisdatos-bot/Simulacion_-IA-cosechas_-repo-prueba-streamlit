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

# --- FUNCIÓN DE LIMPIEZA DE COLUMNAS Y TIPOS (Solución a DuplicateError y ArrowInvalid) ---
def clean_dataframe_columns(df):
    """
    1. Detecta y renombra columnas duplicadas para evitar DuplicateError.
    2. Elimina columnas totalmente vacías.
    3. Normaliza tipos de datos para compatibilidad con PyArrow (Streamlit).
    """
    # Solución al DuplicateError: Renombrar duplicados de forma única
    new_cols = []
    counts = {}
    for col in df.columns:
        col_name = str(col).strip()
        if col_name in counts:
            counts[col_name] += 1
            new_cols.append(f"{col_name}_{counts[col_name]}")
        else:
            counts[col_name] = 0
            new_cols.append(col_name)
    df.columns = new_cols
    
    # Eliminar columnas totalmente vacías que suelen venir de Excel
    df = df.dropna(how='all', axis=1)
    
    # Convertir columnas para evitar errores de tipos mixtos en Arrow (PyArrow)
    for col in df.columns:
        # Intentar convertir a numérico si es posible
        converted_num = pd.to_numeric(df[col], errors='coerce')
        # Si la columna no queda vacía tras la conversión y no era puramente texto, aplicamos
        if not converted_num.isna().all():
            df[col] = converted_num
        else:
            # Si es texto, asegurar que sea string limpio sin valores nulos extraños
            df[col] = df[col].astype(str).replace(['nan', 'None', 'NAT'], np.nan)
    
    return df

# --- CARGA DE DATOS RESILIENTE ---
@st.cache_data(ttl=600)
def load_data():
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            # Usar engine='openpyxl' para mayor compatibilidad con .xlsx
            excel_data = pd.ExcelFile(excel_file, engine='openpyxl')
            dfs = {}
            for sheet in excel_data.sheet_names:
                raw_df = pd.read_excel(excel_file, sheet_name=sheet)
                # Aplicar desinfección profunda
                dfs[sheet] = clean_dataframe_columns(raw_df)
            return dfs, None
        except Exception as e:
            return None, f"Error al procesar el Excel: {e}"
    return None, f"Archivo '{excel_file}' no encontrado en el repositorio."

# --- INTERFAZ DE USUARIO ---
st.title("📊 Inteligencia de Datos Agrícolas")
st.markdown("Plataforma de análisis geoespacial y estadístico para el sector agropecuario.")

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
        st.success(f"Datos normalizados: {df.shape[0]} registros.")

    # Identificación de Columnas Especiales (Georeferenciación vs Análisis)
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

            # Limpiar nulos para el gráfico de dispersión
            plot_df = df.dropna(subset=[var_x, var_y])

            if not plot_df.empty:
                fig_rel = px.scatter(
                    plot_df, x=var_x, y=var_y, 
                    trendline="ols", 
                    title=f"Correlación: {var_x} vs {var_y}",
                    template="plotly_white",
                    color_discrete_sequence=["#1e3a8a"]
                )
                st.plotly_chart(fig_rel, use_container_width=True)
                st.info("💡 **Nota técnica:** Las coordenadas se usan solo para ubicación y se omiten de las regresiones lineales.")
            else:
                st.warning("No hay suficientes datos válidos para generar la correlación.")
        else:
            st.warning("La tabla no tiene suficientes variables numéricas para el análisis.")

    with tab2:
        st.subheader("Ubicación y Georeferenciación")
        
        lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
        lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)
        
        if lat_col and lon_col:
            map_var = st.selectbox("Indicador a mapear", num_cols_analysis)
            
            # Limpieza estricta de coordenadas para el mapa
            map_df = df.copy()
            map_df[lat_col] = pd.to_numeric(map_df[lat_col], errors='coerce')
            map_df[lon_col] = pd.to_numeric(map_df[lon_col], errors='coerce')
            map_df = map_df.dropna(subset=[lat_col, lon_col, map_var])
            
            if not map_df.empty:
                fig_map = px.scatter_mapbox(
                    map_df, lat=lat_col, lon=lon_col, 
                    color=map_var, size=map_var,
                    color_continuous_scale=px.colors.sequential.Viridis,
                    size_max=15, zoom=5,
                    mapbox_style="carto-positron",
                    title=f"Distribución Geográfica: {map_var}"
                )
                fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No hay coordenadas válidas para mostrar en el mapa.")
        else:
            st.info("Esta hoja no contiene datos de Latitud/Longitud detectables.")

    with tab3:
        st.subheader("Diagnóstico de Distribución")
        if num_cols_analysis:
            target_var = st.selectbox("Seleccionar Variable", num_cols_analysis)
            clean_hist_df = df.dropna(subset=[target_var])
            fig_hist = px.histogram(
                clean_hist_df, x=target_var, 
                marginal="box", 
                title=f"Histograma de {target_var}",
                color_discrete_sequence=["#15803d"]
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    with tab4:
        st.subheader("Explorador de Registros")
        # st.dataframe es sensible a nombres duplicados y tipos mixtos, 
        # pero con clean_dataframe_columns ya debería ser seguro.
        st.dataframe(df, use_container_width=True)

st.divider()
st.caption("Fix: Unicidad de Columnas & Compatibilidad Arrow v3.0 | 2026")
