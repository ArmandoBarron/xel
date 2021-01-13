FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential
RUN apt-get -y install python3
RUN apt-get update && apt-get install -y python3-pip && apt-get install -y python3-venv && pip3 install virtualenv
RUN pip3 install numpy && pip3 install pandas && pip3 install flask
RUN apt-get install nano
RUN apt-get update && apt-get -y install --no-install-recommends build-essential r-base r-cran-randomforest
RUN Rscript -e 'install.packages("remotes", repo = "https://cloud.r-project.org")' && Rscript -e 'remotes::install_github("rstudio/reticulate")' && Rscript -e 'reticulate::virtualenv_create()'
RUN Rscript -e "install.packages('devtools')" && Rscript -e "remotes::install_github('rstudio/keras')" && Rscript -e "keras::install_keras()"

RUN pip3 install requests --user


COPY ["app","/home/app/"]
WORKDIR /home/app/

ENTRYPOINT ["python3"]
CMD ["S.py"]
