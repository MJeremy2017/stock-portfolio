import sys
import os

current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import pandas as pd
import numpy as np
from tqdm import tqdm
from abc import ABC
from datetime import datetime, timedelta
from collections import defaultdict
from src.general import download_sp500_ohlc

_PATH = "../artifacts/"

DATA_CUT_OFF = 1985
TRAIN_CUT_OFF = 2005
VAL_CUT_OFF = 2015
_TEST: pd.DataFrame
_DF_OHLC: pd.DataFrame


def make_data():
    """
    Preprocessing train, val and test set for model building.
    :return: Train set, Val set and OHLC price data of all SP500 stocks back to as early as traceable.
    """
    global _PATH, _TEST, _DF_OHLC
    df_stock = pd.DataFrame()
    for d in tqdm(os.listdir(_PATH)):
        sub_path = os.path.join(_PATH, d)
        if os.path.isdir(sub_path):
            sub = pd.read_csv(os.path.join(sub_path, 'quarter', 'key_metrics.csv'))
            df_stock = pd.concat([df_stock, sub])

    df_stock.loc[df_stock['symbol'].isnull(), 'symbol'] = df_stock.loc[df_stock['symbol'].isnull(), 'wsymbol']
    df_stock.drop(['wsymbol'], inplace=True, axis=1)
    print("Loading quarterly metrics done data shape", df_stock.shape)

    basic = pd.read_csv(os.path.join(_PATH, 'sp500_stocks.csv'))
    basic['Symbol'] = basic['Symbol'].str.replace('.', '-')
    print("Loading SP500 tickers done data shape", basic.shape)

    df_stock_all = df_stock.merge(
        basic[['Symbol', 'GICS Sector', 'GICS Sub-Industry']],
        left_on='symbol',
        right_on='Symbol',
        how='left'
    )

    df_stock_all.drop(['Symbol'], axis=1, inplace=True)
    df_stock_all['date'] = pd.to_datetime(df_stock_all['date'])

    train = df_stock_all[
        (df_stock_all['calendarYear'] >= DATA_CUT_OFF) & (df_stock_all['calendarYear'] < TRAIN_CUT_OFF)
        ]

    val = df_stock_all[
        (df_stock_all['calendarYear'] >= TRAIN_CUT_OFF) & (df_stock_all['calendarYear'] < VAL_CUT_OFF)
        ]

    _TEST = df_stock_all[
        (df_stock_all['calendarYear'] >= VAL_CUT_OFF)
    ]

    print('Train size', train.shape, 'Val size', val.shape, 'Test size', _TEST.shape)

    _path = os.path.join(_PATH, "sp500_ohlc.csv")
    if os.path.exists(_path):
        df_ohlc = pd.read_csv(_path)
    else:
        print("Downloading sp500 OHLC")
        df_ohlc = download_sp500_ohlc(period='max', save_file='sp500_ohlc.csv')
    df_ohlc['Date'] = pd.to_datetime(df_ohlc['Date'])
    print("sp500 OHLC downloaded", df_ohlc.shape)
    _DF_OHLC = df_ohlc
    return train, val, df_ohlc


class Model(ABC):
    def preprocess(self, data: pd.DataFrame):
        """
        Put data preprocessing and feature engineering here. The input data should have the same format
        of the val set from the `make_data()` function. This function will be called during evaluation.
        :param data: data frame of the same format as val set.
        :return: preprocessed data.
        """
        raise NotImplementedError("preprocess not implemented")

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Return a data frame with sorted scores of stocks, the stocks at the top K will be picked.
        Note: `symbol` column must be preserved for evaluation.
        """
        raise NotImplementedError("predict not implemented")


class Evaluator:
    _top_k = 30

    def __init__(self, model: Model):
        self.data = None
        self.ohlc = None
        self.model = model

    def evaluate(self, data: pd.DataFrame = None):
        if data is not None:
            self.data = data
            print("Evaluate on user specified data set", self.data.shape)
        else:
            if _TEST is None:
                raise ValueError("Test data is not initialized, run make_data() before evaluation")
            self.data = _TEST
            print("Evaluate on test data set", self.data.shape)

        self.ohlc = _DF_OHLC[_DF_OHLC['Date'] >= self.data['date'].min()][['Date', 'Ticker', 'Close']]

        years = range(self.data['calendarYear'].min(), self.data['calendarYear'].max() - 1)
        quarter = ["Q1"]
        eval_res = dict()
        for year in years:
            for q in quarter:
                cond_ = (self.data['calendarYear'] == year) & (self.data['period'] == q)
                sub_ = self.data[cond_]
                feat_ = self.model.preprocess(sub_)
                top_stocks = self.model.predict(feat_)[:self._top_k]['symbol'].to_list()
                print("Picked stocks", top_stocks)

                cond_ = cond_ & (self.data['symbol'].isin(top_stocks))
                sub_ = self.data[cond_]
                sub_ = self._find_first_monday_after_thirty_days(sub_)
                sub_ohlc_ = self._enrich_with_close_price(sub_)

                # evaluate price change after 1 year
                cond_ = (self.data['calendarYear'] == year + 1) & (self.data['period'] == q) & (
                    self.data['symbol'].isin(top_stocks))
                sub_1yr_ = self.data[cond_]
                sub_1yr_ = self._find_first_monday_after_thirty_days(sub_1yr_)
                sub_1yr_ohlc_ = self._enrich_with_close_price(sub_1yr_)

                sub_c_ = sub_ohlc_.merge(
                    sub_1yr_ohlc_,
                    on='symbol',
                    how='inner',
                    suffixes=('', '_1year')
                )
                sub_c_['inc_pct_1y'] = sub_c_.eval('(Close_1year-Close)/Close')
                eval_res['-'.join([str(year), q, '1y'])] = sub_c_

                # evaluate price change after 2 years
                cond_ = (self.data['calendarYear'] == year + 2) & (self.data['period'] == q) & (
                    self.data['symbol'].isin(top_stocks))
                sub_2yr_ = self.data[cond_]
                sub_2yr_ = self._find_first_monday_after_thirty_days(sub_2yr_)
                sub_2yr_ohlc_ = self._enrich_with_close_price(sub_2yr_)
                sub_c_ = sub_ohlc_.merge(
                    sub_2yr_ohlc_,
                    on='symbol',
                    how='inner',
                    suffixes=('', '_2year')
                )
                sub_c_['inc_pct_2y'] = sub_c_.eval('(Close_2year-Close)/Close')
                eval_res['-'.join([str(year), q, '2y'])] = sub_c_
                print(f'Done evaluation {str(year)}-{q} ###############')

        aggregated_res = defaultdict(list)
        indexes = []
        for year in years:
            for q in quarter:
                indexes.append(f"{str(year)}-{q}")
                for suf in ['1y', '2y']:
                    key = '-'.join([str(year), q, suf])
                    sub_ = eval_res[key]
                    v = sub_[f'inc_pct_{suf}'].values

                    aggregated_res[f'{suf}_mean'].append(np.mean(v))
                    aggregated_res[f'{suf}_std'].append(np.std(v))

        res_df = pd.DataFrame(aggregated_res, index=indexes)
        overall_agg = {
            '1_year_avg': res_df['1y_mean'].mean(),
            '1_year_std': res_df['1y_mean'].std(),
            '2_year_avg': res_df['2y_mean'].mean(),
            '2_year_std': res_df['2y_mean'].std(),
        }
        return overall_agg, res_df

    def calculate_spy_annual_return(self):
        years = range(self.data['calendarYear'].min(), self.data['calendarYear'].max() - 1)
        sub_ = self.ohlc[self.ohlc['Ticker'] == 'SPY']
        sub_.sort_values(by='Date', inplace=True)
        ret = []
        for year in years:
            yr_sub_ = sub_[sub_['Date'].dt.year == year]
            start = yr_sub_.iloc[0]['Close']
            end = yr_sub_.iloc[-1]['Close']
            ret.append((end - start) / start)
        res = pd.DataFrame({'year': years, 'return': ret})
        return res, {'average': res['return'].mean(), 'std': res['return'].std()}

    def _find_first_monday_after_thirty_days(self, data):
        data['date_plus_30'] = data['date'] + pd.Timedelta(days=30)
        data['first_monday'] = data['date_plus_30'].apply(lambda x: find_next_monday(x))
        return data

    def _enrich_with_close_price(self, data):
        return data.merge(
            self.ohlc,
            left_on=['symbol', 'first_monday'],
            right_on=['Ticker', 'Date'],
            how='inner')[['symbol', 'Close']]


def find_next_monday(date: pd.Timestamp):
    # 0 is Monday
    while date.weekday() != 0:
        date += timedelta(days=1)

    return date
