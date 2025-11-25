import logging
import os

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

from preproceso import Preproceso

import sys 
sys.path.append('/code/Src/')

from logger_config import setup_logger
from logger_decorators import log_execution



logger = setup_logger('etl', 'etl_pipeline.log', level = logging.DEBUG)

load_dotenv()

DB = "spotigres"

user = os.getenv("USER")
password = os.getenv("PASSWORD")
engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@172.17.0.1:5432/{DB}", 
    echo=False
)
@log_execution(logger)
def main():

    logger.info("Starting ETL")

    now = datetime.now()

    try:
        logger.info("Creating schemas if not exist")
        
        with engine.connect() as conn:
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS bronze;'))
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS silver;'))
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS gold;'))
            conn.commit()

        logger.info("Schemas created successfully")

        logger.info("Loading Spotify_Youtube.csv")
        spotify_youtube = pd.read_csv("Dataset/Spotify_Youtube.csv")
        spotify_youtube["timestamp"] = [now] * len(spotify_youtube.index)
        logger.info("CSV loaded", extra={'extra_data': {'file': 'Spotify_Youtube.csv','rows': len(spotify_youtube),'columns': len(spotify_youtube.columns)}})

        logger.info("Loading Track_Emotions.csv")
        track_emotions = pd.read_csv("Dataset/Track_Emotions.csv")
        track_emotions["timestamp"] = [now] * len(track_emotions.index)
        logger.info("CSV loaded", extra={'extra_data': {'file': 'Track_Emotions.csv','rows': len(track_emotions),'columns': len(track_emotions.columns)}})

        logger.info("Loading Track_Genres.csv")
        track_genres = pd.read_csv("Dataset/Track_Genres.csv")
        track_genres["timestamp"] = [now] * len(track_genres.index)
        logger.info("CSV loaded", extra={'extra_data': {'file': 'Track_Genres.csv','rows': len(track_genres),'columns': len(track_genres.columns)}})




        # Storing raw data in bronze schema

        logger.info("Storing raw data in bronze schema")
        
        spotify_youtube.to_sql(name='spotify_youtube', con=engine, schema='bronze', if_exists='append', index=False)
        track_emotions.to_sql(name='track_emotions', con=engine, schema='bronze', if_exists='append', index=False)
        track_genres.to_sql(name='track_genres', con=engine, schema='bronze', if_exists='append', index=False)

        logger.info("Raw data stored successfully in bronze schema")

        # Preprocessing and storing in silver and gold schemas
        logger.info("Preprocessing data for silver schemas")

        preprocesador = Preproceso()
        unified = preprocesador.preprocesar(spotify_youtube, track_emotions, track_genres)
        unified["timestamp"] = [now] * len(unified.index)
        unified.to_sql(name='unified', con=engine, schema='silver', if_exists='append', index=False)

        logger.info("Data preprocessed and stored successfully in silver schema")

        logger.info("Converting data to gold schema")

        gold = preprocesador.convertir_gold(unified)
        gold["timestamp"] = [now] * len(gold.index)
        gold.to_sql(name='gold', con=engine, schema='gold', if_exists='append', index=False)

        logger.info("Data converted and stored successfully in gold schema")

    except Exception as e:
        logger.critical(f"Critical error in ETL pipeline: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
