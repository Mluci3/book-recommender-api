# dashboard.py# dashboard.py
import streamlit as st
import pandas as pd
import re

st.title("📊 Dashboard de Monitoramento da API")

# Lê o arquivo de log
with open("logs/api.log", "r") as f:
    lines = f.readlines()

# Regex para logs estruturados
pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\[INFO\]\s+(\w+)\s+(\S+)\s+\[(\d{3})\]\s+([\d.]+)s"

# Extrai os dados
data = []
for line in lines:
    match = re.search(pattern, line)
    if match:
        timestamp, method, url, status, duration = match.groups()
        data.append({
            "timestamp": timestamp,
            "method": method,
            "url": url,
            "status": int(status),
            "duration": float(duration)
        })

df = pd.DataFrame(data)

if df.empty or 'duration' not in df.columns:
    st.error("❌ Nenhum dado estruturado encontrado ou a coluna 'duration' não foi extraída dos logs. Verifique o formato dos logs.")
    st.stop()

# Exibe dados
st.metric("📌 Total de Requisições", len(df))
st.metric("⚡ Tempo Médio de Resposta (s)", round(df['duration'].mean(), 3))
st.bar_chart(df['status'].value_counts())
st.dataframe(df.sort_values(by="timestamp", ascending=False).head(20))
