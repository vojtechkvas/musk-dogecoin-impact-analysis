import dash_bootstrap_components as dbc

import dash
from dash import html

dash.register_page(__name__, path="/analysis")

layout = dbc.Container(
    [
        html.H1("analysis eeeeeee Dashboard"),
    ],
    fluid=True,
)
