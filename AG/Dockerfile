FROM python:3.8.6-slim-buster

WORKDIR home

#requierments for the mesh:
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#for production (only for the AG)
RUN pip install waitress 
RUN pip install dask
#requierments for the app:

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["coordinator_middleware.py"]
