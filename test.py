import yfinance as yf


ticker_symbol = 'SPY'
stock_data = yf.Ticker(ticker_symbol)
info = stock_data.info
stock_data.history()

# Extract Apple's financial ratios
apple_pe_ratio = info.get('trailingPE', None)
apple_pb_ratio = info.get('priceToBook', None)
apple_roe = info.get('returnOnEquity', None)
apple_revenue_growth = info.get('revenueGrowth', None)
apple_debt_to_equity = info.get('debtToEquity', None)
sector = info.get('sectorKey')
industry = info.get('industryKey')

print(sector, industry)
