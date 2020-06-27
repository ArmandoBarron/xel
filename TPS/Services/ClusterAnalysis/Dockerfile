FROM r-base
WORKDIR /usr/local/src/stats
RUN apt-get update
RUN apt-get -y install pandoc
RUN R -e "install.packages('clusterCrit', repos = 'http://cran.us.r-project.org')"
RUN R -e "install.packages('dbscan', repos = 'http://cran.us.r-project.org')"
RUN R -e "install.packages('plumber')"
RUN R -e "install.packages('dplyr')"

COPY ./stats /usr/local/src/stats

ENTRYPOINT ["Rscript"]
CMD ["init.R"]
