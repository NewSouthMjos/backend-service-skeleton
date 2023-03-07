FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y gcc

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./migrations ./migrations
COPY __init__.py .
COPY migrate.py .
COPY config.py .
COPY database.py .

COPY app.py .
COPY __main__.py .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
COPY ./models ./models
COPY ./api ./api
ENTRYPOINT ["./entrypoint.sh"]
