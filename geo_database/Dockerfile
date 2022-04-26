FROM postgres

ADD ./src/main.sql /docker-entrypoint-initdb.d/main.sql

VOLUME psql-geodatabase:/var/lib/postgresql/data 
