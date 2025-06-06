from flask import Flask, request, jsonify
from model import Model
import os

# Инициализация модели
model = Model(model_path="improved_discount_model.joblib")
model.load()

app = Flask(__name__)


@app.route('/healthy', methods=['GET'])
def healthy():
    return jsonify({
        "status": "OK" if model.loaded else "Error",
        "model_loaded": model.loaded
    })


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Получаем параметры из URL
        data = request.get_json()
        price_history = request.args.get('price_history')
        if not data or 'price_history' not in data:
            return jsonify({"error": "price_history parameter is required"}), 400

        # Делаем предсказание
        result = model.predict(data['price_history'])

        return jsonify({
            "prediction": result['prediction'],
            "probability": result['probability'],
            "is_fake": result['is_fake']
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
