"""
Analysis Page Module.

This module defines the layout for the secondary analysis dashboard.
It utilizes Dash Bootstrap Components to provide a responsive container
for specialized data visualizations and in-depth performance metrics
related to Dogecoin and social media impact.
"""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dash_table, dcc, html

import src.config.config as config
from src.config.config import (
    DEFAULT_DOGE_KEYWORDS,
    DOGE_MAX_DATE,
    DOGE_MIN_DATE,
)

dash.register_page(__name__, path="/causalimpact")


import dash_bootstrap_components as dbc
import pandas as pd

icon_map = {
    "possibly_sensitive": "⚠️ Sensitive",
    "quote_id": "🆔 Quote ID",
    "quote": "💬 Quote",
    "retweet": "🔁 Retweet",
    "timestamp": "🕒 Timestamp",
}
icon_map = {}


from src.data_utils import formatters, loaders, processing, utils

TWEET_DATA = loaders.load_data(
    config.PROCESSED_DIR,
    config.PROCESSED_TWEETS_DOGECOIN_PATH,
    types=config.POSTS_DTYPES,
    skiprows=1,
)

TWEET_DATA = utils.convert_datetime_to_unix_timestamp(df=TWEET_DATA)

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "Dogecoin Tweets Visualization",
                        className="text-center my-4 text-primary",
                    ),
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                html.H4("Tweet Table", className="mt-4 mb-3"),
                dash_table.DataTable(
                    id="tweet-selector-table",
                    columns=[
                        {
                            "name": icon_map.get(i, i),
                            "id": i,
                            "selectable": True,
                        }
                        for i in config.COLUMS_FOR_Causal_Impact_selection.keys()
                    ],
                    data=TWEET_DATA.to_dict("records"),
                    sort_action="native",
                    filter_action="native",
                    column_selectable="single",
                    selected_columns=[],
                    page_size=15,
                    style_table={
                        "overflowX": "auto",
                        "color": "white",
                    },
                    style_header={
                        "backgroundColor": "#2c2c2c",
                        "color": "white",
                        "fontWeight": "bold",
                        "border": "1px solid #444",
                        "textAlign": "center",
                    },
                    style_cell={
                        "backgroundColor": "#1e1e1e",
                        "color": "#FFF",
                        "textAlign": "left",
                        "padding": "10px",
                        "fontFamily": "sans-serif",
                        "border": "1px solid #333",
                    },
                    style_filter={
                        "backgroundColor": "#333",
                        "color": "white",
                    },
                    style_data_conditional=[
                        {
                            "if": {"column_editable": False},
                            "backgroundColor": "#1e1e1e",
                        },
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#252525",
                        },
                        {
                            "if": {"state": "active"},
                            "backgroundColor": "#3d3d3d",
                            "border": "1px solid #primary",
                        },
                    ],
                ),
                html.Div(id="selection-output", className="mt-3"),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Stack(),
                    md=2,
                    sm=12,
                    xs=12,
                ),
                dbc.Col(
                    dbc.Stack(
                        [
                            dbc.Label(
                                "Minutes before tweet",
                                html_for="date-from-picker",
                                className="fw-semibold fs-4",
                            ),
                            dbc.Input(
                                id="num-from-input-causalimpact",
                                type="number",
                                min=0,
                                step=10,
                                value=120,
                                placeholder="e.g. 10",
                                className="fs-5 bg-dark text-white border-secondary",
                            ),
                            html.Small(
                                "Number of minutes before tweet used for training",
                                className="text-muted fs-5",
                            ),
                        ]
                    ),
                    md=4,
                    sm=6,
                    xs=12,
                ),
                dbc.Col(
                    dbc.Stack(
                        [
                            dbc.Label(
                                "Minutes after tweet",
                                html_for="date-to-picker",
                                className="fw-semibold fs-4",
                            ),
                            dbc.Input(
                                id="num-to-input-causalimpact",
                                type="number",
                                min=0,
                                step=10,
                                value=60,
                                placeholder="e.g. 10",
                                className="fs-5 bg-dark text-white border-secondary",
                            ),
                            html.Small(
                                "Number of minutes after tweet used for prediction",
                                className="text-muted fs-5",
                            ),
                        ]
                    ),
                    md=4,
                    sm=6,
                    xs=12,
                ),
                dbc.Col(
                    dbc.Stack(),
                    md=2,
                    sm=12,
                ),
            ],
            className="g-4 mb-4",
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.H4("Price and Tweet Volume Over Time")
                            ),
                            dbc.CardBody(
                                dcc.Graph(
                                    id="causalimpact-graph",
                                    figure={"data": [], "layout": {}},
                                )
                            ),
                            dbc.CardFooter(
                                html.Div(
                                    [
                                        html.P(
                                            "Activity peaked between 2021 and 2022. "
                                        ),
                                        html.P(
                                            "A preliminary visual inspection suggests that while individual tweets "
                                            "may cause short term volatility, they do not appear to sustain "
                                            "significant price increases over extended periods."
                                        ),
                                    ],
                                )
                            ),
                        ]
                    ),
                    width=12,
                )
            ],
            className="g-4 mb-4",
        ),
    ],
    fluid=True,
    className="dbc p-4 dbc-dark-theme",
)


@callback(
    Output("selection-output", "children"),
    Input("num-from-input-causalimpact", "value"),
    Input("num-to-input-causalimpact", "value"),
    Input("tweet-selector-table", "active_cell"),
    State("tweet-selector-table", "data"),
)
def display_row_details(num_from, num_to, active_cell, table_data):
    if not active_cell:
        return "Click on any row to see details."

    print(num_from)
    print(num_to)
    print(active_cell)

    row_index = active_cell["row"]
    selected_row = table_data[row_index]

    details_content = [
        html.Div(
            [
                html.H3(
                    "Tweet",
                    className="text-center my-4 text-primary",
                ),
                html.Small(
                    f"Viewing Row Index: {row_index}", className="text-white"
                ),
            ],
            className="mb-3",
        ),
        html.Hr(className="text-secondary"),
    ]

    for col_name, value in selected_row.items():
        display_name = icon_map.get(col_name, col_name)

        display_value = str(value)

        details_content.append(
            dbc.Row(
                [
                    dbc.Col(
                        html.B(f"{display_name}"),
                        width=4,
                        className="text-primary font-monospace",
                    ),
                    dbc.Col(
                        html.Span(display_value),
                        width=8,
                        className="text-white",
                    ),
                ],
                className="mb-2 py-1 border-bottom border-secondary border-opacity-25",
            )
        )

    return dbc.Card(
        dbc.CardBody(details_content),
        className="mt-3 shadow-lg",
        style={
            "backgroundColor": "#1a1a1a",
            "border": "1px solid #333",
            "borderRadius": "10px",
            "color": "white",
        },
    )
