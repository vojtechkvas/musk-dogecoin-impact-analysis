"""
Data transformation and cleaning utilities for social media datasets.

This module provides tools for temporal conversions between datetime objects
and Unix timestamps, chronological filtering, and duplicate detection. It is
specifically optimized for handling tweet DataFrames and ensuring data integrity
before analysis.
"""

from datetime import datetime
from typing import List, Tuple

import pandas as pd
from pandas import DataFrame

from src.config.config import (
    FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
)


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
    cutoff_timestamp = datetime.strptime(cutoff_date, "%Y-%m-%d").timestamp()
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
