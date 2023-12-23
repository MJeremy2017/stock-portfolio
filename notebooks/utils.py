import pandas as pd
from tqdm import tqdm
import os

_PATH = "../artifacts/"

DATA_CUT_OFF = 1985
TRAIN_CUT_OFF = 2005
VAL_CUT_OFF = 2015


def make_data():
    global _PATH
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

    test = df_stock_all[
        (df_stock_all['calendarYear'] >= VAL_CUT_OFF)
    ]

    print('Train size', train.shape, 'Val size', val.shape, 'Test size', test.shape)

    return train, val, test
