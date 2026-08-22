"""Extracts and analyzes URLs found in email bodies for phishing indicators.

URLs are only ever inspected as text -- nothing here fetches or executes
any external link.
"""

import re
from urllib.parse import urlparse

URL_REGEX = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+)", re.IGNORECASE)

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "shorte.st", "cutt.ly", "rb.gy",
}

SUSPICIOUS_TLDS = {
    ".zip", ".mov", ".xyz", ".top", ".club", ".click", ".gq", ".tk", ".ml",
}

IP_REGEX = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


def extract_urls(text):
    if not text:
        return []
    return URL_REGEX.findall(text)


def _looks_like_ip(host):
    return bool(IP_REGEX.match(host))


def analyze_url(raw_url):
    """Return a list of reason strings describing why a URL looks suspicious."""
    url = raw_url if "://" in raw_url else f"http://{raw_url}"
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    reasons = []

    if parsed.scheme == "http":
        reasons.append("Uses HTTP instead of HTTPS")

    if _looks_like_ip(host):
        reasons.append("Uses an IP address instead of a domain name")

    if any(host == s or host.endswith("." + s) for s in URL_SHORTENERS):
        reasons.append("Uses a known URL shortener")

    if host.count(".") >= 3:
        reasons.append("Contains an excessive number of subdomains")

    if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
        reasons.append("Uses an unusual/high-risk top-level domain")

    if "-" in host and host.count("-") >= 2:
        reasons.append("Contains suspicious characters/hyphens in domain")

    if any(brand in host for brand in ("paypal", "amazon", "bank", "microsoft", "apple")) and not any(
        host.endswith(d) for d in ("paypal.com", "amazon.com", "microsoft.com", "apple.com")
    ):
        reasons.append("Domain mimics a well-known brand name")

    return reasons


def detect_suspicious_urls(text):
    """Return (suspicious_urls: list[str], all_urls: list[str])."""
    all_urls = extract_urls(text)
    suspicious = []
    for url in all_urls:
        if analyze_url(url):
            suspicious.append(url)
    return suspicious, all_urls
