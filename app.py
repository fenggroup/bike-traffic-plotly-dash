'''
 # @ Create Time: 2022-07-15 14:22:01.941239
'''

import pathlib
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__, title="Bicycle Traffic Data")

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

def load_data(data_file: str) -> pd.DataFrame:
    '''
    Load data from /data directory
    '''
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()
    return pd.read_csv(DATA_PATH.joinpath(data_file))


df = load_data("./bike_data.csv")

# This block of code reads the data set into a pandas dataframe and formats it
#start

df.columns = ['Time', 'Eastbound', 'Westbound']

df['Both directions'] = df['Eastbound'] + df['Westbound']

df['Time'] = pd.to_datetime(df['Time'])
df['day_of_week'] = df['Time'].dt.day_name()

df = df.reindex(['Time', 'Both directions', 'Eastbound', 'Westbound'], axis="columns")
#end

# This block of code sets a variable for the minimum and maximum date that can be selected in the date picker
# start
min_date_allowed = df['Time'].dt.date.unique().min()

max_date_allowed = df['Time'].dt.date.unique().max()
# end

# This block of code aggregates the data so the user can choice the resolution of the data
# start
df_15m = df.resample('15T', on='Time', axis=0).sum().reset_index()
df_15m['day_of_week'] = df_15m['Time'].dt.day_name()

df_30m = df.resample('30T', on='Time', axis=0).sum().reset_index()
df_30m['day_of_week'] = df_30m['Time'].dt.day_name()
    
df_1h = df.resample('1H', on='Time', axis=0).sum().reset_index()
df_1h['day_of_week'] = df_1h['Time'].dt.day_name()

df_daily = df.resample('D', on='Time', axis=0).sum().reset_index()
df_daily['day_of_week'] = df_daily['Time'].dt.day_name()
# end

# This block of code sets up a preliminary dataframe for the data table
# start
data_table = np.zeros((3,3))

table = pd.DataFrame(data_table, columns = ['','Total volume','Average daily volume'])
# end

app.layout = html.Div([
    
    html.Div(children=[
    html.H1(children='Bicycle Traffic Data', style={'textAlign': 'center'}), 
    html.H2(children=dcc.Markdown("Location: [Rouge Gateway Trail, Dearborn, MI](https://goo.gl/maps/WzSvLWxtkyoro9oK8)"), 
    style={'textAlign': 'center'}),
    html.H4(children='Data collection: 5 weeks (2022-06-15 to 2022-07-19)', style={'textAlign': 'center'})]),
    
    html.Div(children=[
    html.H3(children='Select data range')],
            style={'textAlign': 'center', 'width': '30%', 'display': 'inline-block'}),
    
    html.Div(children=[
    html.H3(children='Select traffic direction')],
            style={'textAlign': 'center', 'width': '40%', 'display': 'inline-block'}),
    
    html.Div(children=[
    html.H3(children='Select data resolution')],
            style={'textAlign': 'center', 'width': '30%', 'display': 'inline-block'}),
    
    html.Div(children=[
    dcc.DatePickerRange(id='my-date-picker-range',
                        min_date_allowed = min_date_allowed,
                        max_date_allowed = max_date_allowed,
                        start_date = min_date_allowed,
                        end_date = max_date_allowed)],
            style={'textAlign': 'center', 'width': '30%', 'display': 'inline-block'}),
    
    html.Div(children=[
    dcc.RadioItems(['Both directions', 'Eastbound only', 'Westbound only'],'Both directions' ,id='data-dir-radio')],
        style={'textAlign': 'center', 'width': '40%', 'display': 'inline-block'}),
    
    html.Div(children=[
    dcc.RadioItems(['1 day', '1 hour', '30 min', '15 min'], '1 day' ,id='data-agg-radio')],
        style={'textAlign': 'center', 'width': '30%', 'display': 'inline-block'}),
    
    html.Div(children=[
    dcc.Graph(id='counter-bar-graph')]),
     
    html.Div(children=[
    html.H3(children='Volume by direction', 
    style={'textAlign': 'center', 'width': '48%', 'display': 'inline-block', 'float': 'right'})]),
    
    html.Div(children=[
    html.H3(children='Bicycle traffic data', 
    style={'textAlign': 'center', 'width': '48%', 'display': 'inline-block'})]),
    
    html.Div(
    dash_table.DataTable(data = table.to_dict("records"), 
                         columns =[{"name": "", "id": ""},
                                   {"name": "Total volume", "id": "Total volume"},
                                   {"name": "Average daily volume", "id": "Average daily volume"}],
                         style_table={'height': '250px', 'overflowY': 'auto'},
                         id='avg-table'),
    style={'width': '48%', 'height': '100%', 'display': 'inline-block'}),
    
    html.Div(children=[
    dcc.Graph(id='counter-pie-chart')],
    style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    
    html.Div(children=[
    html.H4(children=dcc.Markdown("Download the [raw CSV file](http://www.umich.edu/~fredfeng/bike-counter-dearborn-20220615.csv)"), 
    style={'textAlign': 'center'}),]),

    html.Div(children=[
    html.H4(children=dcc.Markdown("[Click here](https://fenggroup.org/bike-counter/) to learn more about our bike counting project."), 
    style={'textAlign': 'center'}),])
    
    
])


@app.callback(
    Output('counter-bar-graph', 'figure'),
    Output('counter-pie-chart', 'figure'),
    Input('data-dir-radio', 'value'),
    Input('data-agg-radio', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_figure(dir_radio_val, agg_radio_val, start_date, end_date):
    
    if agg_radio_val == '15 min':
        
        filtered_df = df_15m[(df_15m['Time'].dt.strftime('%Y-%m-%d') >= start_date) 
                            & (df_15m['Time'].dt.strftime('%Y-%m-%d') <= end_date)]
        
    elif agg_radio_val == '30 min':
        
        filtered_df = df_30m[(df_30m['Time'].dt.strftime('%Y-%m-%d') >= start_date) 
                            & (df_30m['Time'].dt.strftime('%Y-%m-%d') <= end_date)]
        
    elif agg_radio_val == '1 hour':
        
        filtered_df = df_1h[(df_1h['Time'].dt.strftime('%Y-%m-%d') >= start_date) 
                            & (df_1h['Time'].dt.strftime('%Y-%m-%d') <= end_date)]
    
    elif agg_radio_val == '1 day':
        
        filtered_df = df_daily[(df_daily['Time'].dt.strftime('%Y-%m-%d') >= start_date) 
                            & (df_daily['Time'].dt.strftime('%Y-%m-%d') <= end_date)]
        
    
    pie_data = [['Eastbound', np.sum(filtered_df['Eastbound'])], ['Westbound', np.sum(filtered_df['Westbound'])]]

    df_pie = pd.DataFrame(data=pie_data, columns=["names", "values"])
    
    
    if dir_radio_val == 'Eastbound only':

        fig1 = px.bar(filtered_df, x="Time", y='Eastbound', labels = {"Eastbound":"Count", "day_of_week":"Day of week" }, 
                      hover_data= ['day_of_week'])
        fig1.update_traces(marker_color='#636EFA')
    
    elif dir_radio_val == 'Westbound only':
    
        fig1 = px.bar(filtered_df, x="Time", y='Westbound', labels = {"Westbound":"Count", "day_of_week":"Day of week"}, 
                      hover_data= ['day_of_week'])
        fig1.update_traces(marker_color='#EF553B')
    
    elif dir_radio_val == 'Both directions':
    
        fig1 = px.bar(filtered_df, x="Time", y='Both directions', labels = {"Both directions":"Count", "day_of_week":"Day of week"}, 
                      hover_data= ['Eastbound', 'Westbound', 'day_of_week'])
        fig1.update_traces(marker_color='#AB63FA')
    
    
    fig2 = px.pie(df_pie, values='values', names='names')

    fig1.update_layout(yaxis_title="Count", transition_duration=500, hoverlabel=dict(font_color="white"))
    
    fig2.update_layout(width=700, height=250, margin=dict(l=50, r=50, b=50, t=0), transition_duration=500)

    return fig1, fig2

@app.callback(
    Output('avg-table', 'data'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_table(start_date, end_date):
    
    select_data_range = df_daily[(df_daily['Time'].dt.strftime('%Y-%m-%d') >= start_date) 
                                 & (df_daily['Time'].dt.strftime('%Y-%m-%d') <= end_date)]
    
    daily_avg = round(select_data_range.mean(numeric_only=True),1)

    total_vol = round(select_data_range.sum(numeric_only=True),1)

    data_table = (total_vol,daily_avg)

    table = pd.DataFrame(data_table).T

    table.reset_index(inplace=True)

    table.columns = ['','Total volume','Average daily volume']
    
    data_table = table.to_dict("records")
    
    return  data_table

    
if __name__ == '__main__':
    app.run(debug=False)