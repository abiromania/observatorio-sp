import pandas as pd
import plotly.express as px
import json
from sqlalchemy import create_engine
from django.shortcuts import render

# Configuração do BD  ------------------- // ------------------- //
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
    df_bairro = df_bairro.sort_values(by='total', ascending=False)

    fig_bairro = px.pie(
        df_bairro,
        names='bairro',
        values='total', 
        title='(10) Maiores Ocorrências por Bairro',
        height=550,
    )
    fig_bairro.update_layout(
        colorway=px.colors.qualitative.Light24,
        paper_bgcolor='#222222',
        font_color='white',
        font_size=18,
        font_family='Calibri',
        title_x=0.5,
        title_font=dict(
            size=30,
            family='Calibri',
            color='white',),
        hoverlabel=(dict(
            font_size=18,
            font_family='Calibri',)
        ),
    )
    fig_bairro.update_traces(
        hovertemplate="<b>Bairro:</b> %{label}<br>"+
        "<b>Total de Ocorrências:</b> %{value}"
)


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

    fig_hora = px.line(
        df_hora,
        x='hora',
        y='total',
        title=False,
    )

    fig_hora.update_yaxes(
        range=[0, 12000]
    )


    # MAPA DE CALOR ------------------- //
    q_mapa = f"""
        SELECT bairro, latitude, longitude, COUNT(*) AS total
        FROM ocorrencias
        WHERE latitude IS NOT NULL AND
        longitude IS NOT NULL AND
        bairro IS NOT NULL
    """
    if natureza_filtrada != "Sem Filtro":
        # Adiciona WHERE se houver um filtro
        q_mapa += f" AND natureza = '{natureza_filtrada}'"

    q_mapa += """
        GROUP BY bairro, latitude, longitude
        ORDER BY total DESC
        LIMIT 2000;
    """

    df_mapa = pd.read_sql(q_mapa, engine)

    # converter vírgula → ponto e virar número
    for col in ["latitude", "longitude"]:
        df_mapa[col] = pd.to_numeric(
            df_mapa[col].astype(str).str.strip().str.replace(",", ".", regex=False),
            errors="coerce"
        )

    fig_mapa = px.density_map(
        df_mapa, 
        lat='latitude',
        lon='longitude',
        radius=10,
        zoom=8,
        center=dict(
            lat=-23.55052,
            lon=-46.633308),
        height=550,
        map_style='open-street-map',
        title="Mapa de Calor",
        custom_data=['bairro'],
        color_continuous_scale='Plasma_r',
    )

    # Abre o arquivo com o contorno do município
    with open('./dashboard/boundaries.json', 'r', encoding = 'utf-8') as f:
        contorno = json.load(f)

    fig_mapa.update_layout(
        margin={"r":20,"t":100,"l":20,"b":70},
        paper_bgcolor='#222222',
        showlegend=False,
        coloraxis_showscale=False,
        hoverlabel=dict(
            font_size=18,
            font_family='Calibri',
            font_color='white',
            bgcolor='#222222',),
        title_font=dict(
            size=35,
            family='Calibri',
            color='white',),
        title_x=0.5,
        map_layers = [
            {
                "source": contorno,
                "type": "line",
                "color": "red",
                "line": {"width":2},
                "below": "traces"
            }
        ]
    )
    fig_mapa.update_traces(
        hovertemplate="<b>Bairro:</b> %{customdata[0]}",
        opacity=0.6,
    )


    # Converte os gráficos e envia os gráficos para a pagina HTML
    context = {
        'fig_bairro': fig_bairro.to_html(full_html=False, config={"responsive": True}),
        'fig_hora': fig_hora.to_html(full_html=False, config={"responsive": True}),
        'fig_mapa': fig_mapa.to_html(full_html=False, config={"responsive": True}),
    }

    return render(request, 'dashboard/grafico.html', context)