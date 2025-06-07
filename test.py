import requests
from local_server.steam_parser import SteamPriceParser

parser = SteamPriceParser()

# URL вашего сервера
# Замените на реальный URL при развертывании
API_URL = "http://krotoviv.pythonanywhere.com/predict"

price_history = parser.parse('1296830')

# Формируем запрос
data = {
    "price_history": price_history
}

headers = {
    "Content-Type": "application/json"
}

try:
    # Отправляем POST-запрос
    response = requests.post(API_URL, json={"price_history": price_history})

    # Проверяем статус ответа
    if response.status_code == 200:
        # Успешный запрос
        result = response.json()
        print("Успешный ответ от сервера:")
        # print(f"Request ID: {result['request_id']}")
        print(f"Prediction: {result['prediction']}")
        print(f"Probability: {result['probability']}")
        print(f"Is Fake: {result['is_fake']}")
        # print("Features:", json.dumps(result['features'], indent=2))
    elif response.status_code == 429:
        # Превышен лимит запросов
        error = response.json()
        print(f"Ошибка: {error['detail']}")
        print(
            f"Попробуйте снова через: {error.get('retry_after', 'неизвестно')} секунд")
    else:
        # Другие ошибки
        print(f"Ошибка {response.status_code}: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")
