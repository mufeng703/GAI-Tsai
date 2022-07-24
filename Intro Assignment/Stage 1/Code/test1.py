import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from distutils.log import debug
from matplotlib.pyplot import title 
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
import multiprocessing
from multiprocessing import Process
from time import sleep
import yfinance as yf
import datetime as datetime
import os


# Get 5 stock data
tickers = ['SPY', 'GOOG', 'AMZN', 'AAPL', 'TSLA']
start = '2017-01-01'
df = yf.download(tickers, start)['Adj Close']

# calculate features

stats = ['Returns', 'Std Dev', 'Momentum', 'Differences']
df_des = df.copy()

def add_des(x):
    res_df = pd.DataFrame()
    for i in range(len(tickers)):
        if x == 'Returns':
            pct = df.iloc[:, i].pct_change()
            res_df[df.columns[i] + x] = pct

        elif x == 'Std Dev':
            std = df.iloc[:, i].rolling(14).std()
            res_df[df.columns[i] + x] = std

        elif x == 'Momentum':
            mom = df.iloc[:, i] - df.iloc[:, i].shift(10)
            res_df[df.columns[i] + x] = mom

        elif x == 'Differences':
            dif = df.iloc[:, i].diff()
            res_df[df.columns[i] + x] = dif

    return res_df

for i in range(len(stats)):
    rest = add_des(stats[i])
    df_des = pd.concat([df_des, rest], axis=1)

df_des = df_des.reset_index(level=0)

# Dash

app = dash.Dash()
server = app.server

tickers = ['SPY', 'AMZN', 'AAPL', 'TSLA', 'GOOG']
stats = ['Daily Returns', 'Std Dev', 'Momentum', 'Differences']
#path = "./Stock_Arrg.csv"
#df_res = pd.read_csv(path, index_col=0)
features = df_des.iloc[:, 1:6].columns


app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='company',
                options=[{'label': i, 'value': i} for i in features], 
                value='SPY'
                )],
                style={'width': '40%', 'display': 'inline-block'}),
        #html.Br(),
    ]),  # style={'padding': 1}

    html.Div([
        html.Div([
            dcc.Graph(id='speedometer-graphic'),
            dcc.Graph(id='hist-graphic'),
            dcc.Graph(id='scatter-graphic'),
        ], style={'float': 'left', 'width': '25 %'}),

        html.Div([
            dcc.Graph(id='line-graphic'),
            dcc.Graph(id='table-graphic'),
            dcc.Graph(id='bar-graphic'),
        ], style={'float': 'left', 'width': '50 %'}),

        html.Div([
            dcc.Graph(id='heat-graphic'),
            dcc.Graph(id='polar-graphic'),
        ], style={'float': 'left', 'width': '25 %'}),
    ], style={'height': '100 %', 'width': '100 %', 'overflow': 'hidden'})
])


@app.callback([Output('line-graphic', 'figure'), Output('scatter-graphic', 'figure'), 
               Output('hist-graphic', 'figure'), Output('speedometer-graphic', 'figure'),
               Output('bar-graphic', 'figure'), Output('heat-graphic', 'figure'),
               Output('table-graphic', 'figure'), Output('polar-graphic', 'figure')],
              [Input('company', 'value')])  # ,Input('yaxis', 'value')

def update_graph(name):
    df = df_des
    lineC = px.line(df, x="Date", y=name, title='Time Series Line Chart')
    scat = px.scatter(df, x="Date", y=name+'Returns',
                      title='Returns Scatter')
    histC = px.histogram(df[name+'Differences'],
                         title='Differences Histogram')
    

    # speedometer
    lastP = df[name].iloc[-1]
    speedometer = go.Figure(go.Indicator(
        mode="gauge+number", value=lastP,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Last Price"}))
    
    # horizontal bar chart
    stat = [df[name].mean(), df[name].std()]
    bar = go.Figure(go.Bar(
        x=stat, y=['Mean', 'Std Dev'], orientation='h'))
    
    bar.update_layout(title_text='Price Statistics')

    # heatmap
    corr = df.iloc[:, 0:5].corr().round(3)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    df_mask = corr.mask(mask)

    heat = ff.create_annotated_heatmap(z=df_mask.to_numpy(),
                                      x=df_mask.columns.tolist(),
                                      y=df_mask.columns.tolist(),
                                      colorscale=px.colors.diverging.RdBu,
                                      hoverinfo="none",  # Shows hoverinfo for null values
                                      showscale=True, ygap=1, xgap=1
                                      )

    heat.update_xaxes(side="bottom")

    heat.update_layout(
        title_text='Price Correlation Heatmap',
        #title_x=0.5,
        #width=1000,
        #height=1000,
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_zeroline=False,
        yaxis_zeroline=False,
        yaxis_autorange='reversed',
        #template='plotly_white'
    )

    # NaN values are not handled automatically and are displayed in the figure
    # So we need to get rid of the text manually
    for i in range(len(heat.layout.annotations)):
         if heat.layout.annotations[i].text == 'nan':
            heat.layout.annotations[i].text = ""
    
    # table
    stat = df[name+'Returns'].describe()

    tableC = go.Figure(data=[go.Table(header=dict(values=['Statistics', 'Value']),
                               cells=dict(values=[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'], stat]))
                      ])

    tableC.update_layout(title_text='Returns Statistics Table')

    # polar
    maxV = []

    for stock in tickers:
        buf = df[stock+'Returns'].max()
        maxV.append(buf)

    df2 = pd.DataFrame(dict(r=maxV, theta=tickers))

    polarC = px.line_polar(df2, r='r', theta='theta', line_close=True, title='Max Returns Polar')
    polarC.update_traces(fill='toself')

    return lineC, scat, histC, speedometer, bar, heat, tableC, polarC


if __name__ == '__main__':
    app.run_server()