"""
Unit tests for core data utility functions.

This module provides a comprehensive test suite for `src.data_utils.utils`.
It utilizes the `pytest` framework to validate data transformation and
cleaning logic.
"""

import pandas as pd
import pytest

from src.data_utils import utils


class TestDateTimeTransformationsDatetimeToUNIX:
    """
    Test suite for converting datetime strings to Unix timestamps.

    Verifies that the conversion logic correctly handles standard datetime
    strings, produces UTC-based integer timestamps, and appropriately
    raises errors for unparseable input.
    """

    def test_convert_datetime_to_unix_timestamp_success(self):
        """
        Verifies successful conversion of valid datetime strings to Unix seconds.

        Checks that the output column has the correct 'int64' dtype and
        matches expected epoch values.
        """
        df = pd.DataFrame(
            {"created_at": ["2023-01-01 00:00:00", "2023-01-01 00:01:00"]}
        )
        result = utils.convert_datetime_to_unix_timestamp(
            df, date_column="created_at", new_column_name="ts"
        )

        assert result["ts"].iloc[0] == 1672531200
        assert result["ts"].dtype == "int64"

    def test_convert_datetime_to_unix_timestamp_invalid_date(self):
        """Ensures a ValueError is raised when encountering malformed date strings."""
        df = pd.DataFrame({"created_at": ["not-a-date"]})
        with pytest.raises(ValueError):
            utils.convert_datetime_to_unix_timestamp(df)


class TestDateTimeTransformationsUNIXToDatetime:
    """
    Test suite for converting Unix timestamps back to datetime objects.

    Ensures that integer epoch values are correctly mapped to UTC-aware
    pandas datetime objects.
    """

    def test_convert_unix_timestamp_to_datetime_nat_handling(self):
        """Verifies behavior when the timestamp column contains NaN/None."""
        df = pd.DataFrame({"timestamp": [None]})
        result = utils.convert_unix_timestamp_to_datetime(df)
        assert pd.isna(result["created_at"].iloc[0])

    def test_convert_unix_timestamp_to_datetime_success(self):
        """
        Verifies that Unix integers are correctly converted to datetime objects.

        Checks for year/month/day accuracy and ensures the resulting
        series is timezone-aware.
        """
        df = pd.DataFrame({"timestamp": [1672531200]})
        result = utils.convert_unix_timestamp_to_datetime(
            df, timestamp_column="timestamp", new_column_name="dt"
        )

        assert result["dt"].iloc[0].year == 2023
        assert result["dt"].iloc[0].month == 1
        assert result["dt"].iloc[0].day == 1
        assert result["dt"].iloc[0].tzinfo is not None


class TestTweetFilteringByDate:
    """
    Test suite for chronological data filtering.

    Validates that the dataset can be correctly trimmed based on a
    provided cutoff date.
    """

    def test_drop_tweets_before_date(self):
        """
        Verifies that records occurring strictly after a cutoff are removed.

        Note: The implementation logic in the tested function treats the
        cutoff as the 'latest allowed' time (dropping everything newer).
        """
        # 2024-01-01 is 1704067200
        # 2024-01-02 is 1704153600
        df = pd.DataFrame(
            {
                "timestamp": [1704067200, 1704153600, 1704240000],
                "text": ["New Year", "Jan 2nd", "Jan 3rd"],
            }
        )

        cutoff = "2024-01-02"

        result = utils.drop_tweets_before_date(df, cutoff_date=cutoff)

        assert len(result) == 1
        assert result["timestamp"].iloc[0] == 1704067200

    def test_drop_tweets_before_date_empty_result(self):
        """Ensures that if all records are past the cutoff, an empty DataFrame is returned."""
        df = pd.DataFrame({"timestamp": [2000000000]})
        cutoff = "2020-01-01"

        result = utils.drop_tweets_before_date(df, cutoff_date=cutoff)
        assert len(result) == 0


class TestDuplicateIdentification:
    """
    Test suite for the duplicate identification utility.

    This class ensures that the duplicate detection logic accurately identifies
    redundant rows based on variable subsets, handles edge cases like missing
    optional columns (e.g., 'full_text'), and correctly processes empty or
    unique DataFrames. It also validates the internal sorting and display
    logic used for manual data inspection.
    """

    @pytest.fixture
    def sample_duplicate_df(self):
        """Provides a DataFrame with controlled duplicates."""
        return pd.DataFrame(
            {
                "id": [1, 2, 2, 3, 4, 4],
                "full_text": [
                    "Unique post",
                    "Duplicate post",
                    "Duplicate post",
                    "Another unique",
                    "Same text, diff ID",
                    "Same text, diff ID",
                ],
                "metadata": ["a", "b", "c", "d", "e", "f"],
            }
        )

    def test_find_duplicates_with_subset(self, sample_duplicate_df):
        """Tests that duplicates are correctly identified based on specific columns."""

        subset = ["full_text"]
        display = ["id", "full_text"]

        count, _ = utils.find_duplicates(sample_duplicate_df, subset, display)

        assert count == 4

    def test_find_duplicates_no_duplicates(self):
        """Tests that it returns 0 when no duplicates exist."""
        df = pd.DataFrame({"a": [1, 2, 3], "full_text": ["x", "y", "z"]})

        count, _ = utils.find_duplicates(
            df, subset_columns=["a"], display_duplicates=["full_text"]
        )

        assert count == 0

    def test_find_duplicates_missing_full_text_column(
        self, sample_duplicate_df
    ):
        """Identifying duplicates without a 'full_text' column."""
        df_no_text = sample_duplicate_df.drop(columns=["full_text"])

        count, _ = utils.find_duplicates(
            df_no_text, subset_columns=["id"], display_duplicates=["id"]
        )

        assert count == 4

    def test_find_duplicates_no_duplicates_found(self):
        """
        Exercises the 'False' branch of line 119.
        When no duplicates exist, the code should skip the print block
        and return 0.
        """
        df = pd.DataFrame(
            {"id": [1, 2, 3], "full_text": ["Post A", "Post B", "Post C"]}
        )

        count, _ = utils.find_duplicates(
            df, subset_columns=["id"], display_duplicates=["full_text"]
        )

        assert count == 0

    def test_find_duplicates_completely_empty_case(self):
        """
        Exercises the 'False' branch of 'if not duplicates.empty'.
        This covers the jump from line 119 directly to the return statement.
        """
        df = pd.DataFrame()

        count, _ = utils.find_duplicates(
            df, subset_columns=["id"], display_duplicates=["id"]
        )

        assert count == 0

    def test_find_duplicates_no_full_text_column(self):
        """Exercises the else branch in find_duplicates."""
        df = pd.DataFrame({"id": [1, 1, 2], "data": ["a", "a", "b"]})

        count, _ = utils.find_duplicates(
            df, subset_columns=["id"], display_duplicates=["id"]
        )
        assert count == 2

    def test_find_duplicates_sorting_logic(self, sample_duplicate_df):
        """Tests that the function prints and respects the 'full_text' sorting if present."""
        subset = ["full_text"]
        display = ["full_text"]

        count, duplicate_df = utils.find_duplicates(
            sample_duplicate_df, subset, display
        )

        assert "Duplicate post" == duplicate_df.iloc[0]["full_text"]
        assert "Duplicate post" == duplicate_df.iloc[1]["full_text"]
        assert "Same text, diff ID" == duplicate_df.iloc[2]["full_text"]
        assert "Same text, diff ID" == duplicate_df.iloc[3]["full_text"]

        assert count == 4

    def test_find_duplicates_empty_df(self):
        """Tests behavior with an empty DataFrame."""
        df = pd.DataFrame(columns=["id", "full_text"])

        count, _ = utils.find_duplicates(df, ["id"], ["full_text"])

        assert count == 0
