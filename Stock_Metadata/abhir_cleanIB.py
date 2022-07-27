import pandas as pd

data = pd.read_csv("unclean_ibdata_Abhir.csv")

symbol = data.contract.str.split(expand=True)
symbol = symbol.iloc[:,[5]].squeeze()
symbol = symbol.str.replace("'","").str.replace(",","")
try_data = data.secIdList.str.split(expand=True)
try_data=try_data.rename(columns={1:"ISIN"})
try_data=try_data.ISIN.str.replace("value","")
try_data=try_data.str.replace("='","")
try_data=try_data.str.replace(")","")
try_data=try_data.str.replace("'","")
data["ISIN"]=try_data
data["Symbol"]=symbol
data.drop(["secIdList","contract","Unnamed: 0"],axis=1,inplace=True)

data=data.add_prefix('IB-')

data.to_csv('ibdata_Abhir.csv')