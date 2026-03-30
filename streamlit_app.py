import streamlit as st
import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Agro-Clima Intelligence",
    page_icon="🌱",
    layout="wide"
)

# --- CORRECCIÓN DE ESTILOS (Uso de unsafe_allow_html únicamente) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .landing-card {
        background: white; padding: 2rem; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-left: 8px solid #1e3a8a;
    }
    .main-title { color: #1e3a8a; font-size: 3rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA INTELIGENTE ---
@st.cache_data
def load_all_possible_data():
    """
    Busca tanto el archivo Excel original como posibles CSVs 
    para asegurar compatibilidad con el repositorio.
    """
    data_dict = {}
    errors = []
    
    # 1. Intentar cargar el Excel Original
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            excel_obj = pd.ExcelFile(excel_file)
            for sheet in excel_obj.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                # Limpieza básica de columnas
                df.columns = [str(c).replace(':', '').strip() for c in df.columns]
                data_dict[sheet] = df
        except Exception as e:
            errors.append(f"Error en Excel: {e}")

    # 2. Buscar archivos CSV (por si se subieron por separado)
    for file in os.listdir("."):
        if file.endswith(".csv"):
            try:
                name = file.replace(".csv", "")
                data_dict[name] = pd.read_csv(file, encoding='latin1')
            except:
                pass
                
    return data_dict, errors

# --- LÓGICA DE APLICACIÓN ---
dfs, load_errors = load_all_possible_data()

if not dfs:
    st.error("❌ No se encontraron datos en el repositorio.")
    st.info("Asegúrate de que 'Datos  Base de Datos.xlsx' o archivos .csv estén en la raíz.")
    st.expander("Ver archivos detectados").write(os.listdir("."))
    st.stop()

# --- NAVEGACIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # LANDING PAGE
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown('<h1 class="main-title">Agro-Clima <br>Intelligence</h1>', unsafe_allow_html=True)
        st.write("### Análisis de variables climáticas y producción.")
        st.markdown("""
            <div class="landing-card">
                <h4>Estado del Repositorio:</h4>
                <p>✅ Datos cargados correctamente.</p>
                <ul>
                    <li>Hojas detectadas: """ + ", ".join(dfs.keys()) + """</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Ingresar al Panel", type="primary"):
            st.session_state.auth = True
            st.rerun()
    with col2:
        st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=800", use_container_width=True)

else:
    # DASHBOARD
    with st.sidebar:
        st.title("🌱 Panel de Control")
        dataset_sel = st.selectbox("Seleccione Dataset", list(dfs.keys()))
        if st.button("⬅ Salir"):
            st.session_state.auth = False
            st.rerun()

    df = dfs[dataset_sel]
    
    tab1, tab2 = st.tabs(["📊 Visualización", "📄 Datos Crudos"])
    
    with tab1:
        st.subheader(f"Análisis de {dataset_sel}")
        # Métricas Dinámicas
        c1, c2 = st.columns(2)
        c1.metric("Total Registros", len(df))
        
        # Gráfico Automático
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            var = st.selectbox("Variable a visualizar", num_cols)
            fig, ax = plt.subplots()
            sns.histplot(df[var], kde=True, ax=ax)
            st.pyplot(fig)
        else:
            st.warning("Este dataset no contiene columnas numéricas para graficar.")

    with tab2:
        st.dataframe(df, use_container_width=True)
