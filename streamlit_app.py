import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Agro-Clima Intelligence Pro",
    page_icon="🌱",
    layout="wide"
)

# --- INYECCIÓN DE CSS PARA DISEÑO PROFESIONAL DE BOTONES ---
# Se garantiza que la inscripción (texto) sea grande, siempre visible y no se corte.
st.markdown("""
    <style>
    /* Estilo base para todos los botones de la aplicación */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #15803d; /* Verde Agro Principal */
        color: white !important;
        font-weight: 800;
        font-size: 1.1rem;
        border: 2px solid #166534;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex !important;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Efecto al pasar el cursor (Hover) */
    div.stButton > button:hover {
        background-color: #1e3a8a; /* Azul Clima al interactuar */
        border-color: #1e40af;
        color: #ffffff !important;
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    /* Efecto al hacer clic (Active) */
    div.stButton > button:active {
        transform: translateY(0);
        scale: 0.98;
    }

    /* Garantizar que el texto (p) interno sea siempre visible y legible */
    div.stButton > button p {
        font-size: 1.1rem !important;
        white-space: normal !important; /* Permite salto de línea si es muy largo */
        word-break: break-word !important;
        line-height: 1.2 !important;
        margin: 0 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* Estilo específico para botones de formularios (Submit) */
    div.stFormSubmitButton > button {
        background-color: #1e3a8a !important;
        border-color: #1d4ed8 !important;
    }
    
    div.stFormSubmitButton > button:hover {
        background-color: #1e40af !important;
        filter: brightness(1.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE LA APLICACIÓN ---

st.title("🌱 Dashboard Agro-Climático")
st.markdown("### Optimización de Interfaz e Inscripciones")
st.write("Los botones a continuación mantienen su color y texto visible en cualquier resolución.")

# Layout de acciones principales
col1, col2, col3 = st.columns(3)

with col1:
    # El texto se ajustará automáticamente gracias al CSS si es muy largo
    if st.button("📊 Generar Reporte de Cosecha Semanal", help="Haz clic para ver el análisis detallado"):
        st.success("✅ Reporte generado correctamente.")

with col2:
    if st.button("🌦️ Consultar Clima en Tiempo Real"):
        st.info("📡 Conectando con estaciones meteorológicas...")

with col3:
    if st.button("🚀 Ejecutar Optimización por IA"):
        st.warning("🤖 El modelo está calculando la mejor fecha de siembra.")

st.divider()

# --- SECCIÓN DE FORMULARIO DE INSCRIPCIÓN ---
st.subheader("Configuración de Simulación")

with st.form("registro_datos"):
    st.markdown("#### Formulario de Inscripción de Lote")
    
    c1, c2 = st.columns(2)
    with c1:
        municipio = st.selectbox("Municipio", ["Urrao", "Arboletes", "Nechí", "Turbo"])
    with c2:
        cultivo = st.selectbox("Tipo de Cultivo", ["Maíz Tradicional", "Cacao", "Plátano"])
    
    area = st.number_input("Área sembrada (Hectáreas)", min_value=0.0, value=1.0)
    
    # El botón de formulario ocupa el ancho completo y usa el color azul definido
    submitted = st.form_submit_button("Confirmar Inscripción de Datos de Lote", width='stretch')
    
    if submitted:
        st.balloons()
        st.success(f"Lote en {municipio} con {cultivo} registrado exitosamente.")

# --- VISUALIZACIÓN DE APOYO ---
st.subheader("Tendencia de Rendimiento Esperado")
df_dummy = pd.DataFrame({
    'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
    'Rendimiento': [2.1, 2.4, 2.2, 2.8, 3.1, 2.9]
})
fig = px.area(df_dummy, x='Mes', y='Rendimiento', 
              title='Proyección de Producción (Ton/Ha)',
              color_discrete_sequence=['#15803d'])
st.plotly_chart(fig, width='stretch')
