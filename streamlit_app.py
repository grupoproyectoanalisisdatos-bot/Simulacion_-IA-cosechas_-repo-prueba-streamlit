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

# --- FUNCIÓN DE LIMPIEZA PROFUNDA ---
def clean_dataframe_columns(df):
    """
    Limpia nombres de columnas eliminando caracteres especiales y forzando unicidad.
    """
    clean_names = []
    for col in df.columns:
        name = str(col).strip().replace(':', '').replace('.', '')
        clean_names.append(name if name else "columna_sin_nombre")
    
    final_cols = []
    counts = {}
    for name in clean_names:
        low_name = name.lower()
        if low_name in counts:
            counts[low_name] += 1
            final_cols.append(f"{name}_{counts[low_name]}")
        else:
            counts[low_name] = 0
            final_cols.append(name)
            
    df.columns = final_cols
    df = df.dropna(how='all', axis=1)
    
    for col in df.columns:
        # Intentar convertir a fecha si el nombre sugiere tiempo
        if any(x in col.lower() for x in ['fecha', 'date', 'periodo']):
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Intentar numérico
        converted_num = pd.to_numeric(df[col], errors='coerce')
        if not converted_num.isna().all():
            df[col] = converted_num
        else:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str).replace(['nan', 'None', 'NaT'], np.nan)
    
    return df

# --- CARGA DE DATOS RESILIENTE ---
@st.cache_data(ttl=600)
def load_data():
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            excel_data = pd.ExcelFile(excel_file, engine='openpyxl')
            dfs = {}
            for sheet in excel_data.sheet_names:
                raw_df = pd.read_excel(excel_file, sheet_name=sheet)
                dfs[sheet] = clean_dataframe_columns(raw_df)
            return dfs, None
        except Exception as e:
            return None, f"Error al procesar el Excel: {e}"
    return None, f"Archivo '{excel_file}' no encontrado."

# --- INTERFAZ DE USUARIO ---
st.title("📊 Inteligencia de Datos Agrícolas")
st.markdown("Análisis avanzado de variables climáticas y productivas.")

dfs, error = load_data()

if error:
    st.error(error)
else:
    with st.sidebar:
        st.header("⚙️ Configuración")
        selected_sheet = st.selectbox("Seleccionar Tabla", list(dfs.keys()))
        df = dfs[selected_sheet]
        st.success(f"Columnas procesadas: {len(df.columns)}")

    # Clasificación de columnas para UI
    date_cols = df.select_dtypes(include=['datetime64', 'datetime']).columns.tolist()
    # Si no hay columnas de tipo datetime, buscar nombres que sugieran fechas (anio, mes)
    if not date_cols:
        date_cols = [c for c in df.columns if any(x in c.lower() for x in ['fecha', 'anio', 'mes', 'periodo'])]
        
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Excluir latitud y longitud de los análisis de tendencia
    geo_keywords = ['lat', 'lon', 'latitud', 'longitud']
    num_cols = [c for c in num_cols if not any(k in c.lower() for k in geo_keywords)]

    tab1, tab2, tab3 = st.tabs(["🎯 Análisis Temporal", "🌍 Mapa", "📄 Datos Raw"])

    with tab1:
        st.subheader("Análisis de Tendencias")
        if len(num_cols) > 0:
            c1, c2 = st.columns(2)
            
            # Selección de Eje X (Tiempo)
            if date_cols:
                x_axis = c1.selectbox("Eje Temporal (X)", date_cols)
            else:
                x_axis = c1.selectbox("Eje X (Numérico)", num_cols)
            
            # Selección de Variable (Temperatura, Valor, etc)
            # Intentar pre-seleccionar 'Valor' o 'Temperatura' si existen
            default_y = 0
            for i, col in enumerate(num_cols):
                if any(x in col.lower() for x in ['valor', 'temp', 'precip']):
                    default_y = i
                    break
            y_axis = c2.selectbox("Variable de Análisis (Y)", num_cols, index=default_y)
            
            plot_df = df.dropna(subset=[x_axis, y_axis]).sort_values(by=x_axis)
            
            if not plot_df.empty:
                # Gráfico de línea para series temporales
                if x_axis in date_cols:
                    fig = px.line(plot_df, x=x_axis, y=y_axis, markers=True, 
                                 title=f"Evolución de {y_axis} en el tiempo",
                                 template="plotly_white", color_discrete_sequence=['#1e3a8a'])
                else:
                    fig = px.scatter(plot_df, x=x_axis, y=y_axis, trendline="ols",
                                    title=f"Relación entre {x_axis} y {y_axis}",
                                    template="plotly_white")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos válidos para la combinación seleccionada.")
        else:
            st.info("No se encontraron columnas numéricas para graficar.")

    with tab2:
        lat_col = next((c for c in df.columns if any(k in c.lower() for k in ['lat', 'latitud'])), None)
        lon_col = next((c for c in df.columns if any(k in c.lower() for k in ['lon', 'longitud'])), None)
        
        if lat_col and lon_col and num_cols:
            target = st.selectbox("Indicador Visual (Mapa)", num_cols)
            map_df = df.dropna(subset=[lat_col, lon_col, target])
            if not map_df.empty:
                fig_map = px.scatter_mapbox(
                    map_df, lat=lat_col, lon=lon_col, color=target, size=target,
                    mapbox_style="carto-positron", zoom=5, height=600,
                    title=f"Distribución Geográfica de {target}"
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.error("Datos geográficos insuficientes.")
        else:
            st.warning("Se requieren columnas de Latitud y Longitud para el mapa.")

    with tab3:
        st.subheader("Explorador de Datos")
        st.dataframe(df, use_container_width=True)

st.divider()
st.caption("Estructura mejorada: Análisis enfocado en series temporales y relación fecha-valor.")
