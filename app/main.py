# app/main.py

import textwrap
from typing import Dict, Any, List
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse

from .reviews_fetcher import fetch_reviews_by_rating_range
from .processing import (
    extract_negative_keywords,
    extract_negative_bigrams,
    extract_negative_trigrams,
    extract_negative_ngram_2_3,
)
from .review_model import Review
from .visualization_kind import VisualizationKind

from .analysis_kind import AnalysisKind
from .analysis_service import analyze_reviews_core

# Import AI analysis function
from .ai_insights import generate_actionable_insights


app = FastAPI(title="Apple Store Review Analysis API")

# In-memory cache
review_cache: Dict[int, Dict[str, Any]] = {}

# Default App ID (Nebula)
default_app_id = 1447033725


# ------------------------------------------------------------
# 1) Fetch + Cache
# ------------------------------------------------------------
@app.post("/fetch_reviews")
def fetch_reviews(
    app_id: int = Query(default_app_id, description="App Store numeric ID"),
    min_rating: int = Query(1, ge=1, le=5),
    max_rating: int = Query(5, ge=1, le=5),
    limit: int = Query(500, ge=1, le=500),
):
    """
    Fetches reviews from Apple RSS, filters by rating,
    and saves the selection to in-memory cache (review_cache).
    Analytics are NOT calculated here.
    """
    if min_rating > max_rating:
        raise HTTPException(status_code=400, detail="min_rating must be <= max_rating")

    try:
        reviews: List[Review] = fetch_reviews_by_rating_range(
            app_id=app_id,
            min_rating=min_rating,
            max_rating=max_rating,
            target_count=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews fetched from Apple RSS")

    review_cache[app_id] = {
        "min_rating": min_rating,
        "max_rating": max_rating,
        "requested_limit": limit,
        "reviews": reviews,
    }

    return {
        "app_id": app_id,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "requested_limit": limit,
        "returned_reviews": len(reviews),
        "message": "Reviews fetched and cached successfully. Call /analyze_reviews to get metrics.",
    }


# ------------------------------------------------------------
# 2) Analyze cached
# ------------------------------------------------------------
@app.get("/analyze_reviews")
async def analyze_reviews(
        app_id: int = Query(
            default_app_id,
            description="App Store numeric ID (previously fetched)",
        ),
        analysis_kind: AnalysisKind = Query(
            AnalysisKind.BASIC,
            description="Type of analysis: basic or vader",
        ),
        use_ai: bool = Query(
            True, 
            description="Enable AI insight analysis (GPT-4o-mini). Takes 3-10 sec."
        ),
    ):
    cache_entry = review_cache.get(app_id)
    if not cache_entry:
        raise HTTPException(
            status_code=404,
            detail="No cached reviews for this app_id. Call /fetch_reviews first.",
        )

    reviews: List[Review] = cache_entry["reviews"]

    if not reviews:
        raise HTTPException(status_code=404, detail="Cached reviews list is empty")

    # 1. Core mathematical analysis (VADER, Keywords, etc.)
    core_result = analyze_reviews_core(reviews, analysis_kind)

    # 2. AI Analytics (Actionable Insights)
    ai_insights_result = []
    
    if use_ai:
        # Convert Review objects to simple dicts for AI
        reviews_for_ai = [
            {"rating": r.rating, "title": r.title, "text": r.text} 
            for r in reviews
        ]
        # Async GPT call
        ai_response = await generate_actionable_insights(reviews_for_ai)
        ai_insights_result = ai_response.get("top_issues", [])

    return {
        "app_id": app_id,
        "min_rating": cache_entry["min_rating"],
        "max_rating": cache_entry["max_rating"],
        "requested_limit": cache_entry["requested_limit"],
        "returned_reviews": len(reviews),
        "analysis_kind": analysis_kind.value,
        
        # Processing / Vader Results
        "average_rating": core_result["average_rating"],
        "rating_distribution": core_result["rating_distribution"],
        "negative_keywords": core_result["negative_keywords"],
        "sentiment_distribution": core_result["sentiment_distribution"],
        
        # AI Result
        "ai_actionable_insights": ai_insights_result,

        "reviews": [
            {
                "recall_id": r.recall_id,
                "rating": r.rating,
                "title": r.title,
                "text": r.text,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "sentiment": r.sentiment.value if r.sentiment else None,
                "keywords": getattr(r, "keywords", None),
            }
            for r in reviews
        ],
    }


# ------------------------------------------------------------
# 3) Visualization
# ------------------------------------------------------------
@app.get("/visualize_reviews")
async def visualize_reviews(
    app_id: int = Query(
        default_app_id,
        description="App Store numeric ID (previously fetched)",
    ),
    kind: VisualizationKind = Query(
        VisualizationKind.RATINGS,
        description="Visualization type",
    ),
    top_k: int = Query(
        20,
        ge=5,
        le=100,
        description="How many items (keywords / n-grams) to show",
    ),
):
    cache_entry = review_cache.get(app_id)
    if not cache_entry:
        raise HTTPException(
            status_code=404,
            detail="No cached reviews for this app_id. Call /fetch_reviews first.",
        )

    reviews: List[Review] = cache_entry["reviews"]
    if not reviews:
        raise HTTPException(status_code=404, detail="Cached reviews list is empty")

    # Create canvas
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)

    # ==========================================
    # AI INFOGRAPHIC
    # ==========================================
    if kind == VisualizationKind.AI_INSIGHTS:
        reviews_for_ai = [{"rating": r.rating, "title": r.title, "text": r.text} for r in reviews]
        
        ai_response = await generate_actionable_insights(reviews_for_ai)
        insights = ai_response.get("top_issues", [])

        ax.axis("off") # Hide axes
        ax.set_title(f"AI Actionable Insights for App ID {app_id}", fontsize=16, fontweight="bold", pad=20)

        if not insights:
            ax.text(0.5, 0.5, "No Insights Generated", ha="center", va="center", fontsize=20)
        else:
            y_pos = 0.90
            
            for i, item in enumerate(insights, 1):
                problem = item.get("problem_description", "N/A")
                action = item.get("improvement_option", "N/A")

                wrapped_problem = textwrap.fill(f"[!] PROBLEM: {problem}", width=80)
                wrapped_action = textwrap.fill(f"[V] ACTION: {action}", width=80)

                ax.text(0.05, y_pos, wrapped_problem, fontsize=12, color="#b71c1c", 
                        fontweight="bold", va="top", fontfamily="sans-serif")
                
                lines_p = wrapped_problem.count('\n') + 1
                y_pos -= (0.03 * lines_p + 0.02)

                ax.text(0.05, y_pos, wrapped_action, fontsize=12, color="#1b5e20", 
                        va="top", fontfamily="sans-serif")
                
                lines_a = wrapped_action.count('\n') + 1
                y_pos -= (0.03 * lines_a + 0.05)
                
                ax.axhline(y=y_pos + 0.02, xmin=0.05, xmax=0.95, color="#cccccc", linestyle="--", linewidth=0.5)

    # ==========================================
    # PLOTS
    # ==========================================
    elif kind == VisualizationKind.RATINGS:
        ratings = [r.rating for r in reviews]
        dist = {i: ratings.count(i) for i in range(1, 6)}
        ax.bar(dist.keys(), dist.values(), color="#4285F4")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        ax.set_title(f"Rating distribution for app_id={app_id}")
        ax.set_xticks([1, 2, 3, 4, 5])

    elif kind == VisualizationKind.NEGATIVE_KEYWORDS:
        items = extract_negative_keywords(reviews, top_k=top_k)
        if not items:
            plt.close(fig)
            raise HTTPException(status_code=404, detail="No negative keywords")
        labels, values = zip(*items)
        ax.barh(labels, values, color="#EA4335")
        ax.set_title(f"Top {top_k} negative keywords")
        ax.invert_yaxis()

    elif kind == VisualizationKind.NEGATIVE_BIGRAMS:
        items = extract_negative_bigrams(reviews, top_k=top_k)
        if not items:
            plt.close(fig)
            raise HTTPException(status_code=404, detail="No bigrams")
        labels, values = zip(*items)
        ax.barh(labels, values, color="#FBBC05")
        ax.set_title(f"Top {top_k} negative bigrams")
        ax.invert_yaxis()

    elif kind == VisualizationKind.NEGATIVE_TRIGRAMS:
        items = extract_negative_trigrams(reviews, top_k=top_k)
        if not items:
            plt.close(fig)
            raise HTTPException(status_code=404, detail="No trigrams")
        labels, values = zip(*items)
        ax.barh(labels, values, color="#34A853")
        ax.set_title(f"Top {top_k} negative trigrams")
        ax.invert_yaxis()

    elif kind == VisualizationKind.NEGATIVE_NGRAM_2_3:
        items = extract_negative_ngram_2_3(reviews, top_k=top_k)
        if not items:
            plt.close(fig)
            raise HTTPException(status_code=404, detail="No n-grams")
        labels, values = zip(*items)
        ax.barh(labels, values, color="purple")
        ax.set_title(f"Top {top_k} negative n-grams (2-3)")
        ax.invert_yaxis()

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")