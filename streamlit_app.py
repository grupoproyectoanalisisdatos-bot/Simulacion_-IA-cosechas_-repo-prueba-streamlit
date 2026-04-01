import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import mysql.connector # Asegúrate de agregarlo a requirements.txt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Data Intelligence - Agro Clima",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PROFESIONALES (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stApp { background-image: linear-gradient(0deg, #f4f7f9 0%, #ffffff 100%); }
    .landing-card {
        background: white; padding: 2rem; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-left: 8px solid #1e3a8a;
    }
    .main-title { color: #1e3a8a; font-size: 3.5rem; font-weight: 800; margin-bottom: 0px; }
    .sub-title { color: #64748b; font-size: 1.2rem; margin-bottom: 2rem; }
    .doc-section { background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CONEXIÓN A RAILWAY ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"]
        )
        return conn
    except Exception as e:
        return None

# --- CARGA DE DATOS (HÍBRIDA: SQL + EXCEL) ---
@st.cache_data(ttl=600) # Caché de 10 minutos para datos online
def load_data():
    dfs = {}
    source_info = "Local (Excel)"
    
    # 1. Intentar cargar desde Railway (SQL)
    conn = get_db_connection()
    if conn:
        try:
            # Ejemplo: obtenemos las tablas principales
            tables = ["Municipios", "Registros_Clima", "Registros_Produccion"]
            for table in tables:
                query = f"SELECT * FROM {table}"
                dfs[table] = pd.read_sql(query, conn)
            conn.close()
            return dfs, None, "Online (Railway SQL)"
        except Exception as e:
            if conn: conn.close()
            # Si falla SQL, no interrumpimos, intentamos Excel abajo
    
    # 2. Fallback al archivo Excel local
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            excel_data = pd.ExcelFile(excel_file)
            for sheet_name in excel_data.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                df.columns = [c.replace(':', '').strip() for c in df.columns]
                if 'Valor' in df.columns:
                    df['Valor'] = pd.to_numeric(df['Valor'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
                dfs[sheet_name] = df
            return dfs, None, "Local (Excel)"
        except Exception as e:
            return {}, f"Error al procesar el Excel: {e}", "Ninguna"
    else:
        return {}, f"No se encontró conexión SQL ni archivo local: {excel_file}", "Ninguna"

# --- LÓGICA DE NAVEGACIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def enter_dashboard():
    st.session_state.auth = True

# --- RENDERIZADO ---
dfs, error_msg, data_source = load_data()

if not dfs:
    st.error(f"❌ Error en la base de datos.")
    st.info(error_msg if error_msg else "No hay datos disponibles.")
    st.stop()

if not st.session_state.auth:
    # --- LANDING PAGE ---
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown('<h1 class="main-title">Agro-Clima <br>Intelligence</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">Plataforma avanzada. Conectado a: <b>{data_source}</b></p>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="landing-card">
                <h3>Estado de la Conexión</h3>
                <p>Análisis en tiempo real integrando fuentes SQL Online y datasets locales de respaldo.</p>
                <ul>
                    <li>Sincronización con Railway Database</li>
                    <li>Procesamiento de variables climáticas</li>
                    <li>Dashboard de producción municipal</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        st.button("🚀 Ingresar al Panel de Trabajo", on_click=enter_dashboard, type="primary", use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80", use_container_width=True)

else:
    # --- DASHBOARD PANEL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2610/2610098.png", width=100)
        st.title("Data Expert Panel")
        st.caption(f"Fuente: {data_source}")
        
        options = list(dfs.keys())
        dataset_name = st.selectbox("Seleccione Dataset / Tabla", options)
        
        if st.button("⬅ Cerrar Sesión"):
            st.session_state.auth = False
            st.rerun()

    df = dfs.get(dataset_name)
    
    if df is not None:
        tab1, tab2, tab3 = st.tabs(["📊 Visualización Crítica", "📄 Exploración de Datos", "📖 Documentación Técnica"])

        with tab1:
            st.subheader(f"Análisis: {dataset_name}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Registros", f"{len(df):,}")
            
            # Ajuste dinámico de nombres de columnas
            mun_col = next((c for c in df.columns if 'municipio' in c.lower()), None)
            val_col = next((c for c in df.columns if 'valor' in c.lower() or 'produccion' in c.lower() or 'temperatura' in c.lower()), None)

            m2.metric("Municipios", len(df[mun_col].unique()) if mun_col else "N/A")
            
            if val_col and pd.api.types.is_numeric_dtype(df[val_col]):
                val_mean = df[val_col].mean()
                m3.metric("Promedio", f"{val_mean:.2f}" if not np.isnan(val_mean) else "N/A")

            st.divider()

            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                col_a, col_b = st.columns(2)
                with col_a:
                    var_sel = st.selectbox("Variable", numeric_cols, key="v1")
                    fig, ax = plt.subplots()
                    sns.histplot(df[var_sel].dropna(), kde=True, color="#1e3a8a", ax=ax)
                    st.pyplot(fig)
                with col_b:
                    if mun_col:
                        top_10 = df.groupby(mun_col)[var_sel].mean().sort_values(ascending=False).head(10)
                        fig2, ax2 = plt.subplots()
                        sns.barplot(x=top_10.values, y=top_10.index, palette="viridis", ax=ax2)
                        st.pyplot(fig2)

        with tab2:
            st.subheader("Inspección de Datos")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar CSV", df.to_csv(index=False), f"{dataset_name}.csv", "text/csv")

        with tab3:
            st.markdown(f"""
            <div class="doc-section">
                <h3>📖 Documentación Técnica</h3>
                <p><b>Origen:</b> {data_source}</p>
                <p><b>Esquema detectado:</b> {', '.join(df.columns.tolist())}</p>
                <hr>
                <p>Esta conexión se realiza mediante un túnel seguro a Railway. 
                Si la base de datos está caída, el sistema conmuta automáticamente al respaldo Excel.</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
