FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential
RUN apt-get -y install python3
RUN apt-get update && apt-get install -y python3-pip && apt-get install -y python3-venv && pip3 install virtualenv
RUN pip3 install numpy && pip3 install pandas && pip3 install flask
RUN apt-get install nano
RUN apt-get update && apt-get -y install --no-install-recommends build-essential r-base r-cran-randomforest
RUN Rscript -e 'install.packages("remotes", repo = "https://cloud.r-project.org")'

RUN apt-get install libpng-dev -y
RUN Rscript -e 'install.packages("reticulate",version="1.19")' && Rscript -e 'reticulate::virtualenv_create()'

#RUN Rscript -e 'remotes::install_github("rstudio/reticulate@v1.19")' && Rscript -e 'reticulate::virtualenv_create()'
RUN Rscript -e "install.packages('devtools')" && Rscript -e "remotes::install_github('rstudio/keras')" && Rscript -e "keras::install_keras(version=2.4)"

RUN pip3 install requests --user

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --user 

COPY ["app","/home/app/"]
WORKDIR /home/app/

ENTRYPOINT ["python3"]
CMD ["S.py"]
