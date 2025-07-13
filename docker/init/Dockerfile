FROM python:3.11-slim

WORKDIR /init

COPY ./docker/init/requirements.txt /tmp/requirements.txt
COPY ./init/init.py /init/


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* 

RUN pip3 install -r /tmp/requirements.txt

CMD ["python3", "/init/init.py"]