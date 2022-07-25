from ib_insync import *
import pandas as pd

path = "./LIst of 19.7 Stocks with FIGI if available - By Evelyn.xlsx"
df_stockList = pd.read_excel(path, index_col=0)
stocks = df_stockList['symbol_x'].unique()

df2 = pd.DataFrame(columns=["contract", "industry",
                   "longName", "marketName", "secIdList"])
df3 = pd.DataFrame(columns=["contract", "industry",
                   "longName", "marketName", "secIdList"])

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=99)
for i in stocks:
    contract = Stock(i)
    try:
        bars = ib.reqContractDetails(contract)
        df = pd.DataFrame(bars)
        cleandata = df[["contract", "industry",
                        "longName", "marketName", "secIdList"]]
        cleandata = cleandata.explode('secIdList')
        cleandata = cleandata.drop_duplicates(subset=["secIdList"])
        df2 = pd.concat([df2, cleandata])
    except:
        df2 = pd.concat([df2, df3])


df2.to_csv('unclean_ibdata_Abhir.csv')
