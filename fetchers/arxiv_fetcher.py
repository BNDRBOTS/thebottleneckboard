import arxiv
from datetime import datetime
from fetchers.base import BaseFetcher
from config import TZ, MAX_ARTICLES_PER_SOURCE

class ArxivFetcher(BaseFetcher):
    def fetch(self):
        client = arxiv.Client()
        search = arxiv.Search(
            query="cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
            max_results=MAX_ARTICLES_PER_SOURCE,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        articles = []
        for result in client.results(search):
            pub_date = result.published.astimezone(TZ)
            full_text = result.summary
            articles.append({
                "source": self.name,
                "title": result.title,
                "url": result.entry_id,
                "timestamp": pub_date,
                "author": ", ".join([a.name for a in result.authors]),
                "raw_metadata": {"summary": result.summary},
                "fetched_via": "arXiv API",
                "full_text": full_text
            })
        return articles
