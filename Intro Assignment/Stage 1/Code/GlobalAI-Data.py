from multiprocessing import Process
import dns
import pymongo
import pandas as pd
import yfinance as yf
import datetime as datetime
import os

# Get 5 stock data
tickers = ['SPY', 'GOOG', 'AMZN', 'AAPL', 'TSLA']
start = '2017-01-01'
end = '2021-12-31'
df = yf.download(tickers, start, end)['Adj Close']
df.to_csv('fiveStock.csv')

print(df)

# MongoDB, "The DNS query name does not exist"
'''
client = pymongo.MongoClient(
    "mongodb+srv://Newuser:GLOBALAI@cluster0-ujbuf.mongodb.net/test?retryWrites=true&w=majority")
db = client['GlobalAI']
print(db.list_collection_names())
'''

# descriptive statistics

print(df.describe())

