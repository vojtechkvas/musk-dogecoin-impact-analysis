from dash import callback, Output, Input, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from ...app import app

import src.data.processor as processor
import src.data.loader as loader
import src.config.settings as settings

from src.config.settings import (
    DOGE_MIN_DATE,
    DOGE_KEYWORDS,
    POSTS_TEXT_COLUMN,
    QUOTE_TEXT,
    FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
    TWEET_COLOR,
    RELATIVE_TIME_SPREAD_HOURS
)


STOCK_DATA = loader.load_data(
    settings.RAW_DIR,
    "DOGEUSDT.csv",
    settings.CSV_SEPARATOR_DOGEUSDT,
    settings.DOGE_DTYPES,
)
STOCK_DATA = processor.convert_unix_timestamp_to_datetime(df=STOCK_DATA)

TWEET_DATA = loader.load_data(
    settings.RAW_DIR, "all_musk_posts.csv", types=settings.POSTS_DTYPES, skiprows=1
)

TWEET_DATA = processor.convert_datetime_to_unix_timestamp(df=TWEET_DATA)


print("Data Loaded: STOCK_DATA and TWEET_DATA")


@callback(
    Output("price-volume-graph", "figure"),
    Output("tweet-impact-graph", "figure"),
    Output("filtered-tweets-output", "value"),
    Output("kpi-total-tweets", "children"),
    Output("kpi-avg-price", "children"),
    Output("kpi-sentiment", "children"),
    Input("date-from-picker", "date"),
    Input("date-to-picker", "date"),
    Input("text-filter-input", "value"),
    #  prevent_initial_call=True
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

        return (
            go.Figure(),
            go.Figure(),
            "Please select both a start and end date.",
            "N/A",
            "$ N/A",
            "N/A",
        )

    datetime_object = datetime.strptime(date_from, date_format)
    date_from_timestamp = datetime_object.timestamp()

    print(f"Timestamp Range - From: ")

    datetime_object = datetime.strptime(date_to, date_format)
    date_to_timestamp = datetime_object.timestamp()

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

    if text_filter:
        print(f"Applying text filter: {text_filter}: {POSTS_TEXT_COLUMN}")
        coin_tweet_df = coin_tweet_df[
            coin_tweet_df[POSTS_TEXT_COLUMN].str.contains(
                text_filter, case=False, na=False
            )
        ]
        print(f"END Applying text filter: {text_filter}: {POSTS_TEXT_COLUMN}")

    fig = go.Figure()
    fig.update_layout(template="plotly_dark")
    fig.add_trace(
        go.Scatter(
            x=coin_stock_df["created_at"],
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
    
    
    colors = px.colors.qualitative.Plotly

  #   for tweet_time in coin_tweet_df["created_at"]:
    for i, tweet_time in enumerate(coin_tweet_df["created_at"]):
        fig.add_vline(
            x=tweet_time,
            line_width=1,
            #    line_dash="dash",
            line_color=colors[i % len(colors)],
            layer="below",
        )

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
            name="Tweet Details",
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig.update_layout(template="plotly_dark", hovermode="x unified")

    tweets_text = "www"

    kpi_tweets = f"{len(coin_tweet_df):,}"

    kpi_price = (
        f"${coin_stock_df['open'].mean():,.4f}" if not coin_stock_df.empty else "$ N/A"
    )

    kpi_sentiment = ""
    print("Dashboard updated successfully.")



    impact_fig = create_tweet_impact_figure(coin_tweet_df, coin_stock_df, colors)




    return fig, impact_fig, tweets_text, kpi_tweets, kpi_price, kpi_sentiment



def create_tweet_impact_figure(coin_tweet_df, stock_data_full, colors, timespread_hours=RELATIVE_TIME_SPREAD_HOURS):


    impact_fig = go.Figure()
    impact_fig.update_layout(
        title="Price Impact: 6 hours Before vs 6 hours after Tweets",
        template="plotly_dark",
        xaxis_title="Hours relative to Tweet",
        yaxis_title="Price (USD)",
        hovermode="closest"
    )

    
    
    print("Creating tweet impact figure...")
    print("Creating tweet impact figure...")
    print("Creating tweet impact figure...")
    print("Creating tweet impact figure...")
    print("Creating tweet impact figure...")
    
    print()
    
    coin_tweet_df.info()
    
        
    for i, (kk, tweet) in enumerate(coin_tweet_df.iterrows()):
     
        color = colors[i % len(colors)]
     
      #  print(kk)
      #  print(tweet)
        t_time = tweet["created_at"].floor("min").timestamp()
        print(f"Processing tweet at time: {tweet['timestamp'] }")
        print(f"Processing tweet at time: {t_time}")
        print(f"created_at tweet at time: { (tweet['created_at'] )}")
        print(f"created_at tweet at time: { (tweet['created_at'] ) }")
        print(f"created_at tweet at time: {type(tweet['created_at'] )}")
 
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

            # Create a relative time column (0 = the moment of the tweet)

            window_df["normalized_price"] = window_df["open"] / price_at_tweet
            window_df["relative_hours"] = (window_df["timestamp"] - t_time) / 3600
            
            max_val = window_df["normalized_price"].max()
            peak_time = window_df.loc[window_df["normalized_price"].idxmax(), "relative_hours"]
            peak_time_x = window_df.loc[window_df["normalized_price"].idxmax(), "relative_hours"]
            
            positive_hours_df = window_df[window_df["relative_hours"] > 0]
            peak_time_x = positive_hours_df.loc[positive_hours_df["normalized_price"].idxmax(), "relative_hours"]
            print(window_df["relative_hours"].min(), window_df["relative_hours"].max())
            impact_fig.add_trace(
                go.Scatter(
                    x=window_df["relative_hours"],
                    y=window_df["normalized_price"],
                    mode="lines",
                    name=f"Tweet at {datetime.fromtimestamp(t_time).strftime('%H:%M')}",
                    line=dict(color=color, width=2),
                    opacity=0.6,
                    hovertemplate="Hour: %{x}<br>Price: %{y}<extra></extra>",
                )
            )
            """
            impact_fig.add_hline(
                y=max_val,
                line_dash="dot",
                line_width=1,
                line_color=color,
                annotation_text=f"Peak: {max_val:.2f}",
                annotation_position="top right",
                opacity=0.5
            )
            """
            impact_fig.add_vline(
                x=peak_time_x,
                line_dash="dot",
                line_width=1,
                line_color=color,
                opacity=0.5
            )
            
    # Add a central vertical line representing the exact tweet moment
   #   impact_fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="white")
   #   impact_fig.add_hline(y=1.0, line_width=1, line_color="pink", line_dash="dash")
    
    return impact_fig




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
