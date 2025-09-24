CREATE DATABASE observatorio;

CREATE TABLE ocorrencias (
    id SERIAL PRIMARY KEY,
    data_ocorrencia DOUBLE PRECISION,
    hora INTEGER,
    natureza VARCHAR(255),
    bairro VARCHAR(255),
    latitude VARCHAR(50),
    longitude VARCHAR(50)
);
