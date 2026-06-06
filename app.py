import os
import json
import logging
from flask import Flask, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from collections import defaultdict
from config import TZ, PRIMARY_SOURCES, FALLBACK_SOURCES
from fetchers import RSSFetcher, ArxivFetcher, NewsFetcher
from scoring import select_top_10
from output import generate_dashboard_json
import concurrent.futures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)

cached_dashboard = None
last_run = None

def build_all_fetchers():
    fetchers = []
    for name, url in PRIMARY_SOURCES.items():
        if name == "arXiv AI":
            fetchers.append(ArxivFetcher(name, url))
        elif name in ["MIT Technology Review AI", "Reuters AI"]:
            fetchers.append(NewsFetcher(name, url))
        else:
            fetchers.append(RSSFetcher(name, url))
    for name, url in FALLBACK_SOURCES.items():
        fetchers.append(RSSFetcher(name, url))
    return fetchers

def deduplicate_by_url(articles):
    seen = set()
    unique = []
    for art in articles:
        u = art["url"]
        if u not in seen:
            seen.add(u)
            unique.append(art)
    return unique

def run_daily_pipeline():
    global cached_dashboard, last_run
    logging.info("Starting daily pipeline at %s", datetime.now(TZ))
    fetchers = build_all_fetchers()
    all_candidates = []
    source_success = defaultdict(int)
    source_failure = defaultdict(int)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_fetcher = {executor.submit(fetcher.fetch): fetcher for fetcher in fetchers}
        for future in concurrent.futures.as_completed(future_to_fetcher):
            fetcher = future_to_fetcher[future]
            try:
                articles = future.result()
                if articles:
                    source_success[fetcher.name] += len(articles)
                else:
                    source_failure[fetcher.name] += 1
                all_candidates.extend(articles)
            except Exception as e:
                logging.error(f"Fetcher {fetcher.name} failed: {e}")
                source_failure[fetcher.name] += 1

    all_candidates = deduplicate_by_url(all_candidates)

    primary_candidates = [a for a in all_candidates if a["source"] not in FALLBACK_SOURCES]
    fallback_candidates = [a for a in all_candidates if a["source"] in FALLBACK_SOURCES]

    top10, rejection_summary = select_top_10(primary_candidates, fallback_candidates)

    source_health = {
        "succeeded": dict(source_success),
        "failed": dict(source_failure)
    }

    dashboard_json = generate_dashboard_json(top10, rejection_summary, source_health)
    cached_dashboard = dashboard_json
    last_run = datetime.now(TZ)
    logging.info("Pipeline finished. %d articles selected.", len(top10))

def safe_run_pipeline():
    try:
        run_daily_pipeline()
    except Exception as e:
        logging.error("Pipeline failed: %s", e, exc_info=True)

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    if cached_dashboard is None:
        safe_run_pipeline()
    return jsonify(json.loads(cached_dashboard))

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok", "lastRun": last_run.isoformat() if last_run else None}

@app.route('/', methods=['GET'])
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(safe_run_pipeline, 'cron', hour=6, minute=0, timezone=TZ)
    scheduler.start()
    safe_run_pipeline()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
