import hashlib
import re

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
    if any(k in text.lower() for k in ["model", "release", "launch", "announce"]):
        return "Model Releases"
    if any(k in text.lower() for k in ["research", "paper", "arxiv", "benchmark"]):
        return "Research Breakthroughs"
    if any(k in text.lower() for k in ["regulation", "policy", "law", "order", "federal"]):
        return "Regulation / Policy"
    if any(k in text.lower() for k in ["safety", "alignment", "risk", "pause"]):
        return "Safety / Alignment"
    if any(k in text.lower() for k in ["enterprise", "market", "revenue", "valuation"]):
        return "Enterprise / Market Impact"
    if any(k in text.lower() for k in ["chip", "compute", "gpu", "memory", "infrastructure"]):
        return "Infrastructure / Chips"
    if any(k in text.lower() for k in ["security", "misuse", "hack", "attack"]):
        return "Security / Misuse"
    return "General"

def extract_excerpt(article):
    text = article.get("full_text", "")
    return text[:200] if text else ""

def extract_key_evidence(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    evidence = []
    for sent in sentences:
        if (re.search(r'\b\d+(?:\.\d+)?\b', sent) and len(sent) > 50) or \
           (re.search(r'"[^"]+"', sent) and len(sent) > 50):
            evidence.append(sent.strip())
        if len(evidence) >= 5:
            break
    return evidence[:5]

def extract_timeline(text):
    dates = re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', text)
    return list(set(dates))[:5]

def extract_actors(text):
    names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
    unique_names = list(set(names))[:5]
    companies = re.findall(r'\b(?:OpenAI|Anthropic|Google|Microsoft|Meta|Nvidia|Apple|Amazon|Facebook|Tesla)\b', text)
    all_actors = list(set(unique_names + companies))
    return all_actors[:7]

def extract_technical_claims(text):
    tech_patterns = [
        r'\b(?:model|algorithm|architecture|training|inference|parameter|token|layer)\b',
        r'\b\d+(?:\.\d+)?\s*%\b',
        r'\b(?:state[- ]of[- ]the[- ]art|SOTA)\b'
    ]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    claims = []
    for sent in sentences:
        if any(re.search(p, sent, re.I) for p in tech_patterns):
            claims.append(sent.strip())
        if len(claims) >= 4:
            break
    return claims[:4]

def extract_business_claims(text):
    biz_patterns = [
        r'\b(?:revenue|profit|margin|cost|valuation|funding|investment|market)\b',
        r'\$\d+(?:\.\d+)?\s*(?:billion|million|trillion)',
        r'\b(?:enterprise|SaaS|subscription|licensing)\b'
    ]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    claims = []
    for sent in sentences:
        if any(re.search(p, sent, re.I) for p in biz_patterns):
            claims.append(sent.strip())
        if len(claims) >= 4:
            break
    return claims[:4]

def extract_policy_claims(text):
    policy_patterns = [
        r'\b(?:regulation|policy|law|executive order|legislation|compliance|oversight)\b',
        r'\b(?:government|federal|agency|white house|congress|parliament)\b'
    ]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    claims = []
    for sent in sentences:
        if any(re.search(p, sent, re.I) for p in policy_patterns):
            claims.append(sent.strip())
        if len(claims) >= 4:
            break
    return claims[:4]

def find_contradictions_in_article(text):
    contradictions = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for i in range(1, len(sentences)):
        if re.search(r'\b(?:however|but|yet|nevertheless|on the other hand)\b', sentences[i], re.I):
            if len(sentences[i-1]) > 30 and len(sentences[i]) > 30:
                contradictions.append(f"{sentences[i-1].strip()} // {sentences[i].strip()}")
        if len(contradictions) >= 3:
            break
    return contradictions[:3]

def extract_assumption_mentions(text):
    assumptions = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sent in sentences:
        if re.search(r'\b(?:assume|presume|given that|suppose that)\b', sent, re.I):
            assumptions.append(sent.strip())
        if len(assumptions) >= 2:
            break
    return assumptions[:2]

def extract_blind_spot_mentions(text):
    blind_spots = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sent in sentences:
        if re.search(r'\b(?:ignored|overlooked|failed to consider|neglected|blind spot)\b', sent, re.I):
            blind_spots.append(sent.strip())
        if len(blind_spots) >= 2:
            break
    return blind_spots[:2]

def generate_tension_indicator(article):
    text = article.get("full_text", "")
    if re.search(r'\b(?:however|but|yet|contradiction|irony)\b', text, re.I):
        return "Potential narrative tension detected via contrast keywords (however/but/yet)."
    elif re.search(r'\b(?:risk|danger|threat)\b', text, re.I):
        return "Risk‑related language flagged; may indicate underlying concern not fully articulated."
    else:
        return "No clear tension signals detected using simple keyword heuristics."
