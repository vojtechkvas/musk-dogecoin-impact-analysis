# When the Billionaire Tweets: Analyzing the Impact of Elon Musk on Dogecoin

This application provides an interactive dashboard and analytical toolset to investigate the correlation between Elon Musk's social media activity and cryptocurrency market dynamics. Using Bayesian Structural Time-Series models via the CausalImpact library, the app estimates the counterfactual price of Dogecoin, predicting what the price would have been if a specific tweet had never occurred.

## Data Acquisition

### Social Media Data (Tweets):

Sourced from Kaggle: Elon Musk Tweets 2010-2025

https://www.kaggle.com/datasets/dadalyndell/elon-musk-tweets-2010-to-2025-march?resource=download&select=all_musk_posts.csv

https://www.kaggle.com/datasets/dadalyndell/elon-musk-tweets-2010-to-2025-march?resource=download&select=musk_quote_tweets.csv

Save these files to the datasets/raw directory and process them using the exploration_and_preprocessing_tweets.ipynb notebook.

### Market Data (Cryptocurrencies)

Obtain 1-minute OHLCV data (USDT pairs) from CryptoArchive. Note: Free registration is required.

DOGECOIN:
https://www.cryptoarchive.com.au/asset/DOGE

BNB:
https://www.cryptoarchive.com.au/asset/BNB

BTC:
https://www.cryptoarchive.com.au/asset/BTC

ETH:
https://www.cryptoarchive.com.au/asset/ETH

FLOKI:
https://www.cryptoarchive.com.au/asset/FLOKI

SOL:
https://www.cryptoarchive.com.au/asset/SOL

Save the downloaded files to datasets/raw. Process the Dogecoin data using exploration_and_preprocessing_dogecoin_price.ipynb, and use exploration_and_preprocessing_cryptos.ipynb for the remaining assets.

## Data Exploration

Comprehensive exploratory data analysis and preprocessing workflows are provided as documented Jupyter Notebooks in the notebooks/ folder.


## Environment Setup

Create virtual enviroment:

```bash
python3.11 -m venv venv-bipyt
```


Start enviroment:

```bash
source venv-bipyt/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Export new dependencies:

```bash
pip freeze > requirements.txt
```


Stop enviroment:

```bash
deactivate
```

## Running the Application

### Start the Dash Web App:

```bash
python run.py
```

### Quality Assurance

Run tests:

```bash
pytest
# or
pytest --cov=src/data_utils --cov-branch --cov-report=term-missing
```


Run static code analysis:
```bash
find . -type f -name "*.py" | xargs pylint --disable=C0301,C0103 -sn
```

### How to run jupyter notebook

1. Activate the Environment

Before starting, navigate to your project directory and activate your virtual environment:

```bash
source venv-bipyt/bin/activate
```

The quickest way to start a full notebook interface is by launching JupyterLab:

```bash
jupyter lab
```
Note: This should automatically open a new tab in your default web browser. If it doesn't, copy and paste the http://localhost... URL displayed in your terminal into your browser.



### 3. Option B: Run in VS Code
If you prefer working directly inside VS Code, you have two ways to connect:

#### Method 1: Native VS Code Extension (Recommended)
1. Open your `.ipynb` file directly in VS Code.
2. Install the official **Jupyter** extension if prompted.
3. Click **Select Kernel** in the top-right corner of the notebook and choose your active virtual environment (`venv-bipyt`).

#### Method 2: Connect via Jupyter Server URL
If you already started `jupyter lab` in your terminal, you can connect VS Code to that running server:

1. Copy the URL with the token from your terminal logs (it will look like this):
```text
   http://localhost:8889/tree?token=fb702cccdd40cfd4f07a4ee8bf65561d34dfe958b62c6ba8