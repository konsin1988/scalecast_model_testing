FROM nginx:latest

RUN apt-get update && apt-get install build-essential -y && apt-get install -y iputils-ping

EXPOSE 80


CMD ["nginx", "-g", "daemon off;"]
