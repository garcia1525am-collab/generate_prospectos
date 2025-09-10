import streamlit as st
import pandas as pd
import time
from io import BytesIO
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import json

# Configuración de la página
st.set_page_config(
    page_title="Google Maps Business Scraper",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
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
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🗺️ Google Maps Business Scraper</h1>
    <p style="font-size: 1.2em; margin-bottom: 0;">Análisis y Visualización de Datos de Negocios</p>
    <p style="font-size: 0.9em; opacity: 0.9; margin-top: 0.5rem;">Versión Cloud - Sube tu archivo CSV para análisis</p>
</div>
""", unsafe_allow_html=True)

# Inicializar session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = []

# Función para crear datos de ejemplo
def create_sample_data():
    """Crear datos de ejemplo para demostración"""
    sample_businesses = [
        {
            'nombre': 'Restaurante El Buen Sabor',
            'calificacion': '4.5',
            'num_reviews': '120',
            'tipo': 'Restaurante',
            'direccion': 'Av. Principal 123, Roma Norte, CDMX',
            'telefono': '55-1234-5678',
            'website': 'https://elbuensabor.com',
            'busqueda': 'restaurantes_roma',
            'fecha_extraccion': '2025-09-10 11:00:00'
        },
        {
            'nombre': 'Consultorio Dental Sonrisa',
            'calificacion': '4.8',
            'num_reviews': '85',
            'tipo': 'Dentista',
            'direccion': 'Calle Reforma 456, Polanco, CDMX',
            'telefono': '55-8765-4321',
            'website': 'https://dentalsonrisa.mx',
            'busqueda': 'dentistas_polanco',
            'fecha_extraccion': '2025-09-10 11:05:00'
        },
        {
            'nombre': 'Hotel Boutique Central',
            'calificacion': '4.2',
            'num_reviews': '340',
            'tipo': 'Hotel',
            'direccion': 'Zona Rosa, CDMX',
            'telefono': '55-5555-0000',
            'website': 'https://hotelboutique.com',
            'busqueda': 'hoteles_zona_rosa',
            'fecha_extraccion': '2025-09-10 11:10:00'
        },
        {
            'nombre': 'Café Literario',
            'calificacion': '4.7',
            'num_reviews': '95',
            'tipo': 'Cafetería',
            'direccion': 'Coyoacán, CDMX',
            'telefono': '55-2222-3333',
            'website': 'No disponible',
            'busqueda': 'cafeterias_coyoacan',
            'fecha_extraccion': '2025-09-10 11:15:00'
        },
        {
            'nombre': 'Gimnasio Fitness Pro',
            'calificacion': '4.0',
            'num_reviews': '200',
            'tipo': 'Gimnasio',
            'direccion': 'Condesa, CDMX',
            'telefono': 'No disponible',
            'website': 'https://fitnesspro.mx',
            'busqueda': 'gimnasios_condesa',
            'fecha_extraccion': '2025-09-10 11:20:00'
        }
    ]
    return sample_businesses

# Sidebar
st.sidebar.markdown("## ⚙️ Panel de Control")

# Información sobre la versión Cloud
with st.sidebar.expander("ℹ️ Versión Cloud", expanded=True):
    st.markdown("""
    **Esta es la versión cloud optimizada**
    
    ⚠️ **Limitación**: Por razones de seguridad, Streamlit Cloud no permite scraping directo con navegadores.
    
    **Solución**: 
    1. Usa tu app local para scraping
    2. Sube los archivos CSV aquí para análisis
    3. ¡Disfruta de visualizaciones profesionales!
    """)

# Subir archivo o usar datos de ejemplo
st.markdown("## 📊 Cargar Datos")

col_upload, col_sample = st.columns(2)

with col_upload:
    st.markdown("### 📁 Subir Archivo CSV")
    uploaded_file = st.file_uploader(
        "Sube tu archivo CSV con datos de negocios",
        type=['csv'],
        help="Archivo generado por tu scraper local"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_data = df.to_dict('records')
            st.success(f"✅ Archivo cargado: {len(df)} negocios")
        except Exception as e:
            st.error(f"❌ Error al cargar archivo: {e}")

with col_sample:
    st.markdown("### 🎯 Datos de Ejemplo")
    if st.button("🚀 Cargar Datos de Muestra", use_container_width=True):
        st.session_state.uploaded_data = create_sample_data()
        st.success("✅ Datos de ejemplo cargados")

# Mostrar análisis si hay datos
if st.session_state.uploaded_data:
    st.markdown("---")
    st.markdown("## 📊 Dashboard de Análisis")
    
    df = pd.DataFrame(st.session_state.uploaded_data)
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🏪 Total Negocios", len(df))
    
    with col2:
        with_phone = (df['telefono'] != 'No disponible').sum() if 'telefono' in df.columns else 0
        phone_percentage = (with_phone / len(df)) * 100 if len(df) > 0 else 0
        st.metric("📞 Con Teléfono", with_phone, delta=f"{phone_percentage:.1f}%")
    
    with col3:
        with_website = (df['website'] != 'No disponible').sum() if 'website' in df.columns else 0
        website_percentage = (with_website / len(df)) * 100 if len(df) > 0 else 0
        st.metric("🌐 Con Website", with_website, delta=f"{website_percentage:.1f}%")
    
    with col4:
        with_rating = (df['calificacion'] != 'No disponible').sum() if 'calificacion' in df.columns else 0
        rating_percentage = (with_rating / len(df)) * 100 if len(df) > 0 else 0
        st.metric("⭐ Con Calificación", with_rating, delta=f"{rating_percentage:.1f}%")
    
    with col5:
        avg_rating = None
        if 'calificacion' in df.columns:
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
        "🗂️ Información", 
        "💾 Exportar"
    ])
    
    with tab1:
        st.markdown("### 📋 Datos de Negocios")
        
        # Filtros
        if 'busqueda' in df.columns:
            busquedas_unicas = df['busqueda'].unique()
            filtro_busqueda = st.multiselect(
                "🔍 Filtrar por búsqueda:",
                busquedas_unicas,
                default=list(busquedas_unicas)
            )
            df_filtered = df[df['busqueda'].isin(filtro_busqueda)] if filtro_busqueda else df
        else:
            df_filtered = df
        
        # Mostrar tabla
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
            },
            height=400
        )
    
    with tab2:
        st.markdown("### 📈 Visualizaciones Interactivas")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Gráfico de tipos de negocio
            if 'tipo' in df.columns:
                tipo_counts = df[df['tipo'] != 'No disponible']['tipo'].value_counts().head(10)
                if not tipo_counts.empty:
                    fig = px.bar(
                        x=tipo_counts.values,
                        y=tipo_counts.index,
                        orientation='h',
                        title="🏪 Tipos de Negocio",
                        labels={'x': 'Cantidad', 'y': 'Tipo'},
                        color=tipo_counts.values,
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(height=400, showlegend=False)
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
                                color_discrete_sequence=['#667eea']
                            )
                            fig.update_layout(height=400, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.info("No se pudieron procesar las calificaciones")
        
        # Análisis de completitud
        st.markdown("### 📊 Completitud de Datos")
        completeness_data = []
        for col in ['nombre', 'telefono', 'website', 'direccion', 'calificacion', 'tipo']:
            if col in df.columns:
                available = (df[col] != 'No disponible').sum()
                percentage = (available / len(df)) * 100
                completeness_data.append({
                    'Campo': col.title(),
                    'Disponible': available,
                    'Total': len(df),
                    'Porcentaje': percentage
                })
        
        if completeness_data:
            completeness_df = pd.DataFrame(completeness_data)
            
            fig = px.bar(
                completeness_df,
                x='Campo',
                y='Porcentaje',
                title="📈 Completitud de Datos (%)",
                color='Porcentaje',
                color_continuous_scale="RdYlGn"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🗂️ Información del Dataset")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("**📊 Estadísticas Generales:**")
            st.write(f"• Total de registros: {len(df)}")
            st.write(f"• Columnas disponibles: {len(df.columns)}")
            
            if 'busqueda' in df.columns:
                unique_searches = df['busqueda'].nunique()
                st.write(f"• Búsquedas únicas: {unique_searches}")
        
        with col_info2:
            st.markdown("**🔍 Campos del Dataset:**")
            for col in df.columns:
                st.write(f"• {col}")
    
    with tab4:
        st.markdown("### 💾 Exportar Datos Procesados")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # CSV completo
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📊 Descargar CSV Completo",
                data=csv_data,
                file_name=f"analisis_negocios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
        
        with col_exp2:
            # JSON export
            json_data = df.to_json(orient='records', force_ascii=False, indent=2)
            
            st.download_button(
                label="📄 Descargar JSON",
                data=json_data,
                file_name=f"analisis_negocios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

else:
    # Mostrar instrucciones si no hay datos
    st.markdown("""
    <div class="info-box">
        <h3>🚀 ¡Comienza tu Análisis!</h3>
        <p><strong>Opción 1:</strong> Sube un archivo CSV generado por tu scraper local</p>
        <p><strong>Opción 2:</strong> Usa los datos de ejemplo para explorar las funcionalidades</p>
        <p><strong>💡 Tip:</strong> Para scraping en vivo, usa tu aplicación local y luego sube los resultados aquí para análisis avanzado</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; background: linear-gradient(135deg, #f8f9ff 0%, #e6eaff 100%); border-radius: 15px; margin-top: 2rem;">
    <h3 style="color: #667eea; margin-bottom: 1rem;">🗺️ Google Maps Business Scraper</h3>
    <p style="margin-bottom: 0.5rem;"><strong>Versión Cloud - Análisis y Visualización</strong></p>
    <p style="margin-bottom: 0.5rem;">⚠️ <em>Para scraping en vivo, usar la versión local</em></p>
    <p style="font-size: 0.9em; opacity: 0.8;">🚀 Desarrollado con ❤️ usando Streamlit</p>
</div>
""", unsafe_allow_html=True)
