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
    _sleep_seconds = 40
    _path = os.path.join(shared.PROJECT_DIR, 'artifacts', 'sp500_stocks.csv')
    sp500 = pd.read_csv(_path)
    sp500_tickers = sp500['Symbol'].tolist()
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


def _batch_generator(lst: List, batch_size: int):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


if __name__ == '__main__':
    download_sp500_key_metrics(period='annual', limit=1000)
