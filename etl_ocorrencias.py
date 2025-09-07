import pandas as pd
from sqlalchemy import create_engine


# Configurações do banco
USER = 'abiromania'
PASSWORD = 'abiromania'
HOST = 'localhost'
PORT = '5432'
DB = 'observatorio'


# Leitura do arquivo CSV
csv_file = 'ocorrencias.csv'
df = pd.read_csv(csv_file, sep=',', encoding='latin1')


engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")


# FIltra e renomeia colunas
df = df.filter([
    'DATA_OCORRENCIA_BO', 'HORA_OCORRENCIA_BO', 'BAIRRO',
    'LATITUDE', 'LONGITUDE','LOGRADOURO', 'NATUREZA_APURADA'
])

df = df.rename(columns={
    'DATA_OCORRENCIA_BO': 'data_ocorrencia',
    'HORA_OCORRENCIA_BO': 'hora',
    'NATUREZA_APURADA': 'natureza',
    'LOGRADOURO': 'logradouro',
    'BAIRRO': 'bairro',
    'LATITUDE': 'latitude',
    'LONGITUDE': 'longitude'
})


# Inserir banco no PostgreSQL
df.to_sql('ocorrencias', engine, if_exists='append', index=False)

print("Dados inseridos com sucesso!")