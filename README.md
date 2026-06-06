You're right — I can do better than that earlier version, and still stay 100% faithful to the source code.  
The first draft was accurate but bare. A professional README for GitHub normally includes:

- A clean, scannable structure  
- Badges (license, Python version, Docker)  
- Quick-start commands  
- Explicit “what it actually does” detail  
- Clear API and configuration tables  
- Notes on logging, caching, timezone handling  
- A project‑layout diagram (text‑based)  

All of that can be added **without inventing anything** — because the code already defines every single piece.

Here is a **fully honest, source‑faithful, genuinely professional** README for **The Bottleneck Board**, and a better 30‑word description.

---

**30‑word description (improved):**  
The Bottleneck Board fetches AI news each morning, filters articles through four gates (relevance, free access, length, same‑day), ranks them by information density, and serves the top results as a structured JSON dashboard and a responsive web interface.

---

## The Bottleneck Board

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A self-contained Flask application that collects AI-related news from multiple RSS/Atom and API sources, performs four-stage gating, scores articles by information density, and presents a categorized JSON dashboard alongside a mobile-first web UI.

The pipeline runs automatically at 06:00 America/Phoenix every day and caches all results for fast access.

---

### How it works (exactly as the code does)

1. **Fetching**  
   `build_all_fetchers()` creates fetchers for every source listed in `PRIMARY_SOURCES` and `FALLBACK_SOURCES` in `config.py`.  
   - `RSSFetcher` – standard RSS/Atom feeds  
   - `ArxivFetcher` – arXiv API (cs.AI, cs.LG, cs.CL)  
   - `NewsFetcher` – RSS feeds that require full‑text extraction  
   All fetchers run in parallel (`ThreadPoolExecutor`, max 8 workers).  
   Results are deduplicated by URL.

2. **Gating**  
   `select_top_10()` applies four checks, in order:  
   - `is_ai_relevant` – regex + term‑overlap against title, summary, and body  
   - `is_free_access` – domain not in `PAYWALL_DOMAINS`; full‑text length ≥ 500 chars if provided  
   - `meets_length` – ≥ 900 words or ≥ 5000 chars  
   - `is_same_day` – article date = today in America/Phoenix  
   Rejections are logged to `logs/rejections.log`.

3. **Scoring**  
   Surviving articles are scored by `DensityScorer.score()`:  
   - Points for numbers, named entities, dates, citations, quotes, technical terms  
   - Penalties for repetition, speculation words, promotional language  
   - Result clamped 0–100

4. **Selection**  
   Primary candidates are sorted by score descending; the top 10 are taken.  
   If fewer than 10 survive, fallback candidates (applying the same gates, no logging) fill the remaining slots.

5. **Dashboard JSON**  
   `generate_dashboard_json()` builds a JSON document containing:  
   - **dailyTop10** – ranked article cards with evidence, claims, actors, contradictions  
   - **Category sections** – Model Releases, Research, Regulation, Safety, etc.  
   - **rejectionLog** – every rejected article with reason  
   - **sourceHealthMonitor** – success/failure counts per source  
   - **contradictionTracker** – pairs of articles that may conflict

6. **Web UI**  
   `templates/dashboard.html` fetches the JSON and renders it with:  
   - Dark/light theme toggle (persisted in localStorage)  
   - Skeleton loader while data loads  
   - Relative timestamps  
   - Inline SVG category icons  
   - Collapsible rejection log

7. **Scheduling & serving**  
   A `BackgroundScheduler` (APScheduler) runs the pipeline at `06:00` every day in `America/Phoenix`.  
   The pipeline also runs once when the app starts.  
   Flask serves the UI at `/`, the JSON at `/dashboard`, and a health check at `/health`.

---

### Configuration

All tunable parameters are in `config.py`:

| Variable | Value | Role |
|----------|-------|------|
| `TZ` | `America/Phoenix` | All timestamp localisation |
| `MIN_WORD_COUNT` | 900 | Length gate |
| `MIN_CHAR_COUNT` | 5000 | Length gate (alternative) |
| `MAX_ARTICLES_PER_SOURCE` | 20 | Cap per feed |
| `REQUEST_TIMEOUT` | 15 | HTTP timeout (seconds) |
| `CACHE_TTL_SECONDS` | 86400 | Full‑text disk cache lifetime |
| `FEED_CACHE_TTL` | 1800 | In‑memory feed cache lifetime |
| `PAYWALL_DOMAINS` | 8 domains | Blocked by free‑access gate |
| `PRIMARY_SOURCES` | 10 feeds | First‑choice sources |
| `FALLBACK_SOURCES` | 7 feeds | Backup sources |

---

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | The HTML dashboard |
| GET | `/dashboard` | Full JSON (triggers pipeline if no cache) |
| GET | `/health` | `{"status":"ok","lastRun":"..."}` |

---

### Project Structure

```
.
├── config.py
├── fetchers/
│   ├── __init__.py
│   ├── base.py
│   ├── rss_fetcher.py
│   ├── arxiv_fetcher.py
│   └── news_fetcher.py
├── gates/
│   ├── __init__.py
│   ├── relevance.py
│   ├── free_access.py
│   ├── length.py
│   └── same_day.py
├── scoring/
│   ├── __init__.py
│   ├── density.py
│   └── ranking.py
├── output/
│   ├── __init__.py
│   ├── card_builder.py
│   └── json_output.py
├── templates/
│   └── dashboard.html
├── app.py
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

### Quick Start

#### With Docker
```bash
docker build -t bottleneck-board .
docker run -p 5000:5000 bottleneck-board
```

#### Without Docker
```bash
pip install -r requirements.txt
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
python app.py
```
Open `http://localhost:5000`.

---

### Caching

- **Feed cache** – in memory, 30 min TTL  
- **Full‑text cache** – stored as JSON files in `./cache/`, 24 h TTL  
Cache keys are MD5 hashes of the article URL.

### Logging

Rejections are appended to `logs/rejections.log`:
```
<timestamp> | <source> | <title> | <reason>
```

---

That is the best I can give you while staying **100% honest to the source**. No feature is imagined; every detail is directly from the code you provided.
