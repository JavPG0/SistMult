FROM python:3.9

WORKDIR /code

# Copiar requirements
COPY requirements.txt /code/requirements.txt

# Backend - ETL y preproceso
COPY /Src/backend/etl.py /code/etl.py
COPY /Src/backend/preproceso.py /code/preproceso.py

# Datasets
COPY /Dataset/Spotify_Youtube.csv /code/Dataset/Spotify_Youtube.csv
COPY /Dataset/Track_Emotions.csv /code/Dataset/Track_Emotions.csv
COPY /Dataset/Track_Genres.csv /code/Dataset/Track_Genres.csv

# Environment
COPY .env /code/.env

# Logger
COPY /Src/logger_config.py /code/Src/logger_config.py
COPY /Src/logger_decorators.py /code/Src/logger_decorators.py

# Frontend - Streamlit
COPY /Src/frontend/app.py /code/Src/frontend/app.py
COPY /Src/frontend/api_client.py /code/Src/frontend/api_client.py
COPY /Src/frontend/chatbot_nodes.py /code/Src/frontend/chatbot_nodes.py
COPY /Src/frontend/chatbot_graph.py /code/Src/frontend/chatbot_graph.py
COPY /Src/frontend/chatbot_state.py /code/Src/frontend/chatbot_state.py

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Configurar Streamlit
RUN mkdir -p /root/.streamlit
RUN echo "[server]\nenableCORS = false\nport = 8501\naddress = \"0.0.0.0\"\n" > /root/.streamlit/config.toml

# Crear directorio de logs
RUN mkdir -p /code/logs

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8501

# El comando por defecto se sobrescribe en docker-compose
CMD ["streamlit", "run", "Src/frontend/app.py"]
