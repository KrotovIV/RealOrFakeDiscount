import csv
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class PriceGenerator:
    def __init__(self):
        self.sales_events = {
            '2023-06-29': 'Summer Sale 2023',
            '2023-11-21': 'Autumn Sale 2023',
            '2023-12-21': 'Winter Sale 2023',
            '2024-03-14': 'Spring Sale 2024',
            '2024-06-27': 'Summer Sale 2024',
            '2024-11-27': 'Autumn Sale 2024',
            '2024-12-20': 'Winter Sale 2024',
            '2025-03-13': 'Spring Sale 2025'
        }
        self.sale_dates = [datetime.strptime(
            d, '%Y-%m-%d').date() for d in self.sales_events.keys()]

    def generate_real_prices(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Генерация реальных цен со скидкой"""
        base_price = round(random.uniform(300, 1000), 2)
        prices = []
        current_date = start_date

        # Определяем базовые уровни цен (обычно 1-3 уровня)
        price_levels = sorted([base_price * random.uniform(0.6, 0.9)
                              for _ in range(random.randint(1, 3))])
        current_level = random.choice(price_levels)

        while current_date <= end_date:
            is_sale = current_date.date() in self.sale_dates

            # Плавное изменение уровня цен (редко)
            if random.random() < 0.05:  # 5% chance to change price level
                current_level = random.choice(price_levels)

            # Реальная скидка 20-40% во время распродаж, 0-10% в обычное время
            if is_sale:
                discount = random.uniform(0.2, 0.4)
                current_price = current_level * (1 - discount)
            else:
                if random.random() < 0.3:  # 30% chance of small discount
                    discount = random.uniform(0, 0.1)
                    current_price = current_level * (1 - discount)
                else:
                    discount = 0
                    current_price = current_level

            # Небольшие флуктуации текущей цены
            current_price += random.uniform(-10, 10)
            current_price = max(50, current_price)

            prices.append({
                'x': current_date.strftime('%Y-%m-%d'),
                'y': round(current_price, 2),
                'd': round(discount * 100, 2),
                'is_sale': int(is_sale)
            })

            # Неравномерные интервалы
            current_date += timedelta(days=random.randint(1, 7))

        return prices

    def generate_fake_prices(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Генерация фейковых цен со скидкой"""
        base_price = round(random.uniform(300, 1000), 2)
        prices = []
        current_date = start_date

        # Выбираем день, когда начнётся "накрутка" скидки (ближайший к распродаже)
        cheat_date = random.choice(self.sale_dates) - \
            timedelta(days=random.randint(1, 14))

        while current_date <= end_date:
            is_sale = current_date.date() in self.sale_dates

            if current_date.date() >= cheat_date:
                # После cheat_date - начинаем накручивать скидку
                # Резко увеличиваем базовую цену
                base_price += random.uniform(100, 500)
                # Искусственно завышаем скидку
                discount = random.uniform(0.5, 0.9)
            else:
                # До накрутки - ведём себя как честный продавец
                base_price += random.uniform(-20, 20)
                base_price = max(100, min(base_price, 1500))

                if is_sale:
                    discount = random.uniform(0.2, 0.4)
                else:
                    discount = random.uniform(
                        0, 0.1) if random.random() < 0.3 else 0

            # Поддерживаем текущую цену примерно на том же уровне
            current_price = base_price * (1 - discount)
            current_price += random.uniform(-10, 10)
            current_price = max(50, current_price)

            prices.append({
                'x': current_date.strftime('%Y-%m-%d'),
                'y': round(current_price, 2),
                'd': round(discount * 100, 2),
                'is_sale': int(is_sale)
            })

            current_date += timedelta(days=random.randint(1, 7))

        return prices

    def calculate_features(self, prices: List[Dict]) -> Dict:
        """Вычисление признаков для модели"""
        if not prices:
            return {}

        last_entry = prices[-1]
        base_price = last_entry['y'] / (1 - last_entry['d'] /
                                        100) if last_entry['d'] > 0 else last_entry['y']

        # Вычисляем статистики по ценам
        price_values = [p['y'] for p in prices]
        discount_values = [p['d'] for p in prices]

        # Дополнительные признаки для улучшения классификации
        price_changes = [abs(price_values[i] - price_values[i-1])
                         for i in range(1, len(price_values))]
        large_price_changes = sum(1 for change in price_changes if change > 50)
        recent_price_changes = sum(
            1 for change in price_changes[-5:]) if len(price_changes) >= 5 else 0

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
            'days_since_last_change': self._days_since_last_change(prices),
            'large_price_changes': large_price_changes,
            'recent_price_changes': recent_price_changes,
            'is_fake': 0  # Будет установлено позже
        }

        return features

    def _calculate_trend(self, values: List[float]) -> float:
        """Вычисление тренда (линейная регрессия)"""
        if len(values) < 2:
            return 0
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        return slope / np.mean(y) if np.mean(y) != 0 else 0

    def _days_since_last_change(self, prices: List[Dict]) -> int:
        """Вычисление дней с последнего изменения цены"""
        if len(prices) < 2:
            return 0
        last_price = prices[-1]['y']
        for i in range(len(prices)-2, -1, -1):
            if abs(prices[i]['y'] - last_price) > 1:
                last_date = datetime.strptime(prices[i]['x'], '%Y-%m-%d')
                current_date = datetime.strptime(prices[-1]['x'], '%Y-%m-%d')
                return (current_date - last_date).days
        return 0


def generate_dataset(num_samples: int, output_file: str):
    """Генерация датасета и сохранение в CSV"""
    generator = PriceGenerator()

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Заголовки для признаков
        headers = [
            'current_price', 'current_discount', 'base_price', 'price_ratio',
            'max_discount', 'discount_diff', 'is_sale', 'price_std',
            'price_trend', 'days_since_last_change', 'large_price_changes',
            'recent_price_changes', 'is_fake'
        ]
        writer.writerow(headers)

        for _ in range(num_samples):
            # Случайный период (3-12 месяцев)
            start_date = datetime(2023, 1, 1) + \
                timedelta(days=random.randint(0, 365))
            end_date = start_date + timedelta(days=random.randint(90, 365))

            is_fake = random.random() < 0.5  # 50% фейковых скидок

            if is_fake:
                prices = generator.generate_fake_prices(start_date, end_date)
            else:
                prices = generator.generate_real_prices(start_date, end_date)

            if not prices:
                continue

            features = generator.calculate_features(prices)
            features['is_fake'] = int(is_fake)

            writer.writerow([features[h] for h in headers])


generate_dataset(500000, 'improved_discount_dataset.csv')
print("Улучшенный датасет успешно сгенерирован и сохранён в improved_discount_dataset.csv")
