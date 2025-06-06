import requests
import datetime
import time


class SteamPriceParser:
    def __init__(self):
        self.base_url = 'https://steamdb.info'
        self.session = requests.Session()

        # Устанавливаем куки для сессии
        self.session.cookies.update({
            "cf_clearance": "kfk0cewg2zUsbuvtJzcZeXHusb_oqw8tFEmZ_PeVyIc-1749212302-1.2.1.1-81kr7x.P5WmtNut6VTAftApaxHBBv5iWUyOjOz0rPfYizz_OxKmKZi_bVK1sMvmYX8EfdUnlWtkeAY866Gr.HYW.QYSQtZzsAgjT9UG.1RMTuE8cBqQyRRo8tpX0S586KWKGkaNea_s3zrtuS5rsmSfakuB9ZgSpnvShE.WdP4mG3gD6s5kOBMaE4jlTp7I5s0mI5LTB.b37uzButPE3CW3oqLJP1UQzXCudpHyuWaygcXluJgu7.s9qmG9nFwvQpmHGwwHapSPUJ4aLVr.uPkwavo5zoOFEKiijaPewyMOYTCFgi2XBpiu8gsa3PNkp1O8F6X1_hAtYH45cdn15XBCeLDcZkMKyLjJZ0UG.MajeJ5CBgkx9woYhc7oVZbQq"
        })

        # Общие заголовки для API
        self.headers = {
            "Accept": "application/json",
            # Динамически обновляется
            "Referer": "",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
        }

    def __update_headers(self, id):
        self.headers["Referer"] = f"{self.base_url}/app/{id}/"

    def __init_session(self, product_id):
        html_url = f"{self.base_url}/app/{product_id}/"
        self.session.get(html_url)
        time.sleep(1)  # Задержка для имитации поведения браузера

    def parse(self, product_id):
        self.__update_headers(product_id)
        self.__init_session(product_id)

        api_url = f"{self.base_url}/api/GetPriceHistory/?appid={product_id}&cc=ru"
        response = self.session.get(api_url, headers=self.headers)

        if response.status_code == 200:
            return self.__normalize_resopnse(response.json())
        else:
            print("Error:", response.text)
            return None

    def __normalize_resopnse(self, json_response):
        normalized_response = []

        raw_prices = json_response['data']['history']
        raw_sales = json_response['data']['sales']
        sales = []

        # # # normalize sales
        for key in raw_sales.keys():
            sales.append(self.__normalize_unix_date(int(key)))

        # normalize prices
        for i in range(len(raw_prices)):
            normalized_date = self.__normalize_unix_date(raw_prices[i]['x'])
            normalized_response.append({
                'x': normalized_date,
                'y': raw_prices[i]['y'],
                'd': raw_prices[i]['d'],
                'is_sale': int(normalized_date in sales)
            })

        return normalized_response

    def __normalize_unix_date(self, unix_date: int):
        date = datetime.datetime.fromtimestamp(unix_date / 1000)
        return date.strftime('%Y-%m-%d')


if __name__ == "__main__":
    parser = SteamPriceParser()
    data = parser.parse("673450")
    print(data)
