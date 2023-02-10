FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential
RUN apt-get -y install python3
RUN apt-get update && apt-get install -y python3-pip && apt-get install -y python3-venv && pip3 install virtualenv
RUN pip3 install numpy==1.21.4 && pip3 install pandas && pip3 install flask && pip3 install nltk && pip3 install scikit-learn==0.22 && pip3 install mpld3 && pip3 install joblib && pip3 install gensim
RUN apt-get install nano

RUN pip3 install requests --user
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader punkt

COPY ["app","/home/app/"]
WORKDIR /home/app/

ENTRYPOINT ["python3"]
CMD ["S.py"]
