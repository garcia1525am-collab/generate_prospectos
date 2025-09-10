import streamlit as st
import requests
import json
from datetime import datetime

# Configuración básica de Streamlit
try:
    st.set_page_config(
        page_title="WhatsApp API Sender",
        page_icon="📱",
        layout="wide"
    )
except Exception as e:
    st.error(f"Error configurando página: {e}")

# Título principal
st.title("📱 WhatsApp API Message Sender")
st.markdown("---")

# Inicializar session state
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

# Función simple para enviar mensaje template
def send_template_message(to, token, business_id, template_name="hello_world"):
    url = f"https://graph.facebook.com/v22.0/{business_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "en_US"
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, f"Error de conexión: {str(e)}"
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"

# Función para enviar mensaje de texto
def send_text_message(to, token, business_id, message_text):
    url = f"https://graph.facebook.com/v22.0/{business_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, f"Error de conexión: {str(e)}"
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"

# Layout principal con columnas
col1, col2 = st.columns([2, 1])

with col1:
    st.header("⚙️ Configuración")
    
    # Campos de configuración principales
    phone_number = st.text_input(
        "Número de teléfono (con código de país)",
        value="525525604014",
        help="Ejemplo: 525525604014"
    )
    
    business_phone_id = st.text_input(
        "Business Phone Number ID",
        value="739761142555717"
    )
    
    access_token = st.text_area(
        "Access Token de WhatsApp",
        value="EAAbWYaIAxX0BPZAyicBZBt2nRDcChNmKwiCAp4OpEtykYvZBkTiNaFmC8jVt6Q3aGHxt7FDW9Qy0y07DGfdyb7f5SEPLE3d4qZAsUr0Cvef9Bkwrdx6sXKZCzGNd1uqnBjcjmdxN0cfZBeL1F2SF4UAFRKGZBJw3cR8XDZCnMkJJjkd7D2sYyZBHmQctVaHrdqZAqlGFCCjcuR3ZCRpKZAR3zTHkpC69DiwqdSXRJ4M772GsFQZDZD",
        height=80
    )
    
    st.markdown("---")
    
    # Sección de envío de template (como tu código original)
    st.header("📤 Enviar Template Hello World")
    
    if st.button("Enviar Template Hello World", type="primary"):
        if not phone_number or not access_token or not business_phone_id:
            st.error("❌ Por favor completa todos los campos")
        else:
            with st.spinner("Enviando mensaje..."):
                status_code, response_text = send_template_message(
                    phone_number, 
                    access_token, 
                    business_phone_id
                )
                
                # Agregar al historial
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.message_history.append({
                    'timestamp': timestamp,
                    'to': phone_number,
                    'type': 'template',
                    'template': 'hello_world',
                    'status': status_code,
                    'response': response_text
                })
                
                if status_code == 200:
                    st.success("✅ Template enviado correctamente!")
                    try:
                        response_json = json.loads(response_text)
                        st.json(response_json)
                    except:
                        st.text(f"Respuesta: {response_text}")
                else:
                    st.error(f"❌ Error {status_code}")
                    st.text(f"Respuesta: {response_text}")
    
    st.markdown("---")
    
    # Sección de mensaje personalizado
    st.header("✉️ Enviar Mensaje de Texto")
    st.info("💡 Solo funciona si el usuario inició la conversación primero")
    
    custom_message = st.text_area(
        "Mensaje personalizado",
        placeholder="Escribe tu mensaje aquí..."
    )
    
    if st.button("Enviar Mensaje de Texto"):
        if not phone_number or not access_token or not business_phone_id or not custom_message:
            st.error("❌ Por favor completa todos los campos")
        else:
            with st.spinner("Enviando mensaje..."):
                status_code, response_text = send_text_message(
                    phone_number, 
                    access_token, 
                    business_phone_id,
                    custom_message
                )
                
                # Agregar al historial
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.message_history.append({
                    'timestamp': timestamp,
                    'to': phone_number,
                    'type': 'text',
                    'message': custom_message,
                    'status': status_code,
                    'response': response_text
                })
                
                if status_code == 200:
                    st.success("✅ Mensaje enviado correctamente!")
                    try:
                        response_json = json.loads(response_text)
                        st.json(response_json)
                    except:
                        st.text(f"Respuesta: {response_text}")
                else:
                    st.error(f"❌ Error {status_code}")
                    st.text(f"Respuesta: {response_text}")

with col2:
    st.header("📊 Estado")
    
    # Mostrar estado actual
    if phone_number:
        st.success(f"📞 Número: {phone_number}")
    else:
        st.warning("📞 No hay número")
    
    if business_phone_id:
        st.success(f"📱 Business ID configurado")
    else:
        st.warning("📱 Falta Business ID")
    
    if access_token:
        st.success("🔐 Token configurado")
    else:
        st.warning("🔐 Falta token")
    
    st.markdown("---")
    
    # Información útil
    st.subheader("💡 Códigos de Estado")
    st.markdown("""
    - **200**: ✅ Éxito
    - **400**: ❌ Solicitud incorrecta  
    - **401**: ❌ No autorizado
    - **403**: ❌ Prohibido
    - **404**: ❌ No encontrado
    """)

# Historial de mensajes
st.markdown("---")
st.header("📜 Historial de Mensajes")

if st.session_state.message_history:
    for i, msg in enumerate(reversed(st.session_state.message_history[-5:])):  # Mostrar últimos 5
        with st.expander(f"Mensaje {i+1} - {msg['timestamp']}"):
            st.write(f"**Para:** {msg['to']}")
            st.write(f"**Tipo:** {msg['type']}")
            if msg['type'] == 'template':
                st.write(f"**Template:** {msg['template']}")
            else:
                st.write(f"**Mensaje:** {msg['message']}")
            
            if msg['status'] == 200:
                st.success(f"Estado: {msg['status']} ✅")
            else:
                st.error(f"Estado: {msg['status']} ❌")
            
            with st.expander("Ver respuesta completa"):
                st.text(msg['response'])
else:
    st.info("📭 No hay mensajes enviados aún")

# Botón para limpiar historial
if st.button("🗑️ Limpiar Historial") and st.session_state.message_history:
    st.session_state.message_history = []
    st.success("Historial limpiado")
    st.rerun()

# Footer
st.markdown("---")
st.markdown("🚀 **WhatsApp API Interface** - Versión simplificada")

#activar en consola: conda activate mi-entorno, cd (ruta del proyecto) y streamlit run sender_app.py
