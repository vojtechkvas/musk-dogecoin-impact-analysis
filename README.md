# When the Billionaire Tweets: Analyzing the Impact of Elon Musk on Dogecoin

Describe a function of developed application, necessary dependencies (e.g. utilize requirements.txt), how to start it, and last but not least how to run tests from CLI.



## How to get data

Tweets:

https://www.kaggle.com/datasets/dadalyndell/elon-musk-tweets-2010-to-2025-march?resource=download&select=all_musk_posts.csv

https://www.kaggle.com/datasets/dadalyndell/elon-musk-tweets-2010-to-2025-march?resource=download&select=musk_quote_tweets.csv




DOGECOIN:


https://www.cryptoarchive.com.au/asset/DOGE

extract it







## How to run environment

Create virtual enviroment:

```bash
python3.11 -m venv venv-bipyt
```

Start enviroment:

```bash
source venv-bipyt/bin/activate
```

Install requiremnts:

```bash
pip install -r requirements.txt
```

Export new requiremnts:

```bash
pip freeze > requirements.txt
```

Stop enviroment:

```bash
deactivate
```

## How to run app

Start the app:

```bash
python run.py
```

Run test:

```bash
pytest
```


```bash
pytest --cov=src/data_utils --cov-branch --cov-report=term-missing
```


Run code style:
```bash
find . type f -name "*.py" | xargs pylint --disable=C0301,C0103 -sn
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
Paste it in browser, an look for file .ipynb






Quetion mohu používat poetry


## How to run environment

Logging
More data analysis
IS it OK
loadding button
¨




testy a vizualizacy v notebooku cisteni dat




