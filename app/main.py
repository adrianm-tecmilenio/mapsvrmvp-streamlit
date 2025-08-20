import streamlit as st
import requests
import json
from typing import Dict, Any

# --- Config página ---
st.set_page_config(
    page_title="Simulador de Terapia Psicológica",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- URLs del API ---
API_URL = "http://localhost:8000/simulator"           # texto (tu endpoint actual)
API_VOICE_URL = "http://localhost:8000/simulator/voice"  # voz (nuevo endpoint)

# --- Personajes predefinidos (igual que tu código) ---
PERSONAJES = {
    "Ana - Estudiante Ansiosa": {
        "name": "Ana García",
        "age": 22,
        "occupation": "Estudiante universitaria",
        "marital_status": "Soltera",
        "current_situation": "Experimentando ansiedad por los exámenes finales y presión académica",
        "background": "Estudiante de psicología en tercer año, vive con roommates, familia de clase media",
        "motivation": "Quiere aprender a manejar su ansiedad y mejorar su rendimiento académico"
    },
    "Carlos - Ejecutivo Estresado": {
        "name": "Carlos Rodríguez",
        "age": 35,
        "occupation": "Gerente de ventas",
        "marital_status": "Casado",
        "current_situation": "Enfrentando burnout laboral y problemas para equilibrar trabajo y familia",
        "background": "Ejecutivo exitoso, padre de dos hijos, vive en la ciudad, historial de trabajar largas horas",
        "motivation": "Busca encontrar equilibrio entre trabajo y vida personal, reducir estrés"
    },
    "María - Madre Deprimida": {
        "name": "María López",
        "age": 28,
        "occupation": "Madre de tiempo completo",
        "marital_status": "Casada",
        "current_situation": "Lidiando con depresión postparto y sentimientos de aislamiento",
        "background": "Recién madre, dejó su trabajo para cuidar a su bebé, vive lejos de su familia",
        "motivation": "Quiere recuperar su bienestar emocional y conectar mejor con su bebé"
    },
    "Roberto - Adolescente Rebelde": {
        "name": "Roberto Martínez",
        "age": 16,
        "occupation": "Estudiante de preparatoria",
        "marital_status": "Soltero",
        "current_situation": "Teniendo conflictos con sus padres y problemas de conducta en la escuela",
        "background": "Adolescente de familia tradicional, se siente incomprendido, problemas de comunicación en casa",
        "motivation": "Quiere que sus padres lo entiendan y encontrar su identidad"
    },
    "Elena - Adulta Mayor Solitaria": {
        "name": "Elena Hernández",
        "age": 68,
        "occupation": "Jubilada",
        "marital_status": "Viuda",
        "current_situation": "Sintiendo soledad y lidiando con la pérdida de su esposo hace dos años",
        "background": "Profesora jubilada, hijos viven en otras ciudades, activa en la comunidad pero se siente sola",
        "motivation": "Quiere encontrar nuevas formas de conectar con otros y dar sentido a esta etapa de su vida"
    }
}

# -------- Helpers / Estado --------
def inicializar_estado():
    if 'pantalla_actual' not in st.session_state:
        st.session_state.pantalla_actual = 'seleccion'
    if 'personaje_seleccionado' not in st.session_state:
        st.session_state.personaje_seleccionado = None
    if 'configuracion' not in st.session_state:
        st.session_state.configuracion = None
    if 'historial_chat' not in st.session_state:
        st.session_state.historial_chat = []
    if 'voice_mode' not in st.session_state:
        st.session_state.voice_mode = True
    if 'voice' not in st.session_state:
        st.session_state.voice = "alloy"
    if 'audio_format' not in st.session_state:
        st.session_state.audio_format = "wav"

def pantalla_seleccion():
    st.markdown('<h1 style="color: #222831;">🧠 Simulador de Terapia Psicológica</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #222831;">Selecciona un personaje para comenzar la simulación</h3>', unsafe_allow_html=True)
    st.markdown("---")

    cols = st.columns(2)
    for i, (nombre_personaje, config) in enumerate(PERSONAJES.items()):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"""
                <div style="
                    border: 2px solid #f0f2f6;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                    background-color: #fafafa;
                ">
                    <h4 style="color: #1f77b4; margin-top: 0;">{nombre_personaje}</h4>
                    <p><strong>Edad:</strong> {config['age']} años</p>
                    <p><strong>Ocupación:</strong> {config['occupation']}</p>
                    <p><strong>Estado civil:</strong> {config['marital_status']}</p>
                    <p><strong>Situación actual:</strong> {config['current_situation']}</p>
                    <p><strong>Motivación:</strong> {config['motivation']}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Seleccionar {config['name']}", key=f"btn_{i}", use_container_width=True):
                    st.session_state.personaje_seleccionado = nombre_personaje
                    st.session_state.configuracion = config
                    st.session_state.pantalla_actual = 'chat'
                    st.session_state.historial_chat = []
                    st.rerun()

# --- Llamadas al API ---
def enviar_mensaje_api_text(mensaje: str, configuracion: Dict[str, Any]) -> str:
    try:
        payload = {"message": mensaje, "configuration": configuracion}
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            data = data.get("output")
            return data.get('message', 'No hay respuesta del servidor')
        else:
            return f"Error del servidor: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ No se puede conectar al servidor. Revisa que el API esté en http://localhost:8000"
    except requests.exceptions.Timeout:
        return "⏱️ Tiempo de espera agotado."
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"

def enviar_mensaje_api_voice(mensaje: str, voice: str, audio_format: str) -> Dict[str, Any]:
    """
    Llama a /simulator/voice y devuelve dict con:
      - audio_bytes
      - mime (por ej. 'audio/wav')
      - transcript (si viene en header X-Transcript)
    """
    try:
        payload = {"message": mensaje, "voice": voice, "format": audio_format, "configuration": st.session_state.configuracion}
        response = requests.post(API_VOICE_URL, json=payload, timeout=60)

        if response.status_code != 200:
            return {"error": f"Error del servidor: {response.status_code} - {response.text}"}

        transcript = response.headers.get("X-Transcript", "")
        audio_bytes = response.content
        mime = f"audio/{audio_format}"

        return {"audio_bytes": audio_bytes, "mime": mime, "transcript": transcript}
    except requests.exceptions.ConnectionError:
        return {"error": "❌ No se puede conectar al servidor. Asegúrate de que /simulator/voice esté arriba."}
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Tiempo de espera agotado al generar audio."}
    except Exception as e:
        return {"error": f"❌ Error inesperado: {str(e)}"}

# --- Pantalla de chat (texto + voz) ---
def pantalla_chat():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"<h1 style='color: #222; font-weight: bold;'>💬 Conversando con {st.session_state.configuracion['name']}</h1>",
            unsafe_allow_html=True
        )
        st.caption(f"{st.session_state.configuracion['occupation']} | {st.session_state.configuracion['age']} años")
    with col2:
        if st.button("🔙 Volver a Selección", use_container_width=True):
            st.session_state.pantalla_actual = 'seleccion'
            st.session_state.historial_chat = []
            st.rerun()

    st.markdown("---")

    # Sidebar con controles
    with st.sidebar:
        st.markdown("### 👤 Información del Personaje")
        c = st.session_state.configuracion
        st.markdown(f"**Nombre:** {c['name']}")
        st.markdown(f"**Edad:** {c['age']} años")
        st.markdown(f"**Ocupación:** {c['occupation']}")
        st.markdown(f"**Estado civil:** {c['marital_status']}")
        st.markdown(f"**Situación actual:** {c['current_situation']}")
        st.markdown(f"**Trasfondo:** {c['background']}")
        st.markdown(f"**Motivación:** {c['motivation']}")
        st.markdown("---")

        st.session_state.voice_mode = st.toggle("Responder con voz", value=st.session_state.voice_mode)
        if st.session_state.voice_mode:
            st.session_state.voice = st.selectbox("Voz", ["alloy", "echo", "shimmer"], index=["alloy","echo","shimmer"].index(st.session_state.voice))
            st.session_state.audio_format = st.selectbox("Formato", ["wav","mp3","m4a"], index=["wav","mp3","m4a"].index(st.session_state.audio_format))

        if st.button("🗑️ Limpiar Chat", use_container_width=True):
            st.session_state.historial_chat = []
            st.rerun()

    # Contenedor del chat
    chat_container = st.container()
    with chat_container:
        for mensaje in st.session_state.historial_chat:
            if mensaje['tipo'] == 'usuario':
                st.markdown(f"""
                <div style="text-align:right;margin:10px 0;">
                    <div style="display:inline-block;background-color:#007bff;color:white;padding:10px 15px;border-radius:18px;max-width:70%;word-wrap:break-word;">
                        {mensaje['contenido']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            elif mensaje['tipo'] == 'personaje_texto':
                st.markdown(f"""
                <div style="text-align:left;margin:10px 0;">
                    <div style="display:inline-block;background-color:#f1f3f4;color:#202124;padding:10px 15px;border-radius:18px;max-width:70%;word-wrap:break-word;">
                        <strong>{st.session_state.configuracion['name']}:</strong><br>{mensaje['contenido']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            elif mensaje['tipo'] == 'personaje_audio':
                # Burbuja con reproductor de audio y transcript
                st.markdown(f"""
                <div style="text-align:left;margin:10px 0;">
                    <div style="display:inline-block;background-color:#f1f3f4;color:#202124;padding:10px 15px;border-radius:18px;max-width:70%;word-wrap:break-word;">
                        <strong>{st.session_state.configuracion['name']} (voz):</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.audio(mensaje['audio_bytes'], format=mensaje['mime'])
                if mensaje.get('transcript'):
                    st.caption(f"📝 {mensaje['transcript']}")

    st.markdown("---")

    # Form de entrada
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4,1])
        with col1:
            mensaje_usuario = st.text_input(
                "Escribe tu mensaje:",
                placeholder=f"Escribe algo para {st.session_state.configuracion['name']}...",
                label_visibility="collapsed"
            )
        with col2:
            enviar = st.form_submit_button("Enviar", use_container_width=True)

    if enviar and mensaje_usuario.strip():
        # Agregar mensaje del usuario
        st.session_state.historial_chat.append({'tipo': 'usuario', 'contenido': mensaje_usuario})

        if st.session_state.voice_mode:
            with st.spinner(f"🗣️ Generando respuesta en voz..."):
                res = enviar_mensaje_api_voice(
                    mensaje_usuario,
                    st.session_state.voice,
                    st.session_state.audio_format
                )
            if "error" in res:
                st.session_state.historial_chat.append({'tipo':'personaje_texto','contenido':res["error"]})
            else:
                st.session_state.historial_chat.append({
                    'tipo': 'personaje_audio',
                    'audio_bytes': res['audio_bytes'],
                    'mime': res['mime'],
                    'transcript': res.get('transcript','')
                })
        else:
            with st.spinner(f"🤔 {st.session_state.configuracion['name']} está pensando..."):
                respuesta = enviar_mensaje_api_text(mensaje_usuario, st.session_state.configuracion)
            st.session_state.historial_chat.append({'tipo':'personaje_texto','contenido':respuesta})

        st.rerun()

# --- Estilos & main ---
def main():
    inicializar_estado()
    st.markdown("""
    <style>
    .stApp { background-color:#ffffff; }
    .stTextInput > div > div > input { border-radius:20px; }
    .stButton > button { border-radius:20px; border:none; transition: all .3s; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow:0 4px 8px rgba(0,0,0,.1); }
    div[data-testid="stSidebar"] { background-color:#f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.pantalla_actual == 'seleccion':
        pantalla_seleccion()
    elif st.session_state.pantalla_actual == 'chat':
        pantalla_chat()

if __name__ == "__main__":
    main()
