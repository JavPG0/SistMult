import os

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

from preproceso import Preproceso

load_dotenv()

DB = "postgres"

user = os.getenv("USER")
password = os.getenv("PASSWORD")
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@host.docker.internal/{DB}", echo=False)

def main():

    now = datetime.now()

    with engine.connect() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS bronze;'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS silver;'))
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS gold;'))
        conn.commit()

    spotify_youtube = pd.read_csv("Dataset/Spotify_Youtube.csv")
    track_emotions = pd.read_csv("Dataset/Track_Emotions.csv")
    track_genres = pd.read_csv("Dataset/Track_Genres.csv")
    track_genres["timestamp"] = [now] * len(track_genres.index)

    spotify_youtube.to_sql(name='spotify_youtube', con=engine, schema='bronze', if_exists='replace', index=False)
    track_emotions.to_sql(name='track_emotions', con=engine, schema='bronze', if_exists='replace', index=False)
    track_genres.to_sql(name='track_genres', con=engine, schema='bronze', if_exists='replace', index=False)

    preprocesador = Preproceso()
    unified = preprocesador.preprocesar(spotify_youtube, track_emotions, track_genres)
    unified.to_sql(name='unified', con=engine, schema='silver', if_exists='replace', index=False)

if __name__ == "__main__":
    main()
