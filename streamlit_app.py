import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Data Intelligence - Analítica Avanzada",
    page_icon="📊",
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
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-left: 8px solid #0f172a;
    }
    .main-title { color: #0f172a; font-size: 3rem; font-weight: 800; margin-bottom: 0px; }
    .sub-title { color: #475569; font-size: 1.1rem; margin-bottom: 2rem; }
    .metric-card {
        background: white; padding: 1.2rem; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CONEXIÓN A BASE DE DATOS ---
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
    except Exception:
        return None

# --- CARGA DE DATOS INTELIGENTE ---
@st.cache_data(ttl=600)
def load_data():
    dfs = {}
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [t[0] for t in cursor.fetchall()]
            for table in tables:
                dfs[table] = pd.read_sql(f"SELECT * FROM {table}", conn)
            conn.close()
            return dfs, None, "Conexión Activa (Railway SQL)"
        except Exception:
            if conn: conn.close()
    
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            excel_data = pd.ExcelFile(excel_file)
            for sheet in excel_data.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                df.columns = [str(c).strip() for c in df.columns]
                for col in df.columns:
                    if df[col].dtype == 'object':
                        try:
                            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='ignore')
                        except: pass
                dfs[sheet] = df
            return dfs, None, "Archivo Local (Excel)"
        except Exception as e:
            return {}, f"Error al leer Excel: {e}", "Error"
            
    return {}, "No se detectaron fuentes de datos.", "Sin datos"

# --- LÓGICA DE NAVEGACIÓN ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

dfs, error_msg, data_source = load_data()

if not st.session_state.authenticated:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<h1 class="main-title">Data Analytics<br>Expert Suite</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">Infraestructura conectada a: <b>{data_source}</b></p>', unsafe_allow_html=True)
        st.markdown("""
            <div class="landing-card">
                <h4>Validación Geográfica y Productiva</h4>
                <p>Módulo de Inteligencia de Negocios basado en analítica predictiva y diagnóstico de brechas agrícolas.</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Iniciar Exploración de Datos", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.rerun()
    with col2:
        st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=800", use_container_width=True)

else:
    with st.sidebar:
        st.title("🎛️ Control de Datos")
        if dfs:
            selected_table = st.selectbox("Tabla Activa", list(dfs.keys()))
            df = dfs[selected_table].copy()
        else:
            st.error("Sin tablas.")
            df = None
            
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()

    if df is not None:
        df = df.dropna(how='all', axis=0)
        
        tab_geo, tab_viz, tab_data = st.tabs(["🗺️ Georreferenciación", "📈 Diagnóstico Avanzado", "🗂️ Datos Crudos"])

        with tab_geo:
            st.subheader("Ubicación de Puntos de Producción")
            lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
            lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)
            
            if lat_col and lon_col:
                map_df = df.dropna(subset=[lat_col, lon_col]).copy()
                map_df[lat_col] = pd.to_numeric(map_df[lat_col], errors='coerce')
                map_df[lon_col] = pd.to_numeric(map_df[lon_col], errors='coerce')
                map_df = map_df.dropna(subset=[lat_col, lon_col])

                if not map_df.empty:
                    fig_map = px.scatter_mapbox(
                        map_df, lat=lat_col, lon=lon_col, 
                        hover_name=df.columns[0] if not df.empty else None,
                        color_discrete_sequence=["#1e3a8a"],
                        zoom=5, height=500,
                        mapbox_style="carto-positron"
                    )
                    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("La tabla actual no contiene coordenadas geográficas.")

        with tab_viz:
            st.subheader("🚀 Análisis Comparativo y Relaciones Críticas")
            
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(num_cols) >= 2:
                # KPIs Superiores
                kpi1, kpi2, kpi3 = st.columns(3)
                main_var = num_cols[-1]
                kpi1.metric(f"Promedio {main_var}", f"{df[main_var].mean():.2f}")
                kpi2.metric("Eficiencia Max.", f"{df[main_var].max():.2f}")
                kpi3.metric("Nivel de Dispersión", f"{df[main_var].std():.2f}")

                st.divider()

                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("#### 🔍 Relación Causa-Efecto")
                    var_x = st.selectbox("Factor (X)", num_cols[:-1], index=0)
                    var_y = st.selectbox("Resultado (Y)", num_cols, index=len(num_cols)-1)
                    
                    fig_reg = px.scatter(df, x=var_x, y=var_y, trendline="ols", 
                                        color_discrete_sequence=["#15803d"],
                                        title=f"Impacto de {var_x} en {var_y}")
                    st.plotly_chart(fig_reg, use_container_width=True)
                    st.info("La línea de tendencia indica si la relación es positiva o negativa. Útil para predecir rendimientos basados en clima.")

                with col_right:
                    st.markdown("#### 📊 Distribución de Rendimiento")
                    fig_box = px.box(df, y=var_y, points="all", 
                                   color_discrete_sequence=["#1e3a8a"],
                                   title=f"Variabilidad de {var_y} entre Municipios")
                    st.plotly_chart(fig_box, use_container_width=True)
                    st.info("Los puntos fuera de la caja son 'Outliers'. Municipios con rendimientos excepcionales o críticas caídas de producción.")

                st.divider()
                
                st.markdown("#### 🏗️ Análisis de Brecha de Cosecha")
                # Intentar detectar columnas de área sembrada vs cosechada
                sem_col = next((c for c in df.columns if 'sembra' in c.lower()), None)
                cos_col = next((c for c in df.columns if 'cosecha' in c.lower()), None)
                
                if sem_col and cos_col:
                    fig_gap = go.Figure()
                    fig_gap.add_trace(go.Bar(x=df.index, y=df[sem_col], name='Área Sembrada', marker_color='#94a3b8'))
                    fig_gap.add_trace(go.Bar(x=df.index, y=df[cos_col], name='Área Cosechada', marker_color='#22c55e'))
                    fig_gap.update_layout(barmode='group', title="Brecha entre Siembra y Cosecha (Eficiencia Operativa)")
                    st.plotly_chart(fig_gap, use_container_width=True)
                else:
                    st.markdown("#### 🧪 Matriz de Interacción")
                    fig_heat = plt.figure(figsize=(10, 5))
                    sns.heatmap(df[num_cols].corr(), annot=True, cmap='RdYlGn', center=0)
                    st.pyplot(fig_heat)

            else:
                st.warning("Se necesitan al menos 2 columnas numéricas para realizar un análisis de relaciones.")

        with tab_data:
            st.markdown("### Tabla de Datos Normalizada")
            st.dataframe(df, use_container_width=True)

st.caption("Expert Analytics Suite v3.0 | Relaciones Multivariable Verificadas")
