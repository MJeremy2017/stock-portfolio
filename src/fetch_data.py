import os.path
import requests
import json

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch_current_trading_stocks(exchange_names: list, refresh=False):
    """
    This fetches the current trading stocks' specs over the global market from
    https://site.financialmodelingprep.com/developer/docs#symbol-list-stock-list.
    This comprehensive list includes over 25,000 stocks.
    :param exchange_names: select exchange names to filter the results. e.g. ['NASDAQ', 'NYSE']
    :param refresh: If set to True will fetch the latest tickers over the API call.
    Otherwise, will use the cached results saved in /artifacts/current_trading_stocks.json
    :return:
    """
    if refresh:
        API_KEY = os.getenv('API_KEY')
        if API_KEY is None:
            raise ValueError("API KEY is not provided, `source .dev_env` before running")
        url = "https://financialmodelingprep.com/api/v3/stock/list"
        url += f"?apikey={API_KEY}"
        resp = requests.get(url)
        resp_json = resp.json()
        with open(os.path.join(PROJECT_DIR, 'artifacts/current_trading_stocks.json'), 'w') as f:
            json.dump(resp_json, f)
    else:
        with open(os.path.join(PROJECT_DIR, 'artifacts/current_trading_stocks.json'), 'r') as f:
            resp_json = json.load(f)
    resp_json = [it for it in resp_json if it['exchangeShortName'] in exchange_names]
    return resp_json


if __name__ == '__main__':
    resp = fetch_current_trading_stocks(exchange_names=['NASDAQ', 'NYSE'], refresh=True)
    print(resp)
