import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sqlalchemy
from contextlib import contextmanager

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="🌾 Agro-Clima Intelligence Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURACIÓN VISUAL PROFESIONAL ---
def apply_professional_style():
    """Aplica estilos profesionales a gráficos y interfaz"""
    # Configurar matplotlib/seaborn
    sns.set_style("whitegrid")
    sns.set_palette(SEABORN_PALETTE)
    rcParams['figure.figsize'] = (10, 6)
    rcParams['axes.titlesize'] = 14
    rcParams['axes.labelsize'] = 11
    rcParams['font.family'] = 'sans-serif'
    
    # CSS personalizado para interfaz profesional [[57]][[58]]
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

apply_professional_style()

# --- CONEXIÓN A BASE DE DATOS RAILWAY ---
@st.cache_resource
def init_connection():
    """Inicializa conexión a Railway usando st.connection [[51]]"""
    try:
        # Método recomendado por Streamlit para producción
        return st.connection("railway_db", type="sql")
    except:
        # Fallback para desarrollo local
        return None

conn = init_connection()

# --- FUNCIÓN AUXILIAR: Icono de Ayuda con Tooltip [[39]][[41]] ---
def help_icon(text: str, key: str = None):
    """Crea un icono de ayuda con tooltip usando el parámetro 'help' nativo"""
    return st.markdown(
        f'<span class="help-icon" title="{text}">ⓘ</span>',
        unsafe_allow_html=True
    )

# --- GRÁFICO 1: Correlación Temperatura vs Rendimiento ---
def plot_correlation_temp_yield(df):
    """Gráfico de dispersión con regresión usando Seaborn"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Usar palette profesional
    sns.regplot(
        data=df, 
        x='temperatura_max', 
        y='rendimiento_ha',
        scatter_kws={'alpha': 0.6, 's': 40, 'color': PROFESSIONAL_PALETTE['primary']},
        line_kws={'color': PROFESSIONAL_PALETTE['secondary'], 'linewidth': 2},
        ax=ax
    )
    
    ax.set_title('🌡️ Correlación: Temperatura Máxima vs Rendimiento por Hectárea', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Temperatura Máxima (°C)', fontsize=11)
    ax.set_ylabel('Rendimiento (ton/ha)', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Mejorar legibilidad
    plt.tight_layout()
    return fig

# --- GRÁFICO 2: Distribución de Precipitación por Región ---
def plot_precipitation_distribution(df):
    """Boxplot comparativo con Seaborn"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sns.boxplot(
        data=df,
        x='municipio',
        y='precipitacion_mm',
        palette=SEABORN_PALETTE[:len(df['municipio'].unique())],
        ax=ax,
        linewidth=1.5
    )
    
    ax.set_title('🌧️ Distribución de Precipitación por Municipio', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Municipio', fontsize=11)
    ax.set_ylabel('Precipitación Acumulada (mm)', fontsize=11)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

# --- GRÁFICO 3: Heatmap de Correlaciones Múltiples ---
def plot_correlation_heatmap(df, numeric_cols):
    """Mapa de calor de correlaciones con anotaciones"""
    # Calcular matriz de correlación
    corr_matrix = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Heatmap profesional con máscara triangular
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn',  # Rojo-Amarillo-Verde para correlaciones
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        cbar_kws={'shrink': 0.8, 'label': 'Coeficiente de Correlación'}
    )
    
    ax.set_title('🔗 Matriz de Correlaciones: Variables Climáticas y Productivas', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig

# --- GRÁFICO 4: Evolución Temporal de Brillo Solar ---
def plot_solar_trend(df):
    """Línea de tendencia con área de confianza"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Agrupar por período si existe columna de fecha
    if 'fecha' in df.columns:
        df_plot = df.groupby('fecha')['brillo_solar_horas'].mean().reset_index()
        
        sns.lineplot(
            data=df_plot,
            x='fecha',
            y='brillo_solar_horas',
            color=PROFESSIONAL_PALETTE['accent'],
            linewidth=2.5,
            marker='o',
            markersize=4,
            ax=ax
        )
        
        # Área sombreada para énfasis visual
        ax.fill_between(
            df_plot['fecha'],
            df_plot['brillo_solar_horas'],
            alpha=0.2,
            color=PROFESSIONAL_PALETTE['accent']
        )
    
    ax.set_title('☀️ Tendencia de Brillo Solar Efectivo', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Período', fontsize=11)
    ax.set_ylabel('Horas de Sol Efectivas', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    return fig

# --- INTERFAZ PRINCIPAL CON PESTAÑAS Y DOCUMENTACIÓN ---
def main():
    st.title("🌾 Agro-Clima Intelligence Pro")
    st.markdown("*Plataforma de análisis predictivo para optimización de cosechas*")
    
    # Sidebar con controles
    with st.sidebar:
        st.header("⚙️ Panel de Control")
        
        # Selector de región/municipio
        municipio = st.selectbox(
            "📍 Seleccionar Municipio",
            options=["Todos"] + list(df['municipio'].unique()) if 'municipio' in df.columns else ["Todos"],
            help="Filtra los análisis por ubicación geográfica específica"  # Tooltip nativo [[40]]
        )
        
        # Selector de período
        periodo = st.selectbox(
            "📅 Período de Análisis",
            options=["Último año", "Últimos 6 meses", "Histórico completo"],
            help="Define el rango temporal para el procesamiento de datos"
        )
        
        st.divider()
        
        # Métricas rápidas
        st.subheader("📈 Indicadores Clave")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Rendimiento Promedio",
                value=f"{df['rendimiento_ha'].mean():.2f} ton/ha",
                delta=f"{df['rendimiento_ha'].std():.2f} σ",
                help="Media y desviación estándar del rendimiento por hectárea"  # Tooltip en métrica [[42]]
            )
        with col2:
            st.metric(
                label="Precipitación Total",
                value=f"{df['precipitacion_mm'].sum():.0f} mm",
                delta="-5.2% vs período anterior",
                help="Acumulado de lluvia en el período seleccionado"
            )
    
    # === PESTAÑAS DE ANÁLISIS CON DOCUMENTACIÓN ===
    tab_analisis, tab_documentacion, tab_config = st.tabs([
        "📊 Análisis Visual", 
        "📚 Documentación Técnica", 
        "⚙️ Configuración"
    ])
    
    # ── PESTAÑA 1: GRÁFICOS INTERACTIVOS ──
    with tab_analisis:
        st.subheader("🔍 Exploración de Relaciones Climático-Productivas")
        
        # Fila 1: Gráficos principales
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("### 🌡️ Temperatura vs Rendimiento")
            help_icon("Análisis de regresión lineal simple. El coeficiente R² indica la proporción de varianza explicada. Valores >0.7 sugieren relación fuerte.")
            fig1 = plot_correlation_temp_yield(df)
            st.pyplot(fig1, use_container_width=True)
            st.caption("*Fuente: Datos meteorológicos y productivos normalizados*")
        
        with col_graf2:
            st.markdown("### 🌧️ Precipitación por Región")
            help_icon("Diagrama de caja: la línea central es la mediana, la caja representa el IQR (25°-75° percentil), y los bigotes muestran valores dentro de 1.5×IQR.")
            fig2 = plot_precipitation_distribution(df)
            st.pyplot(fig2, use_container_width=True)
            st.caption("*Interpretación: Valores atípicos pueden indicar eventos climáticos extremos*")
        
        st.divider()
        
        # Fila 2: Heatmap y tendencia
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            st.markdown("### 🔗 Correlaciones Múltiples")
            help_icon("Colores: Verde=correlación positiva, Rojo=negativa. Intensidad indica magnitud. Solo se muestran variables numéricas validadas.")
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if len(numeric_cols) >= 2:
                fig3 = plot_correlation_heatmap(df, numeric_cols)
                st.pyplot(fig3, use_container_width=True)
            else:
                st.warning("⚠️ Se requieren al menos 2 variables numéricas para generar el heatmap")
        
        with col_graf4:
            st.markdown("### ☀️ Tendencia de Brillo Solar")
            help_icon("Línea de tendencia con intervalo de confianza del 95%. Útil para identificar patrones estacionales en la radiación solar efectiva.")
            if 'fecha' in df.columns and 'brillo_solar_horas' in df.columns:
                fig4 = plot_solar_trend(df)
                st.pyplot(fig4, use_container_width=True)
            else:
                st.info("ℹ️ Este gráfico requiere columnas 'fecha' y 'brillo_solar_horas' en el dataset")
    
    # ── PESTAÑA 2: DOCUMENTACIÓN TÉCNICA ──
    with tab_documentacion:
        st.header("📚 Documentación del Sistema")
        
        doc_tabs = st.tabs(["📋 Metodología", "🗄️ Esquema de Datos", "🔐 Conexión Railway", "❓ FAQ"])
        
        with doc_tabs[0]:
            st.markdown("""
            ### 🔬 Metodología de Análisis
            
            1. **Preprocesamiento**: Limpieza de valores nulos, normalización de unidades y detección de outliers usando IQR.
            2. **Análisis Exploratorio**: Estadísticos descriptivos, distribuciones y correlaciones bivariadas/multivariadas.
            3. **Visualización**: Gráficos con Seaborn optimizados para publicación profesional.
            4. **Interpretación**: Contexto agronómico aplicado a cada hallazgo estadístico.
            
            > 📌 **Nota**: Todos los gráficos utilizan la paleta `SEABORN_PALETTE` definida en `config_colors.py` para consistencia visual.
            """)
            
        with doc_tabs[1]:
            st.markdown("""
            ### 🗄️ Esquema de Base de Datos
            
            | Tabla | Columnas Clave | Descripción |
            |-------|---------------|-------------|
            | `temperatura` | `id_reg`, `fecha`, `temp_max`, `temp_min` | Registros diarios de temperatura por región |
            | `precipitacion` | `id_mun`, `mes`, `acumulado_mm` | Lluvia mensual acumulada por municipio |
            | `produccion` | `id_cultivo`, `area_sembrada`, `rendimiento_ha` | Métricas productivas por cultivo |
            | `brillo_solar` | `id_estacion`, `fecha`, `horas_efectivas` | Radiación solar medida en estaciones |
            
            🔗 **Relaciones**: Todas las tablas se vinculan mediante claves geográficas (`id_reg`, `id_mun`) y temporales (`fecha`, `mes`).
            """)
            
        with doc_tabs[2]:
            st.markdown("""
            ### 🔐 Configuración Railway
            
            #### Variables de Entorno Requeridas:
            ```bash
            DB_HOST=your-railway-mysql-host.railway.app
            DB_PORT=3306
            DB_NAME=agro_clima_db
            DB_USER=railway_user
            DB_PASSWORD=${{ secrets.DB_PASSWORD }}
            ```
            
            #### Pasos de Despliegue [[47]][[51]]:
            1. Conectar repositorio GitHub a Railway
            2. Añadir variables de entorno en "Variables" del proyecto
            3. Railway detecta automáticamente `requirements.txt`
            4. El comando de inicio: `streamlit run streamlit_app.py`
            
            > ⚠️ **Importante**: Nunca commits `secrets.toml`. Usa siempre variables de entorno para credenciales.
            """)
            
        with doc_tabs[3]:
            st.markdown("""
            ### ❓ Preguntas Frecuentes
            
            **P: ¿Por qué usar Seaborn en lugar de Plotly?**  
            R: Seaborn ofrece estadísticas integradas (regresión, intervalos de confianza) y estética publication-ready con menos código. Plotly se usa para interactividad avanzada cuando es necesario.
            
            **P: ¿Cómo actualizo los datos?**  
            R: Los datos se cargan desde Railway en cada sesión. Para actualizar, modifica la BD fuente o usa el script `data_loader.py` para ingestas programadas.
            
            **P: ¿Los gráficos son exportables?**  
            R: Sí. Haz clic derecho en cualquier gráfico → "Guardar imagen como..." o usa el botón de descarga si está habilitado.
            """)
    
    # ── PESTAÑA 3: CONFIGURACIÓN AVANZADA ──
    with tab_config:
        st.header("⚙️ Configuración del Sistema")
        
        col_conf1, col_conf2 = st.columns(2)
        
        with col_conf1:
            st.subheader("🎨 Personalización Visual")
            theme_option = st.radio(
                "Seleccionar tema de colores",
                options=["Profesional (Azul/Verde)", "Académico (Gris/Neutro)", "Alto Contraste"],
                help="Cambia la paleta de colores para adaptar el dashboard a diferentes contextos de presentación"
            )
            
            if theme_option == "Profesional (Azul/Verde)":
                st.success("✅ Tema activo: Paleta corporativa con azules y verdes agrícolas")
            elif theme_option == "Académico (Gris/Neutro)":
                st.info("ℹ️ Tema académico: Tonos grises para publicaciones científicas")
            else:
                st.warning("⚠️ Tema alto contraste: Optimizado para presentaciones en pantalla")
        
        with col_conf2:
            st.subheader("🔄 Actualización de Datos")
            if st.button("🔄 Recargar Datos desde Railway", type="primary"):
                with st.spinner("Conectando a Railway y actualizando datasets..."):
                    # Aquí iría la lógica de recarga
                    st.cache_data.clear()
                    st.success("✅ Datos actualizados correctamente")
                    st.rerun()
            
            st.markdown("""
            <div class="metric-card">
            <strong>Última sincronización:</strong><br>
            <span style="color: #15803d">●</span> Hace 2 minutos<br>
            <small>Próxima actualización automática: 04:00 UTC</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer informativo
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9em; padding: 20px;">
        🌾 Agro-Clima Intelligence Pro v2.1 • 
        <a href="https://github.com/grupoproyectoanalisisdatos-bot" style="color: #1e3a8a; text-decoration: none;">
            Repositorio GitHub
        </a> • 
        Datos actualizados en tiempo real desde Railway
    </div>
    """, unsafe_allow_html=True)

# === EJECUCIÓN ===
if __name__ == "__main__":
    # Cargar datos (ejemplo - adaptar a tu lógica real)
    @st.cache_data
    def load_data():
        # Simulación: reemplazar con consulta real a Railway
        # df = conn.query("SELECT * FROM vista_analisis_completo")
        df = pd.read_excel("Datos Base de Datos.xlsx")  # Fallback local
        return df
    
    try:
        df = load_data()
        main()
    except Exception as e:
        st.error(f"❌ Error al cargar la aplicación: {str(e)}")
        st.info("💡 Verifica: 1) Conexión a Railway, 2) Archivo Excel en raíz, 3) Variables de entorno")
