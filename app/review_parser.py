from datetime import datetime
from typing import Dict, Optional
from .review_model import Review


def parse_review(raw: Dict, recall_id: int) -> Review:
    date_raw = raw.get("date")
    created_at: Optional[datetime] = None

    if date_raw:
        try:
            created_at = datetime.fromisoformat(date_raw.replace("Z", "+00:00"))
        except Exception:
            created_at = None

    return Review(
        recall_id=recall_id,
        rating=raw.get("rating", 0),
        title=raw.get("title", ""),
        text=raw.get("text", ""),
        created_at=created_at,
        sentiment=None,
    )