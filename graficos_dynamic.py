import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta

def plotar_grafico_dynamic(parametro, df, col, font_color='black'):
    """
    Gera um gráfico interativo no Streamlit para o parâmetro selecionado, considerando os últimos 30 dias.

    Parâmetros:
    - parametro (str): Nome do parâmetro a ser exibido no gráfico.
    - df (DataFrame): DataFrame contendo os dados processados.
    - col (Streamlit Column): Coluna onde o gráfico será renderizado.
    - font_size (int): Tamanho da fonte das legendas e eixos.
    - font_color (str): Cor da fonte das legendas e eixos.
    """
    # Converter o índice para datetime se necessário
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Determinar a última data no DataFrame
    ultima_data = df.index.max()
    data_inicio = ultima_data - timedelta(days=30)
    
    # Filtrar os últimos 30 dias
    df = df.loc[data_inicio:ultima_data]
    
    # Criar coluna correspondente ao flag do parâmetro selecionado
    flag_column = parametro + "flag"
    
    # Filtrar apenas os dados onde o flag indica válido
    df[parametro] = df.apply(lambda x: x[parametro] if x[flag_column] == 1 else None, axis=1)
    
    # Configuração do gráfico no Streamlit
    with col:
        st.markdown(f"<p style='font-size:14px; font-weight:bold; color:{font_color}; text-align:center; margin-bottom:-30px;'>Gráfico de {parametro}</p>", unsafe_allow_html=True)
    
    # Criar a figura do Plotly
    fig = go.Figure()
    
    # Adicionar a linha do parâmetro escolhido
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[parametro],
        mode='lines',
        name=parametro,
        line=dict(color='blue', width=2),
        marker=dict(size=6),
        hoverinfo='text+y',
        text=df.index.strftime('%d/%m/%y %H:%M')
    ))
    
    # Melhorando a formatação do eixo X e Y
    fig.update_xaxes(
        tickformat='%d/%m/%y',
        tickangle=-45,
        #title_text='Data e Hora',
        title_font=dict(size=14, color=font_color),
        tickfont=dict(size=14, color=font_color),
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        dtick=86400000.0
    )
    
    fig.update_yaxes(
        title_text=f'{parametro} (ppb)', 
        range=[0, df[parametro].max() + 4 if not df[parametro].isnull().all() else 10],
        title_font=dict(size=14, color=font_color),
        tickfont=dict(size=14, color=font_color),
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True
    )
    
    # Configuração do layout
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    
    # Exibir o gráfico no Streamlit
    with col:
        st.plotly_chart(fig, use_container_width=True)
