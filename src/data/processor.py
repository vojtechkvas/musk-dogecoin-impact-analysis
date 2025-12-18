from src.config.settings import DOGE_KEYWORDS, POSTS_TEXT, QUOTE_TEXT, FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE
import pandas as pd
from pandas import DataFrame
import datetime

def get_tweets_related_to_dogecoin(
    df, doge_keywords=DOGE_KEYWORDS, text_column=POSTS_TEXT
):
    regex_pattern = "|".join(doge_keywords)

    mask = df[text_column].str.contains(regex_pattern, case=False, na=False)

    return df[mask].copy()


def get_tweets_related_to_dogecoin_quote(
    df, doge_keywords=DOGE_KEYWORDS, text_columns=QUOTE_TEXT
):
    regex_pattern = "|".join(doge_keywords)

    mask_orig = df[text_columns[0]].str.contains(regex_pattern, case=False, na=False)
    mask_quote = df[text_columns[1]].str.contains(regex_pattern, case=False, na=False)

    final_mask = mask_orig | mask_quote

    return df[final_mask].copy()


def convert_datetime_to_unix_timestamp(
    df: DataFrame,
    date_column: str = "created_at",
    new_column_name: str = "timestamp",
    downcast_to_int: bool = True,
) -> DataFrame:
    """
    Converts a date-time column in a DataFrame to a Unix timestamp column (seconds).

    WARNING: Uses errors="raise". If any date string is invalid, this function
    will raise a ValueError and crash the calling program unless handled externally.

    Args:
        df: The input DataFrame.
        date_column: The name of the column containing date-time values.
        new_column_name: The name for the new timestamp column.
        downcast_to_int: If True, the resulting timestamp will be an integer type.

    Returns:
        The DataFrame with the new timestamp column added.
    """
    df[date_column + "_date"] = pd.to_datetime(
        df[date_column], utc=True, errors="raise"
    )

    df[new_column_name] = df[date_column + "_date"].astype(int) // 10**9

    if downcast_to_int:
        df[new_column_name] = df[new_column_name].astype("int64")

    return df

def convert_unix_timestamp_to_datetime(
    df: DataFrame,
    timestamp_column: str = "timestamp",
    new_column_name: str = "created_at"
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
            df[timestamp_column], 
            unit="s", 
            utc=True, 
            errors="raise"
        )

    return df


def drop_tweets_before_date(
    df: DataFrame,
    timestamp_column: str = "timestamp",
    cutoff_date: str = FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE,
) -> DataFrame:
   
    cutoff_timestamp = datetime.datetime.strptime(cutoff_date, "%Y-%m-%d").timestamp()
    mask = df[timestamp_column] <  cutoff_timestamp
    
    print(f"Dropping {len(mask)} {mask.sum()} tweets before {cutoff_date}.")
    
    df_filtered = df[mask].copy()
  

    return df_filtered
 