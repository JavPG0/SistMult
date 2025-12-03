from huggingface_hub import InferenceClient
import os

API_KEY = os.getenv("API_KEY")
# ==============================================================================
# MÓDULO DE CLIENTE API (HUGGING FACE)
# ==============================================================================
# 
# Utiliza la librería oficial 'huggingface_hub' para comunicar nuestro frontend 
# en Streamlit con el endpoint de inferencia de Meta-Llama.

# --------------------------
# Configuración y Constantes
# --------------------------
HF_API_KEY = API_KEY

# Modelo seleccionado: Llama-3.2-3B-Instruct. 
LLAMA_MODEL = "meta-llama/Llama-3.2-3B-Instruct"

# Inicialización del cliente (Singleton pattern simplificado para el script)
try:
    client = InferenceClient(api_key=HF_API_KEY)
except Exception as e:
    # Capturamos fallos de instanciación temprana (ej. problemas de librería)
    print(f"[ERROR CRÍTICO] Fallo al inicializar InferenceClient: {e}")
    client = None


def send_message_to_api(message, session_id=None, history=None):
    """
    Gestiona la comunicación con el LLM.
    
    Responsabilidades:
    1. Validar el estado del cliente.
    2. Serializar el historial de chat de Streamlit al formato estándar de OpenAI/HF.
    3. Configurar hiperparámetros de generación (Temperature, Top-P).
    4. Manejar excepciones de red o API.

    Args:
        message (str): El input actual del usuario.
        session_id (str): ID único para trazabilidad (opcional).
        history (list): Lista de tuplas (sender, msg) proveniente de st.session_state.

    Returns:
        str: La respuesta generada por el modelo o un mensaje de error controlado.
    """
    
    # Fail-safe por si la inicialización global falló
    if client is None:
        return "Error 500: El servicio de inferencia no está disponible."

    if history is None:
        history = []

    # ---------------------------------------------------------
    # Construcción del Payload (Context Window Management)
    # ---------------------------------------------------------
    
    # 1. System Prompt: Inyección de contexto inicial para condicionar el comportamiento
    # del modelo (Persona adoption).
    messages_payload = [
        {
            "role": "system", 
            "content": "Eres un asistente experto en música, amigable y conciso. Ayudas a descubrir canciones, explicar géneros y datos curiosos."
        }
    ]

    # 2. Transformación de Estructuras de Datos
    # El estado de Streamlit usa tuplas [('user', 'hola'), ...], pero la API 
    # espera una lista de diccionarios JSON con claves "role" y "content".
    for sender, msg in history:
        # Mapeo de roles: 'user' -> 'user', cualquier otro -> 'assistant'
        role = "user" if sender == "user" else "assistant"
        messages_payload.append({"role": role, "content": msg})

    # NOTA DE ARQUITECTURA: 
    # No añadimos el 'message' actual manualmente aquí porque la lógica en app.py 
    # ya hace un .append() al historial antes de llamar a esta función.
    # Si lo añadiéramos, duplicaríamos el último prompt en el contexto.

    try:
        # -----------------------------------------------------
        # Llamada a la API (Inferencia)
        # -----------------------------------------------------
        completion = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages_payload,
            # Hiperparámetros de generación:
            temperature=0.7,    # Balance entre creatividad y coherencia.
            max_tokens=500,     # Límite duro para evitar respuestas infinitas y latencia.
            top_p=0.9           # Nucleus sampling para variedad léxica.
        )
        
        # Parsing de la respuesta: Extraemos solo el contenido del mensaje
        respuesta = completion.choices[0].message.content.strip()
        return respuesta

    except Exception as e:
        # Manejo de errores en tiempo de ejecución (Timeouts, Rate Limits, Auth Errors)
        return f"[API ERROR] No se pudo completar la solicitud: {e}"