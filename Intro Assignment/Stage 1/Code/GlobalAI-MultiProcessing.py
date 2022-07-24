import multiprocessing
from multiprocessing import Process
from time import sleep
import pandas as pd
import yfinance as yf
import datetime as datetime
import os

path = "/Users/caichengyun/Documents/User/Documents/Master/Intern/Global AI/Projects/Intro Assignment/Stage 1/Code/fiveStock.csv"

df = pd.read_csv(path)
df_des = df.copy()

tickers = ['SPY', 'GOOG', 'AMZN', 'AAPL', 'TSLA']
stats = ['Returns', 'Std Dev', 'Momentum', 'Differences']

res_df = pd.DataFrame()

def f(x, queue):
    res_df = queue.get()
    
    for i in range(len(tickers)):
        if x == 'Returns':
            pct = df.iloc[:, i+1].pct_change()
            res_df[df.columns[i+1] + x] = pct

        elif x == 'Std Dev':
            std = df.iloc[:, i+1].rolling(14).std()
            res_df[df.columns[i+1] + x] = std

        elif x == 'Momentum':
            mom = df.iloc[:, i+1] - df.iloc[:, i+1].shift(10)
            res_df[df.columns[i+1] + x] = mom

        elif x == 'Differences':
            dif = df.iloc[:, i+1].diff()
            res_df[df.columns[i+1] + x] = dif

    queue.put(res_df)
    return df_des

if __name__ == '__main__':
    for i in range(len(stats)):
        queue = multiprocessing.Queue()
        queue.put(res_df)
        p = Process(target=f, args=(stats[i], queue,))
        p.start()
        p.join()
        df_des = pd.concat([df_des, queue.get()], axis=1)


print(df_des)
df_des.to_csv('Stock_Arrg.csv')


