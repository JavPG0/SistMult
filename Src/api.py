from fastapi import FastAPI, Body
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

DB = "spotigres"

user = os.getenv("USER")
password = os.getenv("PASSWORD")

engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@172.17.0.1:5432/{DB}"
)

app = FastAPI()

last_query = ""

@app.post("/query")
def post_query(sql_query: str = Body(..., embed=True)):
    global last_query
    last_query = sql_query

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()

        df = pd.DataFrame(rows, columns=columns)
        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e), "query": sql_query}


@app.get("/query")
def get_query():
    return {"last_query": last_query}
