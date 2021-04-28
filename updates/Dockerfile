FROM python:3.8.6-slim-buster
#FROM python:3.8.6

WORKDIR home

#requierments for the mesh:
RUN pip install -r requirements.txt --user 
#requierments for the app:

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
