import feedparser
from datetime import datetime, timezone as dt_timezone
from newspaper import Article
from fetchers.base import BaseFetcher
from config import TZ, MAX_ARTICLES_PER_SOURCE, CACHE_DIR, CACHE_TTL_SECONDS, FEED_CACHE_TTL, REQUEST_TIMEOUT
import hashlib, json, os, time, re, logging

logger = logging.getLogger(__name__)

# ---------- cache helpers (full-text) ----------
def _cache_path(url):
    safe = hashlib.md5(url.encode()).hexdigest() + ".json"
    return os.path.join(CACHE_DIR, safe)

def _load_cache(url):
    try:
        path = _cache_path(url)
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if time.time() - data.get('timestamp', 0) < CACHE_TTL_SECONDS:
            return data['text']
    except:
        pass
    return None

def _save_cache(url, text):
    if not text:
        return
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        path = _cache_path(url)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'url': url, 'timestamp': time.time(), 'text': text}, f, ensure_ascii=False)
    except:
        pass

# ---------- feed-level cache (persisted on disk) ----------
def _feed_cache_path(url):
    safe = hashlib.md5(url.encode()).hexdigest() + "_feed.json"
    return os.path.join(CACHE_DIR, safe)

def _load_feed_cache(url):
    try:
        path = _feed_cache_path(url)
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if time.time() - data.get('timestamp', 0) < FEED_CACHE_TTL:
            return data['content']
    except:
        pass
    return None

def _save_feed_cache(url, content):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        path = _feed_cache_path(url)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'url': url, 'timestamp': time.time(), 'content': content}, f, ensure_ascii=False)
    except:
        pass

class RSSFetcher(BaseFetcher):
    def fetch(self):
        if self._is_paywalled():
            return []
        try:
            feed_content = _load_feed_cache(self.url)
            if feed_content is None:
                resp = self.session.get(self.url, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                feed_content = resp.text
                _save_feed_cache(self.url, feed_content)

            feed = feedparser.parse(feed_content)
            articles = []
            for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
                pub_date = self._parse_date(entry)
                if pub_date is None:
                    continue
                article_url = entry.get("link", "")
                full_text = self._extract_full_text(article_url)
                # Fallback: use RSS summary if full_text is too short
                if not full_text or len(full_text.strip()) < 200:
                    summary = entry.get("summary", "")
                    if summary and len(summary.strip()) >= 200:
                        full_text = summary
                articles.append({
                    "source": self.name,
                    "title": entry.get("title", ""),
                    "url": article_url,
                    "timestamp": pub_date,
                    "author": entry.get("author", ""),
                    "raw_metadata": entry,
                    "fetched_via": "RSS",
                    "full_text": full_text
                })
            return articles
        except Exception as e:
            logger.warning(f"RSS fetch error {self.name}: {e}")
            return []

    def _parse_date(self, entry):
        for key in ["published_parsed", "updated_parsed", "created_parsed"]:
            if key in entry and entry[key]:
                dt = datetime(*entry[key][:6])
                if dt.tzinfo is None:
                    # Assume UTC if no timezone info
                    dt = dt.replace(tzinfo=dt_timezone.utc)
                dt = dt.astimezone(TZ)
                return dt
        return None

    def _extract_full_text(self, url):
        cached = _load_cache(url)
        if cached:
            return cached
        try:
            article = Article(url, language='en')
            article.download()
            article.parse()
            text = article.text
            if text:
                text = re.sub(r'\s+', ' ', text).strip()
                _save_cache(url, text)
            return text
        except:
            return ""
