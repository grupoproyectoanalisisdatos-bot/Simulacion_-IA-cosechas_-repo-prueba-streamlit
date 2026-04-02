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

# --- FUNCIÓN DE LIMPIEZA PROFUNDA (Solución a DuplicateError: 'Valor:' y 'anio') ---
def clean_dataframe_columns(df):
    """
    Limpia nombres de columnas eliminando caracteres especiales y forzando unicidad.
    Esto soluciona el DuplicateError reportado en los logs para 'Valor:' y 'anio'.
    """
    # 1. Limpieza inicial de nombres (quitar espacios, dos puntos y convertir a minúsculas)
    clean_names = []
    for col in df.columns:
        # Convertimos a string, quitamos espacios y caracteres como ':'
        name = str(col).strip().replace(':', '').replace('.', '')
        clean_names.append(name if name else "columna_sin_nombre")
    
    # 2. Forzar Unicidad Estricta (Case-insensitive)
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
    
    # 3. Eliminar columnas totalmente vacías
    df = df.dropna(how='all', axis=1)
    
    # 4. Normalización de Tipos para PyArrow
    for col in df.columns:
        # Intentar numérico
        converted_num = pd.to_numeric(df[col], errors='coerce')
        if not converted_num.isna().all():
            df[col] = converted_num
        else:
            # Si es texto, limpiar nulos raros para evitar fallos en Arrow
            df[col] = df[col].astype(str).replace(['nan', 'None', 'NaT', 'None'], np.nan)
    
    return df

# --- CARGA DE DATOS RESILIENTE ---
@st.cache_data(ttl=600)
def load_data():
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            # openpyxl es necesario para .xlsx
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
    # Sidebar: Selección de Hoja
    with st.sidebar:
        st.header("⚙️ Configuración")
        selected_sheet = st.selectbox("Seleccionar Tabla", list(dfs.keys()))
        df = dfs[selected_sheet]
        st.success(f"Columnas procesadas: {len(df.columns)}")

    # Clasificación de columnas para UI
    # Buscamos 'valor' en todas sus variantes limpias
    val_cols = [c for c in df.columns if 'valor' in c.lower()]
    geo_cols = [c for c in df.columns if any(x in c.lower() for x in ['lat', 'lon'])]
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns.tolist() if c not in geo_cols]

    tab1, tab2, tab3 = st.tabs(["🎯 Análisis", "🌍 Mapa", "📄 Datos"])

    with tab1:
        if len(num_cols) >= 2:
            c1, c2 = st.columns(2)
            v1 = c1.selectbox("Variable X", num_cols, index=0)
            v2 = c2.selectbox("Variable Y", num_cols, index=len(num_cols)-1)
            
            plot_df = df.dropna(subset=[v1, v2])
            if not plot_df.empty:
                fig = px.scatter(plot_df, x=v1, y=v2, trendline="ols", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos suficientes para graficar.")
        else:
            st.info("Se requieren al menos 2 columnas numéricas para el análisis de relaciones.")

    with tab2:
        lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
        lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)
        
        if lat_col and lon_col and num_cols:
            target = st.selectbox("Indicador Visual", num_cols)
            map_df = df.dropna(subset=[lat_col, lon_col, target])
            if not map_df.empty:
                fig_map = px.scatter_mapbox(
                    map_df, lat=lat_col, lon=lon_col, color=target, size=target,
                    mapbox_style="carto-positron", zoom=5, height=600
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.error("Los datos de coordenadas o valores están vacíos.")
        else:
            st.warning("No se detectaron columnas de Latitud/Longitud para el mapa.")

    with tab3:
        st.subheader("Explorador de Datos (Limpio)")
        st.dataframe(df, use_container_width=True)

st.divider()
st.caption("Corrección aplicada para duplicados de 'Valor:' y 'anio'.")
