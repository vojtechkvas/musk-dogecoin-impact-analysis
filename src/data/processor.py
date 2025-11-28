from app.data.dataloader import load_data, save_data
from app.config.settings import (
    DATA_INPUT_DIR,
    DATA_INPUT_FILE,
    DATA_OUTPUT_DIR,
    DATA_OUTPUT_FILE,
)


df = load_data(DATA_INPUT_DIR, DATA_INPUT_FILE)
