FROM ddomizzi/deployer:api

WORKDIR /home/app/

ADD ./app/requirements.txt .

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pil python3-pil.imagetk python3-matplotlib
RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install plotly==5.3.1
RUN pip3 install -U kaleido
RUN pip3 install Flask-Cors
RUN pip3 install psutil
RUN pip3 install waitress==1.0.1

ADD ./app .
