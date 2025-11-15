import datetime
import os

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine("postgresql+psycopg2://{USER}:{PASSWORD}@127.0.0.1/postgres", echo=False)

def main():
    spotify_youtube = pd.read_csv("Dataset/Spotify_Youtube.csv")
    track_emotions = pd.read_csv("Dataset/Track_Emotions.csv")
    track_genres = pd.read_csv("Dataset/Track_Genres.csv")

    spotify_youtube.to_sql(name='spotify_youtube', con=engine, if_exists='append')
    track_emotions.to_sql(name='track_emotions', con=engine, if_exists='append')
    track_genres.to_sql(name='track_genres', con=engine, if_exists='append')

if __name__ == "__main__":
    main()
