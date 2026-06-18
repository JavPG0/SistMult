from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
#import Src.api as api

#Imports para logger.
import sys 
sys.path.append('/code/Src')
from logger_config import setup_logger
from logger_decorators import log_execution               
                
logger = setup_logger('api_client', 'api_client.log')

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

@log_execution(logger)
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

    logger.info("Iniciando llamada al LLM", extra={
        'extra_data': {
            'message_length': len(message),
            'has_history': history is not None,
            'session_id': session_id
        }
    })


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
            "content": """Eres un experto en SQL y análisis de hipótesis. Tu tarea es traducir hipótesis o preguntas del usuario en consultas SQL que obtengan los datos necesarios para validar esa hipótesis.

    ⚠️ IMPORTANTE: Solo devuelves código SQL puro, sin explicaciones.

    ═══════════════════════════════════════════════════════════
    🎯 TU OBJETIVO
    ═══════════════════════════════════════════════════════════

    Cuando el usuario te da una HIPÓTESIS (por ejemplo: "El rock tiene más likes que el pop"), debes:

    1. Identificar QUÉ DATOS se necesitan para validar esa hipótesis
    2. Generar la SQL que obtenga EXACTAMENTE esos datos
    3. Los datos serán usados por otro sistema para confirmar o refutar la hipótesis

    ═══════════════════════════════════════════════════════════
    📋 ESTRUCTURA DE LA BASE DE DATOS
    ═══════════════════════════════════════════════════════════

    TABLA: gold.gold (escribir SIN comillas)

    COLUMNAS (escribir CON comillas dobles):
    ┌─────────────────────┬──────────┬─────────────────────────────────────┐
    │ Columna             │ Tipo     │ Descripción                         │
    ├─────────────────────┼──────────┼─────────────────────────────────────┤
    │ "Artista"           │ text     │ Nombre del artista                  │
    │ "Canción"           │ text     │ Nombre de la canción                │
    │ "Genero"            │ text     │ Género musical (sin tilde)          │
    │ "Emociones"         │ text     │ Lista de emociones                  │
    │ "Tonalidad"         │ decimal  │ 0-1 (normalizado)                   │
    │ "Tempo"             │ decimal  │ 0-1 (normalizado)                   │
    │ "Reproducciones"    │ decimal  │ 0-1 (normalizado)                   │
    │ "Likes"             │ decimal  │ 0-1 (normalizado)                   │
    │ "Comentarios"       │ decimal  │ 0-1 (normalizado)                   │
    │ "Duracion"          │ decimal  │ 0-1 (normalizado)                   │
    │ "Popularidad"       │ decimal  │ 0-1 (normalizado)                   │
    │ "timestamp"         │ timestamp│ Fecha de inserción                  │
    └─────────────────────┴──────────┴─────────────────────────────────────┘

    ⚡ IMPORTANTE: Los valores numéricos están normalizados (0 = mínimo, 1 = máximo)

    ═══════════════════════════════════════════════════════════
    ✅ REGLAS DE SINTAXIS
    ═══════════════════════════════════════════════════════════

    ✓ Tabla: FROM gold.gold (sin comillas)
    ✓ Columnas: SELECT "Artista", "Canción" (con comillas dobles)
    ✓ Valores texto: WHERE "Genero" = 'pop' (comillas simples)
    ✗ NO uses markdown: ``````

    ═══════════════════════════════════════════════════════════
    📚 EJEMPLOS DE HIPÓTESIS → SQL
    ═══════════════════════════════════════════════════════════

    🔹 HIPÓTESIS: "El rock tiene más likes que el pop"
    ANÁLISIS: Necesito comparar el promedio de likes de rock vs pop
    SQL:
    SELECT "Genero", AVG("Likes") as likes_promedio
    FROM gold.gold
    WHERE "Genero" IN ('rock', 'pop')
    GROUP BY "Genero"
    ORDER BY likes_promedio DESC;

    🔹 HIPÓTESIS: "Bad Bunny es el artista más popular"
    ANÁLISIS: Necesito ver la popularidad promedio por artista
    SQL:
    SELECT "Artista", AVG("Popularidad") as popularidad_promedio
    FROM gold.gold
    GROUP BY "Artista"
    ORDER BY popularidad_promedio DESC
    LIMIT 10;

    🔹 HIPÓTESIS: "El género con más canciones es el pop"
    ANÁLISIS: Necesito contar canciones por género
    SQL:
    SELECT "Genero", COUNT(*) as total_canciones
    FROM gold.gold
    GROUP BY "Genero"
    ORDER BY total_canciones DESC;

    🔹 HIPÓTESIS: "Las canciones con tempo alto tienen más reproducciones"
    ANÁLISIS: Necesito correlacionar tempo y reproducciones
    SQL:
    SELECT "Tempo", AVG("Reproducciones") as reproducciones_promedio
    FROM gold.gold
    GROUP BY 
        CASE 
            WHEN "Tempo" >= 0.7 THEN 'Alto'
            WHEN "Tempo" >= 0.4 THEN 'Medio'
            ELSE 'Bajo'
        END
    ORDER BY "Tempo" DESC;

    🔹 HIPÓTESIS: "Taylor Swift tiene más canciones que Drake"
    ANÁLISIS: Necesito contar canciones de ambos artistas
    SQL:
    SELECT "Artista", COUNT(*) as total_canciones
    FROM gold.gold
    WHERE "Artista" IN ('Taylor Swift', 'Drake')
    GROUP BY "Artista";

    🔹 HIPÓTESIS: "El género con más likes tiene un tempo mayor a la media"
    ANÁLISIS: Necesito el género con más likes y su tempo promedio vs media global
    SQL:
    SELECT 
        "Genero",
        AVG("Likes") as likes_promedio,
        AVG("Tempo") as tempo_promedio,
        (SELECT AVG("Tempo") FROM gold.gold) as tempo_media_global
    FROM gold.gold
    GROUP BY "Genero"
    ORDER BY likes_promedio DESC
    LIMIT 1;

    🔹 HIPÓTESIS: "Hay más de 1000 canciones en la base de datos"
    ANÁLISIS: Necesito el conteo total
    SQL:
    SELECT COUNT(*) as total_canciones
    FROM gold.gold;

    🔹 HIPÓTESIS: "Las canciones más recientes son más populares"
    ANÁLISIS: Necesito comparar popularidad por periodo temporal
    SQL:
    SELECT 
        CASE 
            WHEN "timestamp" >= NOW() - INTERVAL '30 days' THEN 'Recientes'
            ELSE 'Antiguas'
        END as periodo,
        AVG("Popularidad") as popularidad_promedio
    FROM gold.gold
    GROUP BY periodo;

    ═══════════════════════════════════════════════════════════
    🧠 PROCESO DE RAZONAMIENTO
    ═══════════════════════════════════════════════════════════

    Para cada hipótesis, pregúntate:

    1. ¿Qué COMPARACIÓN se está haciendo?
    → Usa GROUP BY y AVG/SUM/COUNT

    2. ¿Qué ENTIDADES se comparan?
    → Identifica artistas, géneros, rangos numéricos

    3. ¿Se necesita un RANKING o solo valores específicos?
    → Usa ORDER BY y LIMIT si es necesario

    4. ¿Se compara con la MEDIA GLOBAL?
    → Usa subconsultas para obtener el promedio total

    5. ¿Hay CONDICIONES específicas?
    → Usa WHERE para filtrar

    ═══════════════════════════════════════════════════════════
    ⚡ REGLAS CRÍTICAS
    ═══════════════════════════════════════════════════════════

    1. Los datos deben ser SUFICIENTES para validar la hipótesis
    2. Si se comparan entidades, INCLUYE TODAS en la consulta
    3. Usa agregaciones (AVG, COUNT, SUM) cuando sea necesario
    4. Ordena resultados de forma útil (DESC para "más/mayor")
    5. NUNCA devuelvas texto explicativo, solo SQL pura

    RESPONDE ÚNICAMENTE CON LA CONSULTA SQL QUE OBTENGA LOS DATOS NECESARIOS PARA VALIDAR LA HIPÓTESIS."""
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

        logger.debug("Enviando request al LLM", extra={
            'extra_data': {
                'model': LLAMA_MODEL,
                'messages_count': len(messages_payload)
            }
        })

        # Llamada a la API (Inferencia)
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
        
        logger.info("Respuesta recibida del LLM", extra={
            'extra_data': {
                'response_length': len(respuesta),
                'session_id': session_id
            }
        })
        
        return respuesta

    except Exception as e:
        # Manejo de errores en tiempo de ejecución (Timeouts, Rate Limits, Auth Errors)
        return f"[API ERROR] No se pudo completar la solicitud: {e}"

@log_execution(logger)
def validate_hypothesis_with_llm(user_query, sql_results):

    logger.info("Iniciando validación de hipótesis", extra={
        'extra_data': {
            'query': user_query[:100],  # Primeros 100 chars
            'results_count': len(sql_results)
        }
    })

    if client is None:
        return "Error 500: El servicio de inferencia no está disponible."
    
    # FORMATEAR LOS RESULTADOS
    results_text = ""
    for i, row in enumerate(sql_results[:10], 1):
        results_text += f"\nFila {i}: {row}"
    
    if len(sql_results) > 10:
        results_text += f"\n\n(Mostrando 10 de {len(sql_results)} resultados totales)"
    
    # CONSTRUIR EL PROMPT DE ANÁLISIS
    user_message = f"""
        Pregunta/Hipótesis del usuario:
        {user_query}

        Datos obtenidos de la base de datos:
        {results_text}

        Analiza si la hipótesis es correcta o incorrecta basándote ÚNICAMENTE en estos datos.
        """
    
    logger.info("Payload de validación construido", extra={
        'extra_data': {
            'user_message_length': len(user_message),
            'message': user_message 
        }}) 
            
    # SYSTEM PROMPT ESPECÍFICO PARA VALIDACIÓN
    messages_payload = [
        {
        "role": "system",
        "content": """
        Eres un analista de datos experto y objetivo.

        Tu única tarea es determinar si una hipótesis es CORRECTA o INCORRECTA basándote en los datos proporcionados.

        FORMATO OBLIGATORIO DE RESPUESTA:
        1. Empieza con la palabra CORRECTA o INCORRECTA
        2. Después explica brevemente por qué, citando datos específicos

        Ejemplo de respuesta correcta:
        "CORRECTA
        Según los datos, la canción 'Shake It Off' de Taylor Swift tiene una popularidad de 0.95, siendo la más alta de todas las 150 canciones analizadas."

        Ejemplo de respuesta incorrecta:
        "INCORRECTA
        Los datos muestran que Bad Bunny tiene 12 canciones mientras que Taylor Swift tiene 15, por lo tanto la hipótesis no se cumple."

        Sé objetivo, preciso y cita siempre los números de los datos.
        """
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    try:
        # LLAMADA A LA API
        completion = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages_payload,
            temperature=0.5,  # Más bajo que el de SQL para ser más consistente
            max_tokens=500,
            top_p=0.9
        )
        
        logger.debug("Enviando request al LLM", extra={
            'extra_data': {
                'model': LLAMA_MODEL,
                'messages_count': len(messages_payload)
            }
        })
            
        respuesta = completion.choices[0].message.content.strip()
        
        logger.info("Validación completada", extra={
            'extra_data': {
                'response_length': len(respuesta)
            }
        })
        
        return respuesta
        
    except Exception as e:
        return f"[API ERROR] Error al validar hipótesis: {e}"