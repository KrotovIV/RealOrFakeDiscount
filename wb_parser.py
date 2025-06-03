import requests
import json


class ApiHandler:
    def __init__(self, base_url=""):
        self.base_url = base_url

        self.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            "Authorization": "Bearer 92cd43d241a43193b78758db867a40b6d5e9da80"
        }

    def __send_request(self, method, endpoint, data=None, params=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        final_headers = {**self.headers, **(headers or {})}

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=final_headers,
                json=data,
                params=params
            )

        except requests.exceptions.RequestException as e:
            print(
                "error: ", str(e),
                "status_code: ", 500
            )

        if response.status_code != 200:
            raise Exception('status_code: ', response.status_code,
                            "text: ", response.text)

        return response

    def __get_moneyplace_product_id(self, wildberries_product_id, mp):
        endpoint = f'/v1/product?nop=0&per-page=19&q[mp][in]=wildberries,ozon,beru,kazan,lamoda&q[sku][equal]={wildberries_product_id}&period=period'

        try:
            response = self.get(endpoint=endpoint, headers=self.headers)

            found_id = None

            for elem in json.loads(response.text):
                if elem['mp'] == mp:
                    found_id = elem['id']
                    break

            if not found_id:
                raise Exception('item not found in moneyplace')

            return found_id

        except Exception as e:
            print("Exception occured while trying to get moneyplace product id: ", e)

    def __get_moneyplace_product_id_by_wildberries_id(self, wildberries_id: str):
        return self.__get_moneyplace_product_id(wildberries_id, 'wildberries')

    def get(self, endpoint, params=None, headers=None):
        return self.__send_request("GET", endpoint=endpoint,
                                   params=params, headers=headers)

    def __get_prices_history(self, moneyplace_id):
        endpoint = f'/v2/statistic/product/charts/{moneyplace_id}?nop=0&period=month&type=fbo'

        try:
            response = self.get(endpoint=endpoint, headers=self.headers)
        except Exception as e:
            print(e)

        return response

    def get_prices_history_by_wildberries_id(self, id: str):
        moneyplace_id = self.__get_moneyplace_product_id_by_wildberries_id(id)
        return self.__get_prices_history(moneyplace_id)


def main():
    api = ApiHandler(base_url='https://api.moneyplace.io')
    response = api.get_prices_history_by_wildberries_id('4198033')
    print(response.text)


if __name__ == "__main__":
    main()
