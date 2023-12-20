import os
import time
import pandas as pd
import shared
from fetch_data import DataDownloader
from typing import List
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)

_downloader = DataDownloader()


def download_sp500_key_metrics(period: str, limit: int, batch_size: int = 10):
    _sleep_seconds = 30
    sp500_tickers = _load_sp500_tickers()
    cnt = 0
    batch_cnt = len(sp500_tickers) // batch_size + (1 if len(sp500_tickers) % batch_size else 0)
    for tickers in tqdm(_batch_generator(sp500_tickers, batch_size), total=batch_cnt):
        _downloader.batch_fetch_ticker_key_metrics(
            tickers,
            period=period,
            limit=limit
        )
        cnt += len(tickers)
        if cnt % 250 == 0:
            print(f"Sleep {_sleep_seconds}s waiting for rate limit ...")
            time.sleep(_sleep_seconds)


def download_sp500_ohlc(period: str = None, start_date: str = None, end_date: str = None, save_file: str = None):
    sp500_tickers = _load_sp500_tickers()
    df = _downloader.batch_fetch_tickers_ohlc(
        tickers=sp500_tickers,
        period=period,
        start_date=start_date,
        end_date=end_date)
    if save_file:
        _save_path = os.path.join(shared.PROJECT_DIR, 'artifacts', save_file)
        df.to_csv(_save_path, index=False)
        print(f"Data saved to {_save_path}")
    return df


def _batch_generator(lst: List, batch_size: int):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def _load_sp500_tickers() -> List:
    _path = os.path.join(shared.PROJECT_DIR, 'artifacts', 'sp500_stocks.csv')
    sp500 = pd.read_csv(_path)
    return sp500['Symbol'].tolist()


if __name__ == '__main__':
    # download_sp500_key_metrics(period='annual', limit=1000)
    data = download_sp500_ohlc(period='max', save_file='sp500_ohlc.csv')
    print(data.head())
