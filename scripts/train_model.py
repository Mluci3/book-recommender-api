# scripts/train_model.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from joblib import dump
import os

# Caminho para os dados
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/books.csv')
df = pd.read_csv(DATA_PATH)


# Features e alvo
X = df[['price']]
y = df['rating']

# Normaliza os dados
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Treina o modelo
model = LinearRegression()
model.fit(X_scaled, y)

# Salva modelo e scaler
dump(model, 'models/model.joblib')
dump(scaler, 'models/scaler.joblib')

print("Modelo e scaler salvos com sucesso.")
