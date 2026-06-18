from langgraph.graph import StateGraph, END
from chatbot_state import ChatbotState
from chatbot_nodes import (
    greeting_node,
    guardarrailes_node,
    sql_generator_node ,
    sql_execution_node,
    validator_node
)

import sys
sys.path.append('/code/Src')
from logger_config import setup_logger

logger = setup_logger('chatbot_graph', 'chatbot_graph.log')

def continue_after_greeting(state: ChatbotState) -> str:
    """Decide qué hacer después del greeting."""
    if state['is_greeting']:
        logger.debug(f"[ROUTING] continue_after_greeting → END")
        return "END"
    else:
        logger.debug(f"[ROUTING] continue_after_greeting → input_guardrails")
        return "input_guardrails"


def continue_after_input_guardrails(state: ChatbotState) -> str:
    """Decide qué hacer después de guardrails."""
    if state['errors']:
        logger.debug(f"[ROUTING] continue_after_input_guardrails → END")
        return "END"
    else:
        logger.debug(f"[ROUTING] continue_after_input_guardrails → sql_generation")
        return "sql_generation"


def continue_after_sql_execution(state: ChatbotState) -> str:
    """Decide qué hacer después de ejecutar SQL."""
    if state['errors']: 
        logger.debug(f"[ROUTING] continue_after_sql_execution → END")
        return "END"
    else:
        logger.debug(f"[ROUTING] continue_after_sql_execution → hypothesis_validation")
        return "hypothesis_validation"

"""def continue_after_sql_execution(state: ChatbotState) -> bool:
    if state['sql_results']:
        logger.debug(f"[ROUTING] continue_after_sql_execution → hypothesis_validation")
        return "hypothesis_validation"
    else: 
        logger.debug(f"[ROUTING] continue_after_sql_execution → END")
        return "END" """


def create_chatbot_graph():
    """Construye el grafo completo."""
    
    logger.info("[GRAPH] Iniciando construcción del grafo")


    workflow = StateGraph(ChatbotState)
    
    # Añadir nodos
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("input_guardrails", guardarrailes_node)
    workflow.add_node("sql_generation", sql_generator_node)
    workflow.add_node("sql_execution", sql_execution_node)
    workflow.add_node("hypothesis_validation", validator_node)
    
    logger.info("[GRAPH] Iniciando construcción del grafo")

    # Punto de entrada
    workflow.set_entry_point("greeting")
    
    # Conectar nodos
    workflow.add_conditional_edges(
        "greeting",
        continue_after_greeting,
        {
            "END": END,
            "input_guardrails": "input_guardrails"
        }
    )
    
    workflow.add_conditional_edges(
        "input_guardrails",
        continue_after_input_guardrails,
        {
            "END": END,
            "sql_generation": "sql_generation"
        }
    )
    
    workflow.add_edge("sql_generation", "sql_execution")
    
    workflow.add_conditional_edges(
        "sql_execution",
        continue_after_sql_execution,
        {
            "END": END,
            "hypothesis_validation": "hypothesis_validation"
        }
    )
    
    workflow.add_edge("hypothesis_validation", END)
    
    logger.info("[GRAPH] Grafo compilado exitosamente")


    # Compilar
    compiled_graph = workflow.compile()
    return compiled_graph


# Exportar
chatbot_graph = create_chatbot_graph()