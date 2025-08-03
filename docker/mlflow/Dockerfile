FROM python:3.11-slim

WORKDIR /mlflow

COPY ./docker/mlflow/requirements.txt /tmp/requirements.txt

EXPOSE 5000

RUN apt-get update && apt-get install -y \
build-essential \
libpq-dev \
curl \
&& rm -rf /var/lib/apt/lists/* 

RUN pip install -r /tmp/requirements.txt

