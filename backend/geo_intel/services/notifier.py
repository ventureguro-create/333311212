"""
Telegram Alert Notifier Service
Sends proximity alerts via Telegram Bot API
"""
import os
import logging
import httpx
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.environ.get("GEO_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN")


async def send_telegram_alert(
    chat_id: int,
    text: str,
    parse_mode: str = "HTML",
    bot_token: str = None
) -> Dict:
    """
    Send alert message via Telegram Bot API.
    """
    token = bot_token or BOT_TOKEN
    
    if not token:
        logger.warning("No bot token configured for Telegram alerts")
        return {"ok": False, "error": "NO_BOT_TOKEN"}
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                },
                timeout=10.0
            )
            
            data = response.json()
            
            if data.get("ok"):
                logger.info(f"Alert sent to chat {chat_id}")
                return {"ok": True, "message_id": data.get("result", {}).get("message_id")}
            else:
                logger.error(f"Telegram API error: {data}")
                return {"ok": False, "error": data.get("description")}
                
    except Exception as e:
        logger.error(f"Send alert error: {e}")
        return {"ok": False, "error": str(e)}


def format_proximity_alert(
    event_type: str,
    title: str,
    distance: int,
    minutes_ago: int,
    confidence: float = 0.5,
    base_url: str = None
) -> str:
    """
    Format proximity alert message in Ukrainian.
    """
    # Event type emoji
    type_emoji = {
        "virus": "🦠",
        "place": "📍",
        "food": "🍔",
        "venue": "🏛️",
        "traffic": "🚗",
        "infrastructure": "🏗️"
    }.get(event_type, "📍")
    
    # Time formatting
    if minutes_ago < 60:
        time_str = f"{minutes_ago} хв тому"
    elif minutes_ago < 1440:
        time_str = f"{minutes_ago // 60} год тому"
    else:
        time_str = f"{minutes_ago // 1440} дн тому"
    
    # Confidence label
    if confidence >= 0.8:
        conf_label = "🟢 Висока"
    elif confidence >= 0.5:
        conf_label = "🟡 Середня"
    else:
        conf_label = "🟠 Низька"
    
    text = f"""
⚠️ <b>Увага — сигнал поблизу</b>

{type_emoji} <b>{title}</b>

📏 Відстань: <b>{distance} м</b>
🕐 Час: {time_str}
📊 Впевненість: {conf_label}
"""
    
    if base_url:
        text += f"\n🗺️ <a href=\"{base_url}/radar\">Відкрити карту</a>"
    
    return text.strip()


def format_multiple_events_alert(
    events: list,
    radius: int,
    base_url: str = None
) -> str:
    """
    Format alert for multiple nearby events.
    """
    count = len(events)
    
    # Get types summary
    types = {}
    for e in events:
        t = e.get("eventType", "place")
        types[t] = types.get(t, 0) + 1
    
    types_summary = ", ".join([f"{v}x {k}" for k, v in types.items()])
    
    # Nearest event
    nearest = events[0] if events else None
    
    text = f"""
⚠️ <b>Увага — {count} сигналів поблизу</b>

📍 В радіусі {radius}м знайдено:
{types_summary}

"""
    
    if nearest:
        text += f"""
<b>Найближчий:</b>
{nearest.get('title', 'Невідомо')}
~{nearest.get('distanceMeters', '?')} м від вас
"""
    
    if base_url:
        text += f"\n🗺️ <a href=\"{base_url}/radar\">Відкрити карту</a>"
    
    return text.strip()


async def send_test_alert(chat_id: int, bot_token: str = None) -> Dict:
    """
    Send test alert to verify bot connection.
    """
    text = """
✅ <b>Тест Geo Radar Bot</b>

Бот налаштовано правильно.
Ви будете отримувати сповіщення про події поблизу.

Щоб налаштувати радіус:
/radius 1000

Щоб вимкнути сповіщення:
/stop
"""
    
    return await send_telegram_alert(chat_id, text.strip(), bot_token=bot_token)
