import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from django.shortcuts import render

# Configuração do banco  ------------------- // ------------------- //
USER = "abiromania"
PASSWORD = "abiromania"
HOST = "localhost"
PORT = "5432"
DB = "observatorio"

engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")


def ocorrencias(request):
    # Querys SQL e DataFrames ------------------- // ------------------- //
    # NATUREZA
    q_total = """
    SELECT natureza, COUNT(*) AS total
    FROM ocorrencias
    GROUP BY natureza
    ORDER BY total DESC
    LIMIT 5;
    """
    df_total = pd.read_sql(q_total, engine)

    # BAIRRO
    q_bairro = """
    SELECT bairro, COUNT(*) AS total
    FROM ocorrencias
    WHERE bairro IS NOT NULL
    GROUP BY bairro
    ORDER BY total DESC
    LIMIT 5;
    """
    df_bairro = pd.read_sql(q_bairro, engine)

    # Horário
    q_hora = """
    SELECT hora, COUNT(*) AS total
    FROM ocorrencias
    WHERE hora IS NOT NULL
    GROUP BY hora
    ORDER BY hora ASC;
    """
    df_hora = pd.read_sql(q_hora, engine)

    # Gráficos ------------------- // ------------------- //
    fig_total = px.pie(df_total, names='natureza', values='total', title='Maiores Ocorrências em SP')
    fig_bairro = px.bar(df_bairro, x='bairro', y='total', title='Bairros com mais Ocorrências em SP')
    fig_hora = px.line(df_hora, x='hora', y='total', title='Horários com mais Ocorrências em SP')

    context = {
        'fig_total': fig_total.to_html(full_html=False),
        'fig_bairro': fig_bairro.to_html(full_html=False),
        'fig_hora': fig_hora.to_html(full_html=False),
    }

    return render(request, 'dashboard/grafico.html', context)