FROM postgres:12

ADD ./schema-sql/auth.sql /docker-entrypoint-initdb.d/auth.sql

VOLUME psql-auth:/var/lib/postgresql/data
