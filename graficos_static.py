import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import streamlit as st  # Importação mantida dentro da função para evitar conflitos
import pandas as pd

def plotar_grafico(parametro, df, col):
    """
    Gera um gráfico no Streamlit para o parâmetro selecionado, considerando os últimos 30 dias.

    Parâmetros:
    - parametro (str): Nome do parâmetro a ser exibido no gráfico.
    - df (DataFrame): DataFrame contendo os dados processados.
    """
    # Converter o índice para datetime se necessário
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Determinar a última data no DataFrame
    ultima_data = df.index.max()
    data_inicio = ultima_data - pd.Timedelta(days=30)
    
    # Filtrar os últimos 30 dias
    df = df.loc[data_inicio:ultima_data]
    
    # Criar coluna correspondente ao flag do parâmetro selecionado
    flag_column = parametro + "flag"

    # Definir a altura das linhas de flag
    flag_height = 999  # Ajuste conforme necessário

    # Criar colunas para diferentes condições de flag
    conditions_map = {
        "Força Maior": 16,
        "Calibração": 9,
        "Dados Inválidos": 4,
        "Dados Ausentes": 0,
        "Manutenção": 28
    }

    for condition, flag_value in conditions_map.items():
        df[condition] = df[flag_column].apply(lambda x: flag_height if x == flag_value else 0)

    # Filtrar apenas os dados onde o flag indica válido
    df[parametro] = df.apply(lambda x: x[parametro] if x[flag_column] == 1 else None, axis=1)

    # Configuração do gráfico no Streamlit
    with col: st.markdown(f"<p style='font-size:14px; font-weight:bold; color:black; text-align:center; margin-bottom:20px;;'>Gráfico de {parametro}</p>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.canvas.mpl_connect('motion_notify_event', lambda event: ax.annotate(f'{event.xdata:.2f}, {event.ydata:.2f}', xy=(event.xdata, event.ydata), xytext=(10,10), textcoords='offset points', fontsize=10, color='black', bbox=dict(boxstyle='round,pad=0.3', edgecolor='gray', facecolor='white')) if event.xdata and event.ydata else None)


    # Lista de cores para as condições
    colors = ['#FFFF99', '#C3DFF9', '#FCB7AF', '#FFDA9E', '#E4F8D6']
    conditions = list(conditions_map.keys())

    # Plotar as barras para indicar as condições
    bar_width = 0.05  # Ajuste da largura das barras
    for condition, color in zip(conditions, colors):
        ax.bar(df.index, df[condition], width=bar_width, color=color, label=condition)

    # Plotar a linha do parâmetro escolhido
    ax.plot(df.index, df[parametro], label=parametro, color='blue', linewidth=2.5)

    # Melhorando a formatação do eixo X
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Define espaçamento de 5 dias entre as datas  # Define espaçamento automático das datas
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))  # Formata as datas no eixo X
    plt.xticks(rotation=45, ha="right")  # Rotaciona e alinha os rótulos do eixo X
    ax.tick_params(axis='x', labelsize=12)

    # Ajuste dos limites do eixo Y
    ax.set_ylim(0, df[parametro].max() + 4 if not df[parametro].isnull().all() else 10)
    ax.set_ylabel(f"{parametro} (ppb)", fontsize=14)  # Adiciona o nome do parâmetro no eixo Y

    # Configuração da grade no eixo Y
    ax.tick_params(axis='y', labelsize=14)
    ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)

    # Criar legenda personalizada e corrigir o problema da sobreposição
    legend_elements = [
        Line2D([0], [0], color=color, lw=4, label=condition) for condition, color in zip(conditions, colors)
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize='large', frameon=True)

    # Ajuste do layout para evitar cortes no gráfico
    plt.tight_layout()
    col1, col2 = st.columns(2) if 'col1' not in locals() else (col1, col2)
    with col:
        st.pyplot(fig)
