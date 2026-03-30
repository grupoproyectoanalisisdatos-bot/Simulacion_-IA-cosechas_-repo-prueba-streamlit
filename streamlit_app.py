import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="AgroAnalytics Pro",
    page_icon="🌱",
    layout="wide"
)

# Estilo de gráficos
sns.set_theme(style="whitegrid")
COLOR_PRIMARIO = "#2E7D32" # Verde agro

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    file_path = "Datos  Base de Datos.xlsx"
    if not os.path.exists(file_path):
        return None
    try:
        return pd.read_excel(file_path, sheet_name=None)
    except Exception as e:
        st.error(f"Error crítico al leer el Excel: {e}")
        return None

def main():
    st.sidebar.title("🌿 Panel de Control")
    data_dict = load_data()
    
    if data_dict is None:
        st.error("Archivo 'Datos  Base de Datos.xlsx' no encontrado.")
        return

    sheet_name = st.sidebar.selectbox("Seleccionar Hoja", list(data_dict.keys()))
    df = data_dict[sheet_name].copy()

    # --- LIMPIEZA Y NORMALIZACIÓN (Solución al Error de Logs) ---
    # Buscamos columnas por palabras clave
    def find_column(keywords):
        for k in keywords:
            for c in df.columns:
                if k.lower() in str(c).lower(): return c
        return None

    col_lat = find_column(['latitud', 'lat'])
    col_lon = find_column(['longitud', 'lon'])
    col_val = find_column(['valor', 'precipitacion', 'humedad', 'temp', 'medicion'])
    col_mun = find_column(['municipio', 'nombre', 'ciudad']) or df.columns[0]

    # VALIDACIÓN Y CONVERSIÓN FORZADA
    if col_lat and col_lon:
        # Convertimos a numérico y lo que no sea número se vuelve NaN
        df[col_lat] = pd.to_numeric(df[col_lat], errors='coerce')
        df[col_lon] = pd.to_numeric(df[col_lon], errors='coerce')
        
        # Si existe columna de valor, asegurar que no tenga NaNs para el 'size' del mapa
        if col_val:
            df[col_val] = pd.to_numeric(df[col_val], errors='coerce')
            # Llenamos vacíos con la media para que el mapa no falle
            df[col_val] = df[col_val].fillna(df[col_val].mean() if not df[col_val].empty else 0)
        else:
            # Si no hay valor, creamos uno ficticio para el tamaño de los puntos
            col_val = "Punto"
            df[col_val] = 10

        # Eliminamos filas donde lat o lon fallaron la conversión
        df = df.dropna(subset=[col_lat, col_lon])
    else:
        st.error("No se detectaron columnas de Latitud o Longitud en esta hoja.")
        return

    # --- UI PRINCIPAL ---
    st.title(f"Análisis Espacial: {sheet_name}")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Registros", len(df))
    col_m2.metric("Promedio Variable", f"{df[col_val].mean():.2f}" if isinstance(df[col_val].iloc[0], (int, float, np.number)) else "N/A")
    col_m3.metric("Municipios", df[col_mun].nunique())

    tabs = st.tabs(["📍 Mapa de Cosechas", "📊 Distribución Estadística", "📋 Datos Crudos"])

    with tabs[0]:
        st.subheader("Geolocalización de Unidades")
        # Aseguramos que 'size' sea siempre un número positivo y válido
        df['size_mapa'] = df[col_val].apply(lambda x: abs(x) if x != 0 else 1)
        
        fig_map = px.scatter_mapbox(
            df,
            lat=col_lat,
            lon=col_lon,
            size='size_mapa',
            color=col_val,
            hover_name=col_mun,
            color_continuous_scale=px.colors.sequential.Greens,
            zoom=5,
            mapbox_style="carto-positron",
            height=600
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with tabs[1]:
        st.subheader("Análisis de Frecuencia")
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.histplot(df[col_val], kde=True, color=COLOR_PRIMARIO, ax=ax)
        plt.title(f"Distribución de {col_val}")
        st.pyplot(fig)
        
        st.markdown("""
        **Nota Técnica:** Este gráfico muestra la concentración de los valores. 
        Si la curva está desplazada a la derecha, indica condiciones óptimas generalizadas.
        """)

    with tabs[2]:
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
