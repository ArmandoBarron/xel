FROM python
WORKDIR home

RUN pip install flask --user 
RUN pip install pandas --user
RUN pip install requests --user

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
