from typing import TypedDict, Optional, List, Dict, Any

class ChatbotState(TypedDict):
    user_query: str
    is_greeting: bool
    sql_query: Optional[str]
    sql_results: Optional[List[Dict[str, Any]]]
    hypothesis_valid: Optional[bool]
    final_answer: Optional[str]
    errors: List[str]

