FROM python:3.8.6-slim-buster

WORKDIR home

#requierments for the mesh:
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#requierments for the app:
RUN pip install statsmodels --user
RUN pip install plotly --user
RUN pip install kaleido --user
RUN pip install scipy --user
RUN pip install scikit-learn==1.0.1


COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
