import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def layout():
    return dbc.Container([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                dbc.NavItem(dbc.NavLink("Deep Analysis", href="/analysis", active="exact")),
            ],
            brand="DOGE Tracker",
            color="primary",
            dark=True,
        ),

        dash.page_container 
    ], fluid=True)