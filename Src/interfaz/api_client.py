# Este cliente NO llama a ninguna API real.
# Solo devuelve una respuesta falsa para probar la interfaz.

def send_message_to_api(message, session_id=None, model=None, temperature=None):
    return f"Dijiste: {message}"
