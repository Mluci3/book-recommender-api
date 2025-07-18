from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/static/swagger.yaml'  # Caminho do YAML

# Configuração da interface Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Book Recommender API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Servir o swagger.yaml
@app.route('/static/swagger.yaml')
def serve_yaml():
    return send_from_directory('static', 'swagger.yaml')

# Rota de saúde
@app.route('/')
def home():
    return '<h3>✅ Documentação disponível em <a href="/docs">/docs</a></h3>'

if __name__ == '__main__':
    app.run(debug=True)
