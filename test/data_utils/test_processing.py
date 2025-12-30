"""
Unit tests for data processing and analysis logic.

This module contains comprehensive test suites for validating the core analysis
logic of the application. It covers Dogecoin-specific keyword filtering,
general text search, and the temporal alignment between social media events
and financial market data.
"""

import pandas as pd
import pytest

from src.data_utils import processing


class TestDogecoinFiltering:
    """
    Test suite for specialized Dogecoin and department efficiency filters.

    This class validates the regex-based search functionality across various
    post types (original posts and quotes). It specifically tests the
    application's ability to identify relevant financial social media content.
    """

    @pytest.fixture
    def sample_tweets_df(self):
        """Provides a mock DataFrame containing both original and quoted text."""
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
        """
        Verifies that the function uses global config defaults when no arguments
        are passed. Uses monkeypatch to isolate the test from actual config values.
        """
        monkeypatch.setattr(
            "src.data_utils.processing.DOGE_KEYWORDS", ["cats"]
        )
        monkeypatch.setattr(
            "src.data_utils.processing.POSTS_TEXT_COLUMN", "text"
        )

        result = processing.get_posts_related_to_dogecoin(sample_tweets_df)
        assert len(result) == 1
        assert "cats" in result.iloc[0]["text"]

    def test_get_posts_related_to_dogecoin_success(self, sample_tweets_df):
        """Tests multi-keyword matching within a single text column."""
        keywords = ["Dogecoin", "DOGE"]
        result = processing.get_posts_related_to_dogecoin(
            sample_tweets_df, doge_keywords=keywords, text_column="text"
        )

        assert len(result) == 2
        assert "Dogecoin" in result.iloc[0]["text"]
        assert "DOGE" in result.iloc[1]["text"]

    def test_get_posts_related_to_dogecoin_no_match(self, sample_tweets_df):
        """Ensures the function handles cases where no keywords are found gracefully."""
        keywords = ["XRP", "Ethereum"]
        result = processing.get_posts_related_to_dogecoin(
            sample_tweets_df, doge_keywords=keywords, text_column="text"
        )

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_get_repost_related_to_dogecoin_quote(self, sample_tweets_df):
        """Tests the logic for matching keywords across multiple text columns (quotes)."""
        keywords = ["Efficiency"]
        result = processing.get_repost_related_to_dogecoin_quote(
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
        By NOT passing keywords or columns,
        we force the function to use the defaults from src.config.
        """

        monkeypatch.setattr(
            "src.data_utils.processing.DOGE_KEYWORDS", ["Efficiency"]
        )
        monkeypatch.setattr(
            "src.data_utils.processing.QUOTE_TEXT", ["text", "quoted_text"]
        )

        result = processing.get_repost_related_to_dogecoin_quote(
            sample_tweets_df
        )

        assert len(result) == 1
        assert "Government efficiency" in result.iloc[0]["text"]


class TestKeywordFiltering:
    """
    General keyword filtering test suite.

    Validates basic string matching operations, including case-insensitivity,
    handling of empty strings, and null-value (NaN) resilience.
    """

    @pytest.fixture
    def sample_tweet_df(self):
        """Provides a DataFrame with various text content for keyword testing."""
        return pd.DataFrame(
            {
                "text": [
                    "Python is amazing!",
                    "I love data science",
                    "The weather is nice today",
                    "Learning Pytorch and python",
                    None,
                ],
                "other_column": ["a", "b", "c", "d", "e"],
            }
        )

    def test_filter_tweets_by_keyword_success(self, sample_tweet_df):
        """Tests standard keyword matching."""
        keyword = "data"
        result = processing.filter_tweets_by_keyword(
            sample_tweet_df, keyword, text_column="text"
        )

        assert len(result) == 1
        assert "I love data science" in result["text"].values

    def test_filter_tweets_by_keyword_case_insensitive(self, sample_tweet_df):
        """Tests that the filter ignores case (Python vs python)."""
        keyword = "PYTHON"
        result = processing.filter_tweets_by_keyword(
            sample_tweet_df, keyword, text_column="text"
        )

        assert len(result) == 2
        for val in result["text"]:
            assert "python" in val.lower()

    def test_filter_tweets_by_keyword_handles_nan(self, sample_tweet_df):
        """Tests that the function handles missing (NaN) values without crashing."""
        keyword = "nice"

        result = processing.filter_tweets_by_keyword(
            sample_tweet_df, keyword, text_column="text"
        )

        assert len(result) == 1
        assert result["text"].iloc[0] == "The weather is nice today"

    def test_filter_tweets_by_keyword_empty_string(self, sample_tweet_df):
        """Tests that an empty keyword returns the original DataFrame."""
        result = processing.filter_tweets_by_keyword(
            sample_tweet_df, "", text_column="text"
        )

        assert len(result) == len(sample_tweet_df)
        pd.testing.assert_frame_equal(result, sample_tweet_df)

    def test_filter_tweets_by_keyword_no_matches(self, sample_tweet_df):
        """Tests that it returns an empty DataFrame when the keyword is not found."""
        result = processing.filter_tweets_by_keyword(
            sample_tweet_df, "Golang", text_column="text"
        )

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)


class TestAveragePriceAtTweetTime:
    """
    Test suite for financial and temporal data alignment.

    Validates the 'minute-flooring' join logic used to associate social media
    timestamps with corresponding stock market prices.
    """

    @pytest.fixture
    def sample_stock_data(self):
        """
        Provides a stock DataFrame with prices at specific minute intervals.
        1704067200 -> 2024-01-01 00:00:00
        1704067260 -> 2024-01-01 00:01:00
        """
        return pd.DataFrame(
            {
                "timestamp": [1704067200, 1704067260, 1704067320],
                "open": [100.0, 200.0, 300.0],
            }
        )

    def test_calculate_avg_price_success(self, sample_stock_data):
        """Tests that tweets are correctly floored to the minute and averaged."""
        tweet_df = pd.DataFrame(
            {
                "timestamp": [
                    1704067215,
                    1704067245,
                    1704067265,
                ]
            }
        )

        result = processing.calculate_avg_price_at_tweet_time(
            tweet_df, sample_stock_data
        )
        assert result == pytest.approx(133.3333333)

    def test_calculate_avg_price_empty_inputs(self, sample_stock_data):
        """Tests that empty DataFrames return 0.0."""
        empty_df = pd.DataFrame(columns=["timestamp"])

        assert (
            processing.calculate_avg_price_at_tweet_time(
                empty_df, sample_stock_data
            )
            == 0.0
        )
        assert (
            processing.calculate_avg_price_at_tweet_time(
                sample_stock_data, empty_df
            )
            == 0.0
        )

    def test_calculate_avg_price_no_matching_times(self, sample_stock_data):
        """Tests that if no tweet minutes match stock minutes, it returns 0.0."""
        tweet_df = pd.DataFrame({"timestamp": [915148800, 915148860]})

        result = processing.calculate_avg_price_at_tweet_time(
            tweet_df, sample_stock_data
        )
        assert result == 0.0

    def test_calculate_avg_price_duplicate_stock_minutes(self):
        """
        Tests that the function handles duplicate stock minutes by dropping
        them (as per the code logic) instead of creating a Cartesian product.
        """
        stock_df = pd.DataFrame(
            {
                "timestamp": [
                    1704067200,
                    1704067210,
                ],
                "open": [
                    100.0,
                    999.0,
                ],
            }
        )
        tweet_df = pd.DataFrame({"timestamp": [1704067205]})

        result = processing.calculate_avg_price_at_tweet_time(
            tweet_df, stock_df
        )
        assert result == 100.0

    def test_calculate_avg_price_partial_matches(self, sample_stock_data):
        """Tests averaging when only some tweets have corresponding stock data."""
        tweet_df = pd.DataFrame(
            {
                "timestamp": [
                    1704067200,  # Matches 100.0
                    2000000000,  # Matches nothing (NaN)
                ]
            }
        )
        result = processing.calculate_avg_price_at_tweet_time(
            tweet_df, sample_stock_data
        )
        assert result == 100.0
