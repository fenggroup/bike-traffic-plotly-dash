import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    html.H1(children='Welcome to our interact bike traffic dashboard'),

    html.Div(children='''
        Select the location you want to see traffic for above
    '''),

])