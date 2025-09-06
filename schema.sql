CREATE DATABASE observatorio;

CREATE TABLE ocorrencias (
    id SERIAL PRIMARY KEY,
    data_ocorrencia DATE,
    hora TIME,
    natureza VARCHAR(255),
    logradouro VARCHAR(255),
    bairro VARCHAR(255),
    latitude VARCHAR(50),
    longitude VARCHAR(50)
);

CREATE USER abiromania WITH PASSWORD 'abiromnia';
GRANT ALL PRIVILEGES ON DATABASE observatorio TO abiromania;