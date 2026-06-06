import logging
from scoring.density import DensityScorer
from gates.relevance import is_ai_relevant
from gates.free_access import is_free_access
from gates.length import meets_length
from gates.same_day import is_same_day
from config import MIN_WORD_COUNT

logger = logging.getLogger(__name__)

def log_rejection(article, reason):
    logger.info(
        "REJECTED | %s | %s | %s",
        article.get('source', 'unknown'),
        article.get('title', 'unknown'),
        reason
    )

def select_top_10(candidates, fallback_candidates):
    passed = []
    rejection_summary = []

    for art in candidates:
        if not is_ai_relevant(art["title"], art.get("raw_metadata", {})):
            log_rejection(art, "AI relevance gate")
            rejection_summary.append({"title": art["title"], "source": art["source"], "reason": "AI relevance gate"})
            continue
        if not is_free_access(art["url"], art.get("full_text", "")):
            log_rejection(art, "Free access gate (paywall/login)")
            rejection_summary.append({"title": art["title"], "source": art["source"], "reason": "Free access gate"})
            continue
        if not meets_length(art):
            log_rejection(art, f"Length gate (<{MIN_WORD_COUNT} words)")
            rejection_summary.append({"title": art["title"], "source": art["source"], "reason": "Length gate"})
            continue
        if not is_same_day(art["timestamp"]):
            log_rejection(art, "Same-day gate")
            rejection_summary.append({"title": art["title"], "source": art["source"], "reason": "Same-day gate"})
            continue
        art["densityScore"] = DensityScorer.score(art)
        passed.append(art)

    passed.sort(key=lambda x: x["densityScore"], reverse=True)
    top10 = passed[:10]

    if len(top10) < 10:
        needed = 10 - len(top10)
        for fb in fallback_candidates:
            if needed <= 0:
                break
            if not is_ai_relevant(fb["title"], fb.get("raw_metadata", {})):
                continue
            if not is_free_access(fb["url"], fb.get("full_text", "")):
                continue
            if not meets_length(fb):
                continue
            if not is_same_day(fb["timestamp"]):
                continue
            fb["densityScore"] = DensityScorer.score(fb)
            top10.append(fb)
            needed -= 1

    return top10, rejection_summary
