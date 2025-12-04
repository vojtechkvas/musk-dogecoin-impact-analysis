from src.config.settings import DOGE_KEYWORDS, POSTS_TEXT, QUOTE_TEXT
import pandas as pd
from pandas import DataFrame


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
