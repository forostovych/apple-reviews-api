from enum import Enum

class AnalysisKind(str, Enum):
    BASIC = "basic"   # Basic metrics and negative keywords only
    VADER = "vader"   # Additionally VADER sentiment + keywords