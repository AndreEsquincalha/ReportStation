import pandas as pd
import numpy as np
import streamlit as st
import altair as at
from graficos_static import plotar_grafico
from graficos_dynamic import plotar_grafico_dynamic  # Importando a função do arquivo graficos.py

# Ajustando a largura da página para exibir mais informações
st.set_page_config(layout="wide")

# 📂 Carregar dados do Excel
file_path = "./datasets/COCA-DADOS.xlsx"
df = pd.read_excel(file_path, engine="openpyxl", sheet_name="COCA")

# 🎯 Selecionar apenas as colunas necessárias
df = df[["Date_Time", "NO", "Status_NO", "NO2", "Status_NO2", "NOX", "Status_NOX",
         "O3", "Status_O3", "CO", "Status_CO", "SO2", "Status_SO2", "PM10", "Status_PM10"]]

# 🏷️ Renomear colunas
df.columns = ["date", "NO", "NOflag", "NO2", "NO2flag", "NOX", "NOXflag", "O3", "O3flag",
              "CO", "COflag", "SO2", "SO2flag", "PM10", "PM10flag"]

df["date"] = pd.to_datetime(df["date"])  # Converte a coluna para datetime
#df.set_index("date", inplace=True)  # Define a coluna como índice
df.sort_values("date", inplace=True)
df.set_index("date", inplace=True)

ultima_data = df.index.max()


# 🖥️ Criando colunas para organizar layout (Cabeçalho à esquerda, filtro de dias à direita)
col1, col2 = st.columns([3, 1])

# 🎚️ Filtro de dias na coluna da direita
with col2:
    st.markdown("""
        <div style="text-align: right; font-size: 16px; margin-bottom: 5px;">
            ⏳ <b>Filtro de dias:</b>
        </div>
    """, unsafe_allow_html=True)

    # Aplicando CSS para reduzir a largura e alinhar corretamente
    st.markdown("""
        <style>
            div[data-baseweb="input"] {
                width: 90px !important;  /* Ajuste o tamanho conforme necessário */
                margin-left: auto !important; /* Mantém alinhado à direita */
                display: block !important;
            }
        </style>
    """, unsafe_allow_html=True)

    days_input = st.number_input("", min_value=1, max_value=365, value=2, step=1, label_visibility="collapsed")

# 📅 Filtrando dados pelo intervalo selecionado
start_date = df.index.max() - pd.Timedelta(days=days_input)


with col1:
    st.markdown("""
        <div style="
            font-size: 24px; font-weight: bold; text-align: left;
            padding-bottom: 5px;">
            📋 INFORME DIÁRIO - {date}
        </div>
        <div style="font-size: 18px; color: #0072B5; text-align: left;">
            Ref.: {start_date} a {end_date}
        </div>
        <div style="font-size: 16px; font-weight: bold; text-align: left;">
            🚩 ESTAÇÃO Qt - BOM RETIRO (Fazenda)
        </div>
    """.format(
        date=df.index.max().strftime('%d/%m/%Y'),
        start_date=start_date.strftime('%d/%m/%Y'),
        end_date=df.index.max().strftime('%d/%m/%Y')
    ), unsafe_allow_html=True)


df_filtered = df[df.index >= start_date]

# 🎯 Filtrando apenas dados válidos
valid_data = df_filtered[
    (df_filtered["NOflag"] == 1) & (df_filtered["NO2flag"] == 1) & (df_filtered["NOXflag"] == 1) &
    (df_filtered["O3flag"] == 1) & (df_filtered["COflag"] == 1) &
    (df_filtered["SO2flag"] == 1) & (df_filtered["PM10flag"] == 1)
].copy()

# ⚠️ Criando outro filtro para dados válidos e inválidos
valid_invld_data = df_filtered[
    ((df_filtered["NOflag"] == 1) | (df_filtered["NOflag"] == 4)) &
    ((df_filtered["NO2flag"] == 1) | (df_filtered["NO2flag"] == 4)) &
    ((df_filtered["NOXflag"] == 1) | (df_filtered["NOXflag"] == 4)) &
    ((df_filtered["O3flag"] == 1) | (df_filtered["O3flag"] == 4)) &
    ((df_filtered["COflag"] == 1) | (df_filtered["COflag"] == 4)) &
    ((df_filtered["SO2flag"] == 1) | (df_filtered["SO2flag"] == 4)) &
    ((df_filtered["PM10flag"] == 1) | (df_filtered["PM10flag"] == 4))
].copy()

# 📊 Definição dos limites da CONAMA
limits = {
    "NO2": 250,
    "O3": 130,
    "CO": 9,
    "SO2": 50,
    "PM10": 100,
}

# 🔄 Função para calcular médias móveis
def rolling_mean(series, window, min_periods):
    return series.rolling(window, min_periods=min_periods).mean()

# 📈 Cálculo das médias móveis
NO2_hourly_MA = rolling_mean(valid_data["NO2"], "1h", 1)
O3_hourly_MA = rolling_mean(valid_data["O3"], "8h", 6)
CO_hourly_MA = rolling_mean(valid_data["CO"], "8h", 6)
SO2_hourly_MA = rolling_mean(valid_data["SO2"], "24h", 18)
PM10_hourly_MA = rolling_mean(valid_data["PM10"], "24h", 18)

# ⚠️ Verifica ultrapassagem de limites
exceeded_messages = []
for param, limit in limits.items():
    exceeded = eval(f"{param}_hourly_MA") > limit
    exceeded = exceeded[exceeded.index >= start_date]

    if exceeded.any():
        max_val = eval(f"{param}_hourly_MA").max()
        max_time = eval(f"{param}_hourly_MA").idxmax().strftime("%d/%m/%y %H:%M")
        exceeded_messages.append(f"🚨 {param} ultrapassou {limit} µg/m³ ({max_val:.2f}) em {max_time}")

# ⚠️ Verificação de valores negativos e outras anomalias
messages_OC = []

for param in ["NO", "NO2", "NOX", "O3", "CO", "SO2"]:
    negative_values = valid_data[valid_data[param] < 0]
    for index, row in negative_values.iterrows():
        messages_OC.append(f"⚠️ {param} abaixo de 0 em {index.strftime('%d/%m/%y %H:%M')}")

for param in ["PM10"]:
    negative_values = valid_data[valid_data[param] < -2]
    for index, row in negative_values.iterrows():
        messages_OC.append(f"⚠️ {param} abaixo de -2 em {index.strftime('%d/%m/%y %H:%M')}")

# Condição NO2 fora da margem de 10%
valid_data['expected_NO2'] = valid_data['NOX'] - valid_data['NO']
valid_data['NO2_margin'] = valid_data['expected_NO2'] * 0.1
valid_data['is_outside_margin'] = ((valid_data["NO2"] < (valid_data['expected_NO2'] - valid_data['NO2_margin'])) |
                                   (valid_data["NO2"] > (valid_data['expected_NO2'] + valid_data['NO2_margin'])))

for date, row in valid_data[valid_data["is_outside_margin"]].iterrows():
    messages_OC.append(f"⚠️ NO2 fora da margem de 10% no dia {date.strftime('%d/%m/%y %H:%M')}")


# 📊 Mensagens sobre limites ultrapassados
st.markdown("""
    <div style= padding: 5px; border-radius: 5px; margin-bottom: -10px; ">
        <b>📊 Padrão de QAr (CONAMA 506/2024):</b>
    </div>
""", unsafe_allow_html=True)
if exceeded_messages:
    for msg in exceeded_messages:
        st.markdown(f"<div style='background-color: #ffdddd; padding: 3px; border-radius: 5px;'>{msg}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='background-color: #ddffdd; padding: 3px; border-radius: 5px;'>Nenhum limite foi ultrapassado.</div>", unsafe_allow_html=True)

# 📋 Mensagens sobre invalidações
st.markdown("""
    <div style= padding: 5px; border-radius: 5px; margin-bottom: -10px;">
        <b>📋 Feedback de Ocorrências:</b>
    </div>
""", unsafe_allow_html=True)
if messages_OC:
    for msg in messages_OC:
        st.markdown(f"<div style='background-color: #ffcccc; padding: 2px; border-radius: 1px;'>{msg}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='background-color: #ddffdd; padding: 3px; border-radius: 1px;'>Nenhuma ocorrência a relatar.</div>", unsafe_allow_html=True)

st.markdown("")

params = ["NO","NO2"]
cols = st.columns(len(params))
# Criando o estado da aplicação para alternar gráficos
if "use_flag_graphs" not in st.session_state:
    st.session_state.use_flag_graphs = False

if st.session_state.use_flag_graphs:
    for i, param in enumerate(params):
        plotar_grafico(param, df, cols[i])
    button_label = "Gráficos Dinâmicos"
else:
    for i, param in enumerate(params):
        plotar_grafico_dynamic(param, df, cols[i])
    button_label = "Gráficos de Flag"

# Botão para alternar gráficos
if st.button(button_label):
    st.session_state.use_flag_graphs = not st.session_state.use_flag_graphs
    st.rerun()