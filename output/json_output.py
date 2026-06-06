import json
from datetime import datetime
from config import TZ
from output.card_builder import build_card

def generate_dashboard_json(top_articles, rejection_summary, source_health):
    cards = [build_card(art, idx+1) for idx, art in enumerate(top_articles)]

    modules = {
        "Model Releases": [],
        "Research Breakthroughs": [],
        "Regulation / Policy": [],
        "Safety / Alignment": [],
        "Enterprise / Market Impact": [],
        "Infrastructure / Chips": [],
        "Security / Misuse": [],
        "General": []
    }
    for card in cards:
        cat = card["category"]
        if cat in modules:
            modules[cat].append(card)

    contradiction_tracker = []
    for i, card1 in enumerate(cards):
        for card2 in cards[i+1:]:
            if card1["source"] != card2["source"]:
                t1 = card1["title"].lower()
                t2 = card2["title"].lower()
                if ("openai" in t1 and "openai" in t2) or ("anthropic" in t1 and "anthropic" in t2):
                    if ("safety" in t1 and "risk" in t2) or ("risk" in t1 and "safety" in t2):
                        contradiction_tracker.append({
                            "article1": card1["title"],
                            "article2": card2["title"],
                            "nature": "Potential conflicting claims on safety/risk"
                        })

    dashboard = {
        "generatedAt": datetime.now(TZ).isoformat(),
        "timezone": "America/Phoenix",
        "totalArticlesPassed": len(top_articles),
        "dailyTop10": cards,
        "modelReleases": modules["Model Releases"],
        "researchBreakthroughs": modules["Research Breakthroughs"],
        "regulationPolicy": modules["Regulation / Policy"],
        "safetyAlignment": modules["Safety / Alignment"],
        "enterpriseMarketImpact": modules["Enterprise / Market Impact"],
        "infrastructureChips": modules["Infrastructure / Chips"],
        "securityMisuse": modules["Security / Misuse"],
        "general": modules["General"],
        "contradictionTracker": contradiction_tracker,
        "rejectionLog": rejection_summary,
        "sourceHealthMonitor": source_health
    }
    return json.dumps(dashboard, indent=2, ensure_ascii=False)
