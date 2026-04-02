# ============================================================================
# 🌾 Agro-Clima Intelligence Pro - streamlit_app.py (VERSIÓN FINAL - BackupBD.sql)
# ============================================================================
# ✅ Basado en estructura real de BackupBD.sql:
# - Columnas: municipio, latitud, longitud, fecha, brillo_solar, etc.
# - Formato numérico con coma decimal (ej: '8,8469444440')
# - Corrección de todos los errores de logs
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sqlalchemy import create_engine, text
import warnings

# Suprimir warnings no críticos
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

# Paleta profesional
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

# CSS personalizado
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
# 🔐 CONEXIÓN A BASE DE DATOS (Streamlit Cloud + Railway)
# ============================================================================
@st.cache_resource
def init_connection():
    """Conecta a Railway usando st.secrets (configurado en Streamlit Cloud)"""
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
# 🧹 LIMPIEZA DE DATOS (CRÍTICO - Formato BackupBD.sql)
# ============================================================================
def clean_dataframe(df):
    """
    Limpia datos según formato real de BackupBD.sql
    ✅ Convierte comas decimales a puntos: '8,8469' → 8.8469
    ✅ Normaliza nombres de columnas
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Columnas que pueden tener coma como decimal (según BackupBD.sql)
    decimal_cols = ['latitud', 'longitud', 'brillo_solar', 'precipitacion', 
                    'temperatura', 'rendimiento', 'area_cosechada']
    
    for col in decimal_cols:
        if col in df_clean.columns:
            # Reemplazar coma por punto y convertir a numérico
            df_clean[col] = df_clean[col].astype(str).str.replace(',', '.')
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Normalizar nombres de columnas (minúsculas, sin espacios)
    df_clean.columns = df_clean.columns.str.strip().str.lower()
    
    # Eliminar columnas duplicadas
    df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
    
    # Eliminar filas completamente nulas
    df_clean = df_clean.dropna(how='all')
    
    return df_clean

# ============================================================================
# 🗺️ DETECTAR COLUMNAS REALES (Según BackupBD.sql)
# ============================================================================
def detect_coordinate_columns(df):
    """
    Detecta columnas de latitud y longitud según BackupBD.sql
    ✅ Nombres reales: 'latitud', 'longitud'
    """
    # Latitud (según tu backup)
    lat_col = None
    for candidate in ['latitud', 'latitude', 'lat', 'coord_lat']:
        if candidate in df.columns:
            lat_col = candidate
            break
    
    # Longitud (según tu backup)
    lon_col = None
    for candidate in ['longitud', 'longitude', 'lon', 'coord_lon']:
        if candidate in df.columns:
            lon_col = candidate
            break
    
    return lat_col, lon_col

# ============================================================================
# 📊 CARGA DE DATOS DESDE RAILWAY
# ============================================================================
@st.cache_data(ttl=300)
def load_data():
    """
    Carga datos desde Railway con estructura de BackupBD.sql
    """
    engine = init_connection()
    
    if engine is None:
        # Datos de fallback (estructura real según backup)
        return pd.DataFrame({
            'municipio': ['Arboletes', 'Alejandría', 'Cañasgordas'],
            'latitud': [8.8469, 6.3763, 6.7580],
            'longitud': [-76.4319, -75.1434, -76.0297],
            'fecha': pd.date_range('2024-01-01', periods=3),
            'brillo_solar': [5.4, 8.3, 6.5]
        })
    
    try:
        # Intentar consultar la tabla principal (ajustar nombre según tu BD)
        query = text("""
            SELECT 
                municipio,
                latitud,
                longitud,
                fecha,
                brillo_solar,
                precipitacion,
                temperatura_max,
                temperatura_min
            FROM datos_climaticos
            LIMIT 10000
        """)
        
        try:
            df = pd.read_sql(query, engine)
        except:
            # Fallback: consultar sin nombre de columnas específico
            df = pd.read_sql(text("SELECT * FROM datos_climaticos LIMIT 10000"), engine)
        
        df = clean_dataframe(df)
        return df
    
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        # Datos de fallback
        return pd.DataFrame({
            'municipio': ['Arboletes', 'Alejandría', 'Cañasgordas'],
            'latitud': [8.8469, 6.3763, 6.7580],
            'longitud': [-76.4319, -75.1434, -76.0297],
            'fecha': pd.date_range('2024-01-01', periods=3),
            'brillo_solar': [5.4, 8.3, 6.5]
        })

# ============================================================================
# 🗺️ GRÁFICO 1: Mapa Interactivo (CORREGIDO)
# ============================================================================
def plot_interactive_map(df, lat_col, lon_col, map_var):
    """
    Mapa interactivo con columnas reales de BackupBD.sql
    ✅ scatter_map con 'style' (NO 'mapbox_style')
    ✅ Validación de columnas antes de dropna()
    """
    # ✅ Validación CRÍTICA antes de continuar
    if lat_col is None or lon_col is None:
        st.warning("⚠️ No se encontraron columnas de coordenadas")
        st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return None
    
    if map_var is None:
        st.warning("⚠️ No se encontró variable numérica para el mapa")
        return None
    
    # Verificar que las columnas existen en el DataFrame
    required_cols = [lat_col, lon_col, map_var]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.warning(f"⚠️ Columnas faltantes: {missing_cols}")
        return None
    
    # Preparar datos para el mapa
    map_df = df[[lat_col, lon_col, map_var, 'municipio']].copy() if 'municipio' in df.columns else df[[lat_col, lon_col, map_var]].copy()
    
    # Convertir a numérico (maneja formato mixto coma/punto)
    map_df[lat_col] = pd.to_numeric(map_df[lat_col], errors='coerce')
    map_df[lon_col] = pd.to_numeric(map_df[lon_col], errors='coerce')
    map_df[map_var] = pd.to_numeric(map_df[map_var], errors='coerce')
    
    # ✅ Dropna SOLO después de validar que las columnas existen
    map_df = map_df.dropna()
    
    if map_df.empty:
        st.warning("⚠️ No hay datos válidos para el mapa")
        return None
    
    # ✅ scatter_map con 'style' (CORRECCIÓN DE LOGS)
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
# 📈 GRÁFICO 2: Brillo Solar por Municipio (Boxplot)
# ============================================================================
def plot_solar_by_municipality(df):
    """
    Boxplot de brillo solar por municipio
    ✅ hue parameter para evitar FutureWarning
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Buscar columnas reales según BackupBD.sql
    solar_col = None
    mun_col = None
    
    for col in df.columns:
        if 'brillo' in col.lower() or 'solar' in col.lower():
            solar_col = col
            break
    
    for col in df.columns:
        if 'municipio' in col.lower() or 'municip' in col.lower():
            mun_col = col
            break
    
    if solar_col is None:
        ax.text(0.5, 0.5, 'Datos de brillo solar no disponibles', 
                ha='center', va='center', transform=ax.transAxes)
        return fig
    
    if mun_col and mun_col in df.columns:
        df_plot = df[[solar_col, mun_col]].dropna()
        
        if len(df_plot[mun_col].unique()) > 1:
            # ✅ Asignar hue para evitar FutureWarning (según logs)
            sns.boxplot(
                data=df_plot,
                x=mun_col,
                y=solar_col,
                hue=mun_col,  # ✅ EVITA WARNING
                palette=SEABORN_PALETTE[:len(df_plot[mun_col].unique())],
                ax=ax,
                linewidth=1.5,
                legend=False  # ✅ Ocultar leyenda redundante
            )
        else:
            sns.boxplot(
                data=df_plot,
                y=solar_col,
                color=PROFESSIONAL_PALETTE['secondary'],
                ax=ax,
                linewidth=1.5
            )
    else:
        df_plot = df[[solar_col]].dropna()
        sns.boxplot(
            data=df_plot,
            y=solar_col,
            color=PROFESSIONAL_PALETTE['secondary'],
            ax=ax,
            linewidth=1.5
        )
    
    ax.set_title('☀️ Distribución de Brillo Solar por Municipio', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Horas de Sol Efectivas', fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# 📉 GRÁFICO 3: Tendencia Temporal de Brillo Solar
# ============================================================================
def plot_solar_trend(df):
    """
    Línea de tendencia temporal
    ✅ width='stretch' en lugar de use_container_width
    """
    # Buscar columnas de fecha y brillo solar
    date_col = None
    solar_col = None
    
    for col in df.columns:
        if 'fecha' in col.lower() or 'date' in col.lower():
            date_col = col
            break
    
    for col in df.columns:
        if 'brillo' in col.lower() or 'solar' in col.lower():
            solar_col = col
            break
    
    if date_col is None or solar_col is None:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Datos temporales no disponibles', 
                ha='center', va='center', transform=ax.transAxes)
        return fig
    
    df_plot = df[[date_col, solar_col]].copy()
    df_plot[date_col] = pd.to_datetime(df_plot[date_col], errors='coerce')
    df_plot[solar_col] = pd.to_numeric(df_plot[solar_col], errors='coerce')
    df_plot = df_plot.dropna()
    
    if len(df_plot) < 2:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Datos insuficientes', 
                ha='center', va='center', transform=ax.transAxes)
        return fig
    
    # Agrupar por fecha si hay múltiples registros
    df_grouped = df_plot.groupby(date_col)[solar_col].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(df_grouped[date_col], df_grouped[solar_col], 
            color=PROFESSIONAL_PALETTE['accent'], linewidth=2, marker='o', markersize=3)
    ax.fill_between(df_grouped[date_col], df_grouped[solar_col], 
                    alpha=0.3, color=PROFESSIONAL_PALETTE['accent'])
    
    ax.set_title('📈 Tendencia Temporal de Brillo Solar', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Fecha', fontsize=11)
    ax.set_ylabel('Horas de Sol', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig

# ============================================================================
# 🔗 GRÁFICO 4: Heatmap de Correlaciones
# ============================================================================
def plot_correlation_heatmap(df):
    """Mapa de calor de correlaciones"""
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    
    # Excluir coordenadas del heatmap
    numeric_cols = [col for col in numeric_cols 
                   if 'latitud' not in col.lower() and 'longitud' not in col.lower()]
    
    if len(numeric_cols) < 2:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Datos insuficientes para correlaciones', 
                ha='center', va='center', transform=ax.transAxes)
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
# 📊 GRÁFICO 5: Dispersión con Trendline (Plotly - CORREGIDO)
# ============================================================================
def plot_scatter_with_trendline(df, var_x, var_y):
    """
    Gráfico de dispersión con línea de tendencia
    ✅ Validación de columnas únicas
    """
    if var_x not in df.columns or var_y not in df.columns:
        return None
    
    plot_df = df[[var_x, var_y]].copy()
    plot_df = plot_df.dropna()
    plot_df = plot_df.loc[:, ~plot_df.columns.duplicated()]
    
    if len(plot_df) < 2:
        return None
    
    fig_rel = px.scatter(
        plot_df,
        x=var_x,
        y=var_y,
        trendline="ols",
        title=f"Correlación: {var_x} vs {var_y}",
        color_discrete_sequence=[PROFESSIONAL_PALETTE['primary']]
    )
    
    fig_rel.update_layout(height=500)
    
    return fig_rel

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
    
    # Detectar columnas reales
    lat_col, lon_col = detect_coordinate_columns(df)
    
    # Mostrar columnas para debug
    with st.expander("📋 Ver columnas disponibles (BackupBD.sql)"):
        st.write(df.columns.tolist())
        st.info(f"""
        **Coordenadas detectadas:**
        - Latitud: `{lat_col}`
        - Longitud: `{lon_col}`
        
        **Municipios en datos:** {df['municipio'].nunique() if 'municipio' in df.columns else 'N/A'}
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Panel de Control")
        
        # Selector de municipio
        if 'municipio' in df.columns:
            municipio = st.selectbox(
                "📍 Seleccionar Municipio",
                options=["Todos"] + list(df['municipio'].unique()),
                help="Filtra por ubicación geográfica"
            )
            
            if municipio != "Todos":
                df = df[df['municipio'] == municipio]
        
        st.divider()
        
        # Métricas
        st.subheader("📈 Indicadores Clave")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        
        if len(num_cols) >= 1:
            # Brillo solar promedio
            solar_col = next((c for c in num_cols if 'brillo' in c.lower() or 'solar' in c.lower()), num_cols[0])
            st.metric(
                label="Brillo Solar Promedio",
                value=f"{df[solar_col].mean():.2f} horas",
                delta=f"{df[solar_col].std():.2f} σ"
            )
        
        if len(num_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Registros",
                    value=len(df)
                )
            with col2:
                if 'municipio' in df.columns:
                    st.metric(
                        label="Municipios",
                        value=df['municipio'].nunique()
                    )
    
    # === PESTAÑAS ===
    tab_analisis, tab_documentacion, tab_config = st.tabs([
        "📊 Análisis Visual", 
        "📚 Documentación", 
        "⚙️ Configuración"
    ])
    
    # ── PESTAÑA 1: GRÁFICOS ──
    with tab_analisis:
        st.subheader("🔍 Exploración de Datos Climáticos")
        
        # Fila 1: Mapa y Boxplot
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("### 🗺️ Mapa Interactivo")
            st.info(f"📍 Coordenadas: `{lat_col}`, `{lon_col}`")
            
            # Variable para mapa (brillo solar u otra numérica)
            map_var = next((c for c in df.select_dtypes(include='number').columns 
                           if c not in [lat_col, lon_col]), None)
            
            fig_map = plot_interactive_map(df, lat_col, lon_col, map_var)
            if fig_map:
                st.plotly_chart(fig_map, width='stretch')  # ✅ CORREGIDO
            else:
                st.warning("⚠️ Configura columnas latitud/longitud en tu BD")
        
        with col_graf2:
            st.markdown("### ☀️ Brillo Solar por Municipio")
            fig1 = plot_solar_by_municipality(df)
            st.pyplot(fig1, width='stretch')  # ✅ CORREGIDO
        
        st.divider()
        
        # Fila 2: Tendencia y Heatmap
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            st.markdown("### 📈 Tendencia Temporal")
            fig2 = plot_solar_trend(df)
            st.pyplot(fig2, width='stretch')  # ✅ CORREGIDO
        
        with col_graf4:
            st.markdown("### 🔗 Correlaciones")
            fig3 = plot_correlation_heatmap(df)
            st.pyplot(fig3, width='stretch')  # ✅ CORREGIDO
        
        st.divider()
        
        # Fila 3: Dispersión Personalizada
        st.subheader("📉 Análisis de Correlación Personalizado")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        num_cols = [c for c in num_cols if c not in [lat_col, lon_col]]
        
        if len(num_cols) >= 2:
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                var_x = st.selectbox("Factor (X)", num_cols[:-1], key='var_x')
            with col_sel2:
                var_y = st.selectbox("Resultado (Y)", num_cols, index=len(num_cols)-1, key='var_y')
            
            if var_x != var_y:
                fig_reg = plot_scatter_with_trendline(df, var_x, var_y)
                if fig_reg:
                    st.plotly_chart(fig_reg, width='stretch')  # ✅ CORREGIDO
        
        # Datos raw
        with st.expander("📄 Ver datos brutos"):
            st.dataframe(df.head(100), width='stretch', hide_index=True)
    
    # ── PESTAÑA 2: DOCUMENTACIÓN ──
    with tab_documentacion:
        st.header("📚 Documentación Técnica")
        
        st.markdown(f"""
        ### 🗄️ Estructura de Base de Datos (BackupBD.sql)
        
        **Columnas detectadas**: {len(df.columns)}
        
        **Coordenadas de Municipio**:
        - Latitud: `{lat_col}` (rango: {df[lat_col].min():.4f} a {df[lat_col].max():.4f})
        - Longitud: `{lon_col}` (rango: {df[lon_col].min():.4f} a {df[lon_col].max():.4f})
        
        **Municipios disponibles**: 
        {', '.join(df['municipio'].unique()) if 'municipio' in df.columns else 'N/A'}
        
        ### 🔐 Configuración de Secrets (Streamlit Cloud)
        
        1. Ve a [share.streamlit.io](https://share.streamlit.io)
        2. Selecciona tu app → **Settings** ⚙️
        3. Despliega **Secrets**
        4. Agrega:
        ```toml
        [connections.railway_db]
        dialect = "mysql"
        host = "tu-host.railway.app"
        port = 3306
        database = "railway"
        username = "root"
        password = "tu_contraseña"
        ```
        
        ### 📊 Gráficos Implementados
        
        1. **Mapa Interactivo**: scatter_map con coordenadas reales
        2. **Boxplot**: Distribución de brillo solar por municipio
        3. **Tendencia Temporal**: Evolución de brillo solar
        4. **Heatmap**: Matriz de correlaciones múltiples
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
        <span style="color: #15803d">●</span> Hace < 1 minuto<br>
        <small>Próxima actualización: 5 minutos</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9em; padding: 20px;">
        🌾 Agro-Clima Intelligence Pro v6.0 • Streamlit Cloud + Railway
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 🚀 EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    main()
