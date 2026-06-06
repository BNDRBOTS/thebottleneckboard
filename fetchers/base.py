import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import tldextract
from config import PAYWALL_DOMAINS

class BaseFetcher:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.5, status_forcelist=[500,502,503,504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({'User-Agent': 'AIDailyDashboard/1.0'})
        return session

    def fetch(self):
        raise NotImplementedError

    def _is_paywalled(self):
        try:
            ext = tldextract.extract(self.url)
            domain = f"{ext.domain}.{ext.suffix}"
            return domain in PAYWALL_DOMAINS
        except Exception:
            return True
