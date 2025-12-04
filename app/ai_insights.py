import os
import openai
from typing import List, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel

# 1. Load environment variables
load_dotenv()

# 2. Initialize the client
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 3. Define response models (Pydantic)
class Insight(BaseModel):
    problem_description: str
    improvement_option: str


class ProductAnalysis(BaseModel):
    top_issues: List[Insight]


# 4. Helper function to format text
def _format_reviews(reviews: List[Dict], limit: int = 30) -> str:
    # Filter: take only reviews with rating <= 3
    problematic = [r for r in reviews if r.get("rating", 5) <= 3]
    # If no problematic reviews, take any, but within the limit
    selection = problematic[:limit] if problematic else reviews[:limit]

    if not selection:
        return ""

    text_block = "Reviews:\n"
    for i, r in enumerate(selection, 1):
        title = r.get("title", "")
        # Remove line breaks in text to avoid confusing the AI
        body = r.get("text", "").replace("\n", " ").strip()
        text_block += f"{i}. {title}. {body}\n"
    return text_block


# 5. MAIN FUNCTION (Imported in main.py)
async def generate_actionable_insights(reviews: List[Dict]) -> Dict[str, Any]:
    # If key is missing, don't crash, return a placeholder
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "top_issues": [
                {
                    "problem_description": "API Key missing",
                    "improvement_option": "Add OPENAI_API_KEY to .env file"
                }
            ]
        }

    reviews_text = _format_reviews(reviews)

    if not reviews_text:
        return {"top_issues": []}

    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Middle Product Manager. Analyze the reviews. Highlight the top 3 problems. Be concise."
                },
                {"role": "user", "content": reviews_text},
            ],
            response_format=ProductAnalysis,
        )

        parsed_result = completion.choices[0].message.parsed
        return parsed_result.model_dump()

    except Exception as e:
        # Catch any OpenAI errors (no funds, network issues) to prevent server crash
        return {
            "top_issues": [
                {
                    "problem_description": "AI Error",
                    "improvement_option": str(e)
                }
            ]
        }