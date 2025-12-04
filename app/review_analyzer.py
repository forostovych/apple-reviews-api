from typing import List, Dict
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import yake

from .review_model import Review
from .sentiment import Sentiment


class ReviewAnalyzer:
    def __init__(self):
        self.sentiment_model = SentimentIntensityAnalyzer()
        self.keyword_extractor = yake.KeywordExtractor()

    # ---- Sentiment ----
    def analyze_sentiment(self, r: Review) -> Sentiment:
        s = self.sentiment_model.polarity_scores(r.text)
        if s["compound"] >= 0.3:
            return Sentiment.POSITIVE
        elif s["compound"] <= -0.3:
            return Sentiment.NEGATIVE
        return Sentiment.NEUTRAL

    # ---- Keywords ----
    def extract_keywords(self, text: str, top_k: int = 5):
        return [kw for kw, score in self.keyword_extractor.extract_keywords(text)[:top_k]]

    # ---- Full analysis ----
    def run(self, reviews: List[Review]) -> Dict:
        for r in reviews:
            r.sentiment = self.analyze_sentiment(r)
            r.keywords = self.extract_keywords(r.text)

        positive = sum(1 for r in reviews if r.sentiment == Sentiment.POSITIVE)
        neutral  = sum(1 for r in reviews if r.sentiment == Sentiment.NEUTRAL)
        negative = sum(1 for r in reviews if r.sentiment == Sentiment.NEGATIVE)

        return {
            "sentiment_distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
            },
            "reviews": reviews
        }