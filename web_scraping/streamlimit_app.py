import streamlit as st
import pandas as pd
import time
from io import BytesIO
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from undetected_method3 import GoogleMapsScraper
import json

# Configuración de la página
st.set_page_config(
    page_title="Google Maps Business Scraper",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(40,167,69,0.1);
    }
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(220,53,69,0.1);
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(23,162,184,0.1);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102,126,234,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🗺️ Google Maps Business Scraper</h1>
    <p style="font-size: 1.2em; margin-bottom: 0;">Extrae información de negocios de Google Maps de manera fácil y visual</p>
    <p style="font-size: 0.9em; opacity: 0.9; margin-top: 0.5rem;">Versión Profesional con Interfaz Moderna</p>
</div>
""", unsafe_allow_html=True)

# Inicializar session state
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = []
if 'scraping_history' not in st.session_state:
    st.session_state.scraping_history = []
if 'is_scraping' not in st.session_state:
    st.session_state.is_scraping = False

# Función para realizar scraping (SIN threading - versión síncrona)
def perform_scraping(url, max_results, search_name):
    """Realiza el scraping de forma síncrona"""
    try:
        with st.spinner('🔧 Configurando navegador...'):
            scraper = GoogleMapsScraper()
        
        with st.spinner('🌐 Accediendo a Google Maps y extrayendo datos...'):
            businesses = scraper.search_businesses(url, max_results=max_results)
        
        if businesses:
            # Agregar metadatos
            for i, business in enumerate(businesses):
                business['busqueda'] = search_name
                business['fecha_extraccion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                business['indice_global'] = len(st.session_state.scraped_data) + i
            
            # Guardar datos
            st.session_state.scraped_data.extend(businesses)
            st.session_state.scraping_history.append({
                'busqueda': search_name,
                'url': url,
                'resultados': len(businesses),
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return True, businesses
        else:
            return False, "No se encontraron resultados"
            
    except Exception as e:
        return False, f"Error durante el scraping: {str(e)}"
    finally:
        try:
            scraper.close()
        except:
            pass

# Sidebar con configuración
st.sidebar.markdown("## ⚙️ Panel de Control")

# Configuración del scraper
with st.sidebar.expander("🔧 Configuración Avanzada", expanded=True):
    max_results = st.number_input(
        "Número máximo de resultados",
        min_value=1,
        max_value=200,
        value=15,
        step=5,
        help="Cantidad de negocios a extraer (recomendado: 15-50)"
    )

# Información y ayuda
with st.sidebar.expander("💡 Ejemplos de URLs Válidas"):
    st.markdown("""
    **🍽️ Restaurantes:**
    ```
    https://www.google.com/maps/search/restaurantes+mexicanos+cdmx/@19.4326,-99.1332,13z
    ```
    
    **🏥 Servicios de Salud:**
    ```
    https://www.google.com/maps/search/dentistas+cerca+de+mi/@19.4326,-99.1332,15z
    ```
    
    **🏨 Hoteles:**
    ```
    https://www.google.com/maps/search/hoteles+cancun/@21.1619,-86.8515,12z
    ```
    """)

with st.sidebar.expander("📊 Estadísticas de Sesión"):
    if st.session_state.scraped_data:
        total_businesses = len(st.session_state.scraped_data)
        searches_count = len(st.session_state.scraping_history)
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("🏪 Negocios", total_businesses)
        with col_stat2:
            st.metric("🔍 Búsquedas", searches_count)
        
        if total_businesses > 0:
            df = pd.DataFrame(st.session_state.scraped_data)
            completeness_metrics = {}
            for col in ['telefono', 'website', 'direccion', 'calificacion']:
                if col in df.columns:
                    available = (df[col] != 'No disponible').sum()
                    percentage = (available / total_businesses) * 100
                    completeness_metrics[col] = percentage
            
            st.markdown("**📈 Completitud de Datos:**")
            for field, percentage in completeness_metrics.items():
                st.progress(percentage / 100, text=f"{field.title()}: {percentage:.1f}%")
    else:
        st.info("🎯 Realiza tu primera búsqueda para ver estadísticas")

# Área principal
st.markdown("## 🔍 Nueva Búsqueda de Negocios")

# Formulario de búsqueda
with st.form("search_form", clear_on_submit=False):
    search_url = st.text_input(
        "🌐 URL de Búsqueda de Google Maps",
        placeholder="https://www.google.com/maps/search/restaurantes+cerca+de+mi/@19.4326,-99.1332,15z",
        help="Pega aquí la URL completa de tu búsqueda en Google Maps"
    )
    
    col_name, col_results = st.columns([2, 1])
    
    with col_name:
        search_name = st.text_input(
            "🏷️ Nombre de la Búsqueda",
            placeholder="ej: restaurantes_cdmx, dentistas_zona_norte",
            help="Un nombre descriptivo para identificar esta búsqueda"
        )
    
    with col_results:
        form_max_results = st.number_input(
            "📊 Resultados",
            min_value=1,
            max_value=100,
            value=max_results
        )
    
    # Botones del formulario
    col_submit, col_clear = st.columns([1, 1])
    
    with col_submit:
        submit_button = st.form_submit_button(
            "🚀 Iniciar Scraping",
            use_container_width=True,
            type="primary"
        )
    
    with col_clear:
        clear_button = st.form_submit_button(
            "🗑️ Limpiar Datos",
            use_container_width=True
        )

# Limpiar datos
if clear_button:
    st.session_state.scraped_data = []
    st.session_state.scraping_history = []
    st.success("✅ Todos los datos han sido limpiados")
    st.rerun()

# Lógica de scraping
if submit_button and search_url:
    if "google.com/maps" not in search_url and "maps.google.com" not in search_url:
        st.error("❌ La URL no parece ser válida. Debe ser una búsqueda de Google Maps.")
    else:
        # Preparar nombre de búsqueda
        if not search_name:
            search_name = f"busqueda_{len(st.session_state.scraping_history) + 1}"
        
        st.info("🚀 Iniciando scraping. Esto puede tomar varios minutos...")
        
        # Realizar scraping de forma síncrona
        success, result = perform_scraping(search_url, form_max_results, search_name)
        
        if success:
            businesses = result
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Extracción completada exitosamente</strong><br>
                📊 Negocios encontrados: {len(businesses)}<br>
                🏷️ Búsqueda: {search_name}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-box">
                <strong>❌ Error en la extracción</strong><br>
                {result}
            </div>
            """, unsafe_allow_html=True)

# Mostrar resultados si hay datos
if st.session_state.scraped_data:
    st.markdown("---")
    st.markdown("## 📊 Panel de Resultados")
    
    df = pd.DataFrame(st.session_state.scraped_data)
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🏪 Total Negocios", len(df))
    
    with col2:
        with_phone = (df['telefono'] != 'No disponible').sum()
        phone_percentage = (with_phone / len(df)) * 100
        st.metric("📞 Con Teléfono", with_phone, delta=f"{phone_percentage:.1f}%")
    
    with col3:
        with_website = (df['website'] != 'No disponible').sum()
        website_percentage = (with_website / len(df)) * 100
        st.metric("🌐 Con Website", with_website, delta=f"{website_percentage:.1f}%")
    
    with col4:
        with_rating = (df['calificacion'] != 'No disponible').sum()
        rating_percentage = (with_rating / len(df)) * 100
        st.metric("⭐ Con Calificación", with_rating, delta=f"{rating_percentage:.1f}%")
    
    with col5:
        avg_rating = None
        try:
            ratings = df[df['calificacion'] != 'No disponible']['calificacion']
            ratings_numeric = pd.to_numeric(ratings, errors='coerce').dropna()
            if not ratings_numeric.empty:
                avg_rating = ratings_numeric.mean()
        except:
            avg_rating = None
        
        if avg_rating:
            st.metric("📊 Promedio", f"{avg_rating:.1f} ⭐")
        else:
            st.metric("📊 Promedio", "N/A")
    
    # Pestañas para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Tabla de Datos", 
        "📈 Análisis Visual", 
        "🗂️ Historial", 
        "💾 Exportar Datos"
    ])
    
    with tab1:
        st.markdown("### 📋 Datos Extraídos")
        
        # Filtros rápidos
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            busquedas_unicas = df['busqueda'].unique() if 'busqueda' in df.columns else []
            filtro_busqueda = st.multiselect(
                "🔍 Filtrar por búsqueda:",
                busquedas_unicas,
                default=busquedas_unicas
            )
        
        with col_filter2:
            filtros_rapidos = st.multiselect(
                "⚡ Filtros rápidos:",
                ["Solo con teléfono", "Solo con website", "Solo con calificación", "Calificación > 4.0"],
                default=[]
            )
        
        with col_filter3:
            ordenar_por = st.selectbox(
                "📊 Ordenar por:",
                ["Índice", "Nombre", "Calificación", "Número de reviews"],
                index=0
            )
        
        # Aplicar filtros
        df_filtered = df.copy()
        
        if filtro_busqueda and 'busqueda' in df.columns:
            df_filtered = df_filtered[df_filtered['busqueda'].isin(filtro_busqueda)]
        
        for filtro in filtros_rapidos:
            if filtro == "Solo con teléfono":
                df_filtered = df_filtered[df_filtered['telefono'] != 'No disponible']
            elif filtro == "Solo con website":
                df_filtered = df_filtered[df_filtered['website'] != 'No disponible']
            elif filtro == "Solo con calificación":
                df_filtered = df_filtered[df_filtered['calificacion'] != 'No disponible']
            elif filtro == "Calificación > 4.0":
                try:
                    ratings = pd.to_numeric(df_filtered['calificacion'], errors='coerce')
                    df_filtered = df_filtered[ratings > 4.0]
                except:
                    pass
        
        # Mostrar información del filtrado
        if len(df_filtered) != len(df):
            st.info(f"📊 Mostrando {len(df_filtered)} de {len(df)} negocios (filtrados)")
        
        # Tabla con configuración mejorada
        st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nombre": st.column_config.TextColumn("🏪 Nombre", width="large"),
                "calificacion": st.column_config.NumberColumn("⭐ Calificación", format="%.1f"),
                "num_reviews": st.column_config.TextColumn("📝 Reviews"),
                "tipo": st.column_config.TextColumn("🏷️ Tipo"),
                "direccion": st.column_config.TextColumn("📍 Dirección", width="large"),
                "telefono": st.column_config.TextColumn("📞 Teléfono"),
                "website": st.column_config.LinkColumn("🌐 Website"),
                "busqueda": st.column_config.TextColumn("🔍 Búsqueda"),
                "fecha_extraccion": st.column_config.DatetimeColumn("📅 Extraído")
            },
            height=400
        )
    
    with tab2:
        st.markdown("### 📈 Análisis Visual de Datos")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Gráfico de tipos de negocio
            if 'tipo' in df.columns:
                tipo_counts = df[df['tipo'] != 'No disponible']['tipo'].value_counts().head(15)
                if not tipo_counts.empty:
                    fig = px.bar(
                        x=tipo_counts.values,
                        y=tipo_counts.index,
                        orientation='h',
                        title="🏪 Top 15 Tipos de Negocio",
                        labels={'x': 'Cantidad', 'y': 'Tipo de Negocio'},
                        color=tipo_counts.values,
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(height=500, showlegend=False, font=dict(size=12))
                    st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            # Gráfico de calificaciones
            if 'calificacion' in df.columns:
                ratings = df[df['calificacion'] != 'No disponible']['calificacion']
                if not ratings.empty:
                    try:
                        ratings_numeric = pd.to_numeric(ratings, errors='coerce').dropna()
                        if not ratings_numeric.empty:
                            fig = px.histogram(
                                ratings_numeric,
                                title="⭐ Distribución de Calificaciones",
                                labels={'value': 'Calificación', 'count': 'Cantidad'},
                                nbins=20,
                                color_discrete_sequence=['#667eea']
                            )
                            fig.update_layout(height=500, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.info("No se pudieron procesar las calificaciones numéricamente")
    
    with tab3:
        st.markdown("### 🗂️ Historial Completo de Búsquedas")
        
        if st.session_state.scraping_history:
            history_df = pd.DataFrame(st.session_state.scraping_history)
            
            # Métricas del historial
            col_h1, col_h2, col_h3 = st.columns(3)
            
            with col_h1:
                st.metric("📊 Total Búsquedas", len(history_df))
            
            with col_h2:
                total_results = history_df['resultados'].sum()
                st.metric("🏪 Total Negocios", total_results)
            
            with col_h3:
                avg_results = history_df['resultados'].mean()
                st.metric("📈 Promedio por Búsqueda", f"{avg_results:.1f}")
            
            # Tabla de historial
            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'busqueda': st.column_config.TextColumn('🔍 Búsqueda'),
                    'url': st.column_config.TextColumn('🌐 URL', width="large"),
                    'resultados': st.column_config.NumberColumn('📊 Resultados'),
                    'fecha': st.column_config.DatetimeColumn('📅 Fecha')
                }
            )
        else:
            st.info("📝 No hay historial de búsquedas aún.")
    
    with tab4:
        st.markdown("### 💾 Exportar y Descargar Datos")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            st.markdown("#### 📊 Exportaciones Rápidas")
            
            # CSV completo
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📊 Descargar CSV Completo",
                data=csv_data,
                file_name=f"negocios_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
            
            # Solo con teléfono
            df_with_phone = df[df['telefono'] != 'No disponible']
            if not df_with_phone.empty:
                csv_phone_buffer = BytesIO()
                df_with_phone.to_csv(csv_phone_buffer, index=False, encoding='utf-8-sig')
                csv_phone_data = csv_phone_buffer.getvalue()
                
                st.download_button(
                    label="📞 Solo con Teléfono",
                    data=csv_phone_data,
                    file_name=f"negocios_con_telefono_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Solo con website
            df_with_website = df[df['website'] != 'No disponible']
            if not df_with_website.empty:
                csv_website_buffer = BytesIO()
                df_with_website.to_csv(csv_website_buffer, index=False, encoding='utf-8-sig')
                csv_website_data = csv_website_buffer.getvalue()
                
                st.download_button(
                    label="🌐 Solo con Website",
                    data=csv_website_data,
                    file_name=f"negocios_con_website_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col_export2:
            st.markdown("#### 📋 Exportaciones por Búsqueda")
            
            if 'busqueda' in df.columns:
                busquedas_disponibles = df['busqueda'].unique()
                
                for busqueda in busquedas_disponibles:
                    df_busqueda = df[df['busqueda'] == busqueda]
                    
                    csv_busqueda_buffer = BytesIO()
                    df_busqueda.to_csv(csv_busqueda_buffer, index=False, encoding='utf-8-sig')
                    csv_busqueda_data = csv_busqueda_buffer.getvalue()
                    
                    st.download_button(
                        label=f"📁 {busqueda} ({len(df_busqueda)} negocios)",
                        data=csv_busqueda_data,
                        file_name=f"negocios_{busqueda}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key=f"download_{busqueda}"
                    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; background: linear-gradient(135deg, #f8f9ff 0%, #e6eaff 100%); border-radius: 15px; margin-top: 2rem;">
    <h3 style="color: #667eea; margin-bottom: 1rem;">🗺️ Google Maps Business Scraper Pro</h3>
    <p style="margin-bottom: 0.5rem;"><strong>Desarrollado con ❤️ usando Streamlit</strong></p>
    <p style="margin-bottom: 0.5rem;">⚠️ <em>Usar responsablemente y respetando los términos de servicio de Google</em></p>
    <p style="font-size: 0.9em; opacity: 0.8;">🚀 Versión 2.0 - Interfaz Moderna Optimizada</p>
</div>
""", unsafe_allow_html=True)
