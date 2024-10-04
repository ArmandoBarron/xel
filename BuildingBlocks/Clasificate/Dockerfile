FROM python:3.8.6-slim-buster
#FROM python:3.8.6

WORKDIR home

#requierments for the mesh:
RUN apt-get update && apt-get install libmagic1 -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#requierments for the app:
RUN pip install scipy==1.8.0
RUN pip install scikit-learn==1.0.1
RUN pip install matplotlib==3.5.2
RUN pip install argparse==1.4.0

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
