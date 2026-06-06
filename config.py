from pytz import timezone

TZ = timezone('America/Phoenix')

MIN_WORD_COUNT = 900
MIN_CHAR_COUNT = 5000

PRIMARY_SOURCES = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Anthropic": "https://www.anthropic.com/news/rss.xml",
    "Google AI": "https://ai.googleblog.com/feeds/posts/default",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Microsoft AI": "https://blogs.microsoft.com/ai/feed/",
    "Meta AI": "https://ai.meta.com/blog/feed/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "arXiv AI": "http://export.arxiv.org/rss/cs.AI",
    "MIT Technology Review AI": "https://www.technologyreview.com/feed/ai/",
    "Reuters AI": "https://www.reuters.com/technology/artificial-intelligence/?format=rss"
}

FALLBACK_SOURCES = {
    "IEEE Spectrum AI": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence",
    "Nature AI": "https://www.nature.com/subjects/artificial-intelligence.rss",
    "Science AI": "https://www.science.org/rss/news_current.xml",
    "AP Technology": "https://apnews.com/hub/technology?format=rss",
    "The Verge AI": "https://www.theverge.com/rss/ai/index.xml",
    "TechCrunch AI": "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/"
}

PAYWALL_DOMAINS = {
    "nytimes.com", "wsj.com", "ft.com", "economist.com",
    "newyorker.com", "harvard.edu", "nature.com", "science.org"
}

REQUEST_TIMEOUT = 15
MAX_ARTICLES_PER_SOURCE = 20
CACHE_DIR = "cache"
CACHE_TTL_SECONDS = 86400       # 24h for full-text
FEED_CACHE_TTL = 1800           # 30min for RSS/Atom feed contents
