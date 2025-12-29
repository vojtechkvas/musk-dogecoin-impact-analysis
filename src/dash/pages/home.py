"""
Dogecoin Tweets Visualization Page Module.

This module defines the layout for the primary dashboard page, which visualizes
the relationship between historical Dogecoin tweets and cryptocurrency price
movements. It includes interactive filters for date ranges and keyword
searches, Key Performance Indicators (KPIs), and detailed Plotly graphs
for price/volume analysis and individual tweet impact.

Components:
    - Filters: Date pickers and text input for filtering data.
    - KPIs: Metric cards for total tweets and average prices.
    - Graphs: Time-series analysis of price/volume and relative price impact analysis.
"""

import dash_bootstrap_components as dbc

import dash
from dash import dcc, html
from src.config.config import DEFAULT_DOGE_KEYWORDS, DOGE_MAX_DATE, DOGE_MIN_DATE

dash.register_page(__name__, path="/")


def create_card(title: str, value_id: str):
    """
    Creates a Bootstrap card component for displaying a metric.

    Args:
        title (str): The label/title to display at the top of the card.
        value_id (str): The Dash component ID used to target the value
            text in callbacks.

    Returns:
        dbc.Card: A Dash Bootstrap Components Card object containing the
            styled title and value placeholder.
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.P(
                    id=value_id,
                    className="card-text display-4",
                ),
            ],
            className="d-flex justify-content-between align-items-center",
        )
    )


main_layout = dbc.Container(
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
                dbc.Col(
                    html.Div(
                        dbc.Button(
                            "Set First mention of DOGE department",
                            id="mentionning-of-doge-department-button",
                            n_clicks=0,
                            color="primary",
                            className="mt-2",
                        ),
                        className="mt-2",
                    ),
                    md=4,
                    xs=12,
                ),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id="date-from-picker",
                        min_date_allowed=DOGE_MIN_DATE,
                        max_date_allowed=DOGE_MAX_DATE,
                        initial_visible_month=DOGE_MIN_DATE,
                        date=DOGE_MIN_DATE,
                        placeholder="Date From",
                        #   className="dbc-dark-theme text-white bg-dark border-secondary",
                        #  className="text-white bg-dark border-secondary",
                        calendar_orientation="vertical",
                        #  style={'color': 'white', 'background-color': '#303030', 'border': '1px solid #6c757d'} # Dark styles for the input box itself
                    ),
                    md=2,
                    xs=6,
                ),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id="date-to-picker",
                        min_date_allowed=DOGE_MIN_DATE,
                        max_date_allowed=DOGE_MAX_DATE,
                        initial_visible_month=DOGE_MAX_DATE,
                        date=DOGE_MAX_DATE,
                        placeholder="Date To",
                        calendar_orientation="vertical",
                        className="dbc-dark-theme text-white bg-dark border-secondary",
                        style={
                            "color": "white",
                            "backgroundColor": "#343a40",
                            "border": "1px solid #6c757d",
                        },
                    ),
                    md=2,
                    xs=6,
                ),
                dbc.Col(
                    dbc.Input(
                        id="text-filter-input",
                        placeholder="Filter tweets by text (e.g., 'Elon')",
                        type="text",
                        debounce=True,
                        value=DEFAULT_DOGE_KEYWORDS,
                        className="text-white bg-dark border-secondary",
                    ),
                    md=4,
                    xs=12,
                ),
            ],
            className="g-4 mb-4",
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    create_card("Total Tweets", "kpi-total-tweets"),
                    md=4,
                ),
                dbc.Col(
                    create_card("Avg. Crypto Price", "kpi-avg-price"),
                    md=4,
                ),
                dbc.Col(
                    create_card(
                        "Avg. price during tweet",
                        "kpi-avg-price-during-tweet",
                    ),
                    md=4,
                ),
            ],
            className="g-4 mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Price and Tweet Volume Over Time")),
                            dbc.CardBody(
                                dcc.Graph(
                                    id="price-volume-graph",
                                    figure={"data": [], "layout": {}},
                                )
                            ),
                        ]
                    ),
                    width=12,
                )
            ],
            className="g-4 mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.H4(
                                    "Individual Tweet Impact (Relative Time and Price)"
                                )
                            ),
                            dbc.CardBody(
                                dcc.Graph(
                                    id="tweet-impact-graph",
                                    figure={"data": [], "layout": {}},
                                )
                            ),
                        ]
                    ),
                    width=12,
                )
            ],
            #   className="g-4 mb-4",
            className="g-4",
        ),
    ],
    fluid=True,
    className="dbc p-4 dbc-dark-theme",
)


layout = dbc.Container([main_layout], fluid=True)
