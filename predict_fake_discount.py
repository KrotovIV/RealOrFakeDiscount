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
    # example_data = {
    #     'day0_base_price': 1200.0,
    #     'day0_current_price': 900.0,
    #     'day0_discount': 25.0,
    #     'day1_base_price': 1250.0,
    #     'day1_current_price': 950.0,
    #     'day1_discount': 24.0,
    #     # ... добавьте данные для других дней
    # }

    example_data = {'day0_base_price': 9815.0, 'day0_current_price': 11318.0, 'day0_discount': 13.0, 'day1_base_price': 9815.0, 'day1_current_price': 11318.0, 'day1_discount': 13.0, 'day2_base_price': 9815.0, 'day2_current_price': 11318.0, 'day2_discount': 13.0, 'day3_base_price': 9815.0, 'day3_current_price': 11318.0, 'day3_discount': 13.0, 'day4_base_price': 9815.0, 'day4_current_price': 11318.0, 'day4_discount': 13.0, 'day5_base_price': 9815.0, 'day5_current_price': 11318.0, 'day5_discount': 13.0, 'day6_base_price': 9814.0, 'day6_current_price': 11318.0, 'day6_discount': 13.0, 'day7_base_price': 9805.0, 'day7_current_price': 11318.0, 'day7_discount': 13.0, 'day8_base_price': 10039.0, 'day8_current_price': 11200.0, 'day8_discount': 10.0, 'day9_base_price': 9812.0, 'day9_current_price': 10951.0, 'day9_discount': 10.0, 'day10_base_price': 9812.0, 'day10_current_price': 10951.0, 'day10_discount': 10.0, 'day11_base_price': 9816.0, 'day11_current_price': 10920.0, 'day11_discount': 10.0, 'day12_base_price': 9815.0, 'day12_current_price': 10695.0, 'day12_discount': 8.0, 'day13_base_price': 9815.0, 'day13_current_price': 10701.0, 'day13_discount': 8.0, 'day14_base_price': 9815.0, 'day14_current_price': 10706.0, 'day14_discount': 8.0, 'day15_base_price': 9816.0, 'day15_current_price': 10697.0,
                    'day15_discount': 8.0, 'day16_base_price': 9816.0, 'day16_current_price': 10518.0, 'day16_discount': 7.0, 'day17_base_price': 9816.0, 'day17_current_price': 10518.0, 'day17_discount': 7.0, 'day18_base_price': 9815.0, 'day18_current_price': 10629.0, 'day18_discount': 8.0, 'day19_base_price': 9815.0, 'day19_current_price': 10618.0, 'day19_discount': 8.0, 'day20_base_price': 9816.0, 'day20_current_price': 10607.0, 'day20_discount': 7.0, 'day21_base_price': 9815.0, 'day21_current_price': 10598.0, 'day21_discount': 7.0, 'day22_base_price': 9596.0, 'day22_current_price': 10947.0, 'day22_discount': 12.0, 'day23_base_price': 9815.0, 'day23_current_price': 11185.0, 'day23_discount': 12.0, 'day24_base_price': 9815.0, 'day24_current_price': 11185.0, 'day24_discount': 12.0, 'day25_base_price': 9812.0, 'day25_current_price': 11185.0, 'day25_discount': 12.0, 'day26_base_price': 9814.0, 'day26_current_price': 11385.0, 'day26_discount': 14.0, 'day27_base_price': 10168.0, 'day27_current_price': 11799.0, 'day27_discount': 14.0, 'day28_base_price': 10169.0, 'day28_current_price': 11799.0, 'day28_discount': 14.0, 'day29_base_price': 10163.0, 'day29_current_price': 11799.0, 'day29_discount': 14.0, 'day30_base_price': 10162.0, 'day30_current_price': 11799.0, 'day30_discount': 14.0}

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
