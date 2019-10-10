FROM postgres
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB postgres
ADD createDBSchema.sql /docker-entrypoint-initdb.d/
