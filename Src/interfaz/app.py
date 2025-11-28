"""
DOCUMENTACION DE ESTILOS CSS EN STREAMLIT

El estilo de esta aplicacion se maneja mediante CSS (Cascading Style Sheets)
inyectado directamente en el codigo de Streamlit. Esto permite anular (override)
los estilos predeterminados de la libreria para crear un diseno personalizado,
incluyendo el manejo del modo claro y oscuro.

COMO FUNCIONA EL CSS AQUI:
1.  Se define una cadena de texto (string) multilinea para el CSS del modo claro (LIGHT_CSS)
    y otra para el modo oscuro (DARK_CSS).
2.  Se usa 'st.markdown(CSS_STRING, unsafe_allow_html=True)' para inyectar estos estilos
    en el cuerpo del HTML que genera Streamlit.
3.  La variable 'dark_mode' (un checkbox) determina que conjunto de estilos se aplica.

SELECTORES CSS CLAVE UTILIZADOS:

1.  Selectores de alto nivel para el tema general:
    -   `html, body, [class*="css"]`: Selecciona el fondo y el color de texto de la aplicacion entera.
        Streamlit usa clases generadas, por eso el selector de atributo `[class*="css"]`
        se usa para asegurar que la mayoria de los elementos heredan el estilo.
    -   `!important`: Es crucial para forzar la anulacion de los estilos de Streamlit.

2.  Selectores de componentes de Streamlit:
    -   `section[data-testid="stSidebar"]`: Selecciona y estiliza especificamente la barra lateral (sidebar).
    -   `div[data-testid="stChatInput"]`: Selecciona y estiliza la caja contenedora del input de chat.
    -   `h1, h2, h3, h4, h5, h6`: Estiliza todos los titulos.

3.  Selectores personalizados (Burbujas de chat):
    -   `.user-bubble`: Clase CSS aplicada a los mensajes del usuario.
    -   `.bot-bubble`: Clase CSS aplicada a los mensajes de la respuesta del bot.
        Estas clases se inyectan en el HTML de los mensajes de chat en el bucle principal de la aplicacion.

"""

import streamlit as st
import uuid
# Importacion simulada de la funcion para interactuar con la API del chatbot
# NOTA: Asegurate de que el archivo 'api_client.py' exista y contenga la funcion 'send_message_to_api'.
from api_client import send_message_to_api

# -------------------------
# CONFIG DE PAGINA
# -------------------------
# Define la configuracion basica de la pestana del navegador
st.set_page_config(
    page_title="Chatbot Musical",
    page_icon="🎧",
    layout="wide" # Usa todo el ancho disponible
)

# -------------------------
# SIDEBAR
# -------------------------
# Contenido y controles dentro de la barra lateral
with st.sidebar:
    st.title("⚙️ Ajustes")

    # Checkbox para activar/desactivar el modo oscuro
    dark_mode = st.checkbox("Activar modo oscuro", value=False)

    st.markdown("---")
    st.caption("Proyecto Chatbot Musical")

# -------------------------
# CSS MODO LUZ (estilo original)
# -------------------------
# Estilos CSS para el modo claro (default)
LIGHT_CSS = """
<style>
/* Fondo de pagina claro */
body { background-color: #f5f5f5; }

/* Burbuja de chat para el usuario (azul claro) */
.user-bubble {
    background-color: #4F8BF9;    /* color de fondo */
    color: white;                 /* color del texto */
    padding: 10px 15px;           /* espacion ancho y alto del texto al borde */
    border-radius: 15px;          /* esto es para redondear las equinas, me parece mas moderno */
    max-width: 70%;               /* la burbuja solo puede ocupar el 70 porciento de la pantalla, es bastante */
    margin-left: auto;            /* Alinea a la derecha */
    margin-bottom: 10px;          /* añade espacio abajo para que no se peguen las burbujas */
}

/* Burbuja de chat para el bot (gris claro) */
.bot-bubble {
    background-color: #e8e8e8;   /* color de fondo gris claro */
    color: #222;                 /* color del texto (gris muy oscuro, casi negro) */
    padding: 10px 15px;          /* espacio interno: 10px arriba/abajo, 15px izquierda/derecha */
    border-radius: 15px;         /* redondea las esquinas para que parezca una burbuja moderna */
    max-width: 70%;              /* la burbuja puede ocupar como máximo el 70% del ancho */
    margin-right: auto;          /* empuja la burbuja hacia la izquierda */
    margin-bottom: 10px;         /* espacio debajo de cada burbuja para que no se peguen */
    border: 1px solid #ccc;      /* un borde fino gris claro para darle relieve */
}

/* CORRECCION DE ANCHO CHAT INPUT EN MODO CLARO */
/* El padding por defecto de Streamlit en block-container es grande. Lo ajustamos a 1rem */
div.block-container {
    padding-left: 1rem;      /* reduce el espacio del lado izquierdo del contenido */
    padding-right: 1rem;     /* reduce el espacio del lado derecho del contenido */
    padding-top: 5rem;       /* deja bastante espacio arriba (baja el contenido hacia abajo) */
    padding-bottom: 5rem;    /* deja espacio abajo también para que no quede pegado al borde */
}

/* Compensar el padding de 1rem del block-container para que sea full-width en el borde */
div[data-testid="stChatInput"] {
    margin-left: -1rem !important;      /* empuja el chat input 1rem hacia la izquierda para recuperar el espacio perdido */
    margin-right: -1rem !important;     /* lo mismo pero hacia la derecha */
    width: calc(100% + 2rem) !important;/* ancho total sumando los dos márgenes negativos; así ocupa todo el ancho de verdad */
}
</style>
"""

# -------------------------
# CSS MODO OSCURO (estilo retocado)
# -------------------------
# Estilos CSS para el modo oscuro con paleta moderna (azul-gris)
DARK_CSS = """
<style>

/* Colores base para el modo oscuro: Fondo principal y texto */
html, body, [class*="css"] {
    background-color: #1a1a2e !important; /* Color del fondo de toda la página (gris oscuro profundo) */
    color: #e0e0e0 !important;            /* Color del texto por defecto (gris muy claro, cómodo de leer en oscuro) */
}

/* Sidebar: Fondo ligeramente más claro que el fondo principal para diferenciar visualmente */
section[data-testid="stSidebar"] {
    background-color: #252540 !important; /* gris azulado un poco más claro que el fondo general */
    border-right: 1px solid #3c3c5c;      /* línea vertical sutil que separa la sidebar del contenido */
    color: #ffffff !important;            /* textos de la sidebar en blanco */
}

/* Títulos: les damos un color más suave y elegante que el texto normal */
h1, h2, h3, h4, h5, h6 {
    color: #b0b0d0 !important;            /* gris azulado claro, combina bien con fondos oscuros */
}

/* Texto general: aseguramos que todos los textos básicos sean legibles en modo oscuro */
p, span, label, div {
    color: #e0e0e0 !important;            /* gris casi blanco para máxima legibilidad */
}

/* CORRECCION DE ANCHO: Ajusta el padding lateral del contenedor principal */
/* Reducimos el padding por defecto de Streamlit a 1rem para ganar espacio y ajustamos el chat input. */
/* Ajusta el padding del contenedor principal en modo oscuro */
/* Streamlit mete mucho padding por defecto, así que lo reducimos para que el contenido esté más centrado */
div.block-container {
    padding-left: 1rem !important;   /* Espacio a la izquierda reducido */
    padding-right: 1rem !important;  /* Espacio a la derecha reducido */
    padding-top: 5rem !important;    /* Mantiene un buen espacio arriba, para respirar */
    padding-bottom: 5rem !important; /* Igual para la parte inferior */
}

/* Burbuja Usuario: Azul suave */
.user-bubble {
    background-color: #5c6bc0;       /* Fondo azul suave, moderno */
    padding: 12px 16px;              /* Espacio interno: 12px arriba/abajo, 16px lados */
    border-radius: 18px;             /* Bordes redondeados (estilo moderno tipo chat) */
    color: white;                    /* Texto blanco para buen contraste */
    max-width: 70%;                  /* No ocupar más de 70% del ancho, típico de chats */
    margin-left: auto;               /* Alinea la burbuja del usuario a la derecha */
    margin-bottom: 10px;             /* Espacio inferior para separar mensajes */
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); /* Sombra suave para efecto flotante */
}

/* Burbuja Bot: Gris azulado oscuro */
.bot-bubble {
    background-color: #3e3e5c;       /* Fondo gris-azulado oscuro */
    padding: 12px 16px;              /* Espaciado igual que la burbuja del usuario */
    border-radius: 18px;             /* Bordes redondeados iguales para coherencia visual */
    color: #f0f0f0;                  /* Texto gris claro, fácil de leer */
    max-width: 70%;                  /* Misma limitación de ancho que el usuario */
    margin-right: auto;              /* Alinea la burbuja a la izquierda (lado del bot) */
    margin-bottom: 10px;             /* Separación inferior */
    border: 1px solid #4a4a6e;       /* Borde sutil para diferenciar del fondo */
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); /* Sombra para dar profundidad */
}

/* Estilo para los inputs de texto (cajas donde se escribe) */
input, textarea {
    background-color: #2e2e4a !important;  /* Fondo gris-azulado oscuro para integrarse con el tema */
    color: #f0f0f0 !important;             /* Texto claro para buena legibilidad */
    border-radius: 10px !important;        /* Bordes redondeados (más moderno) */
    border: 1px solid #4a4a6e !important;  /* Borde sutil para separarlo del fondo */
}

/* Caja contenedora del input de chat (la barra inferior donde se escribe el mensaje) */
div[data-testid="stChatInput"] {
    background-color: #2e2e4a !important;  /* Fondo oscuro igual que los inputs */
    border-radius: 12px !important;        /* Bordes redondeados para diseño limpio */
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); /* Sombra suave para que parezca elevado */

    /* Corrección para que el input quede más limpio sin padding extraño de Streamlit */
    padding: 0 !important;
    margin: 0 !important;

    /* FIX: expandir el chat input al ancho completo del contenedor */
    margin-left: -1rem !important;         /* Moverlo hacia fuera para compensar padding */
    margin-right: -1rem !important;        
    width: calc(100% + 2rem) !important;   /* Lo hacemos más ancho sumando los márgenes negativos */
}

/* Texto dentro del chat input */
div[data-testid="stChatInput"] textarea {
    color: #f0f0f0 !important;             /* Texto claro */
    padding: 12px 16px !important;         /* Espaciado interior para que el texto */
    border-radius: 12px !important;        /* Bordes redondeados para suavizar el campo */
}

/* Scrollbar (barra de desplazamiento) */
::-webkit-scrollbar {
    width: 10px;                           /* Ancho de la barra */
}
::-webkit-scrollbar-track {
    background: #252540;                   /* Fondo oscuro del track */
}
::-webkit-scrollbar-thumb {
    background: #5c6bc0;                   /* Color del scroll (consistente con los azules del tema) */
    border-radius: 5px;                    /* Bordes redondeados */
}
::-webkit-scrollbar-thumb:hover {
    background: #7986cb;                   /* Color más claro al pasar el ratón (hover) */
}

/* Texto de la descripción debajo del título */
div[data-testid="stVerticalBlock"] > div:nth-child(2) p {
    color: #c0c0c0 !important;             /* Gris claro para que no destaque demasiado */
}

/* Icono del chatbot en el título */
div[data-testid="stVerticalBlock"] > div:nth-child(1) svg {
    color: #b0b0d0 !important;             /* Gris azulado suave */
}

/* Botón de envío del chat (el icono de la flecha) */
div[data-testid="stChatInput"] button {
    color: #f0f0f0 !important;             /* Color del icono */
    background-color: #5c6bc0 !important;  /* Fondo azul suave acorde al tema */
    border-radius: 10px !important;        /* Bordes redondeados */
    padding: 8px 12px !important;          /* Tamaño más grande y cómodo */
}


</style>
"""

# -------------------------
# APLICAR MODO SELECCIONADO
# -------------------------
# Inyecta los estilos CSS en la pagina, basandose en el estado del checkbox
st.markdown(DARK_CSS if dark_mode else LIGHT_CSS, unsafe_allow_html=True)

# -------------------------
# ESTADO DE LA SESION
# -------------------------
# Inicializa la lista de mensajes en el estado de la sesion
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Inicializa un ID de sesion unico para mantener la conversacion con la API
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# -------------------------
# TITULO
# -------------------------
st.title("Chatbot Musical")

st.write("Habla conmigo sobre musica, Spotify, recomendaciones, datos... lo que quieras")

# -------------------------
# MOSTRAR HISTORIAL
# -------------------------
# Itera sobre el historial de mensajes y los renderiza usando los estilos CSS
for sender, message in st.session_state["messages"]:
    # Determina que clase CSS aplicar (user-bubble o bot-bubble)
    css_class = "user-bubble" if sender == "user" else "bot-bubble"
    st.markdown(f"<div class='{css_class}'>{message}</div>", unsafe_allow_html=True)

# -------------------------
# INPUT DEL USUARIO
# -------------------------
# Crea el campo de entrada de chat
user_msg = st.chat_input("Escribe un mensaje...")

if user_msg:
    # 1. Anade el mensaje del usuario al historial
    st.session_state["messages"].append(("user", user_msg))

    try:
        # 2. Envia el mensaje a la API del chatbot (simulado)
        bot_reply = send_message_to_api(
            message=user_msg,
            session_id=st.session_state["session_id"]
        )
    except Exception as e:
        # Manejo basico de errores de conexion
        bot_reply = f"Error conectando al servidor: {e}"

    # 3. Anade la respuesta del bot al historial
    st.session_state["messages"].append(("bot", bot_reply))

    # 4. Vuelve a ejecutar la aplicacion para actualizar la interfaz
    st.rerun()