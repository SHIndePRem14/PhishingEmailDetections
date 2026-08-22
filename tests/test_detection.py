from app.services.keyword_service import detect_keywords
from app.services.url_service import detect_suspicious_urls, analyze_url


def test_keyword_detection_finds_matches():
    text = "URGENT: verify your account and click here immediately."
    matched, score = detect_keywords(text)
    assert "urgent" in matched
    assert "verify your account" in matched
    assert score > 0


def test_keyword_detection_empty_text():
    matched, score = detect_keywords("")
    assert matched == []
    assert score == 0


def test_url_detection_flags_http_and_ip():
    text = "Please login at http://192.168.1.10/secure to verify your account."
    suspicious, all_urls = detect_suspicious_urls(text)
    assert len(all_urls) == 1
    assert len(suspicious) == 1


def test_url_detection_no_urls():
    suspicious, all_urls = detect_suspicious_urls("This email has no links at all.")
    assert suspicious == []
    assert all_urls == []


def test_analyze_url_shortener():
    reasons = analyze_url("http://bit.ly/abc123")
    assert any("shortener" in r.lower() for r in reasons)
