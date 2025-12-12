FROM  python:3.9

WORKDIR /code

COPY requirements.txt /code/requirements.txt
COPY /Src/backend/etl.py /code/etl.py
COPY /Src/backend/preproceso.py /code/preproceso.py
COPY /Dataset/Spotify_Youtube.csv /code/Dataset/Spotify_Youtube.csv
COPY /Dataset/Track_Emotions.csv /code/Dataset/Track_Emotions.csv
COPY /Dataset/Track_Genres.csv /code/Dataset/Track_Genres.csv
COPY .env /code/.env

COPY /Src/logger_config.py /code/Src/logger_config.py
COPY /Src/logger_decorators.py /code/Src/logger_decorators.py

# Streamlit.
COPY /Src/frontend/app.py /code/Src/frontend/app.py
COPY /Src/frontend/api_client.py /code/Src/frontend/api_client.py

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Configurar Streamlit
RUN mkdir -p /root/.streamlit
RUN echo "[server]\nenableCORS = false\nport = 8501\naddress = \"0.0.0.0\"\n" > /root/.streamlit/config.toml

RUN mkdir -p /code/logs

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8501

CMD ["python3","./etl.py"]