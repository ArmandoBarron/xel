FROM python:3.8.8-slim-buster

WORKDIR home

#requierments for the mesh:
RUN apt-get update && apt-get install libmagic1 -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#requierments for the app:
RUN pip install seaborn==0.11.2 --user
RUN pip install matplotlib==3.5.2 --user

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
