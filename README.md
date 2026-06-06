**30‑word description**  
The Bottleneck Board collects articles from configured RSS/Atom/API sources, filters them through four gates (AI relevance, free access, length, same‑day), scores the survivors by information density, and exposes the top results as a JSON dashboard and an HTML page.

---

# The Bottleneck Board – source‑accurate README

## What the code does

1. **Fetching**  
   `build_all_fetchers()` instantiates `RSSFetcher`, `ArxivFetcher`, and `NewsFetcher` for every source listed in `PRIMARY_SOURCES` and `FALLBACK_SOURCES` (all defined in `config.py`).  
   Each fetcher’s `fetch()` method is called in parallel (`ThreadPoolExecutor`, max 8 workers).  
   Results are deduplicated by URL.

2. **Gating**  
   The function `select_top_10()` (in `scoring/ranking.py`) applies four checks *in order*:

   - `is_ai_relevant(title, raw_metadata)` – searches the title, summary, and body for an AI‑specific regex (`AI_KEYWORDS`). If no regex match, checks if the set of words ≥3 letters intersects with a hard‑coded set `{"ai","model","training","data","neural","network","algorithm","compute"}` in at least two terms.  
   - `is_free_access(url, full_text)` – extracts the domain (via `tldextract`), rejects if domain is in `PAYWALL_DOMAINS` (config set). Also rejects if `full_text` is provided and its stripped length is < 500 characters.  
   - `meets_length(article_dict)` – requires `word_count ≥ MIN_WORD_COUNT` (900) **or** `char_count ≥ MIN_CHAR_COUNT` (5000). If `full_text` is missing, falls back to `raw_metadata.summary`.  
   - `is_same_day(article_timestamp)` – localises the timestamp to `America/Phoenix` (`TZ` from config) and checks that its `.date()` equals `datetime.now(TZ).date()`.

   Any primary‑candidate article that fails a gate is logged to `logs/rejections.log` with timestamp, source, title, and reason.

3. **Scoring**  
   Articles that pass all gates receive a `densityScore` via `DensityScorer.score()` (static method in `scoring/density.py`). The score is based on counts of numbers, named entities, dates, citations, quotes, and technical terms, minus penalties for repetition, speculation words, and promotional words. Output is clamped 0–100.

4. **Top‑10 selection**  
   Passed primary candidates are sorted by density score descending, and the top 10 are taken. If fewer than 10 primary candidates survive, the code fills the remaining slots from `fallback_candidates` (applying the same four gates but without logging rejections).

5. **Dashboard generation**  
   `generate_dashboard_json()` (in `output/json_output.py`) builds per‑article cards via `build_card()` (in `output/card_builder.py`). Each card contains:
   - rank, title, source, author, timestamp (ISO format), URL, word count, density score
   - category (inferred by keyword matching)
   - key evidence, timeline, actors, technical/business/policy claims (regex‑extracted)
   - contradictions within the article, assumption mentions, blind‑spot mentions
   - a tension indicator string (based on contrast/risk keywords)
   - a `sourceFaithfulnessLog` with supported claims and an MD5 hash of the full text

   Cards are grouped into categories (Model Releases, Research Breakthroughs, Regulation/Policy, Safety/Alignment, Enterprise/Market Impact, Infrastructure/Chips, Security/Misuse, General).  
   The dashboard JSON also includes a `contradictionTracker` (pairs of cards from different sources that mention similar entities with safety/risk terms), a `rejectionLog` (the list of rejected articles with reasons), and a `sourceHealthMonitor` (counts of successful/failed articles per source).  
   The final JSON string is stored in a global variable and served via Flask.

6. **Web UI**  
   The file `templates/dashboard.html` fetches `/dashboard` and renders the JSON as an HTML page. It uses vanilla JavaScript, supports dark mode (persisted in `localStorage`), shows a skeleton loader, relative timestamps, and inline SVGs for categories.

7. **Scheduling**  
   A `BackgroundScheduler` (APScheduler) triggers `safe_run_pipeline()` every day at 06:00 America/Phoenix time. The pipeline also runs once on startup. The Flask app listens on port 5000.

---

## Configuration

All values are in `config.py`.

| Variable | Value | Used by |
|----------|-------|---------|
| `TZ` | `timezone('America/Phoenix')` | All date handling, same‑day gate, scheduler |
| `MIN_WORD_COUNT` | 900 | Length gate |
| `MIN_CHAR_COUNT` | 5000 | Length gate |
| `PRIMARY_SOURCES` | dict (10 feeds) | Fetcher construction |
| `FALLBACK_SOURCES` | dict (7 feeds) | Fetcher construction |
| `PAYWALL_DOMAINS` | set of 8 domains | Free‑access gate |
| `REQUEST_TIMEOUT` | 15 | HTTP requests |
| `MAX_ARTICLES_PER_SOURCE` | 20 | Fetch loops |
| `CACHE_DIR` | `"cache"` | Full‑text disk cache |
| `CACHE_TTL_SECONDS` | 86400 | Full‑text cache expiry |
| `FEED_CACHE_TTL` | 1800 | In‑memory feed cache expiry |

---

## API Endpoints

- `GET /` – Serves `dashboard.html`
- `GET /dashboard` – Returns the cached dashboard JSON; triggers a pipeline run if no data exists
- `GET /health` – Returns `{"status":"ok","lastRun":"<ISO timestamp>"}`

---

## Running

### Docker

```bash
docker build -t bottleneck-board .
docker run -p 5000:5000 bottleneck-board
```

### Manual

```bash
pip install -r requirements.txt
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
python app.py
```

Access at `http://localhost:5000`.
