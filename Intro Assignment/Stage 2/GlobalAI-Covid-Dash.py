from distutils.log import debug
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from matplotlib.pyplot import title
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
import datetime
from scipy import stats

#pio.templates.default = "plotly_dark"
app = dash.Dash()
server = app.server


# load data
path = "./Data/SDG.csv"
df_sdg = pd.read_csv(path, index_col=0)
path = "./Data/Sentiment.csv"
df_sent = pd.read_csv(path, index_col=0)
path = "./Data/covid-timeline.xlsx"
df_time = pd.read_excel(path)
df_time['Date'] = df_time['Date'].apply(pd.to_datetime, errors='coerce')

path = "./Data/Rank_SDG.csv"
dfResult = pd.read_csv(path, index_col=0)
path = "./Data/Rank_Sentiment.csv"
dfResult_sent = pd.read_csv(path, index_col=0)

# get tickers and sectors
df = df_sent.copy()

tickers = df_sdg['Ticker'].unique()


app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='company',
                options=[{'label': i, 'value': i} for i in tickers],
                #value='SPY'
            )],
            style={'width': '40%', 'display': 'inline-block'}),
        #html.Br(),
    ]),  # style={'padding': 1}

    html.Div([
        html.Div([
            dcc.Graph(id='SDGC-graphic'),
            dcc.Graph(id='sentC-graphic'),
            dcc.Graph(id='rankSDG-graphic'),
        ], style={'float': 'left', 'width': '25 %'}),

        html.Div([
            dcc.Graph(id='tableAll-graphic'),
            dcc.Graph(id='tableOne-graphic'),
            dcc.Graph(id='rankSent-graphic'),
        ], style={'float': 'left', 'width': '25 %'}),

    ], style={'height': '100 %', 'width': '100 %', 'overflow': 'hidden'})
])


@ app.callback([Output('SDGC-graphic', 'figure'), Output('sentC-graphic', 'figure'), 
                Output('tableAll-graphic', 'figure'), Output('tableOne-graphic', 'figure'),
                Output('rankSDG-graphic', 'figure'), Output('rankSent-graphic', 'figure')],
                [Input('company', 'value')])  # ,Input('yaxis', 'value')
            
def update_graph(name):
    # SDG
    df_GOOGL = df_sdg.loc[df_sdg['Ticker'] == name].copy()
    df_GOOGL['Timestamp'] = df_GOOGL['Timestamp'].apply(pd.to_datetime, errors='coerce')
    df_GOOGL_late = df_GOOGL[df_GOOGL['Timestamp'] > '2019-12-12']

    SDGC = px.line(df_GOOGL_late, x="Timestamp",
                    y="SDG_Mean", title='SGD Score with Key Dates')
    mask = df_GOOGL_late["Timestamp"].isin(df_time["Date"].unique())

    df1 = df_GOOGL_late[mask].groupby((~mask).cumsum())['Timestamp'].agg(['first', 'last'])

    fillcolor = 'rgba(200,0,200,0.2)'
    layer = 'below'

    for index, row in df1.iterrows():
        #print(row['first'], row['last'])
        SDGC.add_shape(type="rect",
        xref="x",
        yref="paper",
        x0=row['first'],
        y0=0,
        x1=row['last'] + datetime.timedelta(days=1),
        y1=1,
        line=dict(color="rgba(0,0,0,0)", width=3,),
        fillcolor=fillcolor,
        layer=layer)

    SDGC.update_layout()

    # Sentiment
    df_sent_score = df_sent.loc[df_sent['Ticker'] == name].copy()
    df_sent_score['Timestamp'] = df_sent_score['Timestamp'].apply(pd.to_datetime, errors='coerce')
    df_sent_score_short = df_sent_score[df_sent_score['Timestamp'] > '2019-12-12']

    sentC = px.line(df_sent_score_short, x="Timestamp", y="Sentiment", title='Sentiment Score with Key Dates')
    mask = df_sent_score_short["Timestamp"].isin(df_time["Date"].unique())

    df1 = df_sent_score_short[mask].groupby((~mask).cumsum())['Timestamp'].agg(['first', 'last'])

    fillcolor = 'rgba(200,0,200,0.2)'
    layer = 'below'

    for index, row in df1.iterrows():
        sentC.add_shape(type="rect",
        xref="x",
        yref="paper",
        x0=row['first'],
        y0=0,
        x1=row['last'] + datetime.timedelta(days=1),
        y1=1,
        line=dict(color="rgba(0,0,0,0)", width=3,),
        fillcolor=fillcolor,
        layer=layer)
    
    sentC.update_layout()

    # table all
    df_sent_score['diff'] = df_sent_score['Sentiment'].diff()
    stat = df_sent_score['diff'].describe()

    tableAll = go.Figure(data=[go.Table(header=dict(values=['Statistics', 'Value']),
                                      cells=dict(values=[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'], stat]))
                             ])

    tableAll.update_layout(
        title_text='All Days Differences Statistics (Sentiment)')

    # table key date
    mask = df_sent_score["Timestamp"].isin(df_time["Date"].unique())
    stat = df_sent_score[mask]['diff'].describe()

    tableOne = go.Figure(data=[go.Table(header=dict(values=['Statistics', 'Value']),
                                      cells=dict(values=[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'], stat]))
                             ])

    tableOne.update_layout(title_text='Key Days Differences Statistics (Sentiment)')

    # rank SDG
    df = dfResult.head(10).copy()


    rankSDG = go.Figure(data=[go.Table(header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='left'),
        cells=dict(values=df.transpose().values.tolist(),
        fill_color='lavender',
        align='left'))
    ])

    rankSDG.update_layout(
        title_text='SDG Rank')
    
    # rank Sentiment
    df = dfResult_sent.head(10).copy()

    rankSent = go.Figure(data=[go.Table(header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='left'),
        cells=dict(values=df.transpose().values.tolist(),
                   fill_color='lavender',
                   align='left'))
    ])

    rankSent.update_layout(
        title_text='Sentiment Rank')

    return [go.Figure(data=SDGC), go.Figure(data=sentC), tableAll, tableOne, rankSDG, rankSent]

if __name__ == '__main__':
    app.run_server()
