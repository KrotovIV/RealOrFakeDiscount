# model.py
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from datetime import datetime
from typing import Dict, List, Any
import os


class Model:
    def __init__(self, model_path='improved_discount_model.joblib'):
        """Инициализация модели с указанием пути к файлу модели"""
        self.model_path = model_path
        self.model = None
        self.loaded = False
        self.feature_columns = [
            'current_price', 'current_discount', 'base_price', 'price_ratio',
            'max_discount', 'discount_diff', 'is_sale', 'price_std',
            'price_trend', 'days_since_last_change'
        ]

    def load(self):
        """Загрузка модели из файла"""
        try:
            self.model = joblib.load(self.model_path)
            self.loaded = True
            print("Модель успешно загружена")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке модели: {e}")
            self.loaded = False
            return False

    def train_and_save(self, csv_path, test_size=0.2, random_state=42):
        """
        Обучение модели на данных из CSV и сохранение в файл
        Args:
            csv_path: путь к CSV файлу с данными
            test_size: размер тестовой выборки (по умолчанию 0.2)
            random_state: random state для воспроизводимости (по умолчанию 42)
        """
        # Загрузка и предобработка данных
        df = pd.read_csv(csv_path)
        df.dropna(inplace=True)

        # Убедимся, что у нас есть все нужные колонки
        required_columns = self.feature_columns + ['is_fake']
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"В данных отсутствуют необходимые колонки: {missing_cols}")

        X = df[self.feature_columns]
        y = df['is_fake']

        # Разделение на тренировочный и тестовый наборы
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Создание и обучение модели
        self.model = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                penalty='l2',
                C=1.0,
                solver='lbfgs',
                max_iter=1000,
                random_state=random_state,
                class_weight='balanced'  # Добавляем балансировку классов
            )
        )

        self.model.fit(X_train, y_train)

        # Оценка качества
        y_pred = self.model.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        # Сохранение модели
        joblib.dump(self.model, self.model_path)
        print(f"\nМодель сохранена в файл: {self.model_path}")
        self.loaded = True

    def _calculate_features(self, price_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Вычисление признаков на основе истории цен
        Args:
            price_history: список словарей с историей цен в формате:
                [
                    {
                        'x': 'YYYY-MM-DD',
                        'y': float,  # цена со скидкой
                        'd': float,  # процент скидки
                        'is_sale': int  # флаг распродажи
                    },
                    ...
                ]
        Returns:
            Словарь с вычисленными признаками
        """
        if not price_history:
            raise ValueError("История цен не может быть пустой")

        last_entry = price_history[-1]
        base_price = last_entry['y'] / (1 - last_entry['d'] /
                                        100) if last_entry['d'] > 0 else last_entry['y']

        # Вычисляем статистики по ценам
        price_values = [p['y'] for p in price_history]
        discount_values = [p['d'] for p in price_history]
        sale_dates = [datetime.strptime(p['x'], '%Y-%m-%d')
                      for p in price_history]

        # Вычисляем дни с последнего изменения цены
        days_since_last_change = 0
        if len(price_history) > 1:
            last_price = price_history[-1]['y']
            for i in range(len(price_history)-2, -1, -1):
                if abs(price_history[i]['y'] - last_price) > 1:
                    days_since_last_change = (
                        sale_dates[-1] - sale_dates[i]).days
                    break

        # Признаки для модели
        features = {
            'current_price': last_entry['y'],
            'current_discount': last_entry['d'],
            'base_price': base_price,
            'price_ratio': last_entry['y'] / np.mean(price_values) if price_values else 0,
            'max_discount': max(discount_values) if discount_values else 0,
            'discount_diff': last_entry['d'] - np.mean(discount_values) if discount_values else 0,
            'is_sale': last_entry['is_sale'],
            'price_std': np.std(price_values) if len(price_values) > 1 else 0,
            'price_trend': self._calculate_trend(price_values),
            'days_since_last_change': days_since_last_change
        }

        return features

    def _calculate_trend(self, values: List[float]) -> float:
        """Вычисление тренда цен"""
        if len(values) < 2:
            return 0
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        return slope / np.mean(y) if np.mean(y) != 0 else 0

    def prepare_input_data(self, price_history: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Подготовка данных о ценах для предсказания
        Args:
            price_history: список словарей с историей цен (см. _calculate_features)
        Returns:
            pandas.DataFrame: подготовленные данные для модели
        """
        features = self._calculate_features(price_history)
        df = pd.DataFrame([features])
        return df[self.feature_columns]

    def predict(self, price_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Предсказание типа скидки на основе истории цен
        Args:
            price_history: список словарей с историей цен (см. prepare_input_data)
        Returns:
            dict: {
                'prediction': 'Фейковая' или 'Настоящая',
                'probability': вероятность фейковой скидки в процентах,
                'is_fake': bool,
                'features': dict  # вычисленные признаки для отладки
            }
        """
        if not self.loaded and not self.load():
            raise Exception("Модель не загружена и не может быть загружена")

        # Подготовка данных
        input_data = self.prepare_input_data(price_history)
        features = self._calculate_features(price_history)

        # Предсказание
        prediction = self.model.predict(input_data)[0]
        proba = self.model.predict_proba(input_data)[0][1]

        return {
            'prediction': 'Фейковая' if prediction else 'Настоящая',
            'probability': f"{proba:.1%}",
            'is_fake': bool(prediction),
            'features': features  # Для отладки и анализа
        }
