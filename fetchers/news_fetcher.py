import feedparser
from datetime import datetime, timezone as dt_timezone
from newspaper import Article
from fetchers.base import BaseFetcher
from config import TZ, MAX_ARTICLES_PER_SOURCE, REQUEST_TIMEOUT
from fetchers.rss_fetcher import _load_cache, _save_cache, _load_feed_cache, _save_feed_cache
import re, logging

logger = logging.getLogger(__name__)

class NewsFetcher(BaseFetcher):
    def __init__(self, name, url):
        super().__init__(name, url)
        self.rss_url = url

    def fetch(self):
        if self._is_paywalled():
            return []
        try:
            feed_content = _load_feed_cache(self.rss_url)
            if feed_content is None:
                resp = self.session.get(self.rss_url, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                feed_content = resp.text
                _save_feed_cache(self.rss_url, feed_content)

            feed = feedparser.parse(feed_content)
        except Exception as e:
            logger.warning(f"News fetch error {self.name}: {e}")
            return []
        articles = []
        for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
            article_url = entry.get("link")
            if not article_url:
                continue
            try:
                cached = _load_cache(article_url)
                if cached:
                    body = cached
                else:
                    news_article = Article(article_url, language='en')
                    news_article.download()
                    news_article.parse()
                    body = news_article.text
                    if body:
                        body = re.sub(r'\s+', ' ', body).strip()
                    _save_cache(article_url, body)
                if len(body) < 200:
                    continue
                pub_date = self._parse_date(entry)
                if pub_date is None:
                    continue
                articles.append({
                    "source": self.name,
                    "title": entry.get("title", ""),
                    "url": article_url,
                    "timestamp": pub_date,
                    "author": entry.get("author", ""),
                    "raw_metadata": {"body": body, "summary": ""},
                    "fetched_via": "RSS+FullText",
                    "full_text": body
                })
            except Exception as e:
                logger.warning(f"News fetch error {self.name} {article_url}: {e}")
                continue
        return articles

    def _parse_date(self, entry):
        for key in ["published_parsed", "updated_parsed"]:
            if key in entry and entry[key]:
                dt = datetime(*entry[key][:6])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=dt_timezone.utc)
                dt = dt.astimezone(TZ)
                return dt
        return None
