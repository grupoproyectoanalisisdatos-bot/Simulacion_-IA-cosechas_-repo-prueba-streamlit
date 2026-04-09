import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Predictor Climático Inteligente", layout="wide")

# Carga de modelos y mapeos
@st.cache_resource
def cargar_recursos():
    modelo = joblib.load('modelo_clima_municipios_id.pkl')
    mapa = joblib.load('mapa_municipios.pkl')
    return modelo, mapa

try:
    modelo, mapa_municipios = cargar_recursos()
    
    # Interfaz
    st.title("🌦️ Sistema de Predicción Climática Agrícola")
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Configuración")
        # El selector ahora usa los nombres del mapa que guardaste en Colab
        nombre_municipio = st.selectbox("Seleccione el Municipio:", options=list(mapa_municipios.values()))
        
        # Obtenemos el ID correspondiente al nombre seleccionado
        municipio_id = [id for id, nombre in mapa_municipios.items() if nombre == nombre_municipio][0]
        
        fecha = st.date_input("Fecha de predicción", datetime.now())
        t_min = st.number_input("Temperatura Mínima Estimada (°C)", value=15.0)
        
        btn_predecir = st.button("Calcular Predicción")

    with col2:
        st.header("Resultado del Modelo")
        if btn_predecir:
            # Preparar datos para el modelo: [temp_min, Mes, Dia, Municipio_ID]
            input_data = pd.DataFrame([[t_min, fecha.month, fecha.day, municipio_id]], 
                                      columns=['temp_min', 'Mes', 'Dia', 'Municipio_ID'])
            
            prediccion = modelo.predict(input_data)[0]
            
            st.metric(label=f"Temperatura Máxima en {nombre_municipio}", 
                      value=f"{prediccion:.2f} °C", 
                      delta=f"{prediccion - t_min:.2f} °C vs Mínima")
            
            # Recomendación BI
            st.info(f"Análisis para {nombre_municipio}: El modelo estima una oscilación térmica de {prediccion - t_min:.2f} grados.")

except Exception as e:
    st.error(f"Error al cargar los archivos: {e}")
    st.warning("Asegúrate de que los archivos .pkl estén en la raíz del repositorio.")
