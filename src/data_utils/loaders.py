"""
Module for handling data I/O operations.

This module provides utility functions to load datasets from disk into
pandas DataFrames and save DataFrames back to CSV format, handling
directory path construction and directory creation automatically.
"""

import os
from typing import Dict, List, Optional

import pandas as pd


def load_data(
    directory: List[str],
    filename: str,
    separator: str = None,
    types: Optional[Dict[str, str]] = None,
    skiprows: int = 0,
) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame from a constructed directory path.

    This function joins the directory components and filename, checks for the
    existence of the file, and reads it using specified formatting options.

    Args:
        directory (List[str]): A list of strings representing the path components
            (e.g., ["data", "raw"]).
        filename (str): The name of the file to load (e.g., "results.csv").
        separator (str, optional): The delimiter to use. If None, pandas will
            attempt to detect it or use the default (usually a comma).
        types (Optional[Dict[str, str]], name): A dictionary mapping column names
            to their expected data types. If provided, these keys are also used
            as the column headers.
        skiprows (int): Number of lines to skip at the start of the file.
            Defaults to 0.

    Returns:
        pd.DataFrame: The loaded dataset.

    Raises:
        FileNotFoundError: If the combined path of directory and filename
            does not exist.
    """
    file_path = os.path.join(*directory, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {filename} does not exist in {directory}")

    kwargs = {}
    if separator is not None:
        kwargs["sep"] = separator

    if types is not None:
        kwargs["names"] = types.keys()
        kwargs["dtype"] = types

    df = pd.read_csv(file_path, **kwargs, skiprows=skiprows, low_memory=False)

    return df


def save_data(directory: List[str], filename: str, df: pd.DataFrame) -> None:
    """
    Saves a pandas DataFrame to a CSV file in a specified directory.

    This function constructs a directory path from a list of strings, ensures the
    directory exists (creating it if necessary), and writes the DataFrame to a
    CSV file without including the index.

    Args:
        directory (List[str]): A list of strings representing the path components
            where the file should be saved (e.g., ["data", "processed"]).
        filename (str): The name of the file to be saved (e.g., "output.csv").
        df (pd.DataFrame): The pandas DataFrame to be exported.

    Returns:
        None

    Example:
        save_data(["exports", "daily"], "report.csv", my_dataframe)
    """
    directory_path = os.path.join(*directory)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    file_path = os.path.join(directory_path, filename)

    df.to_csv(file_path, index=False)
