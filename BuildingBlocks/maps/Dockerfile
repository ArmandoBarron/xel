FROM python:3.8.6-slim-buster

WORKDIR home

#requierments for the mesh:
RUN apt-get update && apt-get install libmagic1 -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#requierments for the app:
RUN pip install folium --user 
RUN pip install branca --user 
RUN pip install imageio --user 
RUN pip install markupsafe==2.0.1 --user

RUN pip install geopandas --user
RUN pip install plotly==5.9.0 --user
RUN pip install geojson --user

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
