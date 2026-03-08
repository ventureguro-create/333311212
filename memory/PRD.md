# Geo Intelligence / Radar Module PRD

## Original Problem Statement
Розробка автономного Geo/Radar модуля з Telegram Bot alerts, Background Scheduler, AI Summary.
Telegram використовується як канал доставки сповіщень, не як ingestion source (поки що).

## Architecture
- **Backend**: FastAPI + MongoDB + Telegram Bot + LLM
- **Frontend**: React + Leaflet + TailwindCSS
- **Database**: MongoDB (tg_geo_events, geo_alert_subscriptions, geo_bot_users, geo_alert_log)
- **Bot**: @Free_thinker_bot (token: 8646451851)

## Core Features Implemented

### Етап 1 (2026-03-08) - Geo Core
- ✅ Radar API з distanceMeters, isInsideRadius, freshnessScore
- ✅ Stats API (places, hourly, weekday, districts)
- ✅ Predictions (статистичний прогноз)
- ✅ Frontend Radar Mode з pulse marker
- ✅ Seed Data (virus + trash тільки)

### Етап 2 (2026-03-08) - Delivery Layer
- ✅ **Telegram Bot** (@Free_thinker_bot)
  - /start, /radar_on, /radar_off, /test, /status
  - Location handling
  - Ukrainian messages
- ✅ **Geo Alert Scheduler**
  - Background worker кожні 60 сек
  - Proximity checks
  - Cooldown 30 хв
  - Deduplication
- ✅ **AI Summary**
  - GPT-4o через EMERGENT_LLM_KEY
  - Ukrainian text generation
  - Stats aggregation

### Backend Services
- `geo_intel/services/bot.py` - Telegram bot polling
- `geo_intel/services/scheduler.py` - Alert scheduler
- `geo_intel/services/summary.py` - AI Summary з LLM
- `geo_intel/services/proximity.py` - Radar queries
- `geo_intel/services/stats.py` - Statistics
- `geo_intel/services/predictor.py` - Predictions
- `geo_intel/services/subscriptions.py` - Alert subscriptions
- `geo_intel/services/notifier.py` - Telegram delivery

### API Endpoints
- GET /api/geo/health
- GET /api/geo/map
- GET /api/geo/radar?lat=&lng=&radius=
- GET /api/geo/summary?use_llm=true
- GET /api/geo/stats/full
- GET /api/geo/predict
- POST /api/geo/alerts/subscribe
- POST /api/geo/alerts/test

## Event Types
- 🦠 virus (60%)
- 🗑️ trash (40%)

## User Flow
1. User відкриває карту → бачить події
2. User пише /start боту → реєстрація
3. User пише /radar_on → увімкнення сповіщень
4. User ділиться локацією → збереження позиції
5. Scheduler знаходить події поруч → відправка alert

## P0 Features (Done)
- [x] Geo Core (radar, stats, predictions)
- [x] Telegram Bot delivery
- [x] Alert Scheduler
- [x] AI Summary

## P1 Features (Next)
- [ ] Playback (activity timeline)
- [ ] Pattern Detection (hotspots, movements)
- [ ] Heatmap toggle

## P2 Features (Later)
- [ ] Risk Map
- [ ] Route Safety
- [ ] MTProto ingestion

## Testing Status (2026-03-08)
- Backend: 100% pass
- Frontend: 100% pass
- Telegram Bot: 100% configured
- AI Integration: 100% working
