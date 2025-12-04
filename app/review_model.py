from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .sentiment import Sentiment


@dataclass
class Review:
    recall_id: int
    rating: int
    title: str
    text: str
    created_at: Optional[datetime]
    sentiment: Optional[Sentiment] = None