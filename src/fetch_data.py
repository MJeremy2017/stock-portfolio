import os.path
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# TODO: get PE of ticker by date
class DataDownloader(object):
    def __init__(self):
        self.API_KEY = os.getenv('API_KEY')

    def fetch_tickers_global(self, exchange_names: list, refresh=False):
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
            if self.API_KEY is None:
                raise ValueError("API KEY is not provided, `source .dev_env` before running")
            url = self._add_api_key("https://financialmodelingprep.com/api/v3/stock/list?")
            resp = requests.get(url)
            resp_json = resp.json()
            df = pd.DataFrame(resp_json)
            df.to_csv(_path, index=False)
        else:
            df = pd.read_csv(_path)
        df = df[df['exchangeShortName'].isin(exchange_names)]
        return df

    def fetch_ticker_key_metrics(self, ticker: str, period: str, limit: int, refresh=False):
        """
        Fetch P/B, P/E, ROE and other key metrics of a given ticker
        :param ticker: e.g. AAPL
        :param period: annual or quarter
        :param limit: number of entries to fetch
        :param refresh: refresh artifacts data
        :return:
        """
        _path = os.path.join(PROJECT_DIR, 'artifacts', ticker.lower(), period, 'key_metrics.csv')
        dirname = os.path.dirname(_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        df = None
        if refresh:
            ticker = ticker.upper()
            url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?period={period}&limit={limit}&"
            url = self._add_api_key(url)
            response = requests.get(url)
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                df.to_csv(_path, index=False)
        else:
            df = pd.read_csv(_path)
        return df

    def _add_api_key(self, url: str) -> str:
        return url + f"apikey={self.API_KEY}"


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


def fetch_sp500_ticker_change_history(refresh=False):
    """
    Scrape from wiki the change history of sp500 tickers
    Between January 1, 1963, and December 31, 2014, 1,186 index components were replaced by other components.
    :param refresh: refresh data and save to local
    :return: dataframe
    """
    _path = os.path.join(PROJECT_DIR, 'artifacts/sp500_stocks_change_history.csv')
    if refresh:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        df = pd.read_html(response.text)[1]
        df.to_csv(_path, index=False)
    else:
        df = pd.read_csv(_path)
    return df


if __name__ == '__main__':
    ticker = 'AAPL'
    loader = DataDownloader()
    data = loader.fetch_ticker_key_metrics(
        ticker='AAPL',
        period='annual',
        limit=1000,
        refresh=True
    )
    print(data)

