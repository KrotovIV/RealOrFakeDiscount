import requests
import datetime
import time


class SteamPriceParser:
    def __init__(self):
        self.base_url = 'https://steamdb.info'
        self.session = requests.Session()

        # chrome headers
        self.headers = {
            "accept": "application/json",
            "accept-encoding": "identity",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "cookie": "cf_clearance=zvCTMVexru.WAfJmH4oMG2F63Nd5oM7XEwNm9ppOzyI-1749241979-1.2.1.1-AVIJWG7bqUgL4JYj82zb5y5u1OGKpcdduP3opzC9xTUGg6jYIe2rYuLFEpUU5NlZHWb4de_yeGVHLo73VRk6AZJDCzszerEd04uAgc1bbOLP7k6.7kK6Zuoq.RaLrQ8RWpzPk0UzXqu2YqnzKVPNhCSpo.WGJg3rP5jpk4M2.kqcb9w2kyxAR.zblcQvhtPmgimXRmlWDdmvErKJA6v2BqbytMgyyaGjGxYpTDsQnff7hLvXRfqohDua2Wzs1y_B_w60htYndD4ZXi.yKzPQMJd_3YqewBCiQ.YYpRivdR9rnD5ijx5.HrwsbviYHhhJRcvIbP4SLAn_VAgc0ngI8oNZHuq_o3q.EpLncLnW4vxQpjrrSJRFOwazuH.SLTtu; cf_clearance=aQrWF0awoAFB8UAdZDY.tcKdr0V640G0muJb1MA1SHw-1749297967-1.2.1.1-ewduUcF6_BMrlseB_YT_qzm2ZyasnSfUQZuw7J5XF0CNQyixI3PGt38PmpgfLytvvsLpiHf3YwzZXz5FfHpXiHIxZ00_kkQqM3.4uV8Cp.Myplqfpt6jm2YS7MZj.dTsWI8.q0JSCxsyfSutLVWmNss7l8thhoOeYFDPgL3YAP36xnDDvhqchrogf.kluxnwQX45FLLdU9YR9tCd9Hl2v.utxjvoCmYw_DvcEvjOMhMxvHwnNEkP0nlpP7kXJK9YkjoTRI47srBsNHDjwN.U1FRYSqCiBFKH9WXlAsHCRIxwFwT9qMx6xDUeWnXFriIGYC9JhM5zjfiUG6s2ruMylzjV2iInVKKusV5_6mbUJ.CVcY0sJoyWR9d_0Vc6kuhv",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://steamdb.info/app/252490/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"137.0.7151.69"',
            "sec-ch-ua-full-version-list": '"Google Chrome";v="137.0.7151.69", "Chromium";v="137.0.7151.69", "Not/A)Brand";v="24.0.0.0"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"10.0.0"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

    def __update_headers(self, id):
        self.headers["Referer"] = f"{self.base_url}/app/{id}/"
        # self.headers[":path"] = f"/api/GetPriceHistory/?appid={id}&cc=ru"

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
        print(json_response)
        raw_prices = json_response['data']['history']
        raw_sales = json_response['data']['sales']
        sales = []

        # # # normalize sales
        if sales:
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
    data = parser.parse("2404880")
    print(data)
