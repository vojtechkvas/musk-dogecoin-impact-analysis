import pandas as pd
import os


def load_data(directory, filename):
    # logging.info(f"Loading data from {os.path.join(directory, filename)}")
    file_path = os.path.join(directory, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {filename} does not exist in {directory}")

    df = pd.read_csv(file_path)

    return df


def save_data(directory, filename, df):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, filename)

    df.to_csv(file_path, index=False)
