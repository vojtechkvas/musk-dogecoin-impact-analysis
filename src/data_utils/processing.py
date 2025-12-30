"""
Core processing utilities for social media and financial data analysis.

This module provides specialized filtering and calculation tools designed to
analyze the relationship between social media posts (specifically Dogecoin-related)
and asset pricing. It includes logic for keyword-based filtering across multiple
text columns and temporal alignment between tweet timestamps and stock market data.
"""

from typing import List

import pandas as pd
from pandas import DataFrame

from src.config.config import (
    DOGE_KEYWORDS,
    POSTS_TEXT_COLUMN,
    QUOTE_TEXT,
)


def calculate_avg_price_at_tweet_time(
    tweet_df: pd.DataFrame, stock_df: pd.DataFrame
) -> float:
    """
    Calculates the average asset price at the specific minutes tweets were
    posted by rounding timestamps to the nearest minute.

    Args:
        tweet_df (pd.DataFrame): DataFrame containing tweet data with
                                a 'timestamp' column.
        stock_df (pd.DataFrame): DataFrame containing stock data with
                                'timestamp' and 'open' columns.

    Returns:
        float: The average price at the time of tweets. Returns 0.0 if data is
               missing or no matches are found.
    """

    if tweet_df.empty or stock_df.empty:
        return 0.0

    tweet_minutes = pd.to_datetime(tweet_df["timestamp"], unit="s").dt.floor(
        "min"
    )
    stock_minutes = pd.to_datetime(stock_df["timestamp"], unit="s").dt.floor(
        "min"
    )

    price_lookup = pd.DataFrame(
        {"align_dt": stock_minutes, "price": stock_df["open"]}
    ).drop_duplicates(subset=["align_dt"])

    tweets_with_price = pd.merge(
        pd.DataFrame({"align_dt": tweet_minutes}),
        price_lookup,
        on="align_dt",
        how="left",
    )

    avg_val = tweets_with_price["price"].mean()

    if pd.isna(avg_val):
        return 0.0

    return float(avg_val)


def filter_tweets_by_keyword(
    df: pd.DataFrame, keyword: str, text_column: str = POSTS_TEXT_COLUMN
) -> DataFrame:
    """
    Filters a DataFrame for rows where the text column contains a specific keyword.

    The search is case-insensitive and handles missing (NaN) values by excluding them.

    Args:
        df (pd.DataFrame): The DataFrame containing tweet or post data.
        keyword (str): The string to search for. If empty, the original
            DataFrame is returned.
        text_column (str): The name of the column to search within.
            Defaults to POSTS_TEXT_COLUMN.

    Returns:
        pd.DataFrame: A filtered copy of the DataFrame containing only rows
            where the keyword was found.
    """
    if not keyword:
        return df

    mask = df[text_column].str.contains(keyword, case=False, na=False)

    return df[mask].copy()


def get_posts_related_to_dogecoin(
    df: pd.DataFrame,
    doge_keywords: List[str] = None,
    text_column: str = None,
) -> DataFrame:
    """
    Filters a DataFrame for rows where the text column contains specific Dogecoin keywords.

    Args:
        df: The input DataFrame containing social media posts.
        doge_keywords: A list of strings/keywords to search for.
        text_column: The name of the column containing the text to be searched.

    Returns:
        A filtered copy of the original DataFrame containing only relevant tweets.
    """
    if doge_keywords is None:
        doge_keywords = DOGE_KEYWORDS
    if text_column is None:
        text_column = POSTS_TEXT_COLUMN

    regex_pattern = "|".join(doge_keywords)

    mask = df[text_column].str.contains(regex_pattern, case=False, na=False)

    return df[mask].copy()


def get_repost_related_to_dogecoin_quote(
    df: pd.DataFrame,
    doge_keywords: List[str] = None,
    text_columns: List[str] = None,
) -> DataFrame:
    """
    Filters a DataFrame for reposts or quotes that mention Dogecoin in either
    the original post or the quoted content.

    Args:
        df: The input DataFrame containing repost/quote data.
        doge_keywords: A list of strings/keywords to search for.
        text_columns: A list containing the names of the columns for the
            original text and the quoted text (e.g., [original_col, quote_col]).

    Returns:
        A filtered copy of the DataFrame where at least one text column
        matches the keywords.
    """
    if doge_keywords is None:
        doge_keywords = DOGE_KEYWORDS
    if text_columns is None:
        text_columns = QUOTE_TEXT

    regex_pattern = "|".join(doge_keywords)

    mask_orig = df[text_columns[0]].str.contains(
        regex_pattern, case=False, na=False
    )
    mask_quote = df[text_columns[1]].str.contains(
        regex_pattern, case=False, na=False
    )

    final_mask = mask_orig | mask_quote

    return df[final_mask].copy()
