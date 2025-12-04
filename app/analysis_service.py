from typing import List, Dict, Any

from .review_model import Review
from .processing import compute_metrics, extract_negative_keywords
from .review_analyzer import ReviewAnalyzer
from .analysis_kind import AnalysisKind


# One shared instance of VADER/YAKE per process
_review_analyzer = ReviewAnalyzer()


def analyze_reviews_core(
    reviews: List[Review],
    analysis_kind: AnalysisKind,
) -> Dict[str, Any]:
    """
    Unified entry point for review analysis:
    - Basic metrics (average rating, distribution)
    - Negative keywords
    - Optionally VADER sentiment
    """
    # Basic metrics
    avg, dist = compute_metrics(reviews)
    neg_keywords = extract_negative_keywords(reviews)

    sentiment_distribution = None

    # Additional VADER analysis
    if analysis_kind == AnalysisKind.VADER:
        analyzed = _review_analyzer.run(reviews)
        sentiment_distribution = analyzed["sentiment_distribution"]
        # Note: run() enriches the Review objects themselves
        # with r.sentiment and r.keywords fields

    return {
        "average_rating": avg,
        "rating_distribution": dist,
        "negative_keywords": neg_keywords,
        "sentiment_distribution": sentiment_distribution,
    }