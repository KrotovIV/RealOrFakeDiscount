from flask import Flask, request, jsonify
from flask_cors import CORS  # Импорт модуля CORS
from model import Model
import os

# Инициализация модели
model = Model(model_path="improved_discount_model.joblib")
model.load()

app = Flask(__name__)
CORS(app)  # Включение CORS для всего приложения


@app.route('/healthy', methods=['GET'])
def healthy():
    return jsonify({
        "status": "OK" if model.loaded else "Error",
        "model_loaded": model.loaded
    })


# Добавлен метод OPTIONS для CORS
@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        # Обработка предварительного OPTIONS запроса
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        # Получаем JSON данные из тела запроса
        data = request.get_json()
        if not data or 'price_history' not in data:
            return jsonify({"error": "price_history parameter is required in JSON body"}), 400

        # Делаем предсказание
        result = model.predict(data['price_history'])

        # Создаем ответ с CORS заголовками
        response = jsonify({
            "prediction": result['prediction'],
            "probability": result['probability'],
            "is_fake": result['is_fake']
        })
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

    except Exception as e:
        error_response = jsonify({"error": str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
