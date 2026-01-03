# When the Billionaire Tweets: Analyzing the Impact of Elon Musk on Dogecoin

This application provides an interactive dashboard and analytical toolset to investigate the correlation between Elon Musk's social media activity and cryptocurrency market dynamics. Using Bayesian Structural Time-Series models via the CausalImpact library, the app estimates the counterfactual price of Dogecoin, predicting what the price would have been if a specific tweet had never occurred.

## Data Acquisition

### Social Media Data (Tweets):

Sourced from Kaggle: Elon Musk Tweets 2010-2025

https://www.kaggle.com/datasets/dadalyndell/elon-musk-tweets-2010-to-2025-march?resource=download&select=all_musk_posts.csv

https://www.kaggle.com/datasets/dadalyndell/elon-musk-tweets-2010-to-2025-march?resource=download&select=musk_quote_tweets.csv


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


Start enviroment:

```bash
source venv-bipyt/bin/activate
```

Start Jupyter Server:

```bash
jupyter notebook
```


It can look for something like this:

```bash
http://localhost:8889/tree?token=fb702cccdd40cfd4f07a4ee8bf65561d34dfe958b62c6ba8
```

Open the local server URL in your browser or use the VS Code Jupyter extension to navigate and run the .ipynb notebooks.

