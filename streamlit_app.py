import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Sistema de Monitoreo de Estrés Hídrico",
    page_icon="🌱",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    """Carga el archivo Excel y devuelve un diccionario de DataFrames por hoja."""
    nombre_archivo = "Datos  Base de Datos.xlsx"
    
    if not os.path.exists(nombre_archivo):
        return None, f"No se encontró el archivo: {nombre_archivo}"
    
    try:
        # Cargamos todas las hojas del Excel
        excel_file = pd.ExcelFile(nombre_archivo)
        hojas = {nombre: excel_file.parse(nombre) for nombre in excel_file.sheet_names}
        return hojas, None
    except Exception as e:
        return None, f"Error al leer el archivo: {str(e)}"

# --- INTERFAZ PRINCIPAL ---
def main():
    st.title("📊 Análisis de Estrés Hídrico e Inteligencia Agrícola")
    st.markdown("---")
    
    # 1. Intentar cargar los datos
    hojas_datos, error = cargar_datos()
    
    if error:
        st.error(error)
        st.info("Asegúrate de que el archivo 'Datos  Base de Datos.xlsx' esté en la raíz del proyecto.")
        return

    # 2. Selección de hoja de trabajo
    st.sidebar.header("Configuración")
    hoja_seleccionada = st.sidebar.selectbox("Selecciona una pestaña del Excel", list(hojas_datos.keys()))
    df = hojas_datos[hoja_seleccionada]

    # 3. Validación y Mapeo de Columnas
    # Buscamos columnas de coordenadas y valores de medición (insensible a mayúsculas/minúsculas)
    cols_criticas = {
        'lat': ['Latitud', 'lat', 'LATITUD', 'Latitude'],
        'lon': ['Longitud', 'lon', 'LONGITUD', 'Longitude'],
        'val': ['Valor', 'valor', 'VALOR', 'Medicion', 'Humedad', 'Precipitacion']
    }

    def encontrar_columna(opciones, df_cols):
        for op in opciones:
            for col in df_cols:
                if str(op).lower() == str(col).lower():
                    return col
        return None

    col_lat = encontrar_columna(cols_criticas['lat'], df.columns)
    col_lon = encontrar_columna(cols_criticas['lon'], df.columns)
    col_val = encontrar_columna(cols_criticas['val'], df.columns)

    # Mostrar estado de la validación
    if not (col_lat and col_lon and col_val):
        st.warning(f"⚠️ Faltan columnas críticas en la pestaña '{hoja_seleccionada}'.")
        st.write("Columnas detectadas:", list(df.columns))
        st.info("Se requiere al menos: Latitud, Longitud y un Valor numérico.")
        return

    # 4. LIMPIEZA DE DATOS (Vital para corregir errores de logs)
    # Copiamos para no afectar el cache
    df_clean = df.copy()
    
    # Aseguramos conversión a numérico (lo que no sea número se vuelve NaN)
    df_clean[col_lat] = pd.to_numeric(df_clean[col_lat], errors='coerce')
    df_clean[col_lon] = pd.to_numeric(df_clean[col_lon], errors='coerce')
    df_clean[col_val] = pd.to_numeric(df_clean[col_val], errors='coerce')
    
    # Eliminamos cualquier fila que tenga NaN en columnas esenciales (esto evita el error de Plotly)
    df_clean = df_clean.dropna(subset=[col_lat, col_lon, col_val])

    if df_clean.empty:
        st.error("❌ El dataset quedó vacío tras limpiar valores no numéricos o nulos.")
        return

    # 5. CÁLCULO DE ESTRÉS HÍDRICO (Lógica inversa)
    max_val = df_clean[col_val].max()
    min_val = df_clean[col_val].min()
    
    if max_val != min_val:
        # A menor valor, mayor estrés (normalizado de 0 a 100)
        df_clean['Estres_Hidrico'] = 100 * (1 - (df_clean[col_val] - min_val) / (max_val - min_val))
    else:
        df_clean['Estres_Hidrico'] = 0.0

    # 6. MÉTRICAS RÁPIDAS
    m1, m2, m3 = st.columns(3)
    m1.metric("Registros Válidos", len(df_clean))
    m2.metric("Valor Promedio", f"{df_clean[col_val].mean():.2f}")
    m3.metric("Estrés Promedio", f"{df_clean['Estres_Hidrico'].mean():.1f}%")

    # 7. VISUALIZACIÓN DE MAPA
    st.subheader(f"Mapa de Estrés Hídrico Geolocalizado")
    
    try:
        fig = px.scatter_mapbox(
            df_clean,
            lat=col_lat,
            lon=col_lon,
            color="Estres_Hidrico",
            size=df_clean[col_val].abs() + 1,
            color_continuous_scale="RdYlBu_r", # Rojo (Crítico) a Azul (Óptimo)
            size_max=15,
            zoom=8,
            mapbox_style="carto-positron",
            hover_name=df_clean.columns[0], # Usualmente el nombre del municipio o ID
            hover_data={col_lat: False, col_lon: False, col_val: True, 'Estres_Hidrico': ':.2f'},
            height=600
        )
        
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al generar el mapa: {e}")

    # 8. ANÁLISIS DE DATOS
    with st.expander("Ver tabla de datos procesados y filtrados"):
        st.dataframe(df_clean, use_container_width=True)

if __name__ == "__main__":
    main()
