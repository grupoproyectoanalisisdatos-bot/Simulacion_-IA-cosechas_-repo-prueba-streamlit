import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# --- CONFIGURACIÓN DE ESTILO ---
st.set_page_config(
    page_title="AgroAnalytics Pro | Estrés Hídrico",
    page_icon="🌾",
    layout="wide"
)

# Paleta de colores profesional
AGRO_PALETTE = ["#2E7D32", "#1976D2", "#FBC02D", "#D32F2F", "#7B1FA2"]
sns.set_theme(style="whitegrid")
sns.set_palette(sns.color_palette(AGRO_PALETTE))

# --- CARGA DE DATOS ---
@st.cache_data
def load_excel_data():
    file_path = "Datos  Base de Datos.xlsx"
    if not os.path.exists(file_path):
        return None
    try:
        return pd.read_excel(file_path, sheet_name=None)
    except Exception:
        return None

# --- FUNCIONES DE AYUDA ---
def render_help(text):
    """Renderiza un icono de ayuda con tooltip."""
    st.caption(f"ℹ️ {text}")

# --- PROCESAMIENTO ---
def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2910/2910756.png", width=100)
    st.sidebar.title("Configuración Pro")
    
    data_dict = load_excel_data()
    
    if data_dict is None:
        st.error("Archivo 'Datos  Base de Datos.xlsx' no detectado.")
        return

    sheet_name = st.sidebar.selectbox("Seleccionar Unidad de Análisis", list(data_dict.keys()))
    df_raw = data_dict[sheet_name]

    # Identificación automática de columnas
    def get_col(keywords, columns):
        for k in keywords:
            for c in columns:
                if k.lower() in str(c).lower(): return c
        return None

    col_lat = get_col(['lat', 'latitud'], df_raw.columns)
    col_lon = get_col(['lon', 'longitud'], df_raw.columns)
    col_val = get_col(['valor', 'medicion', 'humedad', 'precipitacion'], df_raw.columns)
    col_mun = get_col(['municipio', 'nombre', 'id'], df_raw.columns) or df_raw.columns[0]

    # Limpieza estricta
    df = df_raw.copy()
    for c in [col_lat, col_lon, col_val]:
        if c: df[c] = pd.to_numeric(df[c], errors='coerce')
    
    df = df.dropna(subset=[col_lat, col_lon, col_val] if col_lat and col_val else [col_val])

    # Tabs Principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📍 Mapa de Riesgo", 
        "📊 Distribución Estadística", 
        "📈 Correlación Espacial",
        "📖 Documentación"
    ])

    # --- TAB 1: MAPA ---
    with tab1:
        st.subheader("Geolocalización de Estrés por Municipio")
        render_help("Los puntos representan los municipios. El tamaño indica la magnitud del valor y el color el nivel de estrés.")
        
        if col_lat and col_lon:
            # Cálculo de estrés (0-100)
            min_v, max_v = df[col_val].min(), df[col_val].max()
            df['Indice_Estres'] = 100 * (1 - (df[col_val] - min_v) / (max_v - min_v)) if max_v != min_v else 0
            
            fig_map = px.scatter_mapbox(
                df, lat=col_lat, lon=col_lon, color="Indice_Estres",
                size=df[col_val].abs() + 1, color_continuous_scale="RdYlBu_r",
                hover_name=col_mun, zoom=6, mapbox_style="carto-positron",
                height=600, title=f"Distribución Geográfica en {sheet_name}"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No se detectaron coordenadas suficientes para el mapa.")

    # --- TAB 2: SEABORN DIST ---
    with tab2:
        st.subheader("Análisis de Distribución y Densidad")
        render_help("Este gráfico muestra cómo se reparten los valores medidos. La curva KDE ayuda a identificar sesgos en la recolección.")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(df[col_val], kde=True, color="#2E7D32", bins=20, ax=ax)
        ax.set_title(f"Distribución de {col_val}", fontsize=14)
        ax.set_xlabel("Valor Medido")
        ax.set_ylabel("Frecuencia")
        st.pyplot(fig)
        
        st.write("**Explicación Profesional:**")
        st.info(f"El valor promedio detectado es **{df[col_val].mean():.2f}**. La distribución permite observar si la mayoría de los municipios se encuentran en rangos críticos o saludables.")

    # --- TAB 3: CORRELACIÓN ---
    with tab3:
        st.subheader("Análisis de Correlación Latitud vs Valor")
        render_help("Visualiza si existe una tendencia climática dependiente de la posición norte-sur (latitud).")
        
        if col_lat:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.regplot(data=df, x=col_lat, y=col_val, 
                        scatter_kws={'alpha':0.5, 'color':'#1976D2'}, 
                        line_kws={'color':'#D32F2F'}, ax=ax)
            ax.set_title("Influencia de la Latitud en el Valor Medido")
            st.pyplot(fig)
            
            st.write("**Interpretación:**")
            st.success("La línea roja indica la tendencia. Si es ascendente o descendente, sugiere que la ubicación geográfica del municipio influye directamente en la variable agrícola.")
        else:
            st.info("Se requiere información de Latitud para este análisis.")
r.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    # --- TAB 4: DOCUMENTACIÓN ---
    with tab4:
        st.markdown(f"### 📑 Documentación Técnica: {sheet_name}")
        st.markdown(f"""
        **Resumen de la Pestaña:**
        - **Fuente de datos:** Hoja `{sheet_name}` del archivo Excel.
        - **Total registros procesados:** {len(df)} municipios.
        - **Variable analizada:** `{col_val}`.
        
        **Manual de Usuario:**
        1. **Mapa**: Use la rueda del ratón para hacer zoom. Los colores rojos indican áreas con valores mínimos (máximo estrés hídrico).
        2. **Histograma**: Si la curva está desplazada a la izquierda, hay déficit hídrico generalizado.
        3. **Regresión**: Utilizada para predecir valores en municipios donde no hay estaciones de monitoreo basadas en su ubicación.
        """)

if __name__ == "__main__":
    main()
