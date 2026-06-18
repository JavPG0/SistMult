from xxlimited import Str
from chatbot_state import ChatbotState
from typing import Any, Dict
from api_client import send_message_to_api, validate_hypothesis_with_llm
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re
import sys
sys.path.append('/code/Src')
from logger_config import setup_logger
from logger_decorators import log_execution

logger = setup_logger('chatbot_nodes', 'chatbot_nodes.log')

# Nodo 1. Greeting Node
@log_execution(logger)
def greeting_node(state: ChatbotState) -> Dict[str, Any]:
    user_query = state['user_query'].lower().strip()

    logger.info(f"[GREETING] Procesando: {user_query}")


    greetings = ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos', 'que tal']
    
    if any(greet in user_query for greet in greetings):
        logger.info("[GREETING] Saludo detectado")
        message = "¡Hola! ¿En qué puedo ayudarte?"
        return {
            'is_greeting': True,
            'final_answer': message,
            'errors': None
        }
    else:
        logger.info("[GREETING] No es saludo, continuar al siguiente nodo")
        return {
            'is_greeting': False,
            'final_answer': None,
            'errors': None
        }
 
# Nodo 2. Guardarrailes Node 
@log_execution(logger)  
def guardarrailes_node(state: ChatbotState) -> Dict[str, Any]:
    user_query = state['user_query'].lower().strip()
    erros = []
    # Validamos varias cosas básicas.
    
    logger.info(f"[GUARDRAILS] Validando consulta: {user_query[:50]}...")


    # Consulta demasiado larga.
    if len(user_query) > 1000:
        erros.append("La consulta es demasiado larga.")
        logger.warning(f"[GUARDRAILS] Consulta muy larga: {len(user_query)} chars")

    #Palabras peligrosas (consultas que pueden hacer que se modifiquen datos).
    dangerous_words = ['borrar', 'eliminar', 'drop', 'update', 'insert', 'create', 'alter', 'crear', 'modificar']

    for word in dangerous_words:
        if word in user_query:
            erros.append(f"La consulta contiene una palabra peligrosa: '{word}'.")
            logger.warning(f"[GUARDRAILS] Palabra peligrosa detectada: {word}")

    # Validamos que la consulta sea sobre música.
    music_keywords = [
        "canción", "canciones", "cancion", "song",
        "artista", "artistas", "artist",
        "género", "genero", "genre",
        "popular", "popularidad", "popularity",
        "reproducción", "reproducciones", "streams",
        "likes", "me gusta",
        "música", "musica", "music",
        "album", "álbum",
        "tempo", "ritmo",
        "spotify", "youtube"
    ]

    musical_quety = any(keyword in user_query for keyword in music_keywords)
    if not musical_quety:
        erros.append("La consulta no parece estar relacionada con música.")

    if erros:
        logger.warning("[GUARDRAILS] Consulta no musical detectada")
        errores = " ".join(erros)

        return {
            'errors': erros,
            'final_answer': errores
        }
    else:
        logger.info("[GUARDRAILS] Validación exitosa")
        return {
            'error': None,
            'final_answer': None
        }
    
# Nodo 3. Generador de SQL.
@log_execution(logger)
def sql_generator_node(state: ChatbotState) -> Dict[str, Any]:
    user_query = state['user_query']
    logger.info(f"[SQL_GEN] Generando SQL para: {user_query[:50]}...")

    
    try:
        response = send_message_to_api(message = user_query)

        logger.debug(f"[SQL_GEN] Respuesta cruda del LLM: {response[:100]}...")

        sql_query = response.strip()

        sql_query = re.sub(r'\bFROM\s+gold\b(?!\.)', 'FROM gold.gold', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'\bJOIN\s+gold\b(?!\.)', 'JOIN gold.gold', sql_query, flags=re.IGNORECASE)

        logger.info(f"SQLGEN SQL corregida: {sql_query}")

        logger.info(f"[SQL GENERATOR] SQL generada: {sql_query}")

        #Eliminamos las comillas del formato md.
        if sql_query.startswith("```sql") and sql_query.endswith("```"):
            sql_query = sql_query[6:-3].strip()
        elif sql_query.startswith("```") and sql_query.endswith("```"):
            sql_query = sql_query[3:-3].strip()
        elif sql_query.startswith("'") and sql_query.endswith("'"):
            sql_query = sql_query[1:-1].strip()
        elif sql_query.startswith('"') and sql_query.endswith('"'):
            sql_query = sql_query[1:-1].strip()

        sql_query = sql_query.strip()

        logger.info(f"[SQL_GEN] SQL generada: {sql_query}")

        #Validamos aqui de forma más básica, en vez de crear otro nodo.
        if not sql_query.lower().startswith("select"):
            logger.error("[SQL_GEN] SQL no válida - no empieza con SELECT")

            return {
                'sql_query': None,
                'errors': ["La consulta SQL generada no es una consulta SELECT válida."]
            }
        
        logger.info("[SQL_GEN] SQL validada correctamente")
        return {
            'sql_query': sql_query,
            'error': None
        }
    
    except Exception as e:
        logger.error(f"[SQL_GEN] Error: {e}", exc_info=True)
        return {
            'sql_query': None,
            'errors': [f"Error al generar la consulta SQL: {str(e)}"]
        }
    
# Nodo 4. Ejecucion de SQL.
@log_execution(logger)
def sql_execution_node(state:ChatbotState) -> Dict [str, Any]:
    sql_query = state['sql_query']

    logger.info(f"[SQL_EXEC] Ejecutando SQL:\n{sql_query}")


    # Variables de configuración
    connection = None
    cursor = None

    try:
        #Conectamos a la base de datos.
        connection = psycopg2.connect(
            dbname="spotigres",
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=os.getenv("POSTGRES_PORT", 5432)
        )

        logger.debug(f"[SQL_EXEC] Conectando a {os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', 5432)}/spotigres")

        #Creacion de un cursor que devuelve diccionarios.
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        logger.info("[SQL_EXEC] Conexión establecida")


        cursor.execute("SET search_path TO gold, public;")
        #Ejecutamos la consulta.
        cursor.execute(sql_query)
        #Obtener los resultados.
        results = cursor.fetchall()
        sql_results = [dict(row) for row in results]
        
        logger.info(f"[SQL_EXEC] Query exitosa - {len(sql_results)} filas devueltas")


        #Validamos si hay resultados.
        if not sql_results:
            logger.warning("[SQL_EXEC] Query no devolvió resultados")

            return {
                'sql_results': None,
                'errors': ["La consulta SQL no devolvió ningún resultado."]
            }
        
        return {
            'sql_results': sql_results,
            'error': None
        }
    
    except psycopg2.Error as db_error:
        logger.error(f"[SQL_EXEC] Error de PostgreSQL: {db_error}", exc_info=True)
        logger.error(f"[SQL_EXEC] SQL que falló:\n{sql_query}")

        import traceback
        
        error_completo = str(db_error)
        
        # Construir mensaje detallado
        error_msg = f"❌ **Error al ejecutar la consulta SQL**\n\n"
        error_msg += f"**Tipo:** {type(db_error).__name__}\n\n"
        error_msg += f"**Detalle completo:**\n``````\n\n"
        error_msg += f"**SQL que falló:**\n``````"
        
        return {
            'sql_results': None,
            'errors': [str(db_error)],
            'final_answer': error_msg
        }
        
    except Exception as e:
        logger.error(f"[SQL_EXEC] Error inesperado: {e}", exc_info=True)
        import traceback
        
        error_msg = f"❌ **Error inesperado**\n\n"
        error_msg += f"**Tipo:** {type(e).__name__}\n\n"
        error_msg += f"**Mensaje:** {str(e)}\n\n"
        error_msg += f"**Traceback:**\n``````"
        
        return {
            'sql_results': None,
            'errors': [str(e)],
            'final_answer': error_msg
        }

    

    #Cerramos el cursor y la conexion.
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Nodo 5. Validador hipótesis.
def validator_node (state: ChatbotState) -> Dict[Str, Any]:
    user_query = state["user_query"]
    sql_results = state["sql_results"]

    logger.info(f"[VALIDATOR] Validando hipótesis: {user_query[:50]}...")
    logger.debug(f"[VALIDATOR] Datos: {len(sql_results)} resultados")


    try:
        #LLm
        llm_response = validate_hypothesis_with_llm(user_query= user_query, sql_results=state['sql_results'])
        logger.info(f"[VALIDATOR] Respuesta cruda del LLM: {llm_response[:100]}...")

        #Analizamos la respuesta.
        llm_response = llm_response.strip()

        if llm_response.upper().startswith("CORRECTA"):
            hip = True
            final_answer = llm_response
            logger.info("[VALIDATOR] Hipótesis CORRECTA")
        elif llm_response.upper().startswith("INCORRECTA"):
            hip = False
            final_answer = llm_response
            logger.info("[VALIDATOR] Hipótesis INCORRECTA")
        else:
            logger.warning("[VALIDATOR] No se pudo determinar validez")
            
            return {
                'hypothesis_valid': None,
                'final_answer': llm_response,
                'error': ["La respuesta del modelo no pudo ser interpretada para validar la hipótesis."]
            }
        
        return {
            'hypothesis_valid': hip,
            'final_answer': final_answer,
            'errors': None
        }
    
    except Exception as e:
        return {
            'hypothesis_valid': None,
            'errors': [f"Error al validar la hipótesis: {str(e)}"]
        }