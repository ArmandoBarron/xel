FROM python
WORKDIR home

RUN pip install flask --user 
RUN pip install pandas --user
RUN pip install requests --user
RUN pip install xlwt --user

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
