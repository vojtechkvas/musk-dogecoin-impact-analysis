import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from src.config.settings import (
    DEFAULT_DOGE_KEYWORDS, DOGE_MAX_DATE, DOGE_MIN_DATE
)

dash.register_page(__name__, path='/')

layout = dbc.Container([
    html.H1("Crypto Tweet Sentiment Dashboard"),
], fluid=True)

 