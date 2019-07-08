from datetime import datetime as dt
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from collections import deque
import pyodbc
import pandas as pd
import plotly
import plotly.graph_objs as go

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(
        children='Database Dashboard',
        style={
            'textAlign':'center'
        }
    ),

    html.H5(
        children='Report Date'
    ),

    dcc.DatePickerSingle(
        id='report-date',
        min_date_allowed = dt(2019,7,7),
        max_date_allowed = dt(2030,12,31),
        initial_visible_month=dt.now(),
        date=str(dt.now())
    ),

    # html.H5(
    #     children='File Type'
    # )

    # dcc.Dropdown(
    #     id='drd-filetype',
    #     options=[
    #         {'label':'Data File','value':'ROWS'},
    #         {'label':'Log File','value':'LOG'}
    #     ],
    #     value='ROWS'
    # ),

    dcc.Graph(
        id='databasesize',
        animate=True
    )
])

@app.callback(
    Output(component_id='databasesize',component_property='figure'),
    [Input(component_id='report-date', component_property='date')
    # ,Input(component_id='drd-filetype',component_property='value')
    ]
)
def update_chart(date):
    try:
        conn_str = (
                r"Driver={SQL Server Native Client 11.0};"
                r"Server=DICTRANTHO1;"
                r"Database=DBA_Management;"
                r"Trusted_Connection=yes;"
                )
        conn = pyodbc.connect(conn_str)
        log = 'LOG'
        rows = 'ROWS'
        dfRows = pd.read_sql("EXEC dbo.ReportDatabaseFileSizes ? , ?",conn,params=(date,rows))
        XRows = dfRows['DatabaseName']
        YRows = dfRows['FileSizeInMbs']
        dfLog = pd.read_sql("EXEC dbo.ReportDatabaseFileSizes ? , ?",conn,params=(date,log))
        XLog = dfLog['DatabaseName']
        YLog = dfLog['FileSizeInMbs']

        return {
            'data':[
                go.Bar(
                    x=list(XRows),
                    y=list(YRows),
                    name='Data File'
                    ),
                go.Bar(
                    x=list(XLog),
                    y=list(YLog),
                    name='Log File'
                ) 
            ],
            'layout':go.Layout(
                xaxis=go.layout.XAxis(
                    title=go.layout.xaxis.Title(
                        text='Database',
                        font=dict(
                            family='Courier New, monospace',
                            size=18,
                            color='#7f7f7f'
                        )
                    )
                ),
                yaxis=go.layout.YAxis(
                    title=go.layout.yaxis.Title(
                        text='File Size (Mbs)',
                        font=dict(
                            family='Courier New, monospace',
                            size=18,
                            color='#7f7f7f'
                        )
                    )
                ),
                title='Database File Size Statistic.',
                barmode='group'
            )
        }
        
      
    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(debug=True)