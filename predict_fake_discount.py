import joblib
import pandas as pd
import numpy as np


def load_model(model_path='discount_model.joblib'):
    """Загрузка обученной модели"""
    try:
        model = joblib.load(model_path)
        print("Модель успешно загружена")
        return model
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
        return None


def prepare_input_data(input_dict):
    """Подготовка входных данных в правильном формате"""
    # Создаем DataFrame с одной строкой
    df = pd.DataFrame([input_dict])

    # Заполняем пропущенные дни NaN (если нужно)
    for day in range(31):
        if f'day{day}_base_price' not in df.columns:
            df[f'day{day}_base_price'] = np.nan
            df[f'day{day}_current_price'] = np.nan
            df[f'day{day}_discount'] = np.nan

    # Упорядочиваем колонки как в обучающих данных
    cols = []
    for day in range(31):
        cols.extend([
            f'day{day}_base_price',
            f'day{day}_current_price',
            f'day{day}_discount'
        ])

    return df[cols]


def predict(model, input_data):
    """Предсказание для новых данных"""
    try:
        # Предсказание и вероятности
        prediction = model.predict(input_data)[0]
        proba = model.predict_proba(input_data)[0][1]  # Вероятность фейка

        return {
            'prediction': 'Фейковая' if prediction else 'Настоящая',
            'probability': f"{proba:.1%}",
            'is_fake': bool(prediction)
        }
    except Exception as e:
        print(f"Ошибка при предсказании: {e}")
        return None


if __name__ == "__main__":
    # Пример входных данных (замените на свои)
    example_data = {
        'day0_base_price': 1200.0,
        'day0_current_price': 900.0,
        'day0_discount': 25.0,
        'day1_base_price': 1250.0,
        'day1_current_price': 950.0,
        'day1_discount': 24.0,
        # ... добавьте данные для других дней
    }

    # Загружаем модель
    model = load_model()
    if model is None:
        exit(1)

    # Подготавливаем данные
    input_data = prepare_input_data(example_data)

    # Делаем предсказание
    result = predict(model, input_data)

    if result:
        print("\nРезультат предсказания:")
        print(f"Тип скидки: {result['prediction']}")
        print(f"Вероятность фейковой скидки: {result['probability']}")
        print(f"Флаг is_fake: {result['is_fake']}")
