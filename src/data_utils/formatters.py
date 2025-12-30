from datetime import datetime, timezone


def convert_date_to_timestamp(
    date_string: str, date_format: str = "%Y-%m-%d"
) -> int:
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
        utc_datetime = datetime_object.replace(tzinfo=timezone.utc)
        return int(utc_datetime.timestamp())
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: {date_string}. Expected {date_format}"
        ) from e


def format_number(number: int | float) -> str:
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
