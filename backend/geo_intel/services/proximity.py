"""
Geo Intel Proximity Service
Radar/nearby events queries
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


async def get_nearby_events(
    db,
    lat: float,
    lng: float,
    radius_m: int = 500,
    days: int = 7,
    limit: int = 50
) -> Dict:
    """
    Get events within radius of a point.
    Uses simple distance calculation (works without 2dsphere index).
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Calculate bounding box (approximate)
    # 1 degree lat ≈ 111km, 1 degree lng ≈ 111km * cos(lat)
    lat_delta = radius_m / 111000
    lng_delta = radius_m / (111000 * 0.65)  # cos(50°) ≈ 0.65
    
    try:
        # Query with bounding box
        cursor = db.tg_geo_events.find({
            "createdAt": {"$gte": since},
            "location.lat": {"$gte": lat - lat_delta, "$lte": lat + lat_delta},
            "location.lng": {"$gte": lng - lng_delta, "$lte": lng + lng_delta},
        }, {"_id": 0}).limit(limit * 2)  # Get more to filter by actual distance
        
        items = []
        async for event in cursor:
            loc = event.get("location", {})
            event_lat = loc.get("lat")
            event_lng = loc.get("lng")
            
            if event_lat is None or event_lng is None:
                continue
            
            # Calculate actual distance (Haversine simplified)
            dlat = (event_lat - lat) * 111000
            dlng = (event_lng - lng) * 111000 * 0.65
            distance = (dlat**2 + dlng**2) ** 0.5
            
            if distance <= radius_m:
                items.append({
                    "id": event.get("dedupeKey"),
                    "eventType": event.get("eventType", "place"),
                    "title": event.get("title", ""),
                    "lat": event_lat,
                    "lng": event_lng,
                    "distance": round(distance),
                    "source": event.get("source", {}),
                    "createdAt": event.get("createdAt"),
                    "evidenceText": event.get("evidenceText", "")[:150]
                })
        
        # Sort by distance and limit
        items.sort(key=lambda x: x.get("distance", 0))
        items = items[:limit]
        
        return {
            "ok": True,
            "items": items,
            "total": len(items),
            "center": {"lat": lat, "lng": lng},
            "radius": radius_m
        }
        
    except Exception as e:
        logger.error(f"Proximity query error: {e}")
        return {
            "ok": False,
            "error": str(e),
            "items": [],
            "total": 0
        }


async def evaluate_radar_alert(
    db,
    lat: float,
    lng: float,
    radius_m: int = 500,
    hours: int = 1
) -> Dict:
    """
    Evaluate if radar should trigger alert.
    Returns alert status and recent events.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    result = await get_nearby_events(db, lat, lng, radius_m, days=1, limit=10)
    
    if not result.get("ok"):
        return {"alert": False, "reason": "query_error"}
    
    # Filter to only recent events
    recent_events = [
        e for e in result.get("items", [])
        if e.get("createdAt") and e["createdAt"] >= since
    ]
    
    if not recent_events:
        return {"alert": False, "count": 0, "events": []}
    
    return {
        "alert": True,
        "count": len(recent_events),
        "events": recent_events[:5],
        "message": f"{len(recent_events)} подій за останню годину в радіусі {radius_m}м"
    }
