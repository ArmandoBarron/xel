FROM ubuntu:16.04

#install requeriments
RUN apt-get update --fix-missing
RUN     apt install -y software-properties-common
RUN     apt-get update --fix-missing
RUN apt-get install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.6
RUN apt-get install -y python3-pip

RUN pip3 install --upgrade pip

ADD ./app /app
WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 7070

ENTRYPOINT [ "python3", "/app/app.py" ]
