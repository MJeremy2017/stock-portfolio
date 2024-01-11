import logging
import os.path
import threading
import yfinance as yf
import requests
from typing import List, Callable
import pandas as pd
from threading import Lock, Event
import multitasking
from src import shared


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
        _path = os.path.join(shared.PROJECT_DIR, 'artifacts/stocks_global.csv')
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

    def fetch_key_metrics(self, ticker: str, period: str, limit: int, refresh=False):
        """
        Fetch P/B, P/E, ROE and other key metrics of a given ticker. Result will be stored as
        a csv data frame under artifacts/{ticker}/key_metrics.csv
        :param ticker: e.g. AAPL
        :param period: annual or quarter
        :param limit: number of entries to fetch
        :param refresh: refresh artifacts data
        :return:
        """
        _api_path = "key-metrics"
        _path = os.path.join(shared.PROJECT_DIR, 'artifacts', ticker.lower(), period, 'key_metrics.csv')
        _check_or_create_directory(_path)
        if refresh:
            df = self._fetch_data_from_api(_api_path, ticker, period, limit)
            df.to_csv(_path, index=False)
            logging.info(f"Successfully fetched key metrics for {ticker}")
        else:
            df = pd.read_csv(_path)
        return df

    def fetch_income_statement(self, ticker: str, period: str, limit: int, refresh=False):
        """
        Reference to: https://site.financialmodelingprep.com/developer/docs#income-statements-financial-statements
        :param ticker: e.g. AAPL
        :param period: annual or quarter
        :param limit: number of entries to fetch
        :param refresh: refresh artifacts data
        :return:
        """
        _api_path = "income-statement"
        _path = os.path.join(shared.PROJECT_DIR, 'artifacts', ticker.lower(), period, 'income_statement.csv')
        _check_or_create_directory(_path)
        if refresh:
            df = self._fetch_data_from_api(_api_path, ticker, period, limit)
            df.to_csv(_path, index=False)
            logging.info(f"Successfully fetched income statement for {ticker}")
        else:
            df = pd.read_csv(_path)
        return df

    def fetch_balance_sheet_statement(self, ticker: str, period: str, limit: int, refresh=False):
        """
        Reference to: https://site.financialmodelingprep.com/developer/docs#balance-sheet-statements-financial-statements
        :param ticker: e.g. AAPL
        :param period: annual or quarter
        :param limit: number of entries to fetch
        :param refresh: refresh artifacts data
        :return:
        """
        _api_path = "balance-sheet-statement"
        _path = os.path.join(shared.PROJECT_DIR, 'artifacts', ticker.lower(), period, 'balance_sheet_statement.csv')
        _check_or_create_directory(_path)
        if refresh:
            df = self._fetch_data_from_api(_api_path, ticker, period, limit)
            df.to_csv(_path, index=False)
            logging.info(f"Successfully fetched balance sheet statement for {ticker}")
        else:
            df = pd.read_csv(_path)
        return df

    def fetch_cashflow_statement(self, ticker: str, period: str, limit: int, refresh=False):
        """
        Reference to: https://site.financialmodelingprep.com/developer/docs#cashflow-statements-financial-statements
        :param ticker: e.g. AAPL
        :param period: annual or quarter
        :param limit: number of entries to fetch
        :param refresh: refresh artifacts data
        :return:
        """
        _api_path = "cash-flow-statement"
        _path = os.path.join(shared.PROJECT_DIR, 'artifacts', ticker.lower(), period, 'cash_flow_statement.csv')
        _check_or_create_directory(_path)
        if refresh:
            df = self._fetch_data_from_api(_api_path, ticker, period, limit)
            df.to_csv(_path, index=False)
            logging.info(f"Successfully fetched {_api_path} for {ticker}")
        else:
            df = pd.read_csv(_path)
        return df

    def fetch_ratios(self, ticker: str, period: str, limit: int, refresh=False):
        """
        Reference to: https://site.financialmodelingprep.com/developer/docs#ratios-statement-analysis
        :param ticker: e.g. AAPL
        :param period: annual or quarter
        :param limit: number of entries to fetch
        :param refresh: refresh artifacts data
        :return:
        """
        _api_path = "ratios"
        _path = os.path.join(shared.PROJECT_DIR, 'artifacts', ticker.lower(), period, 'ratios.csv')
        _check_or_create_directory(_path)
        if refresh:
            df = self._fetch_data_from_api(_api_path, ticker, period, limit)
            df.to_csv(_path, index=False)
            logging.info(f"Successfully fetched {_api_path} for {ticker}")
        else:
            df = pd.read_csv(_path)
        return df

    def batch_fetch(self,
                    func: Callable,
                    tickers: List[str],
                    period: str,
                    limit: int):
        """
        Async fetch ticker key metrics
        :param func: The functional API to call
        :param limit:
        :param period:
        :param tickers: List of tickers
        """
        lock = threading.Lock()
        event = threading.Event()
        done = []
        try:
            for i, ticker in enumerate(tickers):
                self._async_fetch(func, ticker, period, limit, lock, event, len(tickers), done)
            event.wait()
        except Exception as e:
            logging.error(f"Error fetching key metrics {e}\n Finished tickers are {done}")

    @multitasking.task
    def _async_fetch(self,
                     func: Callable,
                     ticker: str,
                     period: str,
                     limit: int,
                     lock: Lock,
                     event: Event,
                     total: int,
                     done: List):
        multitasking.set_max_threads(multitasking.cpu_count() * 2)
        try:
            func(ticker=ticker, period=period, limit=limit, refresh=True)
        except Exception as e:
            raise ValueError(f"Error downloading {ticker} {e}")
        finally:
            with lock:
                shared.CNT += 1
                done.append(ticker)
                if shared.CNT >= total:
                    event.set()
                    shared.CNT = 0

    def batch_fetch_tickers_ohlc(self,
                                 tickers: List[str],
                                 period: str = None,
                                 start_date: str = None,
                                 end_date: str = None) -> pd.DataFrame:
        """
        Fetch the open, high, low, and close price for a single ticker
        :param tickers: List of tickers
        :param period: str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        :param start_date: str in YYYY-DD-MM format
        :param end_date: str in YYYY-DD-MM format
        :return: a data frame
        """
        tickers = [self._standardize_ticker(t) for t in tickers]
        df = yf.download(tickers=tickers, period=period, start=start_date, end=end_date, group_by='ticker')

        return df.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index()

    def _add_api_key(self, url: str) -> str:
        return url + f"apikey={self.API_KEY}"

    def _standardize_ticker(self, ticker: str):
        return ticker.replace('.', '-').upper()

    def _fetch_data_from_api(self, path: str, ticker: str, period: str, limit: int):
        ticker = self._standardize_ticker(ticker)
        url = f"https://financialmodelingprep.com/api/v3/{path}/{ticker}?period={period}&limit={limit}&"
        url = self._add_api_key(url)
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise ValueError(response.status_code, response.json())


def fetch_sp500_tickers(refresh=False):
    """
    Scrape the current s&p500 stocks from wikipedia
    :param refresh: refresh data and save to local
    :return: dataframe of s&p500 stocks
    """
    _path = os.path.join(shared.PROJECT_DIR, 'artifacts/sp500_stocks.csv')
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
    _path = os.path.join(shared.PROJECT_DIR, 'artifacts/sp500_stocks_change_history.csv')
    if refresh:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        df = pd.read_html(response.text)[1]
        df.to_csv(_path, index=False)
    else:
        df = pd.read_csv(_path)
    return df


def _check_or_create_directory(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


if __name__ == '__main__':
    loader = DataDownloader()
    data = loader.fetch_ratios(
        ticker='tsla',
        period='annual',
        limit=1000,
        refresh=True
    )
    print(data)
