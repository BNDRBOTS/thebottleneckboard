from datetime import datetime, timedelta
from config import TZ

def is_same_day(article_timestamp):
    if article_timestamp.tzinfo is None:
        article_timestamp = TZ.localize(article_timestamp)
    else:
        article_timestamp = article_timestamp.astimezone(TZ)
    now = datetime.now(TZ)
    # Allow articles published within the last 24 hours
    return (now - article_timestamp) <= timedelta(hours=24)
