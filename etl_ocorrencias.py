import pandas as pd
from sqlalchemy import create_engine


# Configurações do banco
USER = 'postgres'
PASSWORD = 'postgres'
HOST = 'localhost'
PORT = '5432'
DB = 'observatorio'


# Ler arquivo CSV
csv_file = 'ocorrencias.csv'
df = pd.read_csv(csv_file, sep=',', encoding='latin1')


engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")


# Filtrar e renomear colunas
df = df.filter([
    'DATA_OCORRENCIA_BO', 'HORA_OCORRENCIA_BO', 'BAIRRO',
    'LATITUDE', 'LONGITUDE', 'NATUREZA_APURADA'
])

df = df.rename(columns={
    'DATA_OCORRENCIA_BO': 'data_ocorrencia',
    'HORA_OCORRENCIA_BO': 'hora',
    'NATUREZA_APURADA': 'natureza',
    'BAIRRO': 'bairro',
    'LATITUDE': 'latitude',
    'LONGITUDE': 'longitude'
})

# Converter o campo hora para o formato TIME do SQL
df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M:%S')


# Converter o campo data para o formato DATE do SQL
df['data_ocorrencia'] = pd.to_datetime(df['data_ocorrencia'], format='%d/%m/%Y', errors='coerce').dt.date

# Filtrar ocorrências de 2025
df = df[df['data_ocorrencia'] >= pd.to_datetime('2025-01-01').date()]

# Inserir banco no PostgreSQL
df.to_sql('ocorrencias', engine, if_exists='replace', index=False)

print("Dados inseridos com sucesso!")