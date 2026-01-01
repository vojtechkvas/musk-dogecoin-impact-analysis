"""
Analysis Page Module.

This module defines the layout for the secondary analysis dashboard.
It utilizes Dash Bootstrap Components to provide a responsive container
for specialized data visualizations and in-depth performance metrics
related to Dogecoin and social media impact.
"""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from src.config.config import (
    DEFAULT_DOGE_KEYWORDS,
    DOGE_MAX_DATE,
    DOGE_MIN_DATE,
)

dash.register_page(__name__, path="/causalimpact")


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
    ],
    fluid=True,
    className="dbc p-4 dbc-dark-theme",
)
