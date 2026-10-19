"""Small, dependency-free text helpers (keyword counts + lexicon sentiment)."""
import re
from collections import Counter

STOPWORDS = {
    "the", "and", "for", "but", "with", "this", "that", "very", "too", "quite",
    "its", "are", "was", "use", "used", "using", "some", "all", "can", "have",
    "has", "had", "not", "you", "our", "it's", "sometimes", "times", "at", "of",
    "to", "in", "on", "is", "it", "a", "an", "i", "my", "so", "as", "be",
}
POSITIVE = {"great", "good", "excellent", "useful", "helpful", "easy", "love",
            "amazing", "intuitive", "powerful", "fast", "clear", "super",
            "awesome", "best", "smooth"}
NEGATIVE = {"bad", "poor", "slow", "difficult", "confusing", "hard", "buggy",
            "expensive", "complicated", "frustrating", "worst", "needs",
            "improvement", "crashes"}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", str(text).lower())


def sentiment_label(text: str) -> str:
    """Very simple lexicon sentiment: Positive / Neutral / Negative."""
    words = tokenize(text)
    score = sum(w in POSITIVE for w in words) - sum(w in NEGATIVE for w in words)
    return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"


def top_words(texts, n: int = 15) -> list[tuple[str, int]]:
    counter = Counter()
    for t in texts:
        counter.update(w for w in tokenize(t) if len(w) > 2 and w not in STOPWORDS)
    return counter.most_common(n)
