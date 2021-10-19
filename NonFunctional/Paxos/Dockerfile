FROM python
WORKDIR home

RUN pip install flask --user 
RUN pip install requests --user
RUN pip install pymongo==3.12.0 --user

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["Acepter.py"]
