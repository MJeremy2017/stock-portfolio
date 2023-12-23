# Identify Undervalues Stocks

This competition aims to identify undervalued stocks and evaluate their investment return in 1-2 year time.

## Data

To get the training data, start a new notebook and use the `make_data` function in the `utils.py` file. 
This returns `train`, and `val` set. Note that `test` set will also be created along the way it is hidden 
from the contestants and is used for final evaluation only.

Along the way, `df_ohlc` which contains all the prices of all `S&P500` stocks will also be returned for your training,
however contestants are optional to use this data.

```
from utils import make_data

train, val, df_ohlc = make_data()
```

### Period

- **train**: From year `1985 ~ 2005`
- **val**: From year `2005 ~ 2015`
- **test**: From year `2015 ~ 2023`

### Columns
All data sets contain all tickers in the current `S&P500` following the same format with the following columns:

1. **symbol**: The stock ticker symbol representing the company.
2. **date**: The date on which the data was recorded.
3. **calendarYear**: The year the financial data corresponds to.
4. **period**: The financial period (e.g., Q1, Q2, Q3, Q4, FY for fiscal year).
5. **revenuePerShare**: Total revenue divided by the number of outstanding shares.
6. **netIncomePerShare**: Net income (profits) divided by the number of outstanding shares.
7. **operatingCashFlowPerShare**: Cash flow from operations divided by the number of outstanding shares.
8. **freeCashFlowPerShare**: Free cash flow (operating cash flow minus capital expenditures) per share.
9. **cashPerShare**: Total cash available divided by the number of outstanding shares.
10. **bookValuePerShare**: Company's total assets minus liabilities and intangible assets, divided by the number of outstanding shares.
11. **tangibleBookValuePerShare**: Book value minus intangible assets and goodwill, divided by the number of shares.
12. **shareholdersEquityPerShare**: Total equity divided by the number of outstanding shares.
13. **interestDebtPerShare**: Total interest-bearing debt divided by the number of outstanding shares.
14. **marketCap**: The total market value of the company's outstanding shares.
15. **enterpriseValue**: Company's total value, including debt and excluding cash.
16. **peRatio**: Price-to-Earnings ratio, the ratio of the company's stock price to its earnings per share.
17. **priceToSalesRatio**: The ratio of the company's stock price to its revenue per share.
18. **pocfratio**: Price to Operating Cash Flow ratio.
19. **pfcfRatio**: Price to Free Cash Flow ratio.
20. **pbRatio**: Price-to-Book ratio, the ratio of market price to book value per share.
21. **ptbRatio**: Price-to-Tangible Book ratio, similar to P/B but uses tangible book value.
22. **evToSales**: Enterprise Value to Sales ratio.
23. **enterpriseValueOverEBITDA**: Enterprise value divided by Earnings Before Interest, Taxes, Depreciation, and Amortization.
24. **evToOperatingCashFlow**: Enterprise Value to Operating Cash Flow ratio.
25. **evToFreeCashFlow**: Enterprise Value to Free Cash Flow ratio.
26. **earningsYield**: Earnings per share divided by the stock price.
27. **freeCashFlowYield**: Free Cash Flow per share divided by the stock price.
28. **debtToEquity**: Total debt divided by total shareholders' equity.
29. **debtToAssets**: Total debt divided by total assets.
30. **netDebtToEBITDA**: Net debt divided by EBITDA.
31. **currentRatio**: Current assets divided by current liabilities.
32. **interestCoverage**: Earnings before interest and taxes (EBIT) divided by interest expense.
33. **incomeQuality**: A measure of the proportion of income coming from core business operations.
34. **dividendYield**: Annual dividends per share divided by the stock price.
35. **payoutRatio**: The proportion of earnings paid out as dividends.
36. **salesGeneralAndAdministrativeToRevenue**: SG&A expenses divided by total revenue.
37. **researchAndDdevelopementToRevenue**: R&D expenses divided by total revenue.
38. **intangiblesToTotalAssets**: Intangible assets divided by total assets.
39. **capexToOperatingCashFlow**: Capital expenditures divided by operating cash flow.
40. **capexToRevenue**: Capital expenditures divided by revenue.
41. **capexToDepreciation**: Capital expenditures divided by depreciation expenses.
42. **stockBasedCompensationToRevenue**: Stock-based compensation divided by revenue.
43. **grahamNumber**: A figure that measures a stock's fundamental value calculated using earnings per share and book value.
44. **roic**: Return on Invested Capital.
45. **returnOnTangibleAssets**: Net income divided by tangible assets.
46. **grahamNetNet**: A value investing formula that compares stock price to net current asset value.
47. **workingCapital**: Current assets minus current liabilities.
48. **tangibleAssetValue**: The total value of physical, non-abstract assets.
49. **netCurrentAssetValue**: Current assets minus current liabilities and long-term debt.
50. **investedCapital**: Total capital invested by shareholders and debt holders.
51. **averageReceivables**: Average accounts receivable over a period.
52. **averagePayables**: Average accounts payable over a period.
53. **averageInventory**: Average value of inventory over a period.
54. **daysSalesOutstanding**: Average number of days to collect payment after a sale.
55. **daysPayablesOutstanding**: Average number of days a company takes to pay its invoices.
56. **daysOfInventoryOnHand**: Average number of days a company holds inventory before selling it.
57. **receivablesTurnover**: Sales divided by average accounts receivable.
58. **payablesTurnover**: Cost of goods sold divided by average accounts payable.
59. **inventoryTurnover**: Cost of goods sold divided by average inventory.
60. **roe**: Return on Equity, net income divided by shareholders' equity.
61. **capexPerShare**: Capital expenditures divided by the number of outstanding shares.
62. **GICS Sector**: Global Industry Classification Standard sector classification.
63. **GICS Sub-Industry**: Global Industry Classification Standard sub-industry classification.


## Evaluation

Your task is to build a model to **RANK the TOP 30 stocks** given the data above **at each year with Q1 data**. 
Your result is evaluated by the average return in 1-year and 2-year period as well as the standard deviation over the
evaluation period.

To evaluate your model, your model must 

1. Implement the `Model` interface in the `utils.py`.
2. Use the `Evaluator` in the `utils.py`.

A quick example

```
from utils import Evaluator, Model

class MM(Model):
    def preprocess(self, data):
        """
        Put feature engineering here, the data set shares the same format as `val` from `make_data()`. 
        """
        return data
    
    def predict(self, data):
        """
        The returned data frame must contain a column `symbol` with sorted stocks. Only the top 30 stocks will
        be picked in the evaluation. 
        """
        return pd.DataFrame({'symbol': ['AAPL', 'AAL']})


model = MM()
e = Evaluator(model)
metric, bd_yr = e.evaluate()

print(metric, bd_yr)
```

A more formal example please refer to the [heuristic-example.ipynb](./heuristic-example.ipynb).

### Important Note

1. During the evaluation, each stock's Q1 data per year will be fed to your model, and the buy-in time is taken on the
first Monday and 30 days after the `date` of the report. The rationale is that if a Q1 financial report has a
`date = {year}-03-31`, the
result is normally released on 30 days after that `date`. Taking the first Monday after that is the first date that the stock
can be trade.