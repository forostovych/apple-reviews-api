from enum import Enum

class VisualizationKind(str, Enum):
    RATINGS = "ratings"
    NEGATIVE_KEYWORDS = "negative_keywords"
    NEGATIVE_BIGRAMS = "negative_bigrams"
    NEGATIVE_TRIGRAMS = "negative_trigrams"
    NEGATIVE_NGRAM_2_3 = "negative_ngram_2_3"
    AI_INSIGHTS = "ai_insights"