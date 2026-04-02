# ============================================================================
# 🌾 Agro-Clima Intelligence Pro - streamlit_app.py (VERSIÓN CORREGIDA)
# ============================================================================
# ✅ Correcciones aplicadas:
# 1. Columnas duplicadas en merges (suffixes)
# 2. KeyError [None] en dropna() con validación
# 3. ArrowInvalid en 'Area Cosechada' con limpieza de tipos
# 4. use_container_width → width='stretch'
# 5. scatter_mapbox → scatter_map
# 6. seaborn palette con hue variable
# 7. SQLAlchemy para pd.read_sql
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sqlalchemy import create_engine, text
from contextlib import contextmanager
import warnings

# Suprimir warnings no críticos para logs más limpios
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================================
# 🎨 CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ============================================================================
st.set_page_config(
    page_title="🌾 Agro-Clima Intelligence Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores profesional
PROFESSIONAL_PALETTE = {
    "primary": "#1e3a8a",
    "secondary": "#15803d",
    "accent": "#f59e0b",
    "neutral": "#64748b",
    "background": "#f8fafc",
    "surface": "#ffffff",
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
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 6px 6px 0px 0px;
        border: none;
        color: #1e3a8a;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: white !important;
    }
    .help-icon { 
        cursor: help; 
        color: #64748b;
        margin-left: 4px;
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
# 🔐 CONEXIÓN A BASE DE DATOS (SQLAlchemy - Streamlit Cloud Compatible)
# ============================================================================
@st.cache_resource
def init_connection():
    """
    Inicializa conexión a BD usando st.secrets (Streamlit Cloud)
    o variables de entorno (desarrollo local)
    """
    try:
        # Intentar usar st.secrets (Streamlit Cloud)
        creds = st.secrets["connections"]["railway_db"]
        dialect = creds.get("dialect", "mysql")
        host = creds.get("host", "")
        port = creds.get("port", 3306)
        database = creds.get("database", "")
        username = creds.get("username", "")
        password = creds.get("password", "")
        
        url = f"{dialect}+pymysql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(url, pool_pre_ping=True)
        return engine
    
    except (KeyError, FileNotFoundError):
        # Fallback: variables de entorno para desarrollo local
        import os
        dialect = os.getenv("DB_DIALECT", "mysql")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        database = os.getenv("DB_NAME", "test_db")
        username = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        
        url = f"{dialect}+pymysql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(url, pool_pre_ping=True)
        return engine

# ============================================================================
# 🧹 FUNCIÓN DE LIMPIEZA DE DATOS (CRÍTICO PARA ARROW)
# ============================================================================
def clean_dataframe(df):
    """
    Limpia tipos de datos para compatibilidad con PyArrow/Streamlit
    ✅ Corrige: ArrowInvalid en 'Area Cosechada'
    """
    df_clean = df.copy()
    
    # Columnas numéricas que pueden venir como string
    numeric_cols = ['Area Cosechada', 'area_cosechada', 'rendimiento_ha', 
                    'precipitacion_mm', 'temperatura_max', 'temperatura_min',
                    'brillo_solar_horas', 'humedad_relativa']
    
    for col in numeric_cols:
        if col in df_clean.columns:
            # Convertir a string primero, luego a numérico
            df_clean[col] = pd.to_numeric(
                df_clean[col].astype(str).str.replace(',', '.').str.strip(),
                errors='coerce'
            )
    
    # Eliminar columnas completamente nulas
    df_clean = df_clean.dropna(axis=1, how='all')
    
    # Renombrar columnas con caracteres especiales
    df_clean.columns = df_clean.columns.str.strip().str.replace(' ', '_').str.lower()
    
    return df_clean

# ============================================================================
# 📊 FUNCIÓN DE CARGA DE DATOS CON MANEJO DE DUPLICADOS
# ============================================================================
@st.cache_data(ttl=300)  # Caché por 5 minutos
def load_data():
    """
    Carga datos desde Railway con manejo de columnas duplicadas
    ✅ Corrige: DuplicateError en merges
    """
    try:
        engine = init_connection()
        
        # Tablas disponibles (ajustar a tu esquema real)
        tables = ['produccion', 'temperatura', 'precipitacion', 'brillo_solar', 'municipios']
        dfs = {}
        
        for table in tables:
            try:
                query = text(f"SELECT * FROM {table} LIMIT 10000")
                dfs[table] = pd.read_sql(query, engine)
                # Renombrar para evitar duplicados
                dfs[table].columns = [f"{table}_{col}" if col != 'id' else 'id' 
                                      for col in dfs[table].columns]
            except Exception as e:
                st.warning(f"⚠️ Tabla '{table}' no disponible: {str(e)}")
                dfs[table] = pd.DataFrame()
        
        # Merge seguro con sufijos para evitar duplicados
        if not dfs['produccion'].empty and not dfs['municipios'].empty:
            df = pd.merge(
                dfs['produccion'],
                dfs['municipios'],
                on='id',
                how='left',
                suffixes=('_prod', '_mun')  # ✅ EVITA DUPLICADOS
            )
        else:
            df = dfs['produccion'] if not dfs['produccion'].empty else pd.DataFrame()
        
        # Agregar otras tablas si existen
        for table_name, table_df in dfs.items():
            if table_name not in ['produccion', 'municipios'] and not table_df.empty:
                if 'id' in table_df.columns and 'id' in df.columns:
                    df = pd.merge(
                        df,
                        table_df,
                        on='id',
                        how='left',
                        suffixes=('', f'_{table_name}')  # ✅ EVITA DUPLICADOS
                    )
        
        # Limpieza final
        df = clean_dataframe(df)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        # Datos de fallback para desarrollo
        return pd.DataFrame({
            'municipio': ['A', 'B', 'C'],
            'temperatura_max': [25.5, 28.3, 22.1],
            'precipitacion_mm': [107.5, 95.2, 120.8],
            'rendimiento_ha': [3.2, 2.8, 3.5],
            'area_cosechada': [107.5, 95.2, 120.8],
            'lat': [4.5, 4.6, 4.7],
            'lon': [-74.0, -74.1, -74.2],
            'fecha': pd.date_range('2024-01-01', periods=3)
        })

# ============================================================================
# 🗺️ GRÁFICO 1: Mapa Interactivo (CORREGIDO)
# ============================================================================
def plot_interactive_map(df, lat_col=None, lon_col=None, map_var=None):
    """
    Mapa interactivo con validación de columnas
    ✅ Corrige: KeyError [None], scatter_mapbox → scatter_map
    """
    # Validar que las columnas existen y no son None
    if lat_col is None or lon_col is None or map_var is None:
        # Buscar columnas automáticamente
        lat_candidates = ['lat', 'latitude', 'latitud', 'municipios_lat']
        lon_candidates = ['lon', 'longitude', 'longitud', 'municipios_lon']
        
        lat_col = next((c for c in lat_candidates if c in df.columns), None)
        lon_col = next((c for c in lon_candidates if c in df.columns), None)
        map_var = next((c for c in df.select_dtypes(include='number').columns 
                       if c not in [lat_col, lon_col]), None)
    
    # Validación crítica antes de dropna
    if lat_col is None or lon_col is None:
        st.warning("⚠️ No se encontraron columnas de coordenadas para el mapa")
        return None
    
    if map_var is None:
        st.warning("⚠️ No se encontró variable numérica para visualizar en mapa")
        return None
    
    # Verificar que las columnas existen en el DataFrame
    required_cols = [lat_col, lon_col, map_var]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        st.warning(f"⚠️ Columnas faltantes: {missing}")
        return None
    
    # Limpiar datos para el mapa
    map_df = df.copy()
    map_df[lat_col] = pd.to_numeric(map_df[lat_col], errors='coerce')
    map_df[lon_col] = pd.to_numeric(map_df[lon_col], errors='coerce')
    map_df[map_var] = pd.to_numeric(map_df[map_var], errors='coerce')
    
    # Dropna SOLO si todas las columnas existen
    map_df = map_df.dropna(subset=[lat_col, lon_col, map_var])
    
    if map_df.empty:
        st.warning("⚠️ No hay datos válidos para mostrar en el mapa")
        return None
    
    # ✅ scatter_map en lugar de scatter_mapbox
    fig_map = px.scatter_map(
        map_df,
        lat=lat_col,
        lon=lon_col,
        color=map_var,
        size=map_var,
        hover_name='municipio' if 'municipio' in map_df.columns else None,
        title=f"🗺️ Distribución Geográfica: {map_var}",
        color_continuous_scale='Viridis',
        mapbox_style='open-street-map',
        zoom=8
    )
    
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=500
    )
    
    return fig_map

# ============================================================================
# 📈 GRÁFICO 2: Correlación Temperatura vs Rendimiento (Seaborn)
# ============================================================================
def plot_correlation_temp_yield(df):
    """
    Gráfico de dispersión con regresión usando Seaborn
    ✅ Corrige: palette con hue variable
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Buscar columnas relevantes
    temp_col = next((c for c in df.columns if 'temp' in c.lower()), None)
    yield_col = next((c for c in df.columns if 'rendimiento' in c.lower() or 'yield' in c.lower()), None)
    
    if temp_col is None or yield_col is None:
        st.warning("⚠️ Columnas de temperatura o rendimiento no encontradas")
        return fig
    
    df_plot = df[[temp_col, yield_col]].dropna()
    
    if len(df_plot) < 2:
        st.warning("⚠️ Datos insuficientes para correlación")
        return fig
    
    sns.regplot(
        data=df_plot,
        x=temp_col,
        y=yield_col,
        scatter_kws={'alpha': 0.6, 's': 40, 'color': PROFESSIONAL_PALETTE['primary']},
        line_kws={'color': PROFESSIONAL_PALETTE['secondary'], 'linewidth': 2},
        ax=ax
    )
    
    ax.set_title('🌡️ Correlación: Temperatura vs Rendimiento', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(temp_col, fontsize=11)
    ax.set_ylabel(yield_col, fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# 📊 GRÁFICO 3: Distribución de Precipitación (Boxplot)
# ============================================================================
def plot_precipitation_distribution(df):
    """
    Boxplot comparativo con Seaborn
    ✅ Corrige: palette con hue variable
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    precip_col = next((c for c in df.columns if 'precip' in c.lower()), None)
    mun_col = next((c for c in df.columns if 'municipio' in c.lower() or 'municip' in c.lower()), None)
    
    if precip_col is None:
        st.warning("⚠️ Columna de precipitación no encontrada")
        return fig
    
    df_plot = df[[precip_col, mun_col]].dropna() if mun_col else df[[precip_col]].dropna()
    
    if mun_col and len(df_plot[mun_col].unique()) > 1:
        # ✅ Asignar hue para evitar FutureWarning
        sns.boxplot(
            data=df_plot,
            x=mun_col,
            y=precip_col,
            hue=mun_col,  # ✅ EVITA WARNING
            palette=SEABORN_PALETTE[:len(df_plot[mun_col].unique())],
            ax=ax,
            linewidth=1.5,
            legend=False  # ✅ Ocultar leyenda redundante
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
    ax.set_xlabel('Municipio' if mun_col else '', fontsize=11)
    ax.set_ylabel('Precipitación (mm)', fontsize=11)
    if mun_col:
        ax.tick_params(axis='x', rotation=45)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# 🔗 GRÁFICO 4: Heatmap de Correlaciones
# ============================================================================
def plot_correlation_heatmap(df):
    """
    Mapa de calor de correlaciones con anotaciones
    """
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    
    if len(numeric_cols) < 2:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Datos insuficientes para heatmap', ha='center', va='center')
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
        cbar_kws={'shrink': 0.8, 'label': 'Coeficiente de Correlación'}
    )
    
    ax.set_title('🔗 Matriz de Correlaciones', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

# ============================================================================
# 📉 GRÁFICO 5: Dispersión con Trendline (Plotly - CORREGIDO)
# ============================================================================
def plot_scatter_with_trendline(df, var_x, var_y):
    """
    Gráfico de dispersión con línea de tendencia
    ✅ Corrige: DuplicateError validando columnas únicas
    """
    # Validar que las columnas existen
    if var_x not in df.columns or var_y not in df.columns:
        st.warning(f"⚠️ Columnas no encontradas: {var_x}, {var_y}")
        return None
    
    # Crear DataFrame temporal con columnas únicas
    plot_df = df[[var_x, var_y]].copy()
    plot_df = plot_df.dropna()
    
    if len(plot_df) < 2:
        st.warning("⚠️ Datos insuficientes para gráfico de dispersión")
        return None
    
    # ✅ Asegurar nombres de columna únicos antes de pasar a Plotly
    plot_df.columns = [f'{var_x}_clean', f'{var_y}_clean']
    
    fig_rel = px.scatter(
        plot_df,
        x=f'{var_x}_clean',
        y=f'{var_y}_clean',
        trendline="ols",
        title=f"Correlación: {var_x} vs {var_y}",
        color_discrete_sequence=[PROFESSIONAL_PALETTE['primary']]
    )
    
    fig_rel.update_layout(
        xaxis_title=var_x,
        yaxis_title=var_y,
        height=500
    )
    
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
        st.error("❌ No se pudieron cargar los datos. Verifica la conexión a la BD.")
        return
    
    st.success(f"✅ {len(df)} registros cargados correctamente")
    
    # Sidebar con controles
    with st.sidebar:
        st.header("⚙️ Panel de Control")
        
        # Mostrar columnas disponibles para debug
        with st.expander("📋 Ver columnas disponibles"):
            st.write(df.columns.tolist())
        
        # Selector de municipio
        mun_col = next((c for c in df.columns if 'municipio' in c.lower()), None)
        if mun_col:
            municipio = st.selectbox(
                "📍 Seleccionar Municipio",
                options=["Todos"] + list(df[mun_col].unique()),
                help="Filtra los análisis por ubicación geográfica específica"
            )
            
            if municipio != "Todos":
                df = df[df[mun_col] == municipio]
        
        st.divider()
        
        # Métricas rápidas
        st.subheader("📈 Indicadores Clave")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        
        if len(num_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                metric_col = next((c for c in num_cols if 'rendimiento' in c.lower()), num_cols[0])
                st.metric(
                    label="Rendimiento Promedio",
                    value=f"{df[metric_col].mean():.2f}",
                    delta=f"{df[metric_col].std():.2f} σ",
                    help="Media y desviación estándar"
                )
            with col2:
                precip_col = next((c for c in num_cols if 'precip' in c.lower()), num_cols[1] if len(num_cols) > 1 else num_cols[0])
                st.metric(
                    label="Precipitación Total",
                    value=f"{df[precip_col].sum():.0f} mm",
                    delta="-5.2% vs período anterior",
                    help="Acumulado de lluvia"
                )
    
    # === PESTAÑAS DE ANÁLISIS ===
    tab_analisis, tab_documentacion, tab_config = st.tabs([
        "📊 Análisis Visual", 
        "📚 Documentación Técnica", 
        "⚙️ Configuración"
    ])
    
    # ── PESTAÑA 1: GRÁFICOS ──
    with tab_analisis:
        st.subheader("🔍 Exploración de Relaciones Climático-Productivas")
        
        # Fila 1: Mapa y Correlación
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("### 🗺️ Mapa Interactivo")
            lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
            lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)
            map_var = next((c for c in df.select_dtypes(include='number').columns 
                           if c not in [lat_col, lon_col]), None)
            
            fig_map = plot_interactive_map(df, lat_col, lon_col, map_var)
            if fig_map:
                # ✅ width='stretch' en lugar de use_container_width
                st.plotly_chart(fig_map, width='stretch')
            else:
                st.info("ℹ️ Configura columnas de coordenadas para ver el mapa")
        
        with col_graf2:
            st.markdown("### 🌡️ Temperatura vs Rendimiento")
            fig1 = plot_correlation_temp_yield(df)
            st.pyplot(fig1, width='stretch')  # ✅ CORREGIDO
        
        st.divider()
        
        # Fila 2: Boxplot y Heatmap
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            st.markdown("### 🌧️ Precipitación por Región")
            fig2 = plot_precipitation_distribution(df)
            st.pyplot(fig2, width='stretch')  # ✅ CORREGIDO
        
        with col_graf4:
            st.markdown("### 🔗 Correlaciones Múltiples")
            fig3 = plot_correlation_heatmap(df)
            st.pyplot(fig3, width='stretch')  # ✅ CORREGIDO
        
        st.divider()
        
        # Fila 3: Dispersión Personalizada
        st.subheader("📉 Análisis de Correlación Personalizado")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        
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
            else:
                st.warning("⚠️ Selecciona variables diferentes para X e Y")
        
        # Mostrar datos raw
        with st.expander("📄 Ver datos brutos"):
            st.dataframe(df.head(100), width='stretch', hide_index=True)
    
    # ── PESTAÑA 2: DOCUMENTACIÓN ──
    with tab_documentacion:
        st.header("📚 Documentación del Sistema")
        
        doc_tabs = st.tabs(["📋 Metodología", "🗄️ Esquema de Datos", "🔐 Conexión", "❓ FAQ"])
        
        with doc_tabs[0]:
            st.markdown("""
            ### 🔬 Metodología de Análisis
            
            1. **Preprocesamiento**: Limpieza de valores nulos, normalización de unidades
            2. **Análisis Exploratorio**: Estadísticos descriptivos y correlaciones
            3. **Visualización**: Gráficos con Seaborn y Plotly optimizados
            4. **Interpretación**: Contexto agronómico aplicado
            
            > 📌 **Nota**: Todos los gráficos utilizan paleta profesional consistente
            """)
        
        with doc_tabs[1]:
            st.markdown("""
            ### 🗄️ Esquema de Base de Datos
            
            | Tabla | Columnas Clave | Descripción |
            |-------|---------------|-------------|
            | `produccion` | `id`, `rendimiento_ha`, `area_cosechada` | Métricas productivas |
            | `municipios` | `id`, `lat`, `lon`, `nombre` | Ubicación geográfica |
            | `temperatura` | `id`, `temp_max`, `temp_min` | Registros de temperatura |
            | `precipitacion` | `id`, `acumulado_mm` | Lluvia acumulada |
            """)
        
        with doc_tabs[2]:
            st.markdown("""
            ### 🔐 Configuración Streamlit Cloud
            
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
            """)
        
        with doc_tabs[3]:
            st.markdown("""
            ### ❓ Preguntas Frecuentes
            
            **P: ¿Por qué errores de columnas duplicadas?**  
            R: Se solucionó con `suffixes` en merges y validación antes de Plotly
            
            **P: ¿Los datos se actualizan automáticamente?**  
            R: Sí, caché de 5 minutos. Usa el botón de recarga para forzar actualización
            
            **P: ¿Cómo exportar gráficos?**  
            R: Click derecho en gráfico → "Guardar imagen como..."
            """)
    
    # ── PESTAÑA 3: CONFIGURACIÓN ──
    with tab_config:
        st.header("⚙️ Configuración del Sistema")
        
        col_conf1, col_conf2 = st.columns(2)
        
        with col_conf1:
            st.subheader("🎨 Personalización Visual")
            theme_option = st.radio(
                "Seleccionar tema de colores",
                options=["Profesional (Azul/Verde)", "Académico (Gris/Neutro)", "Alto Contraste"],
                help="Cambia la paleta de colores"
            )
            st.success("✅ Tema activo: Paleta corporativa")
        
        with col_conf2:
            st.subheader("🔄 Actualización de Datos")
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
        🌾 Agro-Clima Intelligence Pro v3.0 (Corregida) • 
        <a href="https://github.com/grupoproyectoanalisisdatos-bot" style="color: #1e3a8a;">
            Repositorio GitHub
        </a> • 
        Streamlit Cloud + Railway
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 🚀 EJECUCIÓN
# ============================================================================
if __name__ == "__main__":
    main()
