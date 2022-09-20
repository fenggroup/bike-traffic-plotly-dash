from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import numpy as np

title = "Bicycle Traffic Dashboard"

app = Dash(__name__, title=title)

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

# Config bike counter location

# # Dearborn data
# data_file_name = "bike_data_dearborn.csv"
# config_direction = {"in": "Eastbound", 
#                     "out": "Westbound"}
# loc_msg_markdown = "Location: [Rouge Gateway Trail, Dearborn, MI](https://goo.gl/maps/WzSvLWxtkyoro9oK8)"
# dates_msg = "Data collection: 5 weeks (2022-06-15 to 2022-07-19)"

# Config for Ann Arbor data
data_file_name = "bike_data_aa.csv"    
config_direction = {"in": "Northbound", 
                    "out": "Southbound"}
loc_msg_markdown = "Location: N Division, Ann Arbor, MI ([Site photo](https://fenggroup.org/images/respic/bike-counter-a2division.png), [Google Maps](https://goo.gl/maps/1bcfHrqSYbqiRSXa8))"
# dates_msg = "Data collection: X weeks (2022-08-26 to 2022-mm-dd)"

path = "./data/" + data_file_name
df = pd.read_csv(path, names=["time", "in", "out"], skiprows=4)

df["bi_direction"] = df["in"] + df["out"]

# Convert the time to a pandas datetime object
df["time"] = pd.to_datetime(df["time"])

df = df.set_index("time")

# Set variables for the min and max date that can be selected in the date picker
min_date_allowed = df.index.date.min()
max_date_allowed = df.index.date.max()

# A function to update the dataframe based on the specified resample rule and date range
def df_update(df, rule, start_date, end_date):

    df_resample = df.resample(rule).sum()

    df_filtered = df_resample[(df_resample.index.strftime("%Y-%m-%d") >= start_date) & 
                              (df_resample.index.strftime("%Y-%m-%d") <= end_date)]

    df_filtered["day_of_week"] = df_filtered.index.strftime("%a")

    return df_filtered


# Set up a preliminary dataframe for the data table
table = pd.DataFrame(np.zeros((3,4)))

app.layout = html.Div([
    
    html.Div(children=[
             html.H1(children=title), 
             html.H3(children=dcc.Markdown(loc_msg_markdown)),
            #  html.H3(children=dates_msg),
             ]),
    
    html.Div(id="select-date-range",
             children=[
             html.H3(children="Select dates"), 
             dcc.DatePickerRange(id='my-date-picker-range',
                                 min_date_allowed = min_date_allowed,
                                 max_date_allowed = max_date_allowed,
                                 start_date = min_date_allowed,
                                 end_date = max_date_allowed, 
                                 minimum_nights=0,),
             ]),
    
    html.Div(id="select-direction",
             children=[
             html.H3(children="Select traffic direction"), 
             dcc.RadioItems(options={"bi-direction": "Both directions", 
                                     "in": config_direction["in"], 
                                     "out": config_direction["out"]},
                            value="bi-direction",
                            id='data-dir-radio'),
            ]),
    
    html.Div(id="select-resolution",
             children=[
             html.H3(children="Select data resolution"), 
             dcc.RadioItems(options={"1_day": "1 day",
                                     "1_hour": "1 hour", 
                                     "30_min": "30 min",
                                     "15_min": "15 min"}, 
                            value="1_day",
                            id='data-agg-radio'),
            ]),

    html.Div(children=[
    dcc.Graph(id='bar-graph')]),

    html.Div(children=[
             html.H3(children='Bicycle volume on the selected dates'), 
             dash_table.DataTable(data = table.to_dict("records"), 
                                  columns =[
                                    dict(id='dir', name=''),
                                    dict(id='total_vol', name='Total volume', type='numeric', format=dash_table.Format.Format().group(True)),
                                    dict(id='daily_avg', name='Ave. daily volume', type='numeric', format=dash_table.Format.Format(precision=1, scheme=dash_table.Format.Scheme.fixed)),
                                    dict(id='perc', name='Percent', type='numeric', format=dash_table.FormatTemplate.percentage(1))
                                    ],
                                    style_cell_conditional=[
                                        {'if': {'column_id': 'dir'},
                                        'width': '25%'},
                                        {'if': {'column_id': 'total_vol'},
                                        'width': '25%'},
                                        {'if': {'column_id': 'daily_avg'},
                                        'width': '25%'},
                                        {'if': {'column_id': 'perc'},
                                        'width': '20%'},
                                        ],
                                  style_table={'height': '250px', 'overflowY': 'auto'},
                                  style_cell={'font-family':'Roboto', 'padding-right': '10px', 'padding-left': '10px'},
                                  id='avg-table'),
            ]), 
    
    html.Div(children=[
             html.H3(children='Hourly traffic by time of day'),
             dcc.Graph(id='time-of-day')]),
    
    html.Div(children=[
             html.H3(children='Daily traffic by day of week'),
             dcc.Graph(id='day-of-week')]),

    html.Div(children=[
        html.H4(children=dcc.Markdown("Download the [data files in CSV](https://github.com/fenggroup/bike-traffic-plotly-dash/tree/main/data)")),
        html.H4(children=dcc.Markdown("[Click here](https://fenggroup.org/bike-counter/) to learn more about our bike counting project.")), 
        html.H4(children=dcc.Markdown("This dashboard is open source and hosted on [our GitHub repository](https://github.com/fenggroup/bike-traffic-plotly-dash).")), 
        html.H4(children=dcc.Markdown("[Feng Group](https://fenggroup.org/) 2022"))
    ])
    
])

@app.callback(
    Output("bar-graph", "figure"),
    Input("data-dir-radio", "value"),
    Input("data-agg-radio", "value"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"))

def update_figure(dir_radio_val, agg_radio_val, start_date, end_date):

    if agg_radio_val == "15_min":
        rule = "15T"
    elif agg_radio_val == "30_min":
        rule = "30T"
    elif agg_radio_val == "1_hour":
        rule = "1H"
    elif agg_radio_val == "1_day":
        rule = "1D"

    df_updated = df_update(df=df, rule=rule, start_date=start_date, end_date=end_date)  
    
    if dir_radio_val == "in":

        direction = "in"
        hover_data= ["day_of_week"]
        marker_color="#636EFA"   # blue
    
    elif dir_radio_val == "out":

        direction = "out"
        hover_data= ["day_of_week"]
        marker_color="#EF553B"   # red

    elif dir_radio_val == "bi-direction":

        direction = "bi_direction"
        hover_data = ["in", "out", "day_of_week"]
        marker_color="#AB63FA"  # purple
    
    labels = {"time": "Date", 
              "bi_direction": "Total",
              "in": config_direction["in"],
              "out": config_direction["out"],
              "day_of_week": "Day of week"}

    fig1 = px.bar(df_updated, 
                  x=df_updated.index, 
                  y=direction, 
                  labels=labels, 
                  hover_data=hover_data)

    fig1.update_traces(marker_color=marker_color)

    fig1.update_layout(xaxis_title="Date & time", 
                       yaxis_title="Count", 
                       transition_duration=500, 
                       hoverlabel=dict(font_color="white"))
    
    return fig1
    

@app.callback(
    Output('avg-table', 'data'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))

def update_table(start_date, end_date):

    df_updated = df_update(df=df, 
                           rule="1D", 
                           start_date=start_date, 
                           end_date=end_date)

    df_updated.drop(columns="day_of_week", inplace=True)

    total_vol = df_updated.sum()
    daily_avg = df_updated.mean()

    # Calculate percentages
    perc_in = total_vol.loc["in"] / total_vol.loc["bi_direction"]
    perc_out = total_vol.loc["out"] / total_vol.loc["bi_direction"]

    perc = pd.Series({"in": perc_in, 
                      "out": perc_out, 
                      "bi_direction": 1})

    direction = pd.Series({"in": config_direction["in"], 
                           "out": config_direction["out"], 
                           "bi_direction": "Both directions"})

    table = pd.DataFrame((direction, total_vol, daily_avg, perc)).T

    table.columns = ["dir", "total_vol", "daily_avg", "perc"]

    data_table = table.loc[["bi_direction", "in", "out"]].to_dict("records")
    
    return  data_table

@app.callback(
    Output("time-of-day", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"))

def update_figure(start_date, end_date):
    
    df_time = df_update(df=df, rule="15T", start_date=start_date, end_date=end_date)
    
    ctb_time = pd.crosstab(index = [df_time.index.isocalendar().week, df_time.index.day], 
                           columns  =df_time.index.hour,
                           rownames=['week', 'day'],
                           values = df_time.bi_direction, aggfunc = 'sum'
                           )
    
    labels = {"col_0": "Time of day", 
              "value": "Count"}
    
    fig2 = px.strip(data_frame=ctb_time,
                    labels=labels)

    xticks=np.arange(-0.5, 24, 1) 
    xlabels=np.arange(0, 25, 1)

    marker_color="#0D2A63"  # dark blue

    fig2['layout'] = {'xaxis':{'tickvals':xticks, 
                               'ticktext':xlabels,
                               'showline':True
                               }
                      }
    
    fig2.update_traces(marker_color=marker_color)
    fig2.add_trace(px.box(data_frame=ctb_time, points=False).data[0])

    fig2.update_layout(xaxis_title="Time of day", 
                       yaxis_title="Count", 
                       transition_duration=500)
    
    return fig2

@app.callback(
    Output("day-of-week", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"))

def update_figure(start_date, end_date):
    
    df_day = df_update(df=df, rule="15T", start_date=start_date, end_date=end_date)

    ctb_day = pd.crosstab(index = df_day.index.isocalendar().week, 
                  columns  =df_day.index.day_of_week,
                  values = df_day.bi_direction, aggfunc = 'sum'
                  )
    labels = {"col_0": "Day of week", 
              "value": "Count"}
    
    fig3 = px.strip(data_frame=ctb_day,
                    labels=labels)

    xticks=np.arange(0, 7, 1)
    xlabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    fig3['layout'] = {'xaxis':{'tickvals':xticks, 
                               'ticktext':xlabels,
                               'showline':True
                               }
                      }

    marker_color='rgba(102, 166, 30, 0.7)'  # dark green

    fig3.update_traces(marker_color=marker_color, marker_size=20)

    fig3.update_layout(xaxis_title="Day of week", 
                       yaxis_title="Count",
                       yaxis = dict(rangemode = 'tozero'),
                       transition_duration=500)
    
    return fig3

if __name__ == '__main__':
    app.run(debug=False)
