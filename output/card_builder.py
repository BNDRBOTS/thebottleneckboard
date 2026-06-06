# output/card_builder.py
import hashlib
import re

# Precompiled patterns
_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')
_KEY_EVIDENCE_NUM = re.compile(r'\b\d+(?:\.\d+)?\b')
_KEY_EVIDENCE_QUOTE = re.compile(r'"[^"]+"')
_TIMELINE = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b')
_ACTOR_NAME = re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')
_COMPANY = re.compile(r'\b(?:OpenAI|Anthropic|Google|Microsoft|Meta|Nvidia|Apple|Amazon|Facebook|Tesla)\b')
_TECH_PATTERNS = [
    re.compile(p, re.I) for p in (
        r'\b(?:model|algorithm|architecture|training|inference|parameter|token|layer)\b',
        r'\b\d+(?:\.\d+)?\s*%\b',
        r'\b(?:state[- ]of[- ]the[- ]art|SOTA)\b'
    )
]
_BIZ_PATTERNS = [
    re.compile(p, re.I) for p in (
        r'\b(?:revenue|profit|margin|cost|valuation|funding|investment|market)\b',
        r'\$\d+(?:\.\d+)?\s*(?:billion|million|trillion)',
        r'\b(?:enterprise|SaaS|subscription|licensing)\b'
    )
]
_POLICY_PATTERNS = [
    re.compile(p, re.I) for p in (
        r'\b(?:regulation|policy|law|executive order|legislation|compliance|oversight)\b',
        r'\b(?:government|federal|agency|white house|congress|parliament)\b'
    )
]
_CONTRADICTION_TRANS = re.compile(r'\b(?:however|but|yet|nevertheless|on the other hand)\b', re.I)
_ASSUMPTION = re.compile(r'\b(?:assume|presume|given that|suppose that)\b', re.I)
_BLIND_SPOT = re.compile(r'\b(?:ignored|overlooked|failed to consider|neglected|blind spot)\b', re.I)
_TENSION_CONTRAST = re.compile(r'\b(?:however|but|yet|contradiction|irony)\b', re.I)
_TENSION_RISK = re.compile(r'\b(?:risk|danger|threat)\b', re.I)

def build_card(article, rank):
    full_text = article.get("full_text", "")
    key_evidence = extract_key_evidence(full_text)
    technical_claims = extract_technical_claims(full_text)
    business_claims = extract_business_claims(full_text)
    policy_claims = extract_policy_claims(full_text)
    all_supported_claims = key_evidence + technical_claims + business_claims + policy_claims

    card = {
        "rank": rank,
        "title": article["title"],
        "source": article["source"],
        "author": article.get("author", ""),
        "publishedAt": article["timestamp"].isoformat(),
        "url": article["url"],
        "category": infer_category(article),
        "wordCount": len(full_text.split()),
        "densityScore": article["densityScore"],
        "whySelected": ["High factual density", "Meets all gates", "Same-day publication"],
        "excerpt": extract_excerpt(article),
        "keyEvidence": key_evidence,
        "timeline": extract_timeline(full_text),
        "actors": extract_actors(full_text),
        "technicalClaims": technical_claims,
        "businessClaims": business_claims,
        "policyClaims": policy_claims,
        "contradictions": find_contradictions_in_article(full_text),
        "assumptionMentions": extract_assumption_mentions(full_text),
        "blindSpotMentions": extract_blind_spot_mentions(full_text),
        "tensionIndicator": generate_tension_indicator(article),
        "sourceFaithfulnessLog": {
            "supportedClaims": all_supported_claims,
            "rejectedClaims": [],
            "uncertainties": [],
            "transformationHash": hashlib.md5(full_text.encode()).hexdigest()
        }
    }
    return card

def infer_category(article):
    text = article["title"] + " " + article.get("full_text", "")[:1000]
    lower = text.lower()
    if any(k in lower for k in ["model", "release", "launch", "announce"]):
        return "Model Releases"
    if any(k in lower for k in ["research", "paper", "arxiv", "benchmark"]):
        return "Research Breakthroughs"
    if any(k in lower for k in ["regulation", "policy", "law", "order", "federal"]):
        return "Regulation / Policy"
    if any(k in lower for k in ["safety", "alignment", "risk", "pause"]):
        return "Safety / Alignment"
    if any(k in lower for k in ["enterprise", "market", "revenue", "valuation"]):
        return "Enterprise / Market Impact"
    if any(k in lower for k in ["chip", "compute", "gpu", "memory", "infrastructure"]):
        return "Infrastructure / Chips"
    if any(k in lower for k in ["security", "misuse", "hack", "attack"]):
        return "Security / Misuse"
    return "General"

def extract_excerpt(article):
    text = article.get("full_text", "")
    return text[:200] if text else ""

def extract_key_evidence(text):
    sentences = _SENTENCE_SPLIT.split(text)
    evidence = []
    for sent in sentences:
        if (_KEY_EVIDENCE_NUM.search(sent) and len(sent) > 50) or \
           (_KEY_EVIDENCE_QUOTE.search(sent) and len(sent) > 50):
            evidence.append(sent.strip())
        if len(evidence) >= 5:
            break
    return evidence[:5]

def extract_timeline(text):
    dates = _TIMELINE.findall(text)
    return list(set(dates))[:5]

def extract_actors(text):
    names = _ACTOR_NAME.findall(text)
    unique_names = list(set(names))[:5]
    companies = _COMPANY.findall(text)
    all_actors = list(set(unique_names + companies))
    return all_actors[:7]

def extract_technical_claims(text):
    sentences = _SENTENCE_SPLIT.split(text)
    claims = []
    for sent in sentences:
        if any(p.search(sent) for p in _TECH_PATTERNS):
            claims.append(sent.strip())
        if len(claims) >= 4:
            break
    return claims[:4]

def extract_business_claims(text):
    sentences = _SENTENCE_SPLIT.split(text)
    claims = []
    for sent in sentences:
        if any(p.search(sent) for p in _BIZ_PATTERNS):
            claims.append(sent.strip())
        if len(claims) >= 4:
            break
    return claims[:4]

def extract_policy_claims(text):
    sentences = _SENTENCE_SPLIT.split(text)
    claims = []
    for sent in sentences:
        if any(p.search(sent) for p in _POLICY_PATTERNS):
            claims.append(sent.strip())
        if len(claims) >= 4:
            break
    return claims[:4]

def find_contradictions_in_article(text):
    sentences = _SENTENCE_SPLIT.split(text)
    contradictions = []
    for i in range(1, len(sentences)):
        if _CONTRADICTION_TRANS.search(sentences[i]) and len(sentences[i-1]) > 30 and len(sentences[i]) > 30:
            contradictions.append(f"{sentences[i-1].strip()} // {sentences[i].strip()}")
        if len(contradictions) >= 3:
            break
    return contradictions[:3]

def extract_assumption_mentions(text):
    sentences = _SENTENCE_SPLIT.split(text)
    assumptions = []
    for sent in sentences:
        if _ASSUMPTION.search(sent):
            assumptions.append(sent.strip())
        if len(assumptions) >= 2:
            break
    return assumptions[:2]

def extract_blind_spot_mentions(text):
    sentences = _SENTENCE_SPLIT.split(text)
    blind_spots = []
    for sent in sentences:
        if _BLIND_SPOT.search(sent):
            blind_spots.append(sent.strip())
        if len(blind_spots) >= 2:
            break
    return blind_spots[:2]

def generate_tension_indicator(article):
    text = article.get("full_text", "")
    if _TENSION_CONTRAST.search(text):
        return "Potential narrative tension detected via contrast keywords (however/but/yet)."
    elif _TENSION_RISK.search(text):
        return "Risk‑related language flagged; may indicate underlying concern not fully articulated."
    else:
        return "No clear tension signals detected using simple keyword heuristics."
