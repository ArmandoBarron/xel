FROM python
WORKDIR home

RUN mkdir static

RUN pip install flask --user 
RUN pip install sklearn --user 
RUN pip install matplotlib --user
RUN pip install pandas --user
RUN pip install numpy --user

COPY ./init.py init.py
COPY ./Functions.py Functions.py

ENTRYPOINT ["python"]
CMD ["init.py"]
