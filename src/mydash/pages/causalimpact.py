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
                    md=4,
                    sm=12,
                    xs=12,
                ),
                dbc.Col(
                    dbc.Stack(
                        [
                            dbc.Label(
                                "Date from",
                                html_for="date-from-picker",
                                className="fw-semibold fs-4",
                            ),
                            dcc.DatePickerSingle(
                                id="date-from-picker-causalimpact",
                                min_date_allowed=DOGE_MIN_DATE,
                                max_date_allowed=DOGE_MAX_DATE,
                                initial_visible_month=DOGE_MIN_DATE,
                                date=DOGE_MIN_DATE,
                                placeholder="Select start date",
                                calendar_orientation="vertical",
                                className="fs-5",
                            ),
                            html.Small(
                                "Start date for DOGE data filtering",
                                className="text-muted fs-5",
                            ),
                        ]
                    ),
                    md=2,
                    sm=6,
                    xs=12,
                ),
                dbc.Col(
                    dbc.Stack(
                        [
                            dbc.Label(
                                "Date to",
                                html_for="date-to-picker",
                                className="fw-semibold fs-4",
                            ),
                            dcc.DatePickerSingle(
                                id="date-to-picker-causalimpact",
                                min_date_allowed=DOGE_MIN_DATE,
                                max_date_allowed=DOGE_MAX_DATE,
                                initial_visible_month=DOGE_MAX_DATE,
                                date=DOGE_MAX_DATE,
                                placeholder="Date To",
                                calendar_orientation="vertical",
                                className="fs-5",
                            ),
                            html.Small(
                                "End date for DOGE data filtering",
                                className="text-muted fs-5",
                            ),
                        ]
                    ),
                    md=2,
                    sm=6,
                    xs=12,
                ),
                dbc.Col(
                    dbc.Stack(),
                    md=4,
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
    Input("tweet-selector-table", "active_cell"),
    State("tweet-selector-table", "data"),
)
def display_row_details(active_cell, table_data):
    if not active_cell:
        return "Click on any row to see details."

    row_index = active_cell["row"]

    selected_row = table_data[row_index]

    tweet_text = selected_row.get("quote", "No text available")
    timestamp = selected_row.get("timestamp", "N/A")

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(
                    "📊 Selected Tweet Details",
                    className="card-title text-info",
                ),
                html.P(
                    f"Row Index: {row_index}", className="text-muted small"
                ),
                html.Hr(),
                html.P(tweet_text, className="fs-5"),
                dbc.Badge(
                    f"Unix TS: {timestamp}",
                    color="secondary",
                    className="me-2",
                ),
            ]
        ),
        className="mt-3 bg-dark border-secondary text-white",
    )
