import os
import logging
import time

# Cria a pasta de logs, se ainda não existir
os.makedirs("logs", exist_ok=True)

# Configura o sistema de log
logging.basicConfig(
    level=logging.INFO,  # registra mensagens de nível INFO e acima (WARNING, ERROR etc.)
    format='%(asctime)s [%(levelname)s] %(message)s',  # formato com data/hora + tipo + mensagem
    handlers=[
        logging.FileHandler("logs/api.log"),   # salva no arquivo
        logging.StreamHandler()                # também mostra no terminal
    ]
)

import pandas as pd
from flask import g
from sklearn.linear_model import LinearRegression
import numpy as np
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from joblib import load


# Define o caminho absoluto para o CSV
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/books.csv')
df = pd.read_csv(DATA_PATH)
df.reset_index(inplace=True)
df.rename(columns={'index': 'id'}, inplace=True)

from_path = os.path.join(os.path.dirname(__file__), '../models')

model = load(os.path.join(from_path, 'model.joblib'))
scaler = load(os.path.join(from_path, 'scaler.joblib'))

# Treinando o modelo simples com os dados do CSV
X_train = df[['price']]
y_train = df['rating']

model = LinearRegression()
model.fit(X_train, y_train)


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'minha-chave-supersecreta'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # desativa expiração (ou defina um tempo)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = False  # idem
jwt = JWTManager(app)

from flask import g, request

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
    else:
        duration = 0.0

    method = request.method
    path = request.path
    status = response.status_code
    log_msg = f"{method} {path} [{status}] {round(duration, 3)}s"
    logging.info(log_msg)
    return response


# Rotas das APIS
# login com JWT
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logging.info(f"🔐 Tentativa de login: usuário = {username}")

    if username == 'admin' and password == '1234':
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        logging.info(f"✅ Login bem-sucedido: usuário = {username}")
        return jsonify(
            access_token=access_token,
            refresh_token=refresh_token
        ), 200

    logging.warning(f"❌ Login falhou para usuário = {username}")
    return jsonify({"msg": "Usuário ou senha inválido"}), 401


# Refresh token 
@app.route('/api/v1/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    logging.info(f"🔁 Token de acesso renovado para o usuário = {current_user}")
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


# Iniciar Scraping (obter dados)
@app.route('/api/v1/scraping/trigger', methods=['POST'])
@jwt_required()
def trigger_scraping():
    user = get_jwt_identity()
    logging.info(f"🚀 Scraping solicitado por {user}")
    return jsonify({"msg": f"Scraping iniciado por {user}!"}), 200

# Saude API
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    logging.info("❤️ Rota /health acessada – checagem de saúde da API")
    return jsonify({"status": "ok"}), 200


# Lista todos os livros
@app.route('/api/v1/books', methods=['GET'])
def get_books():
    logging.info("📚 Rota /books acessada – listando todos os livros")
    books = df.to_dict(orient='records')
    return jsonify(books), 200


# Busca livro por ID - int
@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    logging.info(f"🔍 Rota /books/{book_id} acessada – buscando livro por ID")
    book = df[df['id'] == book_id]
    if not book.empty:
        logging.info(f"✅ Livro encontrado: ID = {book_id}")
        return jsonify(book.to_dict(orient='records')[0]), 200
    logging.warning(f"❌ Livro não encontrado: ID = {book_id}")
    return jsonify({"error": "Livro não encontrado"}), 404


# Busca livro por titulo ou categoria
@app.route('/api/v1/books/search', methods=['GET'])
def search_books():
    title = request.args.get('title', '').lower()
    category = request.args.get('category', '').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    logging.info(f"🔎 Rota /books/search acessada – título='{title}', categoria='{category}', página={page}")

    result = df.copy()

    if title:
        result = result[result['title'].str.lower().str.contains(title)]
    if category and 'category' in result.columns:
        result = result[result['category'].str.lower().str.contains(category)]

    start = (page - 1) * per_page
    end = start + per_page
    paginated_result = result.iloc[start:end]

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_results': len(result),
        'results': paginated_result.to_dict(orient='records')
    }), 200


# Mostra as categorias de livros existentes
@app.route('/api/v1/categories', methods=['GET'])
def list_categories():
    logging.info("📁 Rota /categories acessada – listando categorias")
    if 'category' in df.columns:
        categories = sorted(df['category'].dropna().unique())
        return jsonify(categories), 200
    logging.warning("⚠️ Nenhuma coluna 'category' encontrada no DataFrame")
    return jsonify([]), 200


# Etapa 2 - Endpoints para cientistas de dados e modelos ML

# Pega os dados de livros e transforma em um formato numérico: ideal para modelos ML.
@app.route('/api/v1/ml/features', methods=['GET'])
def get_ml_features():
    logging.info("📊 Rota /ml/features acessada – retornando features numéricas")
    features = df[['price', 'rating']]
    return jsonify(features.to_dict(orient='records')), 200

# Retorna os dados que podem ser usados como X (features) e y (alvo)
# queremos prever a nota (rating) a partir do price
@app.route('/api/v1/ml/training-data', methods=['GET'])
def get_training_data():
    logging.info("📊 Rota /ml/training-data acessada – retornando X e y para treino")
    X = df[['price']]
    y = df['rating']
    data = pd.concat([X, y], axis=1)
    return jsonify(data.to_dict(orient='records')), 200


# Recebe um preço e retorna uma previsão de rating
@app.route('/api/v1/ml/predictions', methods=['POST'])
def predict_rating():
    data = request.get_json()

    try:
        price = float(data.get('price'))
        input_scaled = scaler.transform([[price]])
        prediction = model.predict(input_scaled)[0]

        logging.info(f"📈 Previsão feita para preço {price}: rating previsto = {round(float(prediction), 2)}")

        return jsonify({
            "price": price,
            "predicted_rating": round(float(prediction), 2)
        }), 200

    except (TypeError, ValueError):
        logging.warning("⚠️ Erro: preço inválido ou ausente na requisição.")
        return jsonify({"error": "Preço inválido ou ausente"}), 400


    except (TypeError, ValueError):
        return jsonify({"error": "Preço inválido ou ausente"}), 400

"""Parte 3 - Endpoints de Insights - Estatisticas gerais: 
total de livros, preço médio e distribuição de ratings"""

@app.route('/api/v1/stats/overview', methods=['GET'])
def stats_overview():
    logging.info("📊 Rota /stats/overview acessada – retornando estatísticas gerais")
    total_books = len(df)
    average_price = round(df['price'].mean(), 2)
    rating_distribution = df['rating'].value_counts().sort_index().to_dict()

    return jsonify({
        "total_books": total_books,
        "average_price": average_price,
        "rating_distribution": rating_distribution
    }), 200


# lista livros com rating == 5 (melhor avaliação)
@app.route('/api/v1/books/top-rated', methods=['GET'])
def top_rated_books():
    logging.info("🌟 Rota /books/top-rated acessada – listando livros com maior nota")
    top_books = df[df['rating'] == df['rating'].max()]
    return jsonify(top_books.to_dict(orient='records')), 200


if __name__ == '__main__':
    logging.info("🟢 Servidor Flask iniciado com sucesso")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

