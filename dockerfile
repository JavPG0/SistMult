FROM  python:3.9

WORKDIR /code

COPY requirements.txt /code/requirements.txt
COPY /Src/etl.py /code/etl.py

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["python","etl.py"]