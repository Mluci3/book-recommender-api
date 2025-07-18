# 📚 API de Livros com Machine Learning

API Flask para manipulação de livros, autenticação com JWT, scraping simulado e previsão de avaliação (rating) com base no preço. Contém endpoints públicos e privados, e suporte a modelos de ML treinados.

---

## 🚀 Como rodar localmente

1. Clone o repositório.
2. Certifique-se de ter os arquivos:
   - `books.csv` na pasta `/data`
   - `model.joblib` e `scaler.joblib` na pasta `/models`
3. Instale as dependências:
   ```bash
   pip install flask flask-jwt-extended pandas numpy scikit-learn joblib
