RAW_TWEETS_POSTS = "all_musk_posts.csv"
RAW_TWEETS_QUOTE = "musk_quote_tweets.csv"
RAW_DOGE_PRICE_PATH = "doge_price.csv"
PROCESSED_TWEETS = "combined_data.csv"
RAW_DIR = "datasets/raw"
RAW_DIR = ["datasets", "raw"]
PROCESSED_DIR = "datasets/processed"

CSV_SEPARATOR = ","
CSV_SEPARATOR_DOGEUSDT = "|"

DOGE_DTYPES = {
    "timestamp": "Int64",
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "float64",
    "taker_buy_quote_asset_volume": "float64",
    "taker_buy_base_asset_volume": "float64",
    "quote_asset_volume": "float64",
    "number_of_trades": "Int32",
}

POSTS_TEXT_COLUMN = "full_text"
QUOTE_TEXT = ["orig_tweet_text", "musk_quote_tweet_text"]

QUOTE_DTYPES = {
    "id": "int64",
    "orig_tweet_created_at": "object",
    "orig_tweet_text": "string",
    "orig_tweet_url": "string",
    "orig_tweet_twitter_url": "string",
    "orig_tweet_username": "string",
    "orig_tweet_retweet_count": "int64",
    "orig_tweet_reply_count": "int64",
    "orig_tweet_like_count": "int64",
    "orig_tweet_quote_count": "int64",
    "orig_tweet_view_count": "float64",
    "orig_tweet_bookmark_count": "int64",
    "musk_tweet_id": "int64",
    "musk_quote_tweet_text": "string",
    "musk_quote_retweet_count": "int64",
    "musk_quote_reply_count": "int64",
    "musk_quote_like_count": "int64",
    "musk_quote_quote_count": "int64",
    "musk_quote_view_count": "float64",
    "musk_quote_bookmark_count": "int64",
    "created_at": "object",
}


POSTS_DTYPES = {
    "id": "int64",
    "url": "string",
    "twitter_url": "string",
    "full_text": "string",
    "retweet_count": "Int64",
    "reply_count": "Int64",
    "like_count": "Int64",
    "quote_count": "Int64",
    "view_count": "Int64",
    "created_at": "object",
    "bookmark_count": "float64",
    "is_reply": "boolean",
    "in_reply_to_id": "float64",
    "conversation_id": "float64",
    "in_reply_to_user_id": "float64",
    "in_reply_to_username": "string",
    "is_pinned": "boolean",
    "is_retweet": "boolean",
    "is_quote": "boolean",
    "is_conversation_controlled": "boolean",
    "possibly_sensitive": "boolean",
    "quote_id": "float64",
    "quote": "string",
    "retweet": "string",
}

DOGE_KEYWORDS = ["@DOGE"]
DOGE_KEYWORDS = ["dogecoin"]
DOGE_KEYWORDS = ["doge", "dogecoin", "Ðoge", "Doge", "DOGE"]
DOGE_KEYWORD = "dogecoin"
DEFAULT_DOGE_KEYWORDS = " dogecoin "

FIRST_MENTION_OF_DEPARTMENT_OF_GOVERNMENT_EFFICIENCY_DATE = "2024-08-02"

DOGE_MIN_DATE = "2025-07-05"
DOGE_MIN_DATE = "2024-07-05"
DOGE_MIN_DATE = "2019-07-05"

RELATIVE_TIME_SPREAD_HOURS = 6 * 3600

DOGE_MAX_DATE = "2025-10-24"


DASH_APP_TITLE = "Elon Musk & Dogecoin Impact Analysis"
SERVER_PORT = 8050
PRIMARY_COLOR = "#FFA400"


DOGECOIND_COLOR = "blue"
TWEET_COLOR = "RED"
