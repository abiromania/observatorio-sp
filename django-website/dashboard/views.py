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
    # Filtro natureza
    natureza_filtrada = ""
    if 'natureza' in request.GET:
        natureza_filtrada = request.GET.get('natureza', None)

    # Filtro datas
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)




    # MAPA DE CALOR ------------------- //
    q_mapa = f"""
        SELECT bairro, latitude, longitude, COUNT(*) AS total
        FROM ocorrencias
        WHERE latitude IS NOT NULL AND
        NOT latitude = '0' AND
        bairro IS NOT NULL
    """
    if natureza_filtrada != "":
        # Adiciona WHERE se houver um filtro
        q_mapa += f" AND natureza = '{natureza_filtrada}'"
        
    q_mapa += """
        GROUP BY bairro, latitude, longitude
        ORDER BY total DESC
        LIMIT 2000;
    """

    df_mapa = pd.read_sql(q_mapa, engine)

    # Arrumar formato das colunas de latitude e longitude
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
            size=30,
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




    # BAIRRO ------------------- //
    q_bairro = """
        SELECT bairro, COUNT(*) AS total
        FROM ocorrencias
    """

    if natureza_filtrada != "":
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




    # HORA ------------------- //
    q_hora = """
        SELECT hora, COUNT(*) AS total
        FROM ocorrencias
        WHERE hora IS NOT NULL
    """

    if natureza_filtrada != "":
        # Adiciona WHERE se houver um filtro
        q_hora += f" AND natureza = '{natureza_filtrada}'"

    q_hora += """
        GROUP BY hora
        ORDER BY hora ASC;
    """

    df_hora = pd.read_sql(q_hora, engine)

    fig_hora = px.line(
        df_hora,
        x='hora',
        y='total',
        title="Ocorrências por Horario",
    )

    fig_hora.update_yaxes(
        range=[0, df_hora['total'].max() * 1.1],
    )

    fig_hora.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='white',
        font_size=18,
        font_family='Calibri',
        title_x=0.5,
        title_font=dict(
            size=30,
            family='Calibri',
            color='white',),
        xaxis_title='Hora do Dia',
        yaxis_title='Total de Ocorrências',
        hoverlabel=(dict(
            font_size=18,
            font_family='Calibri',
            )
        ),
    )

    fig_hora.update_traces(
        mode='markers+lines',
        marker=dict(size=10, color="#00eeff"),
        line=dict(width=4, color='#00eeff'),
        hovertemplate="<b>Hora:</b> %{x}:00<br>"+
        "<b>Total de Ocorrências:</b> %{y}"
    )

    fig_hora.update_xaxes(
        dtick = 4,
        showgrid=False,
        range=[0, 23],
    )



    # DATA ------------------- //
    q_data = """
        SELECT data_ocorrencia, COUNT(*) AS total
        FROM ocorrencias
        WHERE data_ocorrencia IS NOT NULL AND
        NOT data_ocorrencia = '2025-07-01'
    """

    if natureza_filtrada != "":
        # Adiciona WHERE se houver um filtro
        q_data += f" AND natureza = '{natureza_filtrada}'"

    q_data += """
        GROUP BY data_ocorrencia
        ORDER BY data_ocorrencia ASC;
    """

    df_data = pd.read_sql(q_data, engine)

    fig_data = px.line(
        df_data,
        x='data_ocorrencia',
        y='total',
        title="Ocorrências por Dia",
    )

    fig_data.update_yaxes(
        range=[0, df_data['total'].max() * 1.1],
    )

    fig_data.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='white',
        font_size=18,
        font_family='Calibri',
        title_x=0.5,
        title_font=dict(
            size=30,
            family='Calibri',
            color='white',),
        xaxis_title='Dia',
        yaxis_title='Total de Ocorrências',
        hoverlabel=(dict(
            font_size=18,
            font_family='Calibri',)
        ),
    )

    fig_data.update_traces(
        mode='lines',
        line=dict(width=4, color='#00eeff'),
        hovertemplate="<b>Data:</b> %{x}<br>"+
        "<b>Total de Ocorrências:</b> %{y}"
    )

    fig_data.update_xaxes(showgrid=False)
    fig_data.update_yaxes(showgrid=False)




    # Resgatar valor total de ocorrências
    q_total = """
        SELECT natureza, COUNT(*) AS total
        FROM ocorrencias
        WHERE natureza IS NOT NULL
        GROUP BY natureza;
    """

    df_total = pd.read_sql(q_total, engine)

    total = int(df_total['total'].sum())
    total_furto = int(df_total[df_total['natureza'] == 'FURTO']['total'].sum()) if 'natureza' in df_total.columns else 0
    total_roubo = int(df_total[df_total['natureza'] == 'ROUBO']['total'].sum()) if 'natureza' in df_total.columns else 0
    total_lesao = int(df_total[df_total['natureza'] == 'LESAO CORPORAL DOLOSA']['total'].sum()) if 'natureza' in df_total.columns else 0
    total_veiculos = int(df_total[df_total['natureza'] == 'ROUBO DE VEICULO']['total'].sum()) if 'natureza' in df_total.columns else 0
    total_sinistros = int(df_total[df_total['natureza'] == 'LESAO CORPORAL CULPOSA POR ACIDENTE DE TRANSITO']['total'].sum()) if 'natureza' in df_total.columns else 0


    # Converte os gráficos e envia os gráficos para a pagina HTML
    context = {
        # Gráficos
        'fig_bairro': fig_bairro.to_html(full_html=False, config={"responsive": True}),
        'fig_hora': fig_hora.to_html(full_html=False, config={"responsive": True}),
        'fig_data': fig_data.to_html(full_html=False, config={"responsive": True}),
        'fig_mapa': fig_mapa.to_html(full_html=False, config={"responsive": True}),
    
        # Indicadores
        'total': total,
        'total_furto': total_furto,
        'total_roubo': total_roubo,
        'total_lesao': total_lesao,
        'total_veiculos': total_veiculos,
        'total_sinistros': total_sinistros,
    }

    return render(request, 'dashboard/grafico.html', context)