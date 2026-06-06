from datetime import datetime
from config import TZ

def is_same_day(article_timestamp):
    if article_timestamp.tzinfo is None:
        article_timestamp = TZ.localize(article_timestamp)
    else:
        article_timestamp = article_timestamp.astimezone(TZ)
    today = datetime.now(TZ).date()
    return article_timestamp.date() == today
