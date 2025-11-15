import os

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("USER")
password = os.getenv("PASSWORD")
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@127.0.0.1/postgres", echo=False)

def main():

    with engine.connect() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
        conn.execute("CREATE SCHEMA IF NOT EXISTS silver;")
        conn.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    spotify_youtube = pd.read_csv("Dataset/Spotify_Youtube.csv")
    track_emotions = pd.read_csv("Dataset/Track_Emotions.csv")
    track_genres = pd.read_csv("Dataset/Track_Genres.csv")

    spotify_youtube.to_sql(name='spotify_youtube', con=engine, schema='bronze', if_exists='replace', index=False)
    track_emotions.to_sql(name='track_emotions', con=engine, schema='bronze', if_exists='replace', index=False)
    track_genres.to_sql(name='track_genres', con=engine, schema='bronze', if_exists='replace', index=False)

if __name__ == "__main__":
    main()
