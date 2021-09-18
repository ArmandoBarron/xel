FROM r-base:4.0.1

RUN apt-get update
RUN apt-get -y install pandoc -o APT::Immediate-Configure=0
RUN apt-get -y install libsodium-dev
RUN apt-get install -y git-core \   
    libssl-dev \   
    libcurl4-gnutls-dev

RUN R -e "install.packages('plumber')"
RUN R -e "install.packages('jsonlite')"
RUN R -e "install.packages('rmarkdown')"
RUN R -e "install.packages('dplyr')"

COPY ./stats /usr/local/src/stats
WORKDIR /usr/local/src/stats

ENTRYPOINT ["Rscript"]
CMD ["init.R"]
