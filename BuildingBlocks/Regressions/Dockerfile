FROM python:3.8.6-slim-buster

WORKDIR home

#requierments for the mesh:
RUN apt-get update && apt-get install libmagic1 -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#requierments for the app:
COPY app_requirements.txt app_requirements.txt
RUN pip install -r app_requirements.txt --user 

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
