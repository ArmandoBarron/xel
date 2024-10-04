FROM python:3.8.6
WORKDIR home

#requierments for the mesh:
RUN apt-get update && apt-get install libmagic1 -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#requierments for the app:

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
