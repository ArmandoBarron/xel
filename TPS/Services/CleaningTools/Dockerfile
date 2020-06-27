FROM python
WORKDIR home

RUN pip install flask --user 
RUN pip install pandas --user
RUN pip install numpy --user

COPY ./init.py init.py

ENTRYPOINT ["python"]
CMD ["init.py"]
