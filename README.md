# 📚 Book Recommender API

Este projeto consiste em:

- Uma **API Flask** com autenticação via JWT e rotas para dados de livros e modelo de machine learning.
- Um **modelo de regressão linear** treinado com `scikit-learn` para prever a nota (`rating`) de livros com base no preço.
- Um **dashboard interativo em Streamlit** para monitoramento das requisições via logs.

---

## 📦 Estrutura do Projeto

```
book-recommender-api/
│
├── api/
│   └── app.py              # Código da API Flask
│
├── data/
│   └── books.csv           # Base de dados de livros
│
├── models/
│   ├── model.joblib        # Modelo treinado (regressão linear)
│   └── scaler.joblib       # Scaler padrão usado na predição
│
├── logs/
│   └── api.log             # Arquivo de log gerado localmente ou via Heroku (manual)
│
├── scripts/
│   └── train_model.py      # Script para treinar o modelo e salvar os arquivos joblib
│
├── dashboard.py            # Dashboard em Streamlit para análise dos logs
├── requirements.txt        # Dependências do projeto
├── runtime.txt             # Versão do Python para deploy no Heroku
└── Procfile                # Comando para rodar a API com gunicorn no Heroku
```

---

## 🚀 API Flask

### 🔐 Autenticação JWT

- Login: `POST /api/v1/auth/login`  
  Enviar JSON com `username` e `password`.  
  Retorna tokens `access` e `refresh`.

- Refresh: `POST /api/v1/auth/refresh`  
  Enviar `refresh token` para obter novo `access token`.

### 📘 Endpoints de livros

- `GET /api/v1/books` → Lista todos os livros  
- `GET /api/v1/books/<id>` → Detalhes por ID  
- `GET /api/v1/books/search?title=...&category=...` → Busca  
- `GET /api/v1/categories` → Lista categorias  
- `GET /api/v1/books/top-rated` → Lista livros com nota máxima

### ⚙️ Machine Learning

- `GET /api/v1/ml/features` → Retorna features numéricas (`price`, `rating`)  
- `GET /api/v1/ml/training-data` → Dados usados no treino  
- `POST /api/v1/ml/predictions` → Enviar `{ "price": valor }` para obter previsão de `rating`

### 📊 Estatísticas

- `GET /api/v1/stats/overview` → Total de livros, preço médio e distribuição das notas

### ❤️ Checagem de saúde

- `GET /api/v1/health` → Verifica se a API está no ar

---

## 🧠 Treinamento do modelo

```bash
python scripts/train_model.py
```

Este script:

- Lê os dados de `books.csv`
- Treina um modelo `LinearRegression`
- Aplica um `StandardScaler`
- Salva os arquivos `model.joblib` e `scaler.joblib` na pasta `models/`

---

## 📊 Dashboard de Logs

### Execução local

```bash
streamlit run dashboard.py
```

O dashboard:

- Lê `logs/api.log`
- Apresenta:
  - Total de requisições
  - Tempo médio de resposta
  - Gráfico de status
  - Tabela das últimas requisições

---

## 🔁 Como obter logs reais do Heroku

O Heroku **não salva os logs em arquivos persistentes**, por isso usei este método manual:

```bash
heroku logs --app book-recommender-api2 --num 1500 > logs/api.log
```

> Após isso, rode o dashboard normalmente.

---

## 🌐 Deploy no Heroku

### 1. Requisitos

- `gunicorn` incluído no `requirements.txt`
- `Procfile` com:

```bash
web: gunicorn api.app:app
```

- `runtime.txt` com a versão do Python desejada (ex: `python-3.11.9`)

### 2. Comandos de deploy

```bash
git init
heroku create book-recommender-api2
git add .
git commit -m "Deploy inicial"
git push heroku master  # ou `main`, dependendo do branch
```

---

## ✅ Notas

- O sistema de logs funciona localmente (arquivo `logs/api.log`)
- Em produção (Heroku), você deve exportar os logs manualmente
- O dashboard pode ser mantido local ou publicado separadamente com adaptação

---

## 🧪 Teste rápido (exemplo de login)

```bash
curl -X POST https://book-recommender-api2.herokuapp.com/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "1234"}'
```

---

## 👩‍⚕️ Desenvolvido por

**Maria L**  
Python Developer | ML Engenieer Student | UX designer IA   
[🔗 book-recommender-api2.herokuapp.com](https://book-recommender-api2.herokuapp.com)