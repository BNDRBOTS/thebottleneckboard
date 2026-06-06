import tldextract
from config import PAYWALL_DOMAINS

def is_free_access(url, full_text=None):
    try:
        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}"
    except Exception:
        return False
    if domain in PAYWALL_DOMAINS:
        return False
    if full_text is not None and len(full_text.strip()) < 500:
        return False
    return True
