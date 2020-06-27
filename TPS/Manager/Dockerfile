FROM python
WORKDIR home
RUN mkdir CONFIG
RUN mkdir SCHEMA

RUN pip install flask --user 
RUN pip install psycopg2 --user 
RUN pip install configparser --user
RUN pip install requests --user
RUN pip install pandas --user
RUN pip install Flask-API --user
RUN pip install pymongo --user
RUN pip install flask-socketio
RUN pip install xlrd

COPY ./Tools Tools
COPY ./TPS-Manager.py TPS-Manager.py

ENTRYPOINT ["python"]
CMD ["TPS-Manager.py"]
