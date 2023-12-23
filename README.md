# Stock Portfolio Management


## Set up Local Environment

```
python3 -m virtualenv venv

source venv/bin/activate

pip install -r requirements.txt
```

## Git Large File Storage(LFS)

It is recommended to not save large files (e.g `*.csv`) on `Github`. In case it is required,
use LFS to track large files. [Reference](https://git-lfs.com/) 

```
brew install git-lfs

git lfs track "*.csv"
```

## Project Structure

```angular2html
|_ artifacts  # this is where all the stocks relevant data are saved.
|_ notebooks  # create a new notebook to run and evaluate your model here.
|_ src  # multi-data fetch that supports both async batch and single Ticker download.
```

## Data Source

The data in this repo contains is acquired from multiple sources:

1. **Wikipedia**: Mainly used to srape high level data of S&P500 tickers.
2. **[FMP](site.financialmodelingprep.com/developer/docs#key-metrics-statement-analysis)**: Major API 
to download various financial metrics of global stocks.
3. **[yfinance](https://pypi.org/project/yfinance/)**: A python package to get ticker OHLC data.

All the data download is implemented in the [src](./src) folder.
