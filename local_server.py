from flask import Flask, request, jsonify
from steam_parser import SteamPriceParser

app = Flask(__name__)
parser = SteamPriceParser()  # Создаем экземпляр парсера при запуске сервера


@app.route('/parse/<product_id>', methods=['GET'])
def get_price_history(product_id):
    print('зашел сюда')
    if not product_id:
        return jsonify({'error': 'Parameter "id" is required'}), 400

    try:
        # Получаем данные с помощью парсера
        price_history = parser.parse(product_id)
        print("price_history: ", price_history)

        if price_history is None:
            return jsonify({'error': 'Failed to get price history'}), 500

        return jsonify({
            'product_id': product_id,
            'price_history': price_history
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7123, debug=True)