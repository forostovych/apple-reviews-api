# 🍎 Apple Store Reviews Analysis API

An intelligent backend service for analyzing user feedback from the Apple App Store. This tool fetches reviews, performs statistical and sentiment analysis (VADER), extracts keywords/n-grams, and generates **actionable product insights using GPT-4o**.

## 🚀 Features

- **Data Fetching:** Scrapes real-time reviews from Apple App Store RSS feeds.
- **NLP Analysis:**
  - Sentiment analysis using **VADER**.
  - Negative keyword extraction (YAKE / Frequency analysis).
  - N-gram analysis (Bigrams, Trigrams).
- **AI-Powered Insights:** Uses **OpenAI GPT-4o-mini** to generate actionable business advice based on user complaints.
- **Visualization:** Generates charts and infographics (Matplotlib) via API endpoints.
- **Performance:** Asynchronous architecture using **FastAPI**.

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **FastAPI** (Web Framework)
- **OpenAI API** (LLM for Insights)
- **NLTK & YAKE** (Natural Language Processing)
- **Matplotlib** (Data Visualization)
- **Pydantic** (Data Validation)

---

## ⚙️ Installation & Setup

Follow these steps to deploy the project locally.

### 1. Clone the repository
```bash
git clone [https://github.com/forostovych/apple-reviews-api.git](https://github.com/forostovych/apple-reviews-api.git)
cd apple-reviews-api


### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

Windows:

Bash

python -m venv venv
.\venv\Scripts\activate
macOS / Linux:

Bash

python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies
Bash

pip install -r requirements.txt
Note: If you encounter errors related to NLTK data, run this python command once:

Bash

python -c "import nltk; nltk.download('vader_lexicon')"


### 4. Configure Environment Variables
Rename .env.example to .env.

Open .env and add your OpenAI API Key.

Ini, TOML

# .env
OPENAI_API_KEY=sk-your-real-openai-key-here


### ▶️ Running the Application
Start the server using Uvicorn:

Bash

uvicorn app.main:app --reload
The API will be available at: http://127.0.0.1:8000




📖 API Documentation & Usage
Once the server is running, you can access the interactive Swagger UI documentation at: 👉 http://127.0.0.1:8000/docs

Recommended Workflow



Конечно! Вот профессиональный, чистый и готовый к использованию README.md.

Я уже вставил твою ссылку на репозиторий в команду клонирования. Просто скопируй этот текст и вставь в файл README.md.

Markdown

# 🍎 Apple Store Reviews Analysis API

An intelligent backend service for analyzing user feedback from the Apple App Store. This tool fetches reviews, performs statistical and sentiment analysis (VADER), extracts keywords/n-grams, and generates **actionable product insights using GPT-4o**.

## 🚀 Features

- **Data Fetching:** Scrapes real-time reviews from Apple App Store RSS feeds.
- **NLP Analysis:**
  - Sentiment analysis using **VADER**.
  - Negative keyword extraction (YAKE / Frequency analysis).
  - N-gram analysis (Bigrams, Trigrams).
- **AI-Powered Insights:** Uses **OpenAI GPT-4o-mini** to generate actionable business advice based on user complaints.
- **Visualization:** Generates charts and infographics (Matplotlib) via API endpoints.
- **Performance:** Asynchronous architecture using **FastAPI**.

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **FastAPI** (Web Framework)
- **OpenAI API** (LLM for Insights)
- **NLTK & YAKE** (Natural Language Processing)
- **Matplotlib** (Data Visualization)
- **Pydantic** (Data Validation)

---

## ⚙️ Installation & Setup

Follow these steps to deploy the project locally.

### 1. Clone the repository
```bash
git clone [https://github.com/forostovych/apple-reviews-api.git](https://github.com/forostovych/apple-reviews-api.git)
cd apple-reviews-api
2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

Windows:

Bash

python -m venv venv
.\venv\Scripts\activate
macOS / Linux:

Bash

python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
Note: If you encounter errors related to NLTK data, run this python command once:

Bash

python -c "import nltk; nltk.download('vader_lexicon')"
4. Configure Environment Variables
Rename .env.example to .env.

Open .env and add your OpenAI API Key.

Ini, TOML

# .env
OPENAI_API_KEY=sk-your-real-openai-key-here
▶️ Running the Application
Start the server using Uvicorn:

Bash

uvicorn app.main:app --reload
The API will be available at: http://127.0.0.1:8000

📖 API Documentation & Usage
Once the server is running, you can access the interactive Swagger UI documentation at: 👉 http://127.0.0.1:8000/docs

Recommended Workflow
1. Fetch Reviews (Load data into cache)
POST /fetch_reviews Fetches the latest reviews from Apple servers.

Bash

curl -X 'POST' \
  '[http://127.0.0.1:8000/fetch_reviews?app_id=1447033725&limit=100](http://127.0.0.1:8000/fetch_reviews?app_id=1447033725&limit=100)'
2. Get AI Insights (Analyze data)
GET /analyze_reviews?use_ai=true Returns metrics, sentiment distribution, and GPT-generated advice.

Bash

curl -X 'GET' \
  '[http://127.0.0.1:8000/analyze_reviews?app_id=1447033725&use_ai=true](http://127.0.0.1:8000/analyze_reviews?app_id=1447033725&use_ai=true)'
3. Visualize Results (Get Infographic)
GET /visualize_reviews?kind=ai_insights Returns a PNG image with top problems and solutions.

Bash

curl -X 'GET' \
  '[http://127.0.0.1:8000/visualize_reviews?app_id=1447033725&kind=ai_insights](http://1



apple-reviews-api/
├── app/
│   ├── main.py              # Entry point
│   ├── ai_insights.py       # OpenAI integration
│   ├── analysis_service.py  # Core analysis logic
│   ├── processing.py        # NLP processing
│   ├── reviews_fetcher.py   # RSS Fetcher
│   └── ...
├── .env                     # Secrets (GitIgnored)
├── requirements.txt         # Dependencies
└── README.md                # Documentation