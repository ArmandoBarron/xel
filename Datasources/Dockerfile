FROM python
WORKDIR home
RUN mkdir static

RUN pip install flask --user 
RUN pip install psycopg2 --user 
RUN pip install datetime --user
RUN pip install configparser --user
RUN pip install requests --user
RUN pip install numpy --user
RUN pip install pandas --user

COPY ./Service.py Service.py
COPY ./HandlerDB.py HandlerDB.py
COPY ./bins.py bins.py
COPY ./config.ini config.ini

ENTRYPOINT ["python"]
CMD ["Service.py"]
