"""
Module for filtering and processing social media data related to Dogecoin.

This module provides utilities to filter DataFrames based on Dogecoin-related
keywords, convert between Unix timestamps and datetime objects, and prune
data based on specific chronological cutoffs.
"""

from datetime import datetime
from typing import List, Tuple

import pandas as pd
from pandas import DataFrame

from src.config.config import (
    DOGE_KEYWORDS,
    FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
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

    tweet_minutes = pd.to_datetime(tweet_df["timestamp"], unit="s").dt.floor("min")
    stock_minutes = pd.to_datetime(stock_df["timestamp"], unit="s").dt.floor("min")

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


def convert_date_to_timestamp(date_string: str, date_format: str = "%Y-%m-%d") -> int:
    """
    Converts a date string in YYYY-MM-DD format to a Unix timestamp.

    Args:
        date_string (str): The date string to convert.
        date_format (str): The expected format of the date string.
                           Defaults to "%Y-%m-%d".
    Returns:
        int: The corresponding Unix timestamp.
    """

    try:
        datetime_object = datetime.strptime(date_string, date_format)

        return int(datetime_object.timestamp())
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: {date_string}. Expected {date_format}"
        ) from e


def filter_tweets(
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

    mask_orig = df[text_columns[0]].str.contains(regex_pattern, case=False, na=False)
    mask_quote = df[text_columns[1]].str.contains(regex_pattern, case=False, na=False)

    final_mask = mask_orig | mask_quote

    return df[final_mask].copy()


def convert_datetime_to_unix_timestamp(
    df: DataFrame,
    date_column: str = "created_at",
    new_column_name: str = "timestamp",
) -> DataFrame:
    """
    Converts a date-time column in a DataFrame to a Unix timestamp column (seconds).

    WARNING: Uses errors="raise". If any date string is invalid, this function
    will raise a ValueError and crash the calling program unless handled externally.

    Args:
        df: The input DataFrame.
        date_column: The name of the column containing date-time values.
        new_column_name: The name for the new timestamp column.

    Returns:
        The DataFrame with the new timestamp column added.
    """

    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], utc=True, errors="raise")

    df[new_column_name] = df[date_column].astype(int) // 10**9

    df[new_column_name] = df[new_column_name].astype("int64")

    return df


def convert_unix_timestamp_to_datetime(
    df: DataFrame,
    timestamp_column: str = "timestamp",
    new_column_name: str = "created_at",
) -> DataFrame:
    """
    Converts a Unix timestamp column (seconds) to a UTC-aware datetime column.

    Args:
        df: The input DataFrame.
        timestamp_column: The name of the column containing Unix timestamps.
        new_column_name: The name for the new datetime column.

    Returns:
        The DataFrame with the new datetime column added.
    """

    df[new_column_name] = pd.to_datetime(
        df[timestamp_column], unit="s", utc=True, errors="raise"
    )

    return df


def drop_tweets_before_date(
    df: DataFrame,
    timestamp_column: str = "timestamp",
    cutoff_date: str = FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
) -> DataFrame:
    """
    Removes tweets from the DataFrame that occurred before a specific cutoff date.

    Args:
        df: The input DataFrame containing tweet data.
        timestamp_column: The name of the column containing Unix timestamps.
        cutoff_date: A date string in 'YYYY-MM-DD' format representing the threshold.

    Returns:
        A filtered copy of the DataFrame containing only tweets posted before the cutoff.
    """
    cutoff_timestamp = datetime.datetime.strptime(cutoff_date, "%Y-%m-%d").timestamp()
    mask = df[timestamp_column] < cutoff_timestamp

    # print(f"Dropping {len(mask)} {mask.sum()} tweets before {cutoff_date}.")

    df_filtered = df[mask].copy()

    return df_filtered


def find_duplicates(
    df: DataFrame, subset_columns: List[str], display_duplicates: List[str]
) -> Tuple[int, pd.DataFrame]:
    """
    Identifies and optionally prints duplicate rows based on specific columns.

    Args:
        df: The input DataFrame to check for duplicates.
        subset_columns: A list of column names to consider when identifying duplicates.
        display_duplicates: A list of column names to show when printing the sample.

    Returns:
        The total count of duplicate rows found in the DataFrame.
    """

    duplicates = df[df.duplicated(subset=subset_columns, keep=False)].copy()

    output = pd.DataFrame(columns=display_duplicates)
    if not duplicates.empty:
        output = duplicates[display_duplicates]
        if "full_text" in duplicates.columns:
            output = output.sort_values(by="full_text")

    return len(duplicates), output


def print_number(number: int | float) -> str:
    """
    Formats a number as a string with space separators for thousands.

    This function uses an underscore as a temporary separator during formatting
    and replaces it with a space to create a human-readable numeric string.

    Args:
        number: The numeric value (int or float) to be formatted.

    Returns:
        A string representation of the number with spaces as thousands separators.
        Example: 1000000 becomes "1 000 000".
    """
    return f"{number:_}".replace("_", " ")
