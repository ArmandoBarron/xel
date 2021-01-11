FROM python
WORKDIR home

RUN pip install flask --user 
RUN pip install requests --user

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["Acepter.py"]
