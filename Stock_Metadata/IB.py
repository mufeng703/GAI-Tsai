import numpy as np
import pandas as pd
from ib_insync import *
from ib_insync.contract import Contract
from bs4 import BeautifulSoup as bs

# stock list
path = "./LIst of 19.7 Stocks with FIGI if available - By Evelyn.xlsx"
df_stockList = pd.read_excel(path, index_col=0)

# IB
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=412)

# stock = Stock('AMD', 'SMART', 'USD')
isinList = []

for index, row in df_stockList.iterrows():
    try:
        stock = Stock(row['symbol_x'],  row['Exchange'], row['currency_y'])
#         stock = Stock(row['symbol_x'])
        fundamentals = ib.reqFundamentalData(stock, 'ReportSnapshot')

        content = bs(fundamentals, "xml")
        ISIN = content.find(Type='ISIN').getText()
        print(ISIN)
    except:
        ISIN = None

    isinList.append(ISIN)

df_stockList_IB = df_stockList[[
    'symbol_x', 'longName', 'Country', 'Exchange', 'currency_y', 'isin']].copy()
df_stockList_IB['ISIN'] = isinList


df_stockList_IB = df_stockList_IB.rename(columns={"symbol_x": "Ticker", "longName": "Name-IB", "Country": "Country-IB",
                                         "Exchange": "Exchange-IB", "currency_y": "Currency-IB", "ISIN": "ISIN-IB", "isin": "ISIN-19.7"})

df_stockList_IB.to_csv('ISIN_from_IB.csv', index=False)
