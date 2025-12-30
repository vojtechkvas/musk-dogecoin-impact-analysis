import pandas as pd
import pytest

from src.data_utils.processing import *


class TestDogecoinFiltering:

    @pytest.fixture
    def sample_tweets_df(self):
        return pd.DataFrame(
            {
                "text": [
                    "I love Dogecoin to the moon!",
                    "Government efficiency is important.",
                    "DOGE is the future",
                    "Just a random post about cats",
                ],
                "quoted_text": [
                    "None",
                    "Department of Government Efficiency",
                    "Bitcoin is okay",
                    "DOGE stuff",
                ],
            }
        )

    def test_get_posts_related_to_dogecoin_defaults(
        self, sample_tweets_df, monkeypatch
    ):
        """Exercises the 'if doge_keywords is None' branch."""
        monkeypatch.setattr(
            "src.data_utils.processing.DOGE_KEYWORDS", ["cats"]
        )
        monkeypatch.setattr(
            "src.data_utils.processing.POSTS_TEXT_COLUMN", "text"
        )

        result = get_posts_related_to_dogecoin(sample_tweets_df)
        assert len(result) == 1
        assert "cats" in result.iloc[0]["text"]

    def test_get_posts_related_to_dogecoin_success(self, sample_tweets_df):
        keywords = ["Dogecoin", "DOGE"]
        result = get_posts_related_to_dogecoin(
            sample_tweets_df, doge_keywords=keywords, text_column="text"
        )

        assert len(result) == 2
        assert "Dogecoin" in result.iloc[0]["text"]
        assert "DOGE" in result.iloc[1]["text"]

    def test_get_posts_related_to_dogecoin_no_match(self, sample_tweets_df):
        keywords = ["XRP", "Ethereum"]
        result = get_posts_related_to_dogecoin(
            sample_tweets_df, doge_keywords=keywords, text_column="text"
        )

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_get_repost_related_to_dogecoin_quote(self, sample_tweets_df):
        keywords = ["Efficiency"]
        result = get_repost_related_to_dogecoin_quote(
            sample_tweets_df,
            doge_keywords=keywords,
            text_columns=["text", "quoted_text"],
        )

        assert len(result) == 1
        assert "Efficiency" in result.iloc[0]["quoted_text"]

    def test_get_repost_related_to_dogecoin_quote_defaults(
        self, sample_tweets_df, monkeypatch
    ):
        """
        By NOT passing keywords or columns, we force the function to use the defaults from src.config.
        """

        monkeypatch.setattr(
            "src.data_utils.processing.DOGE_KEYWORDS", ["Efficiency"]
        )
        monkeypatch.setattr(
            "src.data_utils.processing.QUOTE_TEXT", ["text", "quoted_text"]
        )

        result = get_repost_related_to_dogecoin_quote(sample_tweets_df)

        assert len(result) == 1
        assert "Government efficiency" in result.iloc[0]["text"]


class TestDateTimeTransformationsDatetimeToUNIX:

    def test_convert_datetime_to_unix_timestamp_success(self):
        df = pd.DataFrame(
            {"created_at": ["2023-01-01 00:00:00", "2023-01-01 00:01:00"]}
        )
        result = convert_datetime_to_unix_timestamp(
            df, date_column="created_at", new_column_name="ts"
        )

        assert result["ts"].iloc[0] == 1672531200
        assert result["ts"].dtype == "int64"

    def test_convert_datetime_to_unix_timestamp_invalid_date(self):
        df = pd.DataFrame({"created_at": ["not-a-date"]})
        with pytest.raises(ValueError):
            convert_datetime_to_unix_timestamp(df)


class TestDateTimeTransformationsUNIXToDatetime:
    def test_convert_unix_timestamp_to_datetime_success(self):
        df = pd.DataFrame({"timestamp": [1672531200]})
        result = convert_unix_timestamp_to_datetime(
            df, timestamp_column="timestamp", new_column_name="dt"
        )

        assert result["dt"].iloc[0].year == 2023
        assert result["dt"].iloc[0].month == 1
        assert result["dt"].iloc[0].day == 1
        assert result["dt"].iloc[0].tzinfo is not None


class TestTweetFilteringByDate:

    def test_drop_tweets_before_date(self):
        # 2024-01-01 is 1704067200
        # 2024-01-02 is 1704153600
        df = pd.DataFrame(
            {
                "timestamp": [1704067200, 1704153600, 1704240000],
                "text": ["New Year", "Jan 2nd", "Jan 3rd"],
            }
        )

        cutoff = "2024-01-02"

        result = drop_tweets_before_date(df, cutoff_date=cutoff)

        assert len(result) == 1
        assert result["timestamp"].iloc[0] == 1704067200

    def test_drop_tweets_before_date_empty_result(self):
        df = pd.DataFrame({"timestamp": [2000000000]})
        cutoff = "2020-01-01"

        result = drop_tweets_before_date(df, cutoff_date=cutoff)
        assert len(result) == 0


class TestDuplicateIdentification:

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

        count, _ = find_duplicates(sample_duplicate_df, subset, display)

        assert count == 4

    def test_find_duplicates_no_duplicates(self):
        """Tests that it returns 0 when no duplicates exist."""
        df = pd.DataFrame({"a": [1, 2, 3], "full_text": ["x", "y", "z"]})

        count, _ = find_duplicates(
            df, subset_columns=["a"], display_duplicates=["full_text"]
        )

        assert count == 0

    def test_find_duplicates_missing_full_text_column(
        self, sample_duplicate_df
    ):
        """Identifying duplicates without a 'full_text' column."""
        df_no_text = sample_duplicate_df.drop(columns=["full_text"])

        count, _ = find_duplicates(
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

        count, _ = find_duplicates(
            df, subset_columns=["id"], display_duplicates=["full_text"]
        )

        assert count == 0

    def test_find_duplicates_completely_empty_case(self):
        """
        Exercises the 'False' branch of 'if not duplicates.empty'.
        This covers the jump from line 119 directly to the return statement.
        """
        df = pd.DataFrame()

        count, _ = find_duplicates(
            df, subset_columns=["id"], display_duplicates=["id"]
        )

        assert count == 0

    def test_find_duplicates_no_full_text_column(self):
        """Exercises the else branch in find_duplicates."""
        df = pd.DataFrame({"id": [1, 1, 2], "data": ["a", "a", "b"]})

        count, _ = find_duplicates(
            df, subset_columns=["id"], display_duplicates=["id"]
        )
        assert count == 2

    def test_find_duplicates_sorting_logic(self, sample_duplicate_df):
        """Tests that the function prints and respects the 'full_text' sorting if present."""
        subset = ["full_text"]
        display = ["full_text"]

        count, duplicate_df = find_duplicates(
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

        count, _ = find_duplicates(df, ["id"], ["full_text"])

        assert count == 0
