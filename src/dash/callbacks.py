from dash import callback, Output, Input, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from .app import app

import src.data.processor as processor
import src.data.loader as loader
import src.config.settings as settings

from src.config.settings import (
    DOGE_MIN_DATE,
    DOGE_KEYWORDS,
    POSTS_TEXT,
    QUOTE_TEXT,
    FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
)


STOCK_DATA = loader.load_data(
    settings.RAW_DIR,
    "DOGEUSDT.csv",
    settings.CSV_SEPARATOR_DOGEUSDT,
    settings.DOGE_DTYPES,
)
TWEET_DATA = loader.load_data(
    settings.RAW_DIR, "all_musk_posts.csv", types=settings.POSTS_DTYPES, skiprows=1
)

TWEET_DATA = processor.convert_datetime_to_unix_timestamp(df=TWEET_DATA)

TEXT = POSTS_TEXT


@callback(
    Output("price-volume-graph", "figure"),
    Output("filtered-tweets-output", "value"),
    Output("kpi-total-tweets", "children"),
    Output("kpi-avg-price", "children"),
    Output("kpi-sentiment", "children"),
    Input("date-from-picker", "date"),
    Input("date-to-picker", "date"),
    Input("text-filter-input", "value"),
)
def update_dashboard(date_from, date_to, text_filter):

    selected_coin = "selected_coin"
    print(
        f"Filters Applied - Coin: {selected_coin}, Date From: {date_from}, Date To: {date_to}, Text Filter: {text_filter}"
    )

    date_format = "%d %m %Y %H:%M:%S"
    date_format = "%Y-%m-%d"

    print(f"Raw Date Inputs - From: {date_from}, To: {date_to}")

    if date_from is None or date_to is None:
        print("Date input is None. Returning empty dashboard state.")
        # Return a blank figure and placeholder values for all outputs
        return (
            go.Figure(),
            "Please select both a start and end date.",
            "N/A",
            "$ N/A",
            "N/A",
        )

    datetime_object = datetime.strptime(date_from, date_format)
    date_from = datetime_object.timestamp()

    print(f"Timestamp Range - From: ")

    datetime_object = datetime.strptime(date_to, date_format)
    date_to = datetime_object.timestamp()

    coin_stock_df = STOCK_DATA
    coin_tweet_df = TWEET_DATA

    coin_stock_df = coin_stock_df[
        (coin_stock_df["timestamp"] >= date_from)
        & (coin_stock_df["timestamp"] <= date_to)
    ]
    coin_tweet_df = coin_tweet_df[
        (coin_tweet_df["timestamp"] >= date_from)
        & (coin_tweet_df["timestamp"] <= date_to)
    ]

    if text_filter:
        coin_tweet_df = coin_tweet_df[
            coin_tweet_df[TEXT].str.contains(text_filter, case=False, na=False)
        ]

    fig = go.Figure()
    fig.update_layout(template="plotly_dark")
    fig.add_trace(
        go.Scatter(
            x=coin_stock_df["timestamp"],
            y=coin_stock_df["open"],
            name="Price (USD)",
            yaxis="y1",
            line=dict(color="blue"),
        )
    )
    """
    fig.add_trace(go.Bar(
        x=coin_tweet_df['timestamp'],
        y=coin_stock_df['open'],
        name='Tweet Volume',
        yaxis='y2',
        marker=dict(color='orange', opacity=0.6)
    ))
    """

    tweets_text = "www"

    kpi_tweets = f"{len(coin_tweet_df):,}"

    kpi_price = (
        f"${coin_stock_df['open'].mean():,.4f}" if not coin_stock_df.empty else "$ N/A"
    )

    kpi_sentiment = ""

    return fig, tweets_text, kpi_tweets, kpi_price, kpi_sentiment


@app.callback(
    Output("date-to-picker", "date"),
    [
        Input("mentionning-of-doge-department-button", "n_clicks"),
    ],
    [
        State("date-to-picker", "date"),
    ],
)
def update_date_picker(n_clicks, current_date):
    """
    Sets the date-to-picker to the DOGE mention date *only* when the button is clicked.
    The date picker's manual changes will not trigger this callback.
    """

    if n_clicks is not None and n_clicks > 0:
        return FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE
    else:
        return current_date
