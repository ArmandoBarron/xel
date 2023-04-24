FROM python:3.8.6-slim-buster

WORKDIR home

#requierments for the mesh:
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#for production (only for the AG)
RUN pip install waitress==1.0.1
RUN pip install dask
#requierments for storage:
RUN python -m pip install --upgrade pip
RUN apt-get update
RUN apt-get install libmagic1 -y
RUN pip install python-magic==0.4.27 && pip install nanoid
#RUN pip install -i https://test.pypi.org/simple/ mictlanx==0.0.29

RUN pip install --extra-index-url https://testpypi.python.org/pypi mictlanx==0.0.32


COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["coordinator_middleware.py"]
