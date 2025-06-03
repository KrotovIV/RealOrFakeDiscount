import csv
import random
import numpy as np


def generate_real_prices(days):
    """Генерация реальных цен со скидкой"""
    base_price = round(random.uniform(500, 5000), 2)
    current_price = base_price * random.uniform(0.7, 0.95)

    base_prices = []
    current_prices = []
    discounts = []

    for _ in range(days):
        # Плавные изменения базовой цены
        base_price += random.uniform(-50, 50)
        base_price = max(300, min(base_price, 10000))

        # Реальная скидка 5-30%
        discount = random.uniform(0.05, 0.3)
        current_price = base_price * (1 - discount)

        # Небольшие флуктуации текущей цены
        current_price += random.uniform(-20, 20)
        current_price = max(300, current_price)

        base_prices.append(round(base_price, 2))
        current_prices.append(round(current_price, 2))
        discounts.append(round(discount * 100, 2))

    return base_prices, current_prices, discounts


def generate_fake_prices(days):
    """Генерация фейковых цен со скидкой"""
    base_price = round(random.uniform(500, 5000), 2)
    current_price = base_price * random.uniform(0.7, 0.95)

    base_prices = []
    current_prices = []
    discounts = []

    # Выбираем день, когда начнётся "накрутка" скидки
    cheat_day = random.randint(5, days-5)

    for day in range(days):
        if day < cheat_day:
            # До накрутки - ведём себя как честный продавец
            base_price += random.uniform(-50, 50)
            base_price = max(300, min(base_price, 10000))
            discount = random.uniform(0.05, 0.3)
        else:
            # После cheat_day - начинаем накручивать скидку
            # Резко увеличиваем базовую цену
            base_price += random.uniform(100, 500)
            # Искусственно завышаем скидку
            discount = random.uniform(0.4, 0.8)

        # Поддерживаем текущую цену примерно на том же уровне
        current_price = base_price * (1 - discount)
        current_price += random.uniform(-20, 20)
        current_price = max(300, current_price)

        base_prices.append(round(base_price, 2))
        current_prices.append(round(current_price, 2))
        discounts.append(round(discount * 100, 2))

    return base_prices, current_prices, discounts


def generate_dataset(num_samples, output_file):
    """Генерация датасета и сохранение в CSV"""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Заголовки: is_fake + динамика по дням (базовая цена, текущая цена, скидка)
        headers = ['is_fake']
        for day in range(31):  # Максимальное количество дней в месяце
            headers.extend([
                f'day{day}_base_price',
                f'day{day}_current_price',
                f'day{day}_discount'
            ])
        writer.writerow(headers)

        for _ in range(num_samples):
            is_fake = random.random() < 0.5  # 50% фейковых скидок
            days_in_month = random.choice([28, 30, 31])

            if is_fake:
                base_prices, current_prices, discounts = generate_fake_prices(
                    days_in_month)
            else:
                base_prices, current_prices, discounts = generate_real_prices(
                    days_in_month)

            # Заполняем недостающие дни NaN
            row = [int(is_fake)]
            for day in range(31):
                if day < days_in_month:
                    row.extend([
                        base_prices[day],
                        current_prices[day],
                        discounts[day]
                    ])
                else:
                    row.extend([np.nan, np.nan, np.nan])

            writer.writerow(row)


# Генерация датасета (1000 samples)
generate_dataset(1000, 'discount_dataset.csv')
print("Датасет успешно сгенерирован и сохранён в discount_dataset.csv")
