import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from django.shortcuts import render

# Configuração do banco  ------------------- // ------------------- //
USER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = "5432"
DB = "observatorio"

engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")


def ocorrencias(request):
    # Querys SQL e DataFrames ------------------- // ------------------- //
    natureza_filtrada = "Sem Filtro"
    if 'natureza' in request.GET:
        natureza_filtrada = request.GET.get('natureza', None)



    # BAIRRO ------------------- //
    q_bairro = """
        SELECT bairro, COUNT(*) AS total
        FROM ocorrencias
    """

    if natureza_filtrada != "Sem Filtro":
        # Adiciona WHERE se houver um filtro
        q_bairro += f" WHERE natureza = '{natureza_filtrada}'"

    q_bairro += """
        GROUP BY bairro
        ORDER BY total DESC
        LIMIT 10;
    """
    df_bairro = pd.read_sql(q_bairro, engine)



    # HORARIO ------------------- //
    q_hora = """
        SELECT hora, COUNT(*) AS total
        FROM ocorrencias
    """

    if natureza_filtrada != "Sem Filtro":
        # Adiciona WHERE se houver um filtro
        q_hora += f" WHERE natureza = '{natureza_filtrada}'"

    q_hora += """
        GROUP BY hora
        ORDER BY hora ASC;
    """

    df_hora = pd.read_sql(q_hora, engine)



    # MAPA DE CALOR ------------------- //
    q_mapa = f"""
        SELECT latitude, longitude, COUNT(*) AS total
        FROM ocorrencias
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """
    if natureza_filtrada != "Sem Filtro":
        # Adiciona WHERE se houver um filtro
        q_mapa += f" AND natureza = '{natureza_filtrada}'"

    q_mapa += """
        GROUP BY latitude, longitude;
    """



    df_mapa = pd.read_sql(q_mapa, engine)

    # converter vírgula → ponto e virar número
    for col in ["latitude", "longitude"]:
        df_mapa[col] = pd.to_numeric(
            df_mapa[col].astype(str).str.strip().str.replace(",", ".", regex=False),
            errors="coerce"
        )

    # Gráficos ------------------- // ------------------- //
    fig_bairro = px.bar(df_bairro, x='bairro', y='total', 
                        title=False)
    
    fig_hora = px.line(df_hora, x='hora', y='total',
                       title=False)
    fig_hora.update_yaxes(range=[0, 12000])

    fig_mapa = px.density_map(df_mapa, lat='latitude', lon='longitude',
                              radius=10, zoom=8, map_style='open-street-map',
                              title=False)

    context = {
        'fig_bairro': fig_bairro.to_html(full_html=False),
        'fig_hora': fig_hora.to_html(full_html=False),
        'fig_mapa': fig_mapa.to_html(full_html=False),

    }

    return render(request, 'dashboard/grafico.html', context)