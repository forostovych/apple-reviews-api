import logging
from typing import List, Dict, Optional
import requests
from concurrent.futures import ThreadPoolExecutor

# Імпорт ваших моделей та парсера тут...
from .review_parser import parse_review
from .review_model import Review

logger = logging.getLogger(__name__)

BASE_URL = "https://itunes.apple.com"

# --- Ваша функція _fetch_rss_page залишається синхронною ---
def _fetch_rss_page(app_id: int, country: str, page: int) -> Optional[List[Dict]]:
    """
    Завантажує одну RSS-сторінку.
    Повертає список відгуків або None, якщо сталася помилка.
    """
    url = (
        f"{BASE_URL}/{country}/rss/customerreviews/"
        f"page={page}/id={app_id}/sortBy=mostRecent/json"
    )

    logger.info(f"Fetching RSS page {page}: {url}")

    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException as e:
        logger.error(f"Request error for page {page}: {e}")
        return None  # Повертаємо None при помилці

    if resp.status_code != 200:
        logger.warning(f"RSS page {page} returned status {resp.status_code}")
        return None

    try:
        data = resp.json()
    except ValueError:
        logger.error(f"Invalid JSON from Apple RSS on page {page}.")
        return None

    entries = data.get("feed", {}).get("entry", [])
    if not entries:
        return None # Повертаємо None, якщо немає відгуків (кінець пагінації)

    # ... (Частина з парсингом відгуків у Dict залишається без змін) ...
    # Ми можемо спростити, просто повертаючи 'entries' і парсячи їх пізніше
    
    # Використовуємо вашу існуючу логіку парсингу для чистоти:
    reviews: List[Dict] = []
    # (Весь цикл for entry in entries ... повинен бути тут)
    # Щоб не дублювати код, припустимо, що _fetch_rss_page повертає лише list[Dict]
    # Як у вашому оригінальному коді:
    
    # [Ваш існуючий парсинг тут, для кінцевої List[Dict]]
    
    # Тимчасово повернемо сирі дані, щоб фокусуватись на паралелізмі:
    # return entries 
    # Щоб відповідати вашому оригінальному коду:
    # ... (повернути оброблені 'reviews', як у вашому оригіналі)
    return reviews


def fetch_reviews_parallel(
    app_id: int,
    min_rating: int = 1,
    max_rating: int = 5,
    target_count: int = 50,
    country: str = "us",
    max_pages: int = 10
) -> List[Review]:
    """
    Виконує паралельні запити для збору всіх доступних сторінок.
    """

    # 1. Готуємо список усіх сторінок для завантаження
    pages_to_fetch = list(range(1, max_pages + 1))
    collected_raw: List[Dict] = []

    # 2. Використовуємо ThreadPoolExecutor для паралельних запитів
    with ThreadPoolExecutor(max_workers=max_pages) as executor:
        # Створюємо завдання для кожної сторінки
        future_to_page = {
            executor.submit(_fetch_rss_page, app_id, country, page): page 
            for page in pages_to_fetch
        }
        
        # Обробляємо результати, що надходять
        for future in concurrent.futures.as_completed(future_to_page):
            page = future_to_page[future]
            try:
                page_reviews = future.result()
            except Exception as exc:
                logger.error(f"Page {page} generated an exception: {exc}")
                continue # Пропускаємо сторінку, що викликала помилку

            if page_reviews is None:
                # Це може означати 404/порожню сторінку, що є нормальним для кінця
                logger.info(f"Page {page} returned no reviews or error.")
                continue

            # 3. Фільтрація та збір (виконується в основному потоці)
            for r in page_reviews:
                if min_rating <= r["rating"] <= max_rating:
                    collected_raw.append(r)

    # 4. Обмеження до target_count (якщо target_count менше, ніж 500)
    final_raw = collected_raw[:target_count]
    
    # 5. Фінальний парсинг
    result: List[Review] = []
    for idx, raw in enumerate(final_raw, start=1):
        result.append(parse_review(raw, recall_id=idx))

    return result