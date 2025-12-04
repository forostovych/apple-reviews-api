import re
from collections import Counter
from typing import List
from .review_model import Review
from nltk.util import ngrams


def _clean_tokens(text: str, stop: set):
    """
    Converts to lowercase, removes junk, splits into words,
    filters short tokens and stop-words.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if len(t) > 2 and t not in stop]
    return tokens


def extract_negative_bigrams(reviews, top_k=10):
    stop = {"the", "and", "you", "for", "but", "with", "this", "that", "are",
            "was", "very", "just", "not", "have", "has", "can", "get", "all",
            "its", "too"}

    tokens = []
    for r in reviews:
        if r.rating <= 2:
            tokens += _clean_tokens(r.text, stop)

    bigram_counts = Counter([" ".join(bg) for bg in ngrams(tokens, 2)])

    # Remove rare occurrences
    bigram_counts = {k: v for k, v in bigram_counts.items() if v >= 3}

    return sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)[:top_k]


def extract_negative_trigrams(reviews, top_k=10):
    stop = {"the", "and", "you", "for", "but", "with", "this", "that", "are"}

    tokens = []
    for r in reviews:
        if r.rating <= 2:
            tokens += _clean_tokens(r.text, stop)

    trigram_counts = Counter([" ".join(bg) for bg in ngrams(tokens, 3)])

    trigram_counts = {k: v for k, v in trigram_counts.items() if v >= 2}

    return sorted(trigram_counts.items(), key=lambda x: x[1], reverse=True)[:top_k]


def extract_negative_ngram_2_3(reviews, top_k=10):
    stop = {"the", "and", "you", "for", "but", "with", "this", "that"}

    tokens = []
    for r in reviews:
        if r.rating <= 2:
            tokens += _clean_tokens(r.text, stop)

    result = Counter()

    # bigrams
    for bg in ngrams(tokens, 2):
        result[" ".join(bg)] += 1

    # trigrams
    for tg in ngrams(tokens, 3):
        result[" ".join(tg)] += 1

    # Filter out garbage
    result = {k: v for k, v in result.items() if v >= 2}

    return sorted(result.items(), key=lambda x: x[1], reverse=True)[:top_k]


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def compute_metrics(reviews: List[Review]):
    ratings = [r.rating for r in reviews]
    avg = sum(ratings) / len(ratings)
    dist = {i: ratings.count(i) for i in range(1, 6)}
    return avg, dist


def extract_negative_keywords(reviews: List[Review], top_k=10):
    neg = [r for r in reviews if r.rating <= 2]
    if not neg:
        return []

    stop = {
        "i", "and", "to", "the", "it", "my", "for", "a", "in", "of",
        "t", "is", "was", "me", "on", "that", "this", "so", "but",
        "with", "at", "have", "had", "you", "your", "they", "are",
        "be", "as", "if", "just", "not", "from", "im", "do", "all",
        "or", "no", "m", "s", "very", "really",
        "instagram", "insta", "ig", "app",
        "dont", "cant", "doesnt",
    }

    tokens = []
    for r in neg:
        txt = clean_text(r.text)
        tokens += [w for w in txt.split() if w not in stop and len(w) > 2]

    counter = Counter(tokens)
    filtered = [(w, c) for w, c in counter.items() if c >= 3]
    filtered = sorted(filtered, key=lambda x: x[1], reverse=True)

    return filtered[:top_k]