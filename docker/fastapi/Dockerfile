FROM python:3.11-slim

WORKDIR /fastapi

COPY ./docker/fastapi/requirements.txt /tmp/requirements.txt


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* 

RUN pip3 install -r /tmp/requirements.txt

CMD ["fastapi", "run", "app.py", "--reload", "--port", "8000"]
