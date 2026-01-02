"""
Causal Impact Analysis Page Module.

This module defines the layout for the specialized Causal Impact dashboard.
It allows users to select individual tweets and perform Bayesian structural
time-series analysis to estimate the causal effect of social media posts
on Dogecoin price.

Components:
    - Tweet Selector: A DataTable for choosing specific tweets for analysis.
    - Parameter Inputs: Numeric inputs to define the training (pre-period)
      and prediction (post-period) time windows.
    - Impact Visualization: Displays the CausalImpact Matplotlib results as
      a static image to preserve complex confidence intervals.
    - Statistical Reports: Centered text blocks providing a mathematical
      summary and a detailed linguistic report of the estimated impact.
"""

import dash
import dash_bootstrap_components as dbc
import matplotlib
from dash import dash_table, html

from src.config import config
from src.data_utils import loaders, utils

matplotlib.use("Agg")

dash.register_page(__name__, path="/causalimpact")


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
                        "Causal Impact Visualization",
                        className="text-center my-4 text-primary",
                    ),
                    width=12,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.P("Activity peaked between 2021 and 2022. "),
                            html.P(
                                "A preliminary visual inspection suggests that while individual "
                                "tweets may cause short term volatility, they do not appear to "
                                "sustain significant price increases over extended periods."
                            ),
                        ],
                    ),
                ),
            ]
        ),
        dbc.Row(
            [
                html.H4("Tweet Table", className="mt-4 mb-3"),
                dash_table.DataTable(
                    id="tweet-selector-table",
                    columns=[
                        {
                            "name": i,
                            "id": i,
                            "selectable": True,
                        }
                        for i in config.COLUMS_FOR_CAUSAL_IMPACT_SELECTION
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
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Stack(),
                    md=2,
                    sm=12,
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
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.H4("Price and Tweet Volume Over Time")
                            ),
                            dbc.CardBody(
                                dbc.CardBody(
                                    [
                                        dbc.Spinner(
                                            html.Img(
                                                id="causalimpact-plot-img",
                                                style={
                                                    "width": "80%",
                                                    "height": "auto",
                                                    "paddingLeft": "20%",
                                                },
                                            ),
                                            color="primary",
                                        ),
                                        html.Hr(),
                                        html.H5(
                                            "Analysis Summary",
                                            className="text-primary mt-3 text-center",
                                        ),
                                        html.Pre(
                                            "Summary",
                                            id="causal-summary-text",
                                            className="text-white bg-black p-3 border border-white",
                                            style={
                                                "textAlign": "center",
                                                "margin": "0 auto",
                                                "width": "fit-content",
                                            },
                                        ),
                                        html.H5(
                                            "Detailed Report",
                                            className="text-primary mt-3 text-center",
                                        ),
                                        html.Pre(
                                            "Report",
                                            id="causal-report-text",
                                            className="text-white bg-black p-3 border border-white",
                                            style={
                                                "whiteSpace": "pre-wrap",
                                                "textAlign": "center",
                                                "margin": "0 auto",
                                                "width": "fit-content",
                                            },
                                        ),
                                    ]
                                ),
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
                    html.Div(id="selection-output", className="mt-3 mb-5"),
                    width=12,
                )
            ]
        ),
    ],
    fluid=True,
    className="dbc p-4 dbc-dark-theme",
)
