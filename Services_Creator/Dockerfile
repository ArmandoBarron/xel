FROM ubuntu:18.04
RUN apt-get update && \
    apt-get -qy full-upgrade && \
    apt-get install -qy curl
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose
RUN apt-get update && apt-get install -y build-essential
RUN apt-get -y install python3
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install psutil && pip3 install Flask && pip3 install Flask-Cors
WORKDIR /home/app/
