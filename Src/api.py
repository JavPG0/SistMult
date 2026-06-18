from fastapi import FastAPI
from Src.backend.etl import get_query_data

app = FastAPI()

@app.get("/query")  # Enviar y recibir la query inicial y su resultado
def get_query(query):
    data = get_query_data(query)
    return data
