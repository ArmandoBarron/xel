FROM python:3.10.14-bullseye

WORKDIR home

#requierments for the mesh:
RUN apt-get update && apt-get install libmagic1 -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --user 
#requierments for the app:
RUN pip install statsmodels --user
RUN pip install plotly --user
RUN pip install kaleido --user
#RUN pip install scipy --user
RUN pip install scikit-learn==1.5.0
#RUN pip install pyjanitor==0.23.1
COPY requirements-activex.txt requirements-activex.txt
RUN pip install -r requirements-activex.txt --user 


#RUN apt-get update
#RUN apt-get install -y ffmpeg
#RUN pip install pivottablejs
#RUN pip install ipython

COPY ./app app
WORKDIR /home/app

ENTRYPOINT ["python"]
CMD ["S.py"]
