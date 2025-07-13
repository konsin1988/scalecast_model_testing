FROM python:3.11-slim

WORKDIR /streamlit

COPY ./docker/streamlit/requirements.txt /tmp/requirements.txt

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r /tmp/requirements.txt

EXPOSE 8502 

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "Introduction.py", "--server.port=8502", "--server.address=0.0.0.0"]

