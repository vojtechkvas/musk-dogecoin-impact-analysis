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

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from src.config.config import (
    DEFAULT_DOGE_KEYWORDS,
    DOGE_MAX_DATE,
    DOGE_MIN_DATE,
)

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
                    dbc.Stack(
                        [
                            dbc.Label(
                                "Quick date selection",
                                className="fw-semibold fs-4",
                            ),
                            dbc.Button(
                                "Set end date to first DOGE mention",
                                id="mentionning-of-doge-department-button",
                                n_clicks=0,
                                color="primary fs-5",
                            ),
                            html.Small(
                                "Automatically sets the end date to the first "
                                "date mentioning the DOGE department.",
                                className="text-muted fs-5",
                            ),
                        ],
                        gap=1,
                    ),
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
                                id="date-from-picker",
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
                                id="date-to-picker",
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
                    dbc.Stack(
                        [
                            dbc.Label(
                                "Text filter",
                                html_for="text-filter-input",
                                className="fw-semibold fs-4",
                            ),
                            dbc.Input(
                                id="text-filter-input",
                                placeholder="Filter tweets by text (e.g., 'dogecoin')",
                                type="text",
                                debounce=True,
                                value=DEFAULT_DOGE_KEYWORDS,
                                className="bg-black text-white fw-bold fs-5 border-white border-2",
                            ),
                            html.Small(
                                "Shows only tweets containing the specified keyword or phrase.",
                                className="text-muted fs-5",
                            ),
                        ],
                        gap=1,
                    ),
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
                            dbc.CardHeader(
                                html.H4("Price and Tweet Volume Over Time")
                            ),
                            dbc.CardBody(
                                dcc.Graph(
                                    id="price-volume-graph",
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
                            dbc.CardFooter(
                                html.Div(
                                    [
                                        html.P(
                                            [
                                                "The data suggests that Elon Musk's tweets have a measurable impact on Dogecoin's price volatility. ",
                                                "On average (indicated by the ",
                                                html.B("white line"),
                                                "), the price increases by ",
                                                html.B("4%"),
                                                " shortly after a tweet, though this gain typically retraces to approximately ",
                                                html.B("1%"),
                                                " after six hours.",
                                            ]
                                        ),
                                        html.P(
                                            [
                                                "Historically, the highest average returns occurred when selling approximately ",
                                                html.B("45 minutes"),
                                                " after a tweet, yielding an average gain of 4%. However, these patterns are ",
                                                html.Span(
                                                    "not guaranteed",
                                                    className="text-danger fw-bold",
                                                ),
                                                " and individual results vary significantly.",
                                            ]
                                        ),
                                    ],
                                    className="mt-3",
                                )
                            ),
                        ]
                    ),
                    width=12,
                )
            ],
            className="g-4",
        ),
    ],
    fluid=True,
    className="dbc p-4 dbc-dark-theme",
)


layout = dbc.Container([main_layout], fluid=True)
