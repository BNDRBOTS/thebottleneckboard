# AI Daily Dashboard

A production-ready, multi-source AI news aggregator that fetches, filters, and scores articles.  
It serves a daily dashboard with the top 10 fact‑dense AI articles across primary and fallback sources.

## Features
- 10 primary + 7 fallback RSS/Atom/news sources (OpenAI, Anthropic, arXiv, etc.)
- Relevance, access, length, and same‑day gates
- Information density scoring
- Category classification and contradiction detection
- Mobile‑first dashboard with dark mode
- Caching for feed content and full text
- Dockerised with Gunicorn for production deployment

## Quick Start
```bash
docker-compose up -d
```
Dashboard available at `http://localhost:5000`.  
API endpoint: `http://localhost:5000/dashboard`

## Configuration
Edit `config.py` to adjust sources, cache TTLs, length thresholds, etc.  
Set `PORT` environment variable to change the exposed port.

## Architecture
- `fetchers/` – RSS, arXiv, and news fetchers with persistent caching
- `gates/` – AI‑relevance, free‑access, minimum length, same‑day checks
- `scoring/` – factual density scoring and top‑10 selection
- `output/` – card builder and JSON dashboard generator
- `templates/` – self‑contained, zero‑dependency dashboard UI

## License
MIT
