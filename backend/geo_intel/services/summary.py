"""
Geo Intel AI Summary Service
Generates Ukrainian language summaries of geo activity
"""
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

from .aggregator import get_top_places, get_event_types_stats

logger = logging.getLogger(__name__)

# Try to import LLM
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM not available for geo summaries")


async def generate_geo_summary(
    db,
    days: int = 7,
    language: str = "uk"
) -> Dict:
    """
    Generate AI summary of geo activity in Ukrainian.
    """
    # Get stats
    top_places = await get_top_places(db, days=days, limit=20)
    event_types = await get_event_types_stats(db, days=days)
    
    # Get total counts
    since = datetime.now(timezone.utc) - timedelta(days=days)
    total_events = await db.tg_geo_events.count_documents({"createdAt": {"$gte": since}})
    
    stats = {
        "totalEvents": total_events,
        "topPlaces": top_places.get("items", [])[:10],
        "eventTypes": event_types.get("items", []),
        "days": days
    }
    
    if not LLM_AVAILABLE or total_events == 0:
        # Fallback summary without AI
        if total_events == 0:
            return {
                "ok": True,
                "summary": "Немає даних за вказаний період. Додайте канали до радару для збору геоподій.",
                "stats": stats
            }
        
        top_place = top_places.get("items", [{}])[0] if top_places.get("items") else {}
        return {
            "ok": True,
            "summary": f"За останні {days} днів зафіксовано {total_events} геоподій. "
                       f"Найчастіше згадується: {top_place.get('title', 'N/A')} ({top_place.get('count', 0)} разів).",
            "stats": stats
        }
    
    # Build prompt
    places_text = "\n".join([
        f"- {p['title']}: {p['count']} згадувань, тип: {p['eventType']}"
        for p in top_places.get("items", [])[:10]
    ])
    
    types_text = "\n".join([
        f"- {t['eventType']}: {t['count']}"
        for t in event_types.get("items", [])
    ])
    
    prompt = f"""Проаналізуй статистику геоподій за останні {days} днів.

Топ локацій:
{places_text}

Типи подій:
{types_text}

Всього подій: {total_events}

Напиши короткий аналіз українською мовою (2-3 речення):
- де найбільша концентрація активності
- які типи подій переважають
- загальна тенденція

Відповідай нейтрально, без оцінок. Тільки факти."""

    try:
        llm = LlmChat(
            api_key=os.getenv("EMERGENT_LLM_KEY", ""),
            model="gpt-4o-mini"
        )
        
        response = await llm.send_async([UserMessage(content=prompt)])
        summary_text = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "ok": True,
            "summary": summary_text,
            "stats": stats,
            "aiGenerated": True
        }
        
    except Exception as e:
        logger.error(f"AI summary error: {e}")
        return {
            "ok": True,
            "summary": f"За останні {days} днів зафіксовано {total_events} геоподій.",
            "stats": stats,
            "aiGenerated": False
        }
