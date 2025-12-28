from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import src.config.config as config
import src.data_utils.loaders as loaders
import src.data_utils.processing as processing
from dash import Input, Output, State, callback
from src.config.config import (
    FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
    HOVER_COLUMNS,
    POSTS_TEXT_COLUMN,
    RELATIVE_TIME_SPREAD_HOURS,
)

from ...app import app

STOCK_DATA = loaders.load_data(
    config.PROCESSED_DIR,
    config.PROCESSED_DOGE_PRICE_PATH,
    types=config.DOGE_DTYPES,
    skiprows=1,
)

STOCK_DATA = processing.convert_unix_timestamp_to_datetime(df=STOCK_DATA)

TWEET_DATA = loaders.load_data(
    config.PROCESSED_DIR,
    config.PROCESSED_TWEETS_DOGECOIN_PATH,
    types=config.POSTS_DTYPES,
    skiprows=1,
)

TWEET_DATA = processing.convert_datetime_to_unix_timestamp(df=TWEET_DATA)


print("Data Loaded: STOCK_DATA and TWEET_DATA")


@callback(
    Output("price-volume-graph", "figure"),
    Output("tweet-impact-graph", "figure"),
    #    Output("filtered-tweets-output", "value"),
    Output("kpi-total-tweets", "children"),
    Output("kpi-avg-price", "children"),
    Output("kpi-avg-price-during-tweet", "children"),
    Input("date-from-picker", "date"),
    Input("date-to-picker", "date"),
    Input("text-filter-input", "value"),
    #  prevent_initial_call=True,
)
def update_dashboard(date_from, date_to, text_filter):

    print(
        f"Filters Applied - Date From: {date_from}, Date To: {date_to}, Text Filter: {text_filter}"
    )

    print(f"Raw Date Inputs - From: {date_from}, To: {date_to}")

    if date_from is None or date_to is None:
        print("Date input is None. Returning empty dashboard state.")

        return (
            go.Figure(),
            go.Figure(),
            "Please select both a start and end date.",
            "N/A",
            "N/A",
            "N/A",
        )
    date_from_timestamp = processing.convert_date_to_timestamp(date_from)
    date_to_timestamp = processing.convert_date_to_timestamp(date_to)

    coin_stock_df = STOCK_DATA
    coin_tweet_df = TWEET_DATA

    coin_stock_df = coin_stock_df[
        (coin_stock_df["timestamp"] >= date_from_timestamp)
        & (coin_stock_df["timestamp"] <= date_to_timestamp)
    ]
    coin_tweet_df = coin_tweet_df[
        (coin_tweet_df["timestamp"] >= date_from_timestamp)
        & (coin_tweet_df["timestamp"] <= date_to_timestamp)
    ]

    print(f"Applying text filter: {text_filter}: {POSTS_TEXT_COLUMN}")
    coin_tweet_df = processing.filter_tweets(coin_tweet_df, text_filter)
    print(f"END Applying text filter: {text_filter}: {POSTS_TEXT_COLUMN}")

    fig = go.Figure()
    fig.update_layout(
        template="plotly_dark",
        height=600,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=coin_stock_df["created_at"],
            y=coin_stock_df["open"],
            name="Price (USD)",
            yaxis="y1",
            line=dict(color="blue"),
        )
    )

    colors = px.colors.qualitative.Plotly

    y_min = coin_stock_df["open"].min()
    y_max = coin_stock_df["open"].max()

    for i, (idx, row) in enumerate(coin_tweet_df.iterrows()):
        tweet_text = str(row[POSTS_TEXT_COLUMN])
        tweet_time = row["created_at"]

        short_text = (tweet_text[:30] + "..") if len(tweet_text) > 30 else tweet_text
        short_text = tweet_text

        fig.add_trace(
            go.Scatter(
                x=[tweet_time, tweet_time],
                y=[y_min, y_max],
                mode="lines",
                name=short_text,
                line=dict(color=colors[i % len(colors)], width=1),
                #   legendgroup="tweets",
                showlegend=True,
                hoverinfo="skip",
            )
        )

    coin_tweet_df["timestamp"] = pd.to_datetime(coin_tweet_df["timestamp"], unit="s")

    coin_tweet_df["date_display"] = coin_tweet_df["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    template_lines = [
        f"<b>{col}:</b> %{{customdata[{i}]}}" for i, col in enumerate(HOVER_COLUMNS)
    ]
    full_hovertemplate = "<br>".join(template_lines) + "<extra></extra>"

    fig.add_trace(
        go.Scatter(
            x=coin_tweet_df["created_at"],
            y=[coin_stock_df["open"].mean()] * len(coin_tweet_df),
            mode="markers",
            marker=dict(
                size=15,
                color="rgba(0,0,0,0)",
            ),
            text=coin_tweet_df[POSTS_TEXT_COLUMN],
            customdata=coin_tweet_df[HOVER_COLUMNS],
            hovertemplate=full_hovertemplate,
            name="",
            showlegend=True,
        )
    )

    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified",
    )

    kpi_tweets = f"{len(coin_tweet_df):,}"

    kpi_price = (
        f"{coin_stock_df['open'].mean():,.4f}" if not coin_stock_df.empty else "N/A"
    )

    impact_fig, max_vals = create_tweet_impact_figure(
        coin_tweet_df, coin_stock_df, full_hovertemplate, HOVER_COLUMNS, colors
    )
    print(max_vals)

    avg_price_during_tweet = processing.calculate_avg_price_at_tweet_time(
        coin_tweet_df, coin_stock_df
    )
    print("Dashboard updated successfully.")
    return (
        fig,
        impact_fig,
        kpi_tweets,
        kpi_price,
        f"{avg_price_during_tweet:.4f}",
    )


def create_tweet_impact_figure(
    coin_tweet_df,
    stock_data_full,
    full_hovertemplate,
    hover_columns,
    colors,
    timespread_hours=RELATIVE_TIME_SPREAD_HOURS,
):

    impact_fig = go.Figure()
    impact_fig.update_layout(
        title="Price Impact: 6 hours Before vs 6 hours after Tweets",
        template="plotly_dark",
        xaxis_title="Hours relative to Tweet",
        yaxis_title="Price (USD)",
        hovermode="closest",
        height=1000,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
    )

    print("Creating tweet impact figure...")
    print("Creating tweet impact figure...")

    coin_tweet_df.info()
    max_vals = []
    for i, (kk, tweet) in enumerate(coin_tweet_df.iterrows()):

        color = colors[i % len(colors)]

        t_time = tweet["created_at"].floor("min").timestamp()

        window_df = stock_data_full[
            (stock_data_full["timestamp"] >= t_time - timespread_hours)
            & (stock_data_full["timestamp"] <= t_time + timespread_hours)
        ].copy()

        if not window_df.empty:

            tweet_price_row = window_df[window_df["timestamp"] == t_time]

            if tweet_price_row.empty:
                tweet_price_row = window_df.iloc[
                    (window_df["timestamp"] - t_time).abs().argsort()[:1]
                ]

            price_at_tweet = tweet_price_row["open"].values[0]

            window_df["normalized_price"] = window_df["open"] / price_at_tweet
            window_df["relative_hours"] = (window_df["timestamp"] - t_time) / 3600

            max_val = window_df["normalized_price"].max()
            peak_time = window_df.loc[
                window_df["normalized_price"].idxmax(), "relative_hours"
            ]

            positive_hours_df = window_df[window_df["relative_hours"] > 0]
            max_val = positive_hours_df["normalized_price"].max()
            peak_time_x = positive_hours_df.loc[
                positive_hours_df["normalized_price"].idxmax(), "relative_hours"
            ]
            max_vals.append((max_val, peak_time_x))

            single_tweet_data = [tweet[hover_columns].values] * len(window_df)

            impact_fig.add_trace(
                go.Scatter(
                    x=window_df["relative_hours"],
                    y=window_df["normalized_price"],
                    mode="lines",
                    #     name=f"Tweet at {datetime.fromtimestamp(t_time).strftime('%H:%M')}",
                    name=tweet["full_text"],
                    line=dict(color=color, width=2),
                    opacity=0.6,
                    text=coin_tweet_df[POSTS_TEXT_COLUMN],
                    #    customdata=coin_tweet_df[HOVER_COLUMNS],
                    #    colors[i % len(colors)],
                    customdata=single_tweet_data,
                    hovertemplate=full_hovertemplate,
                    #   name="Tweet Details",
                    showlegend=True,
                )
            )

            impact_fig.add_vline(
                x=peak_time_x,
                line_dash="dot",
                line_width=1,
                line_color=color,
                opacity=0.5,
            )

    return impact_fig, max_vals


@app.callback(
    Output("date-to-picker", "date"),
    [
        Input("mentionning-of-doge-department-button", "n_clicks"),
    ],
    [
        State("date-to-picker", "date"),
    ],
    prevent_initial_call=True,
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
