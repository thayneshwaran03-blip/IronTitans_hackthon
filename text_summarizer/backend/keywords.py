
"""
Lightweight keyword extraction using TF (term frequency) scoring with
stopword removal — no extra model download needed. Used to highlight the
most important terms in the original text, giving the tool an
"explainability" angle for judges.
"""
import re
from collections import Counter

STOPWORDS = set("""
a an the is are was were be been being have has had do does did will would
shall should may might must can could of in on at to for with by from as
and or but if then than that this these those it its it's he she they them
his her their we you i our your not no so such very just about over under
into out up down off again further more most other some any all each few
""".split())


def extract_keywords(text: str, top_n: int = 10):
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(top_n)]


def highlight_keywords(text: str, keywords: list):
    """Wrap keyword occurrences in <mark> tags for display, case-insensitive,
    whole-word matches only."""
    def repl(match):
        return f"<mark>{match.group(0)}</mark>"

    result = text
    for kw in keywords:
        pattern = re.compile(rf"\b({re.escape(kw)})\b", re.IGNORECASE)
        result = pattern.sub(repl, result)
    return result


