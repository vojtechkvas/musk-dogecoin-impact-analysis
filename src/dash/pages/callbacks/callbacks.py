from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import Input, Output, State, callback
from src.config import config
from src.config.config import (
    FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
    HOVER_COLUMNS,
    POSTS_TEXT_COLUMN,
    RELATIVE_TIME_SPREAD_HOURS,
)
from src.dash.app import app
from src.data_utils import loaders, processing

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
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5,
        },
    )
    fig.add_trace(
        go.Scatter(
            x=coin_stock_df["created_at"],
            y=coin_stock_df["open"],
            name="Price (USD)",
            yaxis="y1",
            line={"color": "blue"},
        )
    )

    colors = px.colors.qualitative.Plotly

    y_min = coin_stock_df["open"].min()
    y_max = coin_stock_df["open"].max()

    for i, (idx, row) in enumerate(coin_tweet_df.iterrows()):

        fig.add_trace(
            go.Scatter(
                x=[row["created_at"], row["created_at"]],
                y=[y_min, y_max],
                mode="lines",
                name=str(row[POSTS_TEXT_COLUMN]),
                line={"color": colors[i % len(colors)], "width": 1},
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
            marker={
                "size": 15,
                "color": "rgba(0,0,0,0)",
            },
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

    kpi_price = (
        f"{coin_stock_df['open'].mean():,.4f}" if not coin_stock_df.empty else "N/A"
    )

    impact_fig, _ = create_tweet_impact_figure(
        coin_tweet_df, coin_stock_df, full_hovertemplate, HOVER_COLUMNS, colors
    )

    avg_price_during_tweet = processing.calculate_avg_price_at_tweet_time(
        coin_tweet_df, coin_stock_df
    )
    print("Dashboard updated successfully.")
    return (
        fig,
        impact_fig,
        f"{len(coin_tweet_df):,}",
        kpi_price,
        f"{avg_price_during_tweet:.4f}",
    )


def create_tweet_impact_figure(
    coin_tweet_df,
    stock_data_full,
    full_hovertemplate,
    hover_columns,
    colors,
):
    impact_fig = go.Figure()
    impact_fig.update_layout(
        title="Price Impact: 6 hours Before vs 6 hours after Tweets",
        template="plotly_dark",
        xaxis_title="Hours relative to Tweet",
        yaxis_title="Normalized Price (Relative to Tweet)",
        hovermode="closest",
        height=900,
        legend={
            "orientation": "v",
            "yanchor": "top",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    max_vals = []
    all_normalized_series = []

    for i, (kk, tweet) in enumerate(coin_tweet_df.iterrows()):
        color = colors[i % len(colors)]
        t_time = tweet["created_at"].floor("min").timestamp()

        window_df = stock_data_full[
            (stock_data_full["timestamp"] >= t_time - RELATIVE_TIME_SPREAD_HOURS)
            & (stock_data_full["timestamp"] <= t_time + RELATIVE_TIME_SPREAD_HOURS)
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

            all_normalized_series.append(
                window_df[["relative_hours", "normalized_price"]]
            )

            positive_hours_df = window_df[window_df["relative_hours"] > 0]
            if not positive_hours_df.empty:
                max_val = positive_hours_df["normalized_price"].max()
                peak_time_x = positive_hours_df.loc[
                    positive_hours_df["normalized_price"].idxmax(), "relative_hours"
                ]
                max_vals.append((max_val, peak_time_x))

                impact_fig.add_vline(
                    x=peak_time_x,
                    line_dash="dot",
                    line_width=1,
                    line_color=color,
                    opacity=0.3,
                )

            single_tweet_data = [tweet[hover_columns].values] * len(window_df)
            impact_fig.add_trace(
                go.Scatter(
                    x=window_df["relative_hours"],
                    y=window_df["normalized_price"],
                    mode="lines",
                    name=f"Tweet: {tweet['full_text'][:30]}...",
                    line={"color": color, "width": 1.5},
                    opacity=0.4,
                    customdata=single_tweet_data,
                    hovertemplate=full_hovertemplate,
                )
            )

    if all_normalized_series:
        agg_df = pd.concat(all_normalized_series)
        agg_df["relative_hours"] = agg_df["relative_hours"].round(4)
        mean_impact = (
            agg_df.groupby("relative_hours")["normalized_price"].mean().reset_index()
        )

        agg_post_tweet = mean_impact[mean_impact["relative_hours"] > 0]
        if not agg_post_tweet.empty:
            agg_max_val = agg_post_tweet["normalized_price"].max()
            agg_peak_x = agg_post_tweet.loc[
                agg_post_tweet["normalized_price"].idxmax(), "relative_hours"
            ]

            impact_fig.add_trace(
                go.Scatter(
                    x=mean_impact["relative_hours"],
                    y=mean_impact["normalized_price"],
                    mode="lines",
                    name="AVERAGE IMPACT",
                    line={"color": "white", "width": 3},
                    opacity=1.0,
                    hovertemplate=(
                        "<b>AVERAGE TREND</b><br>"
                        + "Rel. Time: %{x:.2f}h<br>"
                        + "Avg Change: %{y:.4f}x<br>"
                        + "<extra></extra>"
                    ),
                )
            )

            impact_fig.add_vline(
                x=agg_peak_x,
                line_dash="dash",
                line_width=3,
                line_color="white",
                annotation_text=f"AVG PEAK: {agg_max_val:.3f}x",
                annotation_position="top right",
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
