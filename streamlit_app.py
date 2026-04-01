import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import mysql.connector

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
    .doc-section { background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
    .help-box { background-color: #eff6ff; padding: 10px; border-radius: 8px; border-left: 4px solid #3b82f6; font-size: 0.9rem; }
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

# --- CARGA DE DATOS (HÍBRIDA) ---
@st.cache_data(ttl=600)
def load_data():
    dfs = {}
    conn = get_db_connection()
    if conn:
        try:
            tables = ["Municipios", "Registros_Clima", "Registros_Produccion"]
            for table in tables:
                query = f"SELECT * FROM {table}"
                dfs[table] = pd.read_sql(query, conn)
            conn.close()
            return dfs, None, "Online (Railway SQL)"
        except Exception:
            if conn: conn.close()
    
    excel_file = "Datos  Base de Datos.xlsx"
    if os.path.exists(excel_file):
        try:
            excel_data = pd.ExcelFile(excel_file)
            for sheet_name in excel_data.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                df.columns = [c.replace(':', '').strip() for c in df.columns]
                # Limpieza robusta de datos numéricos
                for col in df.columns:
                    if any(x in col.lower() for x in ['valor', 'produccion', 'hectareas', 'temp', 'precip']):
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
                dfs[sheet_name] = df
            return dfs, None, "Local (Excel)"
        except Exception as e:
            return {}, f"Error al procesar el Excel: {e}", "Ninguna"
    return {}, "No se encontró fuente de datos.", "Ninguna"

# --- LÓGICA DE SESIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def enter_dashboard():
    st.session_state.auth = True

# --- INICIO DE RENDERIZADO ---
dfs, error_msg, data_source = load_data()

if not st.session_state.auth:
    # --- LANDING PAGE ---
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown('<h1 class="main-title">Expert Data <br>Analytics</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">Inteligencia Agrícola Basada en Evidencia | <b>{data_source}</b></p>', unsafe_allow_html=True)
        st.markdown("""
            <div class="landing-card">
                <h3>Capacidades del Sistema</h3>
                <p>Análisis estadístico avanzado de la cuenca del Magdalena y sectores productivos.</p>
                <ul>
                    <li>Modelado de correlación de variables (Seaborn)</li>
                    <li>Detección de anomalías climáticas</li>
                    <li>Ranking de eficiencia municipal</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        st.write("")
        st.button("🚀 Acceder al Laboratorio de Datos", on_click=enter_dashboard, type="primary", use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&q=80&w=800", use_container_width=True)

else:
    # --- PANEL DASHBOARD ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1541/1541400.png", width=80)
        st.title("Data Expert")
        options = list(dfs.keys())
        dataset_name = st.selectbox("Dataset de Análisis", options)
        st.divider()
        if st.button("⬅ Salir"):
            st.session_state.auth = False
            st.rerun()

    df = dfs.get(dataset_name)
    
    if df is not None:
        tab_viz, tab_data, tab_doc = st.tabs(["📊 Análisis Estadístico", "🗂️ Explorador", "📖 Metodología"])

        with tab_viz:
            st.subheader(f"Insights Críticos: {dataset_name}")
            
            # --- KPIS INICIALES ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Muestra (N)", f"{len(df):,}")
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            mun_col = next((c for c in df.columns if 'municipio' in c.lower() or 'nombre' in c.lower()), None)
            
            if mun_col: m2.metric("Entidades", len(df[mun_col].unique()))
            if numeric_cols:
                m3.metric("Promedio Gral", f"{df[numeric_cols[0]].mean():.2f}")
                m4.metric("Desv. Estándar", f"{df[numeric_cols[0]].std():.2f}")

            st.divider()

            # --- GRÁFICO 1: DISTRIBUCIÓN Y DENSIDAD ---
            col_g1, col_t1 = st.columns([2, 1])
            with col_g1:
                st.markdown("#### 1. Distribución y Probabilidad")
                var_dist = st.selectbox("Seleccione Variable de Interés", numeric_cols, key="dist")
                fig1, ax1 = plt.subplots(figsize=(10, 5))
                sns.histplot(df[var_dist].dropna(), kde=True, color="#1e3a8a", palette="mako", ax=ax1)
                ax1.set_title(f"Densidad de {var_dist}", fontsize=12)
                st.pyplot(fig1)
            with col_t1:
                st.info("💡 **Ayuda**: Este gráfico muestra la frecuencia de los valores. La línea curva (KDE) indica dónde se concentra la mayor probabilidad de los datos.")
                st.markdown(f"""
                **Análisis Experto:**
                - **Asimetría:** {'Positiva' if df[var_dist].skew() > 0 else 'Negativa'}
                - **Outliers:** Se detectan {len(df[df[var_dist] > df[var_dist].mean() + 2*df[var_dist].std()])} valores atípicos.
                """)

            st.divider()

            # --- GRÁFICO 2: RELACIÓN Y TENDENCIA ---
            if len(numeric_cols) >= 2:
                col_g2, col_t2 = st.columns([2, 1])
                with col_g2:
                    st.markdown("#### 2. Regresión Lineal y Correlación")
                    vx = st.selectbox("Variable X (Causa)", numeric_cols, index=0)
                    vy = st.selectbox("Variable Y (Efecto)", numeric_cols, index=min(1, len(numeric_cols)-1))
                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                    sns.regplot(data=df, x=vx, y=vy, scatter_kws={'alpha':0.5, 'color':'#1e3a8a'}, line_kws={'color':'#ef4444'}, ax=ax2)
                    st.pyplot(fig2)
                with col_t2:
                    st.help("La línea roja representa la tendencia central. Si los puntos están cerca de la línea, existe una fuerte relación predictiva entre las variables.")
                    corr_val = df[[vx, vy]].corr().iloc[0,1]
                    st.metric("Coef. Correlación", f"{corr_val:.2f}")
                    st.write("**Decisión:** " + ("Fuerte relación detectada. Use X para predecir Y." if abs(corr_val) > 0.6 else "Relación débil. Busque otras variables influyentes."))

            st.divider()

            # --- GRÁFICO 3: COMPARATIVA REGIONAL (HEATMAP) ---
            if mun_col and len(numeric_cols) > 1:
                st.markdown("#### 3. Mapa de Calor: Desempeño por Municipio")
                col_g3, col_t3 = st.columns([2, 1])
                with col_g3:
                    # Top 10 municipios para no saturar el heatmap
                    pivot_df = df.groupby(mun_col)[numeric_cols].mean().sort_values(by=numeric_cols[0], ascending=False).head(10)
                    # Normalización simple para visualización
                    pivot_norm = (pivot_df - pivot_df.min()) / (pivot_df.max() - pivot_df.min())
                    fig3, ax3 = plt.subplots(figsize=(10, 8))
                    sns.heatmap(pivot_norm, annot=pivot_df, fmt=".1f", cmap="YlGnBu", ax=ax3)
                    st.pyplot(fig3)
                with col_t3:
                    st.info("🕵️ **Exploración**: Los colores oscuros indican valores máximos normalizados. Útil para identificar qué municipio destaca en múltiples métricas a la vez.")
                    st.write("**Top Líder:** " + str(pivot_df.index[0]))

        with tab_data:
            st.subheader("Acceso a Microdatos")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Exportar para Auditoría (CSV)", df.to_csv(index=False), f"audit_{dataset_name}.csv")

        with tab_doc:
            st.markdown(f"""
            <div class="doc-section">
                <h3>📖 Documentación de Consultas y Lógica</h3>
                <p><b>Origen de Datos:</b> {data_source}</p>
                <hr>
                <h4>Metodología de Análisis:</h4>
                <ol>
                    <li><b>Limpieza (Data Wrangling):</b> Conversión de tipos de datos, manejo de comas decimales y normalización de nombres de columnas.</li>
                    <li><b>Consultas SQL Sugeridas:</b>
                        <ul>
                            <li><code>SELECT municipio, AVG(valor) FROM tabla GROUP BY municipio</code>: Para tendencias regionales.</li>
                            <li><code>SELECT * FROM clima WHERE precip > 200</code>: Identificación de eventos de inundación.</li>
                        </ul>
                    </li>
                    <li><b>Modelado:</b> Se utiliza el Coeficiente de Pearson para validar la relación entre el Clima y la Producción.</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

st.caption("Agro-Clima Intelligence Expert System © 2024")
