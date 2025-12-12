from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
#import Src.api as api

load_dotenv()

API_KEY = os.getenv("API_KEY")
# ==============================================================================
# MÓDULO DE CLIENTE API (HUGGING FACE)
# ==============================================================================

# Utiliza la librería oficial 'huggingface_hub' para comunicar nuestro frontend
# en Streamlit con el endpoint de inferencia de Meta-Llama.

# --------------------------
# Configuración y Constantes
# --------------------------
HF_API_KEY = str(API_KEY)

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
            "content": """
                ***Solo puedes devolver sentencias SQL, sin explicación ni lenguaje natural.
                Eres un agente experto en SQL, traduce la peticion del usuario de lenguaje natural a SQL.
                Apoyate en el modelo semantico de los datos que te proporciono para generar la SQL.***

                El modelo semantico es un json que sigue la siguiente estructura:
                    - Hay un campo schema que indica el schema donde se encuentra la tabla en la base de datos.
                    - Hay un campo tabla que indica la tabla donde se encuentran las columnas.
                    - Hay un campo columna que indica la columna donde se encuentran los datos.
                    - Hay un campo descripcion que indica qué representan los datos de esa columna.

                Dentro de cada schema hay un array de tablas.
                Dentro de cada tabla tabla hay un array de columnas.
                Dentro de cada columna se encuentra su descripcion.

                Sigue estas ***reglas***:
                    - Devuelve unicamente la SQL generada, sin explicación.
                    - Haz la SQL de la manera más sencilla posible.
                    - Siempre que puedas, utiliza los datos del schema gold.
                    - No utilices los datos del schema silver a no ser que sea estríctamente necesario.
                    - Siempre intenta utilizar los datos de las filas con el "timestamp" más reciente.
                    - Ten en cuenta que los datos numéricos están escalados entre 0 y 1 para que sea más facil su comparación. Por eso es importante que, si recibes algún valor numérico en la petición del usuario, lo intentes adaptar si fuera necesario.

                <Modelo semantico de los datos>
                {
                    "schema": "gold"[
                        {
                        "tabla": "gold"[
                            {
                            "columna": "Artista"
                            "descripcion": "Artista al que se le atribuye la canción."
                            },
                            {
                            "columna": "Canción"
                            "descripcion": "Canción a la que se le atribuyen las métricas del resto de columnas."
                            },
                            {
                            "columna": "Género"
                            "descripcion": "Género musical que se le atribuye a la canción."
                            },
                            {
                            "columna": "Emociones"
                            "descripcion": "Emociones que transmite la canción."
                            },
                            {
                            "columna": "Tonalidad"
                            "descripcion": "Tonalidad que tiene la canción la canción."
                            },
                            {
                            "columna": "Tempo"
                            "descripcion": "Tempo que tiene la canción."
                            },
                            {
                            "columna": "Reproducciones"
                            "descripcion": "Número de reproducciones que ha tenido la canción."
                            },
                            {
                            "columna": "Likes"
                            "descripcion": "Número de likes que ha tenido la canción."
                            },
                            {
                            "columna": "Popularidad"
                            "descripcion": "Valor que representa la popularidad general de la canción."
                            },
                            {
                            "columna": "timestamp"
                            "descripcion": "Fecha y hora en la que esa fila ha sido introducida en la tabla."
                            },
                        ]
                        }
                    ]
                    }
                    </Modelo semantico de los datos>
                    """
        }
    ]

# Implementación del schema silver (por si hiciese falta más adelante)
    """
    ,
                    {
                    "schema": "silver"[
                        {
                        "tabla": "unified"[
                            {
                            "columna": "artist_name"
                            "descripcion": "Artista al que se le atribuye la canción."
                            },
                            {
                            "columna": "Track"
                            "descripcion": "Canción a la que se le atribuyen las métricas del resto de columnas."
                            },
                            {
                            "columna": "Title"
                            "descripcion": "Título de la canción en YouTube."
                            },
                            {
                            "columna": "genre"
                            "descripcion": "Género musical que se le atribuye a la canción."
                            },
                            {
                            "columna": "seeds"
                            "descripcion": "Emociones que transmite la canción."
                            },
                            {
                            {
                            "columna": "Tempo"
                            "descripcion": "Tempo que tiene la canción."
                            },
                            {
                            "columna": "Reps"
                            "descripcion": "Número de reproducciones que ha tenido la canción."
                            },
                            {
                            "columna": "Likes"
                            "descripcion": "Número de likes que ha tenido la canción."
                            },
                            {
                            "columna": "popularity"
                            "descripcion": "Valor que representa la popularidad general de la canción."
                            },
                            {
                            "columna": "timestamp"
                            "descripcion": "Fecha y hora en la que esa fila ha sido introducida en la tabla."
                            },
                            {
                            "columna": "Unnamed: 0"
                            "descripcion": "Número sin valor que intenta representar un id único de la canción."
                            },
                            {
                            "columna": "Url_spotify"
                            "descripcion": "URL que aloja la canción en Spotify."
                            },
                            {
                            "columna": "Album"
                            "descripcion": "Album al que pertenece l canción."
                            },
                            {
                            "columna": "Album_type"
                            "descripcion": "Determina si el album al que pertenece la canción es un album o un single."
                            },
                            {
                            "columna": "Uri"
                            "descripcion": "Uri que que identifica a la canción dentro del sistema de Spotify."
                            },
                            {
                            "columna": "Danceability"
                            "descripcion": "Valor que intenta medir la bailabilidad de la canción."
                            },
                            {
                            "columna": "Energy"
                            "descripcion": "Valor que intenta medir la energía de la canción."
                            },
                            {
                            "columna": "Key"
                            "descripcion": "Valor que representa la armadura (bemoles/sostenidos) que utiliza la canción."
                            },
                            {
                            "columna": "Loudness"
                            "descripcion": "Valor que mide qué tan ruidosa es la canción."
                            },
                            {
                            "columna": "Danceability"
                            "descripcion": "Valor que intenta medir la bailabilidad de la canción."
                            },
                            {
                            "columna": "Speechiness"
                            "descripcion": "Valor que intenta medir la vocalidad de la canción."
                            },
                            {
                            "columna": "Acousticness"
                            "descripcion": "Valor que intenta medir la musicalidad de la canción."
                            },
                            {
                            "columna": "Instrumentalness"
                            "descripcion": "Valor que intenta medir la instrumentalidad de la canción."
                            },
                            {
                            "columna": "Liveness"
                            "descripcion": "Valor que intenta medir la vitalidad de la canción."
                            },
                            {
                            "columna": "Valence"
                            "descripcion": "Valor que intenta medir la valencia de la canción."
                            },
                            {
                            "columna": "Duration_ms"
                            "descripcion": "Valor que mide cuánto dura la canción en milisegundos."
                            },
                            {
                            "columna": "Url_youtube"
                            "descripcion": "URL que aloja la canción en YouTube."
                            },
                            {
                            "columna": "Channel"
                            "descripcion": "Canal donde está subida la canción en YouTube."
                            },
                            {
                            "columna": "Views"
                            "descripcion": "Número de visualiaciones que ha tenido la canción en YouTube."
                            },
                            {
                            "columna": "Comments"
                            "descripcion": "Cantidad de comentarios de la canción en YouTube."
                            },
                            {
                            "columna": "Description"
                            "descripcion": "Descripción de la canción en YouTube."
                            },
                            {
                            "columna": "Licensed"
                            "descripcion": "Booleano que indica si la canción tiene licencia o no."
                            },
                            {
                            "columna": "official_video"
                            "descripcion": "Booleano que indica si el video de YouTube es oficial o no."
                            },
                            {
                            "columna": "Stream"
                            "descripcion": "Numero de streams que ha tenido la canción en Spotify."
                            },
                            {
                            "columna": "artist_track"
                            "descripcion": "Columna que relaciona el artista con la canción"
                            },
                            {
                            "columna": "mode"
                            "descripcion": "Indica el modo de la canción."
                            },
                            {
                            "columna": "time_signature"
                            "descripcion": "Compás que tiene la canción."
                            }
                        ]
                        }
                    ]
                    }
    """

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
