import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from graficos_static import gerar_grafico_html
from weasyprint import HTML
import os

# 📂 Carregar dados do Excel
file_path = "./datasets/COCA-DADOS.xlsx"
df = pd.read_excel(file_path, engine="openpyxl", sheet_name="COCA")

# 🎯 Selecionar apenas as colunas necessárias
df = df[["Date_Time", "NO", "Status_NO", "NO2", "Status_NO2", "NOX", "Status_NOX",
         "O3", "Status_O3", "CO", "Status_CO", "SO2", "Status_SO2", "PM10", "Status_PM10"]]

# 🏷️ Renomear colunas
df.columns = ["date", "NO", "NOflag", "NO2", "NO2flag", "NOX", "NOXflag", "O3", "O3flag",
              "CO", "COflag", "SO2", "SO2flag", "PM10", "PM10flag"]

df["date"] = pd.to_datetime(df["date"])
df.sort_values("date", inplace=True)
df.set_index("date", inplace=True)

ultima_data = df.index.max()
start_date = df.index.max() - pd.Timedelta(days=2)  
df_filtered = df[df.index >= start_date]

# 📊 Definição dos limites da CONAMA
limits = {
    "NO2": 250,
    "O3": 130,
    "CO": 9,
    "SO2": 50,
    "PM10": 100,
}

# 🟡 Cálculo das médias móveis
def rolling_mean(series, window, min_periods):
    return series.rolling(window, min_periods=min_periods).mean()

NO2_hourly_MA = rolling_mean(df_filtered["NO2"], "1h", 1)
O3_hourly_MA = rolling_mean(df_filtered["O3"], "8h", 6)
CO_hourly_MA = rolling_mean(df_filtered["CO"], "8h", 6)
SO2_hourly_MA = rolling_mean(df_filtered["SO2"], "24h", 18)
PM10_hourly_MA = rolling_mean(df_filtered["PM10"], "24h", 18)

# 🚨 Verifica ultrapassagem de limites
exceeded_messages = []
for param, limit in limits.items():
    exceeded = eval(f"{param}_hourly_MA") > limit
    exceeded = exceeded[exceeded.index >= start_date]

    if exceeded.any():
        max_val = eval(f"{param}_hourly_MA").max()
        max_time = eval(f"{param}_hourly_MA").idxmax().strftime("%d/%m/%y %H:%M")
        exceeded_messages.append(f"{param} ultrapassou {limit} µg/m³ ({max_val:.2f}) em {max_time}")

# ⚠️ Verificação de valores negativos e anomalias
messages_OC = []
for param in ["NO", "NO2", "NOX", "O3", "CO", "SO2"]:
    negative_values = df_filtered[df_filtered[param] < 0]
    for index, row in negative_values.iterrows():
        messages_OC.append(f"{param} abaixo de 0 em {index.strftime('%d/%m/%y %H:%M')}")

for param in ["PM10"]:
    negative_values = df_filtered[df_filtered[param] < -2]
    for index, row in negative_values.iterrows():
        messages_OC.append(f"{param} abaixo de -2 em {index.strftime('%d/%m/%y %H:%M')}")

# 📈 Criar gráficos corretamente
graficos_path = "graficos"
os.makedirs(graficos_path, exist_ok=True)

# 📊 Gerar gráficos para os parâmetros desejados
params = ["NO", "NO2", "NOX", "O3", "CO", "SO2", "PM10"]
graficos_gerados = {param: gerar_grafico_html(param, df.copy()) for param in params}

# 🔹 Criar um HTML formatado para A4 com gráficos organizados em uma única coluna
html_report = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Qualidade do Ar</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 280mm;
            min-height: 396mm;
            background-color: white;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 15mm 10mm;
            box-sizing: border-box;
            position: relative;
        }}
        h1 {{
            text-align: center;
            font-size: 18px;
            margin-bottom: 10px;
            margin-top: -45px;
        }}
        h2 {{
            font-size: 16px;
            padding: 1px;
            margin-bottom: 6px;
            margin-top: 6px;
            page-break-after: avoid;
        }}
        p {{
            font-size: 14px;
            margin: 3px;
            margin-bottom: 1px;
        }}
        .exceeded-container, .alerta-container {{
            background-color: #ffcccc;
            padding: 2px;
            border-radius: 5px;
            margin-top: 5px;
        }}
        .graficos-container {{
            display: block;
            flex-direction: column;
            align-items: center;
            margin-top: 10px;
            page-break-inside: auto;
        }}
        .graficos-container img {{
            width: 100%;
            max-height: 350px;
            object-fit: contain;
            padding: 1px;
            page-break-before: auto;
            align-items: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>INFORME DIÁRIO - {ultima_data.strftime('%d/%m/%Y')}</h1>
        <p><b>Período:</b> {start_date.strftime('%d/%m/%Y')} a {ultima_data.strftime('%d/%m/%Y')}</p>
        <p><b>Estação Monitorada:</b> Qt - BOM RETIRO</p>

        <div class="exceeded-container">
            <p><b>Padrão de QAr (CONAMA 506/2024):</b></p>
            {"".join([f"<p>{msg}</p>" for msg in exceeded_messages]) if exceeded_messages else "<p>Nenhum limite foi ultrapassado.</p>"}
        </div>

        <div class="alerta-container">
            <p><b>Ocorrências:</b></p>
            {"".join([f"<p>{msg}</p>" for msg in messages_OC]) if messages_OC else "<p>Nenhuma ocorrência encontrada.</p>"}
        </div>

        <div class="graficos-container">
            {"".join([f'<img src="{graficos_gerados[param]}" alt="Gráfico de {param}">' for param in params])}
        </div>
    </div>
</body>
</html>
"""

# 📄 Salvar o relatório
with open("relatorio.html", "w", encoding="utf-8") as file:
    file.write(html_report)

print("✅ Relatório salvo como 'relatorio.html' 📄")

# 📄 Converter o HTML para PDF
html_file = "relatorio.html"
pdf_file = "relatorio.pdf"

HTML(html_file).write_pdf(pdf_file)

print("✅ Relatório convertido para PDF com sucesso! 📄")
