import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import joblib
import os


def load_and_preprocess_data(csv_path):
    """Загрузка и предобработка данных"""
    df = pd.read_csv(csv_path)

    # Удаляем строки с пропущенными значениями (можно заменить на imputation)
    df.dropna(inplace=True)

    # Разделяем на признаки (X) и целевую переменную (y)
    X = df.drop(columns=['is_fake'])
    y = df['is_fake']

    return X, y


def train_and_save_model(X, y, model_path='discount_model.joblib'):
    """Обучение модели и сохранение в файл"""
    # Разделение на тренировочный и тестовый наборы
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Создаем pipeline: стандартизация + логистическая регрессия
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            penalty='l2',  # Регуляризация L2
            C=1.0,         # Сила регуляризации
            solver='lbfgs',  # Алгоритм оптимизации
            max_iter=1000,  # Максимальное число итераций
            random_state=42
        )
    )

    # Обучение модели
    model.fit(X_train, y_train)

    # Оценка качества
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Сохранение модели
    joblib.dump(model, model_path)
    print(f"\nМодель сохранена в файл: {model_path}")

    return model


if __name__ == "__main__":
    DATA_PATH = "discount_dataset.csv"
    MODEL_PATH = "discount_model.joblib"

    if os.path.exists(MODEL_PATH):
        print("Найдена существующая модель. Загружаем...")
        model = joblib.load(MODEL_PATH)

        # Для примера предсказания нужно загрузить данные
        # Загружаем только X (y не нужен)
        X, _ = load_and_preprocess_data(DATA_PATH)
    else:
        print("Обучение новой модели...")
        X, y = load_and_preprocess_data(DATA_PATH)
        model = train_and_save_model(X, y, MODEL_PATH)

    # Теперь X всегда определен
    print("\nПример предсказания:")
    sample_data = X.iloc[1:2]
    print(sample_data)
    prediction = model.predict(sample_data)
    print(
        f"Предсказание: {'Фейковая скидка' if prediction[0] else 'Настоящая скидка'}")
    # Берем только вероятность класса 1 (фейковая)
    proba = model.predict_proba(sample_data)[0][1]
    print(f"Вероятность фейковой скидки: {proba:.2%}")
