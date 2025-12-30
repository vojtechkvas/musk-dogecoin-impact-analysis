"""
Analysis Page Module.

This module defines the layout for the secondary analysis dashboard.
It utilizes Dash Bootstrap Components to provide a responsive container
for specialized data visualizations and in-depth performance metrics
related to Dogecoin and social media impact.
"""

import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, path="/analysis")

layout = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                html.H1(
                    "Crypto Tweets Visualization",
                    className="text-center my-4 text-primary",
                ),
                width=12,
            ),
            dbc.Col(
                dbc.RadioItems(
                    id="doge-filter-state",
                    options=[
                        {"label": "Exclue replies", "value": False},
                        {"label": "Only replies", "value": True},
                        {"label": "All", "value": None},
                    ],
                    value=None,
                    inline=True,
                )
            ),
        ]
    ),
    fluid=True,
)
