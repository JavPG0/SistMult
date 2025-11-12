# SistMult
# Chatbot Inteligente de Hipótesis Musicales

Este proyecto consiste en desarrollar un **chatbot con inteligencia artificial** al que el usuario podrá plantear **hipótesis sobre música, artistas o canciones**, como por ejemplo:

> *"La canción más escuchada de Coldplay tiene más del doble de escuchas que la canción más escuchada de Melendi."*

El chatbot será capaz de **confirmar o negar** dichas hipótesis mediante un **razonamiento basado en datos** almacenados en una base de datos **PostgreSQL**, estructurada en **tres capas (bronce, plata y oro)**.

El sistema ofrecerá **respuestas argumentadas** basándose en esta base de datos, la cual será alimentada por **fuentes de datos preprocesadas** (CSV, APIs, etc.).  
El módulo de IA estará **basado en un modelo de lenguaje de Hugging Face**.

---

## Arquitectura del Proyecto

El sistema está compuesto por los siguientes componentes:

1. **Fuentes de datos**  
   - Conjuntos de datos en formato CSV, APIs u otras fuentes abiertas de información musical.

2. **Base de datos PostgreSQL (en Docker)**  
   - Almacena los registros musicales y el historial de prompts del chatbot.  
   - Estructurada en capas **Bronce**, **Plata** y **Oro** para garantizar calidad y trazabilidad de los datos.

3. **API de Servicio (FastAPI)**  
   - Expone **endpoints REST** para la consulta y orquestación de inferencias.  
   - Se encarga de recibir las hipótesis del usuario y preparar el contexto para la IA.

4. **Módulo de Inteligencia Artificial (Hugging Face LLM)**  
   - Realiza el **razonamiento sobre las hipótesis** usando la evidencia proporcionada por la base de datos.  
   - Genera respuestas explicativas y fundamentadas.

5. **Interfaz Gráfica (Python)**  
   - Permite al usuario **formular hipótesis** y **visualizar respuestas argumentadas** de forma interactiva.

---

## Flujo de Trabajo

El flujo de trabajo garantiza que **todas las consultas a los datos estén mediadas por FastAPI**, que:
1. Prepara el contexto con los datos relevantes desde PostgreSQL.  
2. Invoca al modelo de lenguaje (LLM) para generar una inferencia.  
3. Persiste la interacción en la base de datos para **trazabilidad y análisis posterior**.

---

## Tecnologías Principales

- **PostgreSQL** – Base de datos principal (Docker)
- **FastAPI** – Backend y orquestación
- **Hugging Face Transformers** – Modelo de lenguaje
- **Python** – Lenguaje principal
- **Pandas / SQLAlchemy** – Procesamiento y acceso a datos
- **Tkinter / Streamlit (según versión)** – Interfaz de usuario

---

## Objetivo

Crear un **asistente inteligente y razonador** que no solo devuelva respuestas directas, sino que **explique sus conclusiones con base en evidencia verificable**, combinando procesamiento de lenguaje natural, ingeniería de datos y arquitectura de software moderna.
