"""
Unit tests for data formatting utilities.

This module contains test suites for verifying the correctness of number formatting
(e.g., thousands separators) and date-to-Unix-timestamp conversions. It utilizes
pytest's parametrization to cover a wide range of valid and invalid input scenarios.
"""

import pytest

from src.data_utils import formatters


class TestNumberFormatting:
    """Tests for the format_number utility function."""

    @pytest.mark.parametrize(
        "input_val, expected_output",
        [
            (-50000, "-50 000"),
            (0, "0"),
            (4, "4"),
            (123, "123"),
            (1000, "1 000"),
            (10000, "10 000"),
            (100000, "100 000"),
            (1234.56, "1 234.56"),
        ],
    )
    def test_format_number_multi_thousands(self, input_val, expected_output):
        """Property-based check for different thousands thresholds."""
        assert formatters.format_number(input_val) == expected_output

    def test_format_number_with_none_input(self):
        """Verifies behavior when input is None (if applicable)."""
        with pytest.raises(TypeError):
            formatters.format_number(None)


class TestDateToTimestamp:
    """Tests for the convert_date_to_timestamp utility function."""

    @pytest.mark.parametrize(
        "date_string, date_format, expected_timestamp",
        [
            ("1970-01-01", "%Y-%m-%d", 0),
            ("2023-01-01", "%Y-%m-%d", 1672531200),
            ("2024-12-25", "%Y-%m-%d", 1735084800),
            ("01/01/2024", "%m/%d/%Y", 1704067200),
            ("2024-02-29", "%Y-%m-%d", 1709164800),
        ],
    )
    def test_convert_date_valid_inputs(
        self, date_string, date_format, expected_timestamp
    ):
        """Verify correct Unix timestamps for various valid date strings and formats."""
        assert (
            formatters.convert_date_to_timestamp(date_string, date_format)
            == expected_timestamp
        )

    @pytest.mark.parametrize(
        "invalid_date, date_format",
        [
            ("2023-13-01", "%Y-%m-%d"),  # Invalid month
            ("2023-01-32", "%Y-%m-%d"),  # Invalid day
            ("not-a-date", "%Y-%m-%d"),  # Not a date
            ("2023/01/01", "%Y-%m-%d"),  # Wrong separator
        ],
    )
    def test_convert_date_invalid_formats(self, invalid_date, date_format):
        """Verify that ValueError is raised with a helpful message for bad inputs."""
        with pytest.raises(
            ValueError, match=f"Invalid date format: {invalid_date}"
        ):
            formatters.convert_date_to_timestamp(invalid_date, date_format)
