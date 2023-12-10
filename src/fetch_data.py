import os.path
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# TODO: get sp500 stocks
# TODO: get PE of ticker by date


def fetch_current_trading_stocks(exchange_names: list, refresh=False):
    """
    This fetches the current trading stocks' specs over the global market from
    https://site.financialmodelingprep.com/developer/docs#symbol-list-stock-list.
    This comprehensive list includes over 25,000 stocks.
    :param exchange_names: select exchange names to filter the results. e.g. ['NASDAQ', 'NYSE']
    :param refresh: If set to True will fetch the latest tickers over the API call.
    Otherwise, will use the cached results saved in /artifacts/current_trading_stocks.json
    :return: dataframe
    """
    _path = os.path.join(PROJECT_DIR, 'artifacts/stocks_global.csv')
    if refresh:
        API_KEY = os.getenv('API_KEY')
        if API_KEY is None:
            raise ValueError("API KEY is not provided, `source .dev_env` before running")
        url = "https://financialmodelingprep.com/api/v3/stock/list"
        url += f"?apikey={API_KEY}"
        resp = requests.get(url)
        resp_json = resp.json()
        df = pd.DataFrame(resp_json)
        df.to_csv(_path, index=False)
    else:
        df = pd.read_csv(_path)
    df = df[df['exchangeShortName'].isin(exchange_names)]
    return df


def fetch_sp500_tickers(refresh=False):
    """
    Scrape the current s&p500 stocks from wikipedia
    :param refresh: refresh data and save to local
    :return: dataframe of s&p500 stocks
    """
    _path = os.path.join(PROJECT_DIR, 'artifacts/sp500_stocks.csv')
    if refresh:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        # Read the first table found on the page
        df = pd.read_html(response.text)[0]
        df.to_csv(_path, index=False)
    else:
        df = pd.read_csv(_path)
    return df


if __name__ == '__main__':
    df = fetch_current_trading_stocks(exchange_names=['NASDAQ', 'NYSE'], refresh=True)
    print(df)
