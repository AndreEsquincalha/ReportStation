import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
from matplotlib.lines import Line2D

def plotar_grafico(parametro, df):
    """
    Gera um gráfico no Streamlit para o parâmetro selecionado.

    Parâmetros:
    - parametro (str): Nome do parâmetro a ser exibido no gráfico.
    - df (DataFrame): DataFrame contendo os dados processados.
    """
    import streamlit as st  # Importar dentro da função para evitar conflitos

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
    st.markdown(f"### 📊 Gráfico de {parametro}")

    fig, ax = plt.subplots(figsize=(15, 5))

    # Lista de cores para as condições
    colors = ['#FFFF99', '#C3DFF9', '#FCB7AF', '#FFDA9E', '#E4F8D6']
    conditions = list(conditions_map.keys())

    # Plotar as barras para indicar as condições
    bar_width = 0.05  # Ajuste da largura das barras
    for condition, color in zip(conditions, colors):
        ax.bar(df.index, df[condition], width=bar_width, color=color, label=condition)

    # Plotar a linha do parâmetro escolhido
    ax.plot(df.index, df[parametro], label=parametro, color='blue', linewidth=2.5)

    # Configurar o eixo X com datas formatadas
    ax.xaxis.set_major_locator(DayLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
    plt.xticks(rotation=40)

    # Ajuste dos limites do eixo Y
    ax.set_ylim(0, df[parametro].max() + 4 if not df[parametro].isnull().all() else 10)

    # Configuração da grade no eixo Y
    ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)

    # Criar legenda personalizada
    legend_elements = [Line2D([0], [0], marker='s', color='w', label=parametro, markerfacecolor='blue', markersize=20)]
    ax.legend(handles=legend_elements, loc='upper left', fontsize='large')

    # Ajuste do layout
    plt.tight_layout()
    st.pyplot(fig)
