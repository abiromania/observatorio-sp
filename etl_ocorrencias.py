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

# Remove pontuação do nome dos bairros
df['bairro'] = df['bairro'].str.upper()
df['bairro'] = df['bairro'].map(lambda x: str(x).replace('Ã', 'A')).map(lambda x: str(x).replace('Á', 'A'))
df['bairro'] = df['bairro'].map(lambda x: str(x).replace('É', 'E')).map(lambda x: str(x).replace('Ê', 'E'))
df['bairro'] = df['bairro'].map(lambda x: str(x).replace('Í', 'I')).map(lambda x: str(x).replace('Ç', 'C'))
df['bairro'] = df['bairro'].map(lambda x: str(x).replace('Ó', 'O')).map(lambda x: str(x).replace('Õ', 'O'))
df['bairro'] = df['bairro'].map(lambda x: str(x).replace('Ú', 'U'))

# Arrenda o horário das ocorrências
df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S', errors='coerce')
df['hora'] = df['hora'].dt.round('H').dt.hour

# Inserir banco no PostgreSQL
df.to_sql('ocorrencias', engine, if_exists='replace', index=False)

print("Dados inseridos com sucesso!")