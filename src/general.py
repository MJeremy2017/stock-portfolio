import os
import pandas as pd
import shared
from fetch_data import DataDownloader

downloader = DataDownloader()


def download_sp500_key_metrics(period: str, limit: int):
    _path = os.path.join(shared.PROJECT_DIR, 'artifacts', 'sp500_stocks.csv')
    sp500 = pd.read_csv(_path)
    sp500_tickers = sp500['Symbol'].tolist()
    downloader.batch_fetch_ticker_key_metrics(
        sp500_tickers,
        period=period,
        limit=limit
    )


if __name__ == '__main__':
    download_sp500_key_metrics(period='annual', limit=1000)
