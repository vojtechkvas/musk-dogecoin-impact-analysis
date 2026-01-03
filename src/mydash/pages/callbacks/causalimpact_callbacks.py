"""
Causal Impact Analysis Module.

This module provides the analytical dashboard for estimating the causal effect
of specific events (e.g., individual tweets) on cryptocurrency price movements.
It leverages Bayesian Structural Time-Series models to forecast counterfactuals
and calculate statistical significance.

Key Functionalities:
    - Interactive Tweet Selection: Users can select specific tweets from a
      DataTable to trigger a localized causal analysis.
    - Parameter Configuration: Allows dynamic adjustment of pre-intervention
      (training) and post-intervention (prediction) time windows.
    - Automated Reporting: Generates visual plots, quantitative summaries,
      and detailed linguistic analysis reports for the selected event.

Exported Objects:
    - layout: A Dash Bootstrap Component (dbc.Container) defining the
      page structure.
    - display_row_details: A primary callback managing data updates and
      figure rendering.
"""

import base64
import io
from typing import Any, Dict, List, Tuple, Union

import causalimpact
import dash_bootstrap_components as dbc
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from dash import Input, Output, State, callback, html

from src.config import config
from src.data_utils import loaders

matplotlib.use("Agg")

CRYPTOS_MASTER = loaders.load_data(
    config.PROCESSED_DIR, config.PROCESSED_CRYPTOS_PATH
)
CRYPTOS_MASTER["timestamp"] = pd.to_datetime(CRYPTOS_MASTER["timestamp"])
CRYPTOS_MASTER.set_index("timestamp", inplace=True)
CRYPTOS_MASTER.sort_index(inplace=True)


def create_tweet_selector_table(
    table_data: list[dict], active_cell: dict
) -> dbc.Card:
    """
    Generates a Bootstrap Card containing detailed metadata for a selected tweet.

    This function extracts data from a specific row in the DataTable based on
    user interaction and builds a vertical key-value display. It uses monospaced
    fonts and high-contrast colors to ensure tweet metadata (like ID and text)
    is easily readable.

    Args:
        table_data (list[dict]): The complete dataset from the DataTable
            represented as a list of dictionaries (records).
        active_cell (dict): A Dash dictionary containing 'row' and 'column'
            indices of the user's current selection.

    Returns:
        dbc.Card: A styled Dash Bootstrap Component card containing the
            formatted tweet metadata.
    """
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
        display_name = col_name

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


def create_causal_impact_figure(
    num_from: int, num_to: int, created_at: str
) -> causalimpact.CausalImpact:
    """
    Executes a Bayesian Structural Time-Series analysis to estimate causal effect.

    This function prepares the time-series data by loading historical crypto prices,
    aligning them with the tweet's timestamp, and defining 'pre' and 'post'
    intervention periods. It then initializes the CausalImpact model to calculate
    the counterfactual prediction.

    Args:
        num_from (int): Number of minutes prior to the tweet used for training
            the model (pre-period).
        num_to (int): Number of minutes following the tweet used for impact
            prediction (post-period).
        created_at (str): The ISO-formatted timestamp of the tweet event.

    Returns:
        causalimpact.CausalImpact: A fitted CausalImpact object containing
            the statistical results, summary, and internal Matplotlib figures.
    """

    print(created_at)
    created_at = pd.to_datetime(created_at).tz_localize(None).floor("min")

    print(created_at)

    start_date = created_at - pd.Timedelta(minutes=num_from)
    intervention_date = created_at
    end_date = created_at + pd.Timedelta(minutes=num_to)

    pre_period = [
        str(start_date),
        str(intervention_date),
    ]

    post_period = [
        str(intervention_date + pd.Timedelta(minutes=1)),
        str(end_date),
    ]

    analysis_start = pd.to_datetime(pre_period[0])
    analysis_end = pd.to_datetime(post_period[1])
    data_ci = CRYPTOS_MASTER.loc[analysis_start:analysis_end].copy()

    print(len(data_ci))
    print(data_ci)

    data_ci = data_ci.dropna(axis=1, how="any")
    print(data_ci)
    print(len(data_ci))

    print(pre_period)
    print(post_period)

    ci = causalimpact.CausalImpact(data_ci, pre_period, post_period)

    return ci


@callback(
    Output("selection-output", "children"),
    Output("causalimpact-plot-img", "src"),
    Output("causal-summary-text", "children"),
    Output("causal-report-text", "children"),
    Input("num-from-input-causalimpact", "value"),
    Input("num-to-input-causalimpact", "value"),
    State("tweet-selector-table", "data"),
    Input("tweet-selector-table", "active_cell"),
    #  background=True,
    prevent_initial_call=True,
)
def display_row_details(
    num_from: int,
    num_to: int,
    table_data: List[Dict[str, Any]],
    active_cell: Union[Dict[str, Any], None],
) -> Tuple[Union[dbc.Card, str, html.Div], str, str, str]:
    """
    Orchestrates the UI updates for the Causal Impact analysis dashboard.

    This primary callback triggers whenever a user selects a new tweet or
    adjusts the time windows. It handles the end-to-end pipeline: generating
    the metadata card, running the Bayesian model, rendering the Matplotlib
    figure to a base64 string, and cleaning the statistical text summaries.

    Args:
        num_from (int): Training window duration from the numeric input.
        num_to (int): Prediction window duration from the numeric input.
        table_data (list[dict]): Current state of the tweet selection table.
        active_cell (dict): The coordinates of the currently selected table cell.

    Returns:
        tuple: A 4-element tuple containing:
            - card (dbc.Card): The metadata display for the selected tweet.
            - img_src (str): Base64 encoded PNG string of the impact plot.
            - summary (str): A cleaned, multi-line string of quantitative metrics.
            - report (str): The full linguistic interpretation of the causal analysis.
    """

    if not active_cell:
        return "Click on any row to see details.", "", "", ""

    try:
        card = create_tweet_selector_table(table_data, active_cell)
        selected_row = table_data[active_cell["row"]]

        ci = create_causal_impact_figure(
            num_from, num_to, selected_row["created_at"]
        )
        print(ci.summary())
        print(ci.summary("report"))

        ci.plot()

        fig = plt.gcf()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")

        plt.close("all")

        encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        return (
            card,
            f"data:image/png;base64,{encoded_image}",
            "\n".join(ci.summary().splitlines()[:-1]),
            ci.summary("report"),
        )

    except (ValueError, KeyError) as e:
        print(f"Data or Model Error: {e}")
        error_msg = f"Analysis Error: {str(e)}"
        return html.Div(error_msg, className="text-danger"), "", error_msg, ""

    except FileNotFoundError as e:
        print(f"Missing Data File: {e}")
        error_msg = "Critical Error: Price data file not found."
        return html.Div(error_msg, className="text-danger"), "", error_msg, ""

    except RuntimeError as e:
        print(f"Model Execution Error: {e}")
        error_msg = (
            "Analysis Error: The CausalImpact model failed to converge."
        )
        return html.Div(error_msg, className="text-danger"), "", error_msg, ""
