import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/analysis")

layout = dbc.Container(
    [
        html.H1("analysis eeeeeee Dashboard"),
    ],
    fluid=True,
)
