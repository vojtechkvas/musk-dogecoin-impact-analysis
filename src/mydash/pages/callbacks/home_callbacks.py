"""
Dashboard Callback Module for Dogecoin Price and Social Media Impact Analysis.

This module orchestrates the reactive data pipeline for the primary dashboard.
It manages the high-performance loading of historical price and social data,
processes user-driven filtering (temporal and textual), and updates complex
Plotly visualizations to reveal correlation patterns between influencer
activity and cryptocurrency volatility.

Key Functionalities:
    - Data Initialization: Loads and synchronizes multi-source datasets
      (Binance price history and Twitter/X archives) with optimized timestamp
      conversions.
    - Multi-Axis Plotting: Constructs primary price-volume figures with
      overlaid event markers and standardized unified hover templates.
    - Normalization Analysis: Calculates and visualizes "Tweet Impact"
      trajectories by normalizing asset prices to the exact minute of a
      social media post.
    - KPI Orchestration: Reactive calculation of aggregate metrics, including
      volume counts and average prices during specified periods.
    - Temporal Controls: Provides specialized shortcuts for historical
      milestones, such as the initial mention of the DOGE department.
"""

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
from src.data_utils import formatters, loaders, processing, utils

STOCK_DATA = loaders.load_data(
    config.PROCESSED_DIR,
    config.PROCESSED_DOGE_PRICE_PATH,
    types=config.DOGE_DTYPES,
    skiprows=1,
)

TWEET_DATA = loaders.load_data(
    config.PROCESSED_DIR,
    config.PROCESSED_TWEETS_DOGECOIN_PATH,
    types=config.POSTS_DTYPES,
    skiprows=1,
)

STOCK_DATA = utils.convert_unix_timestamp_to_datetime(df=STOCK_DATA)
TWEET_DATA = utils.convert_datetime_to_unix_timestamp(df=TWEET_DATA)


print("Data Loaded: STOCK_DATA and TWEET_DATA")


def _build_main_price_figure(
    coin_stock_df: pd.DataFrame, coin_tweet_df: pd.DataFrame
) -> tuple[go.Figure, str, list[str]]:
    """
    Constructs the primary price-volume Scatter plot and generates visual metadata.

    This helper function handles the dark-mode layout configuration, plots the
    asset price line, adds vertical markers for tweet events, and constructs
    the standardized hover template used across dashboard figures.

    Args:
        coin_stock_df (pd.DataFrame): DataFrame containing stock price data
            with 'created_at' and 'open' columns.
        coin_tweet_df (pd.DataFrame): DataFrame containing filtered tweet data
            with 'created_at' and content columns.

    Returns:
        tuple: A 3-element tuple containing:
            - fig (go.Figure): The main Plotly Figure with price and tweet traces.
            - full_hovertemplate (str): The HTML string for unified hover styling.
            - colors (list[str]): The qualitative color palette used for traces.
    """
    fig = go.Figure()
    fig.update_layout(
        template="plotly_dark",
        height=600,
        font={"size": 18},
        xaxis_title={"text": "Ti", "font": {"size": 20}},
        yaxis_title={"text": "USDT", "font": {"size": 20}},
        legend={
            "font": {"size": 16},
            "orientation": "h",
            "yanchor": "top",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5,
        },
        hoverlabel={"font_size": 18},
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

    for i, (_, row) in enumerate(coin_tweet_df.iterrows()):

        fig.add_trace(
            go.Scatter(
                x=[row["created_at"], row["created_at"]],
                y=[y_min, y_max],
                mode="lines",
                name=str(row[POSTS_TEXT_COLUMN]),
                line={"color": colors[i % len(colors)], "width": 1},
                showlegend=True,
                hoverinfo="skip",
            )
        )

    coin_tweet_df["timestamp"] = pd.to_datetime(
        coin_tweet_df["timestamp"], unit="s"
    )

    coin_tweet_df["date_display"] = coin_tweet_df["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    template_lines = [
        f"<b>{col}:</b> %{{customdata[{i}]}}"
        for i, col in enumerate(HOVER_COLUMNS)
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
    return fig, full_hovertemplate, colors


@callback(
    Output("price-volume-graph", "figure"),
    Output("tweet-impact-graph", "figure"),
    Output("kpi-total-tweets", "children"),
    Output("kpi-avg-price", "children"),
    Output("kpi-avg-price-during-tweet", "children"),
    Input("date-from-picker", "date"),
    Input("date-to-picker", "date"),
    Input("text-filter-input", "value"),
)
def update_dashboard(
    date_from: str, date_to: str, text_filter: str
) -> tuple[go.Figure, go.Figure, str, str, str]:
    """
    Updates the dashboard visualizations and KPIs based on user-selected
    filters for dates and tweet content.

    Args:
        date_from (str): The start date string from the date picker (ISO format).
        date_to (str): The end date string from the date picker (ISO format).
        text_filter (str): Text query to filter tweets by their content.

    Returns:
        tuple: A 5-element tuple containing:
            - fig (go.Figure): The price-volume Scatter plot with tweet markers.
            - impact_fig (go.Figure): The relative time impact analysis figure.
            - total_tweets_kpi (str): Formatted string of total filtered tweets.
            - avg_price_kpi (str): Formatted string of the mean stock price.
            - impact_kpi (str): Formatted string of avg price at tweet timestamps.
    """

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
    date_from_timestamp = formatters.convert_date_to_timestamp(date_from)
    date_to_timestamp = formatters.convert_date_to_timestamp(date_to)

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
    coin_tweet_df = processing.filter_tweets_by_keyword(
        coin_tweet_df, text_filter
    )
    print(f"END Applying text filter: {text_filter}: {POSTS_TEXT_COLUMN}")

    fig, full_hovertemplate, colors = _build_main_price_figure(
        coin_stock_df, coin_tweet_df
    )

    kpi_price = (
        f"{coin_stock_df['open'].mean():,.4f}"
        if not coin_stock_df.empty
        else "N/A"
    )

    impact_fig, _ = create_tweet_impact_figure(
        coin_tweet_df, coin_stock_df, full_hovertemplate, colors
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


def _add_average_trend(
    impact_fig: go.Figure, all_normalized_series: list[pd.DataFrame]
) -> None:
    """
    Calculates and plots the aggregate average price trend across all tweet events.

    This helper function takes individual normalized price windows, computes the
    mean price for each relative time step, and adds a high-visibility trend
    line and peak annotation to the impact figure.

    Args:
        impact_fig (go.Figure): The Plotly figure object to which the average
            trend trace will be added.
        all_normalized_series (list[pd.DataFrame]): A list of DataFrames, where
            each contains 'relative_hours' and 'normalized_price' for a single
            tweet event.

    Returns:
        None: The function modifies the impact_fig object in-place.
    """
    if all_normalized_series:
        agg_df = pd.concat(all_normalized_series)
        agg_df["relative_hours"] = agg_df["relative_hours"].round(4)
        mean_impact = (
            agg_df.groupby("relative_hours")["normalized_price"]
            .mean()
            .reset_index()
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


def _process_single_tweet(
    tweet: pd.Series,
    stock_data_full: pd.DataFrame,
    color: str,
    impact_fig: go.Figure,
    full_hovertemplate: str,
) -> tuple[pd.DataFrame | None, tuple[float, float] | None]:
    """
    Computes and plots the normalized price impact for a single tweet event.

    This helper function extracts a relative time window around the tweet's
    creation time, normalizes asset prices to the price at tweet-time,
    plots the resulting price trajectory on the provided Plotly figure,
    and identifies the peak post-tweet price movement.

    Args:
        tweet (pd.Series): A single row from the tweet DataFrame containing
            tweet metadata, including the 'created_at' timestamp.
        stock_data_full (pd.DataFrame): Full historical price data with
            'timestamp' and 'open' price columns.
        color (str): Color used for the tweet's price trajectory and
            associated annotations.
        impact_fig (go.Figure): Plotly figure to which the tweet impact
            trace and peak marker will be added.
        full_hovertemplate (str): HTML hover template used to render
            detailed tweet metadata on hover.

    Returns:
        tuple: A 2-element tuple containing:
            - pd.DataFrame | None: DataFrame with 'relative_hours' and
              'normalized_price' for the tweet window, or None if no
              valid price data was available.
            - tuple[float, float] | None: A tuple of (peak_price, peak_hour)
              for the post-tweet window, or None if no post-event peak exists.
    """
    t_time = tweet["created_at"].floor("min").timestamp()

    window_df = stock_data_full[
        (stock_data_full["timestamp"] >= t_time - RELATIVE_TIME_SPREAD_HOURS)
        & (stock_data_full["timestamp"] <= t_time + RELATIVE_TIME_SPREAD_HOURS)
    ].copy()

    if window_df.empty:
        return None, None

    tweet_price_row = window_df[window_df["timestamp"] == t_time]
    if tweet_price_row.empty:
        tweet_price_row = window_df.iloc[
            (window_df["timestamp"] - t_time).abs().argsort()[:1]
        ]

    price_at_tweet = tweet_price_row["open"].iloc[0]
    window_df["normalized_price"] = window_df["open"] / price_at_tweet
    window_df["relative_hours"] = (window_df["timestamp"] - t_time) / 3600

    positive_df = window_df[window_df["relative_hours"] > 0]
    peak_info = None

    if not positive_df.empty:
        max_val = positive_df["normalized_price"].max()
        peak_x = positive_df.loc[
            positive_df["normalized_price"].idxmax(), "relative_hours"
        ]

        impact_fig.add_vline(
            x=peak_x,
            line_dash="dot",
            line_width=1,
            line_color=color,
            opacity=0.3,
        )

        peak_info = (max_val, peak_x)

    customdata = [tweet[HOVER_COLUMNS].values] * len(window_df)

    impact_fig.add_trace(
        go.Scatter(
            x=window_df["relative_hours"],
            y=window_df["normalized_price"],
            mode="lines",
            name=f"{tweet['full_text']}",
            line={"color": color, "width": 1.5},
            opacity=0.4,
            customdata=customdata,
            hovertemplate=full_hovertemplate,
        )
    )

    return window_df[["relative_hours", "normalized_price"]], peak_info


def create_tweet_impact_figure(
    coin_tweet_df: pd.DataFrame,
    stock_data_full: pd.DataFrame,
    full_hovertemplate: str,
    colors: list[str],
) -> tuple[go.Figure, list[tuple[float, float]]]:
    """
    Creates a Plotly figure showing the normalized price impact of tweets
    over a relative time window.

    This function calculates asset price changes relative to the exact moment
    a tweet was posted, normalizes those prices (setting the price at
    tweet-time to 1.0), and plots both individual tweet impacts and an
    aggregated average trend.

    Args:
        coin_tweet_df (pd.DataFrame): DataFrame containing filtered tweet data
            with 'created_at' and 'timestamp' columns.
        stock_data_full (pd.DataFrame): The complete historical stock price
            DataFrame with 'timestamp' and 'open' columns.
        full_hovertemplate (str): A string defining the HTML layout for the
            Plotly hover labels.
        colors (list[str]): A list of color hex codes or names to cycle through
            for different tweet traces.

    Returns:
        tuple: A 2-element tuple containing:
            - impact_fig (go.Figure): The generated Plotly figure showing
              normalized price trajectories.
            - max_vals (list[tuple[float, float]]): A list of tuples containing
              (peak_price, peak_hour) for each tweet's post-event window.
    """
    impact_fig = go.Figure()
    impact_fig.update_layout(
        title={
            "text": "Price Impact: 6 hours Before vs 6 hours after Tweets",
            "font": {"size": 24},
        },
        template="plotly_dark",
        xaxis_title={"text": "Hours relative to Tweet", "font": {"size": 20}},
        yaxis_title={"text": "Normalized Price", "font": {"size": 20}},
        hovermode="closest",
        height=900,
        font={"size": 18},
        legend={
            "font": {"size": 16},
            "orientation": "v",
            "yanchor": "top",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    max_vals: list[tuple[float, float]] = []
    all_normalized_series: list[pd.DataFrame] = []

    for i, (_, tweet) in enumerate(coin_tweet_df.iterrows()):
        color = colors[i % len(colors)]

        series_df, peak_info = _process_single_tweet(
            tweet=tweet,
            stock_data_full=stock_data_full,
            color=color,
            impact_fig=impact_fig,
            full_hovertemplate=full_hovertemplate,
        )

        if series_df is not None:
            all_normalized_series.append(series_df)

        if peak_info is not None:
            max_vals.append(peak_info)

    _add_average_trend(impact_fig, all_normalized_series)

    return impact_fig, max_vals


@callback(
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

    return current_date
