FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential
RUN apt-get -y install python3
RUN apt-get update -y && apt-get install -y graphviz
RUN apt-get update && apt-get install -y python3-pip && apt-get install -y python3-venv && pip3 install virtualenv
RUN pip3 install --upgrade pip
RUN pip3 install numpy && pip3 install pandas && pip3 install flask && pip3 install nltk && pip3 install scikit-learn && pip3 install mpld3 && pip3 install joblib && pip3 install gensim && pip3 install keras && pip3 install tensorflow && pip3 install pydot && pip3 install pydotplus
RUN apt-get install nano

RUN pip3 install requests --user


COPY ["app","/home/app/"]
WORKDIR /home/app/

ENTRYPOINT ["python3"]
CMD ["S.py"]
