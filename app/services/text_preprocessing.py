"""Shared text preprocessing used by both training and prediction, so the
exact same cleaning function is applied at train time and inference time.
"""

import re
import string

try:
    from nltk.corpus import stopwords
    _STOPWORDS = set(stopwords.words("english"))
except Exception:  # pragma: no cover - fallback if nltk data isn't downloaded
    _STOPWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "to", "of", "and",
        "in", "on", "for", "with", "this", "that", "it", "you", "your",
        "we", "our", "as", "at", "by", "be", "or", "from",
    }

HTML_TAG_REGEX = re.compile(r"<[^>]+>")
URL_REGEX = re.compile(r"https?://\S+|www\.\S+")
WHITESPACE_REGEX = re.compile(r"\s+")
PUNCT_TABLE = str.maketrans("", "", string.punctuation)

# Words that are strong phishing signals -- never strip these as "stopwords".
KEEP_WORDS = {
    "urgent", "verify", "click", "password", "otp", "suspended",
    "confirm", "prize", "reward", "bank", "payment", "invoice",
}


def clean_text(text):
    """Lowercase, strip HTML/URLs/punctuation, normalize whitespace, and
    remove non-informative stopwords while preserving phishing-indicator
    words that a naive stopword pass might otherwise touch.
    """
    if not text:
        return ""

    text = text.lower()
    text = HTML_TAG_REGEX.sub(" ", text)
    text = URL_REGEX.sub(" url ", text)
    text = text.translate(PUNCT_TABLE)
    text = WHITESPACE_REGEX.sub(" ", text).strip()

    tokens = text.split()
    tokens = [t for t in tokens if t in KEEP_WORDS or t not in _STOPWORDS]
    return " ".join(tokens)
