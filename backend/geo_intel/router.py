"""
Geo Intel API Router
All endpoints for the Geo/Radar module
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional

from .services.aggregator import get_map_points, get_top_places, get_heatmap_data, get_event_types_stats
from .services.proximity import get_nearby_events, evaluate_radar_alert
from .services.summary import generate_geo_summary
from .services.builder import build_geo_events_for_channel, rebuild_all_channels
from .__version__ import VERSION

logger = logging.getLogger(__name__)


def build_geo_router(db, config) -> APIRouter:
    """Build the geo intel router"""
    
    router = APIRouter(prefix="/api/geo", tags=["geo-intel"])
    
    # ==================== Health & Version ====================
    
    @router.get("/health")
    async def geo_health():
        """Geo module health check"""
        return {
            "ok": True,
            "module": "geo-intel",
            "version": VERSION,
            "config": {
                "defaultCity": config.default_city,
                "schedulerEnabled": config.enable_scheduler
            }
        }
    
    @router.get("/version")
    async def geo_version():
        """Get module version"""
        return {"version": VERSION, "frozen": False}
    
    # ==================== Map & Visualization ====================
    
    @router.get("/map")
    async def map_points(
        days: int = Query(7, ge=1, le=90),
        type: Optional[str] = Query(None, description="Event type filter"),
        limit: int = Query(500, ge=1, le=2000)
    ):
        """Get geo events as map points"""
        return await get_map_points(db, days=days, event_type=type, limit=limit)
    
    @router.get("/heatmap")
    async def heatmap_data(days: int = Query(7, ge=1, le=90)):
        """Get heatmap density data"""
        return await get_heatmap_data(db, days=days)
    
    @router.get("/top")
    async def top_places(
        days: int = Query(30, ge=1, le=90),
        limit: int = Query(50, ge=1, le=200)
    ):
        """Get top places by mention frequency"""
        return await get_top_places(db, days=days, limit=limit)
    
    @router.get("/event-types")
    async def event_types(days: int = Query(30, ge=1, le=90)):
        """Get event type distribution"""
        return await get_event_types_stats(db, days=days)
    
    # ==================== Proximity/Radar ====================
    
    @router.get("/radar")
    async def radar_nearby(
        lat: float = Query(..., description="Latitude"),
        lng: float = Query(..., description="Longitude"),
        radius: int = Query(500, ge=100, le=5000, description="Radius in meters"),
        days: int = Query(7, ge=1, le=30)
    ):
        """Get events near a location (radar mode)"""
        return await get_nearby_events(db, lat=lat, lng=lng, radius_m=radius, days=days)
    
    @router.get("/radar/alert")
    async def radar_alert_check(
        lat: float = Query(...),
        lng: float = Query(...),
        radius: int = Query(500, ge=100, le=5000),
        hours: int = Query(1, ge=1, le=24)
    ):
        """Check if radar should alert (events in last N hours)"""
        return await evaluate_radar_alert(db, lat=lat, lng=lng, radius_m=radius, hours=hours)
    
    # ==================== Summary ====================
    
    @router.get("/summary")
    async def summary(
        days: int = Query(7, ge=1, le=90),
        lang: str = Query("uk", description="Language: uk/ru/en")
    ):
        """Get AI-generated summary of geo activity"""
        return await generate_geo_summary(db, days=days, language=lang)
    
    # ==================== Radar Channels Management ====================
    
    @router.get("/channels")
    async def list_radar_channels(
        enabled_only: bool = Query(False)
    ):
        """List channels in radar watchlist"""
        query = {"enabled": True} if enabled_only else {}
        channels = await db.tg_radar_channels.find(query, {"_id": 0}).to_list(100)
        return {"ok": True, "items": channels, "total": len(channels)}
    
    @router.post("/channels")
    async def add_radar_channel(request: Request):
        """Add channel to radar watchlist"""
        body = await request.json()
        username = body.get("username", "").lower().replace("@", "").strip()
        
        if not username:
            raise HTTPException(status_code=400, detail="username required")
        
        # Check if channel exists in tg_channel_states
        channel_info = await db.tg_channel_states.find_one({"username": username})
        
        doc = {
            "username": username,
            "title": channel_info.get("title", username) if channel_info else username,
            "avatarUrl": channel_info.get("avatarUrl") if channel_info else None,
            "members": channel_info.get("participantsCount", 0) if channel_info else 0,
            "addedAt": datetime.now(timezone.utc),
            "lastScanAt": None,
            "eventsCount": 0,
            "enabled": True
        }
        
        try:
            await db.tg_radar_channels.update_one(
                {"username": username},
                {"$setOnInsert": doc},
                upsert=True
            )
            return {"ok": True, "channel": doc}
        except Exception as e:
            logger.error(f"Add channel error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/channels/{username}")
    async def remove_radar_channel(username: str):
        """Remove channel from radar watchlist"""
        clean = username.lower().replace("@", "").strip()
        result = await db.tg_radar_channels.delete_one({"username": clean})
        return {"ok": True, "deleted": result.deleted_count > 0}
    
    @router.patch("/channels/{username}")
    async def update_radar_channel(username: str, request: Request):
        """Update channel settings (enable/disable)"""
        body = await request.json()
        clean = username.lower().replace("@", "").strip()
        
        update = {}
        if "enabled" in body:
            update["enabled"] = bool(body["enabled"])
        
        if update:
            await db.tg_radar_channels.update_one(
                {"username": clean},
                {"$set": update}
            )
        
        return {"ok": True, "username": clean}
    
    # ==================== Search ====================
    
    @router.get("/search/channels")
    async def search_channels(
        q: str = Query(..., min_length=2, description="Search query")
    ):
        """Search Telegram channels (from existing tg_channel_states)"""
        query = {
            "$or": [
                {"username": {"$regex": q, "$options": "i"}},
                {"title": {"$regex": q, "$options": "i"}}
            ]
        }
        
        channels = await db.tg_channel_states.find(
            query,
            {"_id": 0, "username": 1, "title": 1, "avatarUrl": 1, "participantsCount": 1}
        ).limit(20).to_list(20)
        
        # Check which are already in radar
        radar_usernames = set()
        radar_channels = await db.tg_radar_channels.find({}, {"username": 1}).to_list(100)
        for rc in radar_channels:
            radar_usernames.add(rc["username"])
        
        for ch in channels:
            ch["inRadar"] = ch["username"] in radar_usernames
        
        return {"ok": True, "items": channels, "total": len(channels)}
    
    # ==================== Admin/Build ====================
    
    @router.post("/admin/rebuild")
    async def admin_rebuild(
        days: int = Query(7, ge=1, le=30)
    ):
        """Rebuild geo events for all enabled radar channels"""
        result = await rebuild_all_channels(db, days=days)
        return {"ok": True, **result}
    
    @router.post("/admin/rebuild/{username}")
    async def admin_rebuild_channel(
        username: str,
        days: int = Query(7, ge=1, le=30)
    ):
        """Rebuild geo events for a specific channel"""
        clean = username.lower().replace("@", "").strip()
        result = await build_geo_events_for_channel(db, username=clean, days=days)
        return {"ok": True, **result}
    
    @router.post("/admin/seed")
    async def admin_seed_data(
        count: int = Query(200, ge=10, le=500)
    ):
        """Seed test geo events for development"""
        from .dev_seed import seed_geo_events
        result = await seed_geo_events(db, count=count)
        return {"ok": True, **result}
    
    @router.delete("/admin/seed")
    async def admin_clear_seed():
        """Clear seeded test data"""
        from .dev_seed import clear_seed_data
        result = await clear_seed_data(db)
        return {"ok": True, **result}
    
    # ==================== Stats ====================
    
    @router.get("/stats")
    async def geo_stats(days: int = Query(30)):
        """Get overall geo module statistics"""
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        total_events = await db.tg_geo_events.count_documents({"createdAt": {"$gte": since}})
        total_channels = await db.tg_radar_channels.count_documents({})
        enabled_channels = await db.tg_radar_channels.count_documents({"enabled": True})
        
        # Get event types distribution
        event_types = await get_event_types_stats(db, days=days)
        
        # Recent activity (events per day)
        pipeline = [
            {"$match": {"createdAt": {"$gte": since}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$createdAt"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": -1}},
            {"$limit": 7}
        ]
        daily_activity = []
        async for doc in db.tg_geo_events.aggregate(pipeline):
            daily_activity.append({"date": doc["_id"], "count": doc["count"]})
        
        return {
            "ok": True,
            "totalEvents": total_events,
            "totalChannels": total_channels,
            "enabledChannels": enabled_channels,
            "eventTypes": event_types.get("items", []),
            "dailyActivity": daily_activity,
            "days": days
        }
    
    return router
