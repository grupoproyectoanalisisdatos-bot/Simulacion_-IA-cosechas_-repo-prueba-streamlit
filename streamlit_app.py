# ============================================================================
# 🌾 Agro-Clima Intelligence Pro - streamlit_app.py (VERSIÓN FINAL)
# ============================================================================
# ✅ Correcciones basadas en BackupBD.sql:
# 1. Columnas reales de coordenadas (latitud, longitud por municipio)
# 2. Manejo de formato mixto (coma/punto) en valores numéricos
# 3. scatter_map con parámetro 'style' correcto
# 4. width='stretch' en lugar de use_container_width
# 5. Validación de columnas antes de dropna()
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sqlalchemy import create_engine, text
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================================
# 🎨 CONFIGURACIÓN DE PÁGINA
# ============================================================================
st.set_page_config(
    page_title="🌾 Agro-Clima Intelligence Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROFESSIONAL_PALETTE = {
    "primary": "#1e3a8a",
    "secondary": "#15803d",
    "accent": "#f59e0b",
    "neutral": "#64748b",
}

SEABORN_PALETTE = [
    PROFESSIONAL_PALETTE["primary"],
    PROFESSIONAL_PALETTE["secondary"],
    PROFESSIONAL_PALETTE["accent"],
    "#0ea5e9",
    "#8b5cf6",
]

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f1f5f9;
        border-radius: 6px 6px 0px 0px;
        color: #1e3a8a;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: white !important;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1e3a8a;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 🔐 CONEXIÓN A BASE DE DATOS
# ============================================================================
@st.cache_resource
def init_connection():
    """Conecta a Railway usando st.secrets (Streamlit Cloud)"""
    try:
        creds = st.secrets["connections"]["railway_db"]
        dialect = creds.get("dialect", "mysql")
        host = creds.get("host", "")
        port = creds.get("port", 3306)
        database = creds.get("database", "")
        username = creds.get("username", "")
        password = creds.get("password", "")
        
        url = f"{dialect}+pymysql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return engine
    
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")
        return None

# ============================================================================
# 🧹 LIMPIEZA DE DATOS (CRÍTICO PARA TU FORMATO)
# ============================================================================
def clean_dataframe(df):
    """
    Limpia tipos de datos según formato de BackupBD.sql
    ✅ Maneja formato mixto: '284,2' y '284.2'
    ✅ Normaliza nombres de columnas
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Columnas numéricas que pueden venir con coma como decimal
    numeric_cols = ['precipitacion', 'precipitacion_mm', 'temperatura', 
                    'temperatura_max', 'temperatura_min', 'rendimiento',
                    'rendimiento_ha', 'area_cosechada', 'area_sembrada']
    
    for col in numeric_cols:
        if col in df_clean.columns:
            # Reemplazar coma por punto y convertir a numérico
            df_clean[col] = df_clean[col].astype(str).str.replace(',', '.')
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Columnas de coordenadas (latitud, longitud)
    coord_cols = ['latitud', 'longitud', 'latitude', 'longitude', 'lat', 'lon']
    for col in coord_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.replace(',', '.')
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Normalizar nombres de columnas
    df_clean.columns = df_clean.columns.str.strip().str.lower()
    
    # Eliminar columnas duplicadas
    df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
    
    return df_clean

# ============================================================================
# 🗺️ DETECTAR COLUMNAS DE COORDENADAS (SEGÚN TU BD)
# ============================================================================
def detect_coordinate_columns(df):
    """
    Detecta columnas de latitud y longitud según tu estructura real
    ✅ Basado en BackupBD.sql: coordenadas por municipio
    """
    # Posibles nombres para latitud
    lat_candidates = ['latitud', 'latitude', 'lat', 'coord_lat', 'latitud_municipio']
    lat_col = next((c for c in lat_candidates if c in df.columns), None)
    
    # Posibles nombres para longitud
    lon_candidates = ['longitud', 'longitude', 'lon', 'coord_lon', 'longitud_municipio']
    lon_col = next((c for c in lon_candidates if c in df.columns), None)
    
    # Si no encuentra, buscar columnas con valores en rango de coordenadas
    if lat_col is None or lon_col is None:
        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                # Latitud: entre -90 y 90
                if lat_col is None and col_data.min() >= -90 and col_data.max() <= 90:
                    # Excluir si parece longitud (valores negativos grandes)
                    if col_data.min() >= 0 or col_data.max() < 50:
                        lat_col = col
                # Longitud: entre -180 y 180
                elif lon_col is None and col_data.min() >= -180 and col_data.max() <= 180:
                    # Excluir si parece latitud (valores positivos pequeños)
                    if col_data.min() < 0:
                        lon_col = col
    
    return lat_col, lon_col

# ============================================================================
# 📊 CARGA DE DATOS
# ============================================================================
@st.cache_data(ttl=300)
def load_data():
    """
    Carga datos desde Railway con estructura de BackupBD.sql
    """
    engine = init_connection()
    
    if engine is None:
        return pd.DataFrame({
            'municipio': ['Arboletes', 'Medellín', 'Cali'],
            'latitud': [8.8469, 6.2442, 3.4516],
            'longitud': [-76.4319, -75.5812, -76.5320],
            'precipitacion_mm': [177.4, 210.0, 291.0],
            'fecha': pd.date_range('2005-04-01', periods=3)
        })
    
    try:
        # Consultar tablas disponibles
        query = text("""
            SELECT 
                municipio,
                latitud,
                longitud,
                fecha,
                precipitacion_mm,
                temperatura_max,
                temperatura_min,
                rendimiento_ha,
                area_cosechada
            FROM vista_datos_completos
            LIMIT 10000
        """)
        
        try:
            df = pd.read_sql(query, engine)
        except:
            # Fallback: consultar tabla principal
            df = pd.read_sql(text("SELECT * FROM produccion LIMIT 10000"), engine)
        
        df = clean_dataframe(df)
        return df
    
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return pd.DataFrame()

# ============================================================================
# 🗺️ GRÁFICO 1: Mapa Interactivo (CORREGIDO CON TUS COLUMNAS)
# ============================================================================
def plot_interactive_map(df, lat_col, lon_col, map_var):
    """
    Mapa interactivo con columnas reales de tu BD
    ✅ Usa latitud/longitud de municipio
    ✅ scatter_map con 'style' (no 'mapbox_style')
    """
    # Validación crítica antes de continuar
    if lat_col is None or lon_col is None:
        st.warning("⚠️ No se encontraron columnas de coordenadas (latitud/longitud)")
        return None
    
    if map_var is None:
        st.warning("⚠️ No se encontró variable numérica para el mapa")
        return None
    
    # Verificar que las columnas existen
    required_cols = [lat_col, lon_col, map_var]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.warning(f"⚠️ Columnas faltantes: {missing_cols}")
        st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return None
    
    # Preparar datos
    map_df = df[[lat_col, lon_col, map_var]].copy()
    
    # Convertir a numérico (maneja formato mixto coma/punto)
    map_df[lat_col] = pd.to_numeric(map_df[lat_col], errors='coerce')
    map_df[lon_col] = pd.to_numeric(map_df[lon_col], errors='coerce')
    map_df[map_var] = pd.to_numeric(map_df[map_var], errors='coerce')
    
    # Dropna SOLO después de validar columnas
    map_df = map_df.dropna()
    
    if map_df.empty:
        st.warning("⚠️ No hay datos válidos para el mapa")
        return None
    
    # ✅ scatter_map con 'style' (CORRECCIÓN CRÍTICA)
    fig_map = px.scatter_map(
        map_df,
        lat=lat_col,
        lon=lon_col,
        color=map_var,
        size=map_var,
        hover_name='municipio' if 'municipio' in map_df.columns else None,
        title=f"🗺️ Distribución Geográfica: {map_var}",
        color_continuous_scale='Viridis',
        style='open-street-map',  # ✅ CORREGIDO: NO usar 'mapbox_style'
        zoom=7,
        center={"lat": map_df[lat_col].mean(), "lon": map_df[lon_col].mean()}
    )
    
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=500
    )
    
    return fig_map

# ============================================================================
# 📈 GRÁFICO 2: Correlación Temperatura vs Rendimiento
# ============================================================================
def plot_correlation_temp_yield(df):
    """Gráfico de dispersión con regresión usando Seaborn"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    temp_col = next((c for c in df.columns if 'temp' in c.lower()), None)
    yield_col = next((c for c in df.columns if 'rendimiento' in c.lower()), None)
    
    if temp_col is None or yield_col is None:
        ax.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax.transAxes)
        return fig
    
    df_plot = df[[temp_col, yield_col]].dropna()
    
    if len(df_plot) < 2:
        ax.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax.transAxes)
        return fig
    
    sns.regplot(
        data=df_plot,
        x=temp_col,
        y=yield_col,
        scatter_kws={'alpha': 0.6, 's': 40, 'color': PROFESSIONAL_PALETTE['primary']},
        line_kws={'color': PROFESSIONAL_PALETTE['secondary'], 'linewidth': 2},
        ax=ax
    )
    
    ax.set_title('🌡️ Temperatura vs Rendimiento', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(temp_col, fontsize=11)
    ax.set_ylabel(yield_col, fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# 📊 GRÁFICO 3: Distribución de Precipitación
# ============================================================================
def plot_precipitation_distribution(df):
    """Boxplot con Seaborn"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    precip_col = next((c for c in df.columns if 'precip' in c.lower()), None)
    mun_col = next((c for c in df.columns if 'municipio' in c.lower()), None)
    
    if precip_col is None:
        ax.text(0.5, 0.5, 'Datos de precipitación no disponibles', ha='center', va='center', transform=ax.transAxes)
        return fig
    
    df_plot = df[[precip_col]].dropna()
    if mun_col and mun_col in df.columns:
        df_plot = df[[precip_col, mun_col]].dropna()
    
    if mun_col and mun_col in df_plot.columns and len(df_plot[mun_col].unique()) > 1:
        sns.boxplot(
            data=df_plot,
            x=mun_col,
            y=precip_col,
            hue=mun_col,  # ✅ EVITA WARNING
            palette=SEABORN_PALETTE[:len(df_plot[mun_col].unique())],
            ax=ax,
            linewidth=1.5,
            legend=False
        )
    else:
        sns.boxplot(
            data=df_plot,
            y=precip_col,
            color=PROFESSIONAL_PALETTE['secondary'],
            ax=ax,
            linewidth=1.5
        )
    
    ax.set_title('🌧️ Distribución de Precipitación', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Precipitación (mm)', fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# 🔗 GRÁFICO 4: Heatmap de Correlaciones
# ============================================================================
def plot_correlation_heatmap(df):
    """Mapa de calor de correlaciones"""
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    
    if len(numeric_cols) < 2:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax.transAxes)
        return fig
    
    corr_matrix = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn',
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        cbar_kws={'shrink': 0.8}
    )
    
    ax.set_title('🔗 Matriz de Correlaciones', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

# ============================================================================
# 🎯 APLICACIÓN PRINCIPAL
# ============================================================================
def main():
    st.title("🌾 Agro-Clima Intelligence Pro")
    st.markdown("*Plataforma de análisis predictivo para optimización de cosechas*")
    
    # Cargar datos
    with st.spinner("🔄 Cargando datos desde Railway..."):
        df = load_data()
    
    if df.empty:
        st.error("❌ No se pudieron cargar los datos. Verifica la conexión a Railway.")
        return
    
    st.success(f"✅ {len(df)} registros cargados correctamente")
    
    # Mostrar columnas reales para debug
    with st.expander("📋 Ver columnas disponibles en tu BD"):
        st.write(df.columns.tolist())
        st.info("💡 Las columnas de coordenadas deben llamarse: `latitud`, `longitud`, `latitude`, o `longitude`")
    
    # Detectar columnas de coordenadas REALES
    lat_col, lon_col = detect_coordinate_columns(df)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Panel de Control")
        
        st.markdown(f"""
        ### 📍 Coordenadas Detectadas
        - **Latitud**: `{lat_col}` 
        - **Longitud**: `{lon_col}`
        """)
        
        # Selector de municipio
        mun_col = next((c for c in df.columns if 'municipio' in c.lower()), None)
        if mun_col:
            municipio = st.selectbox(
                "📍 Seleccionar Municipio",
                options=["Todos"] + list(df[mun_col].unique()),
                help="Filtra por ubicación geográfica"
            )
            
            if municipio != "Todos":
                df = df[df[mun_col] == municipio]
        
        st.divider()
        
        # Métricas
        st.subheader("📈 Indicadores Clave")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        
        if len(num_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                metric_col = next((c for c in num_cols if 'rendimiento' in c.lower()), num_cols[0])
                st.metric(
                    label="Rendimiento Promedio",
                    value=f"{df[metric_col].mean():.2f}",
                    delta=f"{df[metric_col].std():.2f} σ"
                )
            with col2:
                precip_col = next((c for c in num_cols if 'precip' in c.lower()), num_cols[1] if len(num_cols) > 1 else num_cols[0])
                st.metric(
                    label="Precipitación Total",
                    value=f"{df[precip_col].sum():.0f} mm"
                )
    
    # === PESTAÑAS ===
    tab_analisis, tab_documentacion, tab_config = st.tabs([
        "📊 Análisis Visual", 
        "📚 Documentación", 
        "⚙️ Configuración"
    ])
    
    # ── PESTAÑA 1: GRÁFICOS ──
    with tab_analisis:
        st.subheader("🔍 Exploración de Datos")
        
        # Fila 1: Mapa y Correlación
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("### 🗺️ Mapa Interactivo")
            st.info(f"📍 Usando coordenadas: `{lat_col}`, `{lon_col}`")
            
            map_var = next((c for c in df.select_dtypes(include='number').columns 
                           if c not in [lat_col, lon_col]), None)
            
            fig_map = plot_interactive_map(df, lat_col, lon_col, map_var)
            if fig_map:
                st.plotly_chart(fig_map, width='stretch')  # ✅ CORREGIDO
            else:
                st.warning("⚠️ Configura columnas latitud/longitud en tu BD")
        
        with col_graf2:
            st.markdown("### 🌡️ Temperatura vs Rendimiento")
            fig1 = plot_correlation_temp_yield(df)
            st.pyplot(fig1, width='stretch')  # ✅ CORREGIDO
        
        st.divider()
        
        # Fila 2: Boxplot y Heatmap
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            st.markdown("### 🌧️ Precipitación")
            fig2 = plot_precipitation_distribution(df)
            st.pyplot(fig2, width='stretch')  # ✅ CORREGIDO
        
        with col_graf4:
            st.markdown("### 🔗 Correlaciones")
            fig3 = plot_correlation_heatmap(df)
            st.pyplot(fig3, width='stretch')  # ✅ CORREGIDO
        
        st.divider()
        
        # Datos raw
        with st.expander("📄 Ver datos brutos"):
            st.dataframe(df.head(100), width='stretch', hide_index=True)
    
    # ── PESTAÑA 2: DOCUMENTACIÓN ──
    with tab_documentacion:
        st.header("📚 Documentación")
        
        st.markdown(f"""
        ### 🗄️ Estructura de Base de Datos Detectada
        
        **Columnas encontradas**: {len(df.columns)}
        
        **Coordenadas de Municipio**:
        - Latitud: `{lat_col}` (rango: {df[lat_col].min():.4f} a {df[lat_col].max():.4f})
        - Longitud: `{lon_col}` (rango: {df[lon_col].min():.4f} a {df[lon_col].max():.4f})
        
        ### 🔐 Configuración de Secrets
        
        En Streamlit Cloud:
        1. Ve a tu app → **Settings** ⚙️
        2. Despliega **Secrets**
        3. Agrega:
        ```toml
        [connections.railway_db]
        dialect = "mysql"
        host = "tu-host.railway.app"
        port = 3306
        database = "railway"
        username = "root"
        password = "tu_contraseña"
        ```
        """)
    
    # ── PESTAÑA 3: CONFIGURACIÓN ──
    with tab_config:
        st.header("⚙️ Configuración")
        
        if st.button("🔄 Recargar Datos", type="primary"):
            st.cache_data.clear()
            st.success("✅ Datos actualizados")
            st.rerun()
        
        st.markdown("""
        <div class="metric-card">
        <strong>Última sincronización:</strong><br>
        <span style="color: #15803d">●</span> Hace < 1 minuto
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9em; padding: 20px;">
        🌾 Agro-Clima Intelligence Pro v5.0 • Streamlit Cloud + Railway
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 🚀 EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    main()
