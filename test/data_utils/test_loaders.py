import os

import pandas as pd
import pytest

from src.data_utils.loaders import load_data, save_data


class TestLoadData:

    @pytest.fixture
    def mock_csv(self, tmp_path, request):
        """
        Fixture to create a temporary CSV file with dynamic content.
        Expects a tuple of (filename, content) from the test marker.
        """

        params = getattr(request, "param", ("test.csv", "col1,col2\nval1,10\nval2,20"))
        filename, content = params

        d = tmp_path / "data"
        d.mkdir(exist_ok=True)
        f = d / filename
        f.write_text(content)

        return [str(d)], filename

    @pytest.mark.parametrize(
        "mock_csv", [("standard.csv", "col1,col2\nval1,10\nval2,20")], indirect=True
    )
    def test_load_data_success(self, mock_csv):
        """
        Positive test: Verifies that a standard CSV is correctly loaded into a DataFrame.

        Checks that the resulting object is a pandas DataFrame, contains the
        expected number of rows, and maintains correct column headers.
        """
        directory, filename = mock_csv
        df = load_data(directory, filename, separator=",")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["col1", "col2"]

    @pytest.mark.parametrize("mock_csv", [("typed.csv", "1;10.5")], indirect=True)
    def test_load_data_with_types(self, mock_csv):
        """
        Boundary test: Verifies data type enforcement during the loading process.

        Ensures that when a 'types' dictionary is provided, load_data correctly
        casts the columns to the specified numpy/pandas dtypes.
        """
        directory, filename = mock_csv
        types = {"id": "int", "val": "float"}

        df = load_data(directory, filename, separator=";", types=types)

        assert df["id"].dtype == "int"
        assert df["val"].dtype == "float"

    @pytest.mark.parametrize(
        "wrong_dir, wrong_file",
        [(["non", "existent"], "data.csv"), (["data"], "missing.csv")],
    )
    def test_load_data_file_not_found(self, wrong_dir, wrong_file):
        """Negative test: Verifies FileNotFoundError is raised."""
        with pytest.raises(FileNotFoundError):
            load_data(wrong_dir, wrong_file)

    @pytest.mark.parametrize(
        "mock_csv", [("default.csv", "a,b\n1,2\n3,4")], indirect=True
    )
    def test_load_data_defaults(self, mock_csv):
        """Tests loading with default parameters (None values)."""
        directory, filename = mock_csv
        df = load_data(directory, filename)

        assert len(df) == 2
        assert "a" in df.columns

    @pytest.mark.parametrize(
        "mock_csv",
        [("skip.csv", "garbage_line\nimportant_line\ncol1,col2\nval1,10")],
        indirect=True,
    )
    def test_load_data_skiprows(self, mock_csv):
        """Tests that skiprows correctly bypasses header noise."""
        directory, filename = mock_csv
        df = load_data(directory, filename, separator=",", skiprows=2)

        assert list(df.columns) == ["col1", "col2"]
        assert len(df) == 1


class TestSaveData:

    @pytest.fixture
    def sample_df(self):
        """Fixture to provide a standard DataFrame for testing."""
        return pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 80]})

    def test_save_data_creates_directory_and_file(self, tmp_path, sample_df):
        """Positive test: Verifies directory creation and file persistence."""
        base_dir = str(tmp_path / "output")
        sub_dir = "results"
        directory_list = [base_dir, sub_dir]
        filename = "test_save.csv"

        save_data(directory_list, filename, sample_df)

        expected_path = os.path.join(base_dir, sub_dir, filename)
        assert os.path.exists(expected_path)

        reloaded_df = pd.read_csv(expected_path)
        pd.testing.assert_frame_equal(reloaded_df, sample_df)

    def test_save_data_nested_directories(self, tmp_path, sample_df):
        """Verifies that multiple levels of missing directories are created."""
        directory_list = [str(tmp_path), "level1", "level2", "level3"]
        filename = "deep_file.csv"

        save_data(directory_list, filename, sample_df)

        expected_path = os.path.join(
            str(tmp_path), "level1", "level2", "level3", filename
        )
        assert os.path.exists(expected_path)
        updated_df = pd.read_csv(expected_path)
        assert len(updated_df) == 2
        pd.testing.assert_frame_equal(updated_df, sample_df)

    def test_save_data_overwrites_existing_file(self, tmp_path, sample_df):
        """Verifies that the function overwrites a file if it already exists."""
        directory_list = [str(tmp_path)]
        filename = "overwrite_test.csv"
        file_path = os.path.join(str(tmp_path), filename)

        initial_df = pd.DataFrame({"col": [1, 2, 3]})
        initial_df.to_csv(file_path, index=False)

        save_data(directory_list, filename, sample_df)

        updated_df = pd.read_csv(file_path)
        assert len(updated_df) == 2
        pd.testing.assert_frame_equal(updated_df, sample_df)

    def test_save_data_no_index_preserved(self, tmp_path, sample_df):
        """Verifies that the index is not saved to the CSV (index=False)."""
        directory_list = [str(tmp_path)]
        filename = "index_test.csv"

        save_data(directory_list, filename, sample_df)

        with open(os.path.join(str(tmp_path), filename), "r") as f:
            header = f.readline().strip()

        assert header == "name,score"
        updated_df = pd.read_csv(os.path.join(str(tmp_path), filename))
        assert len(updated_df) == 2
        pd.testing.assert_frame_equal(updated_df, sample_df)
