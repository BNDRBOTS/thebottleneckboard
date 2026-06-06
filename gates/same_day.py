from datetime import datetime, timedelta, timezone as dt_timezone
from config import TZ

def is_same_day(article_timestamp):
    if article_timestamp.tzinfo is None:
        # assume UTC if naive
        article_timestamp = article_timestamp.replace(tzinfo=dt_timezone.utc)
    article_timestamp = article_timestamp.astimezone(TZ)
    now = datetime.now(TZ)
    return (now - article_timestamp) <= timedelta(hours=24)
