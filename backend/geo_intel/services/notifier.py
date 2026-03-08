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
    type_emoji = "🦠" if event_type == "virus" else "🗑️"
    type_label = "вірус" if event_type == "virus" else "сміття"
    
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
Тип: {type_label}

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
    virus_count = sum(1 for e in events if e.get("eventType") == "virus")
    trash_count = sum(1 for e in events if e.get("eventType") == "trash")
    
    types_summary = []
    if virus_count > 0:
        types_summary.append(f"🦠 {virus_count} вірус")
    if trash_count > 0:
        types_summary.append(f"🗑️ {trash_count} сміття")
    
    # Nearest event
    nearest = events[0] if events else None
    
    text = f"""
⚠️ <b>Увага — {count} сигналів поблизу</b>

📍 В радіусі {radius}м знайдено:
{', '.join(types_summary)}

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
✅ <b>Geo Radar Bot підключено</b>

Бот налаштовано правильно.
Ви будете отримувати сповіщення про події поблизу:

🦠 Вірус
🗑️ Сміття

Щоб налаштувати радіус — використовуйте веб-інтерфейс.
"""
    
    return await send_telegram_alert(chat_id, text.strip(), bot_token=bot_token)
