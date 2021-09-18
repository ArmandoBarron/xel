FROM python:3.8.6-slim-buster

WORKDIR home
#requierments for the app:

COPY ./app/requirements.txt  requirements.txt
RUN pip install -r requirements.txt --user 

COPY ./app app
WORKDIR /home/app

#EXPOSE 7070

ENTRYPOINT [ "python3", "app.py" ]
