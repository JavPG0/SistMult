FROM  python:3.9

WORKDIR /code

COPY requirements.txt /code/requirements.txt
COPY /Src/etl.py /code/etl.py
COPY /Src/preproceso.py /code/preproceso.py
COPY /Dataset/Spotify_Youtube.csv /code/Dataset/Spotify_Youtube.csv
COPY /Dataset/Track_Emotions.csv /code/Dataset/Track_Emotions.csv
COPY /Dataset/Track_Genres.csv /code/Dataset/Track_Genres.csv
COPY .env /code/.env

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["python3","./etl.py"]