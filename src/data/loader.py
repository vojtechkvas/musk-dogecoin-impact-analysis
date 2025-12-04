import pandas as pd
from typing import List, Optional, Dict
import os
 
def load_data(directory: List[str], filename: str, separator: str = None , types: Optional[Dict[str, str]] = None, skiprows:int= 0) -> pd.DataFrame:

    file_path = os.path.join(*directory, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {filename} does not exist in {directory}")
    
    kwargs = {}
    if separator is not None:
        kwargs["sep"] = separator
    
    if types is not None:
        kwargs["names"] = types.keys()
        kwargs["dtype"] = types 

    df = pd.read_csv(file_path,  **kwargs ,   skiprows=skiprows, low_memory=False)

    return df


def save_data(directory, filename, df):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, filename)

    df.to_csv(file_path, index=False)
