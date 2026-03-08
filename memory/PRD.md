# Geo Intelligence / Radar Module PRD

## Original Problem Statement
Разработка автономного Geo/Radar модуля без MTProto. Этап 1 - работа на seed/mock данных.
Telegram потом будет просто source adapter / event producer.

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Leaflet + TailwindCSS
- **Database**: MongoDB (tg_geo_events, geo_alert_subscriptions, geo_alert_log)

## Core Features Implemented (2026-03-08)

### Backend Services
- ✅ `geo_intel/services/proximity.py` - Radar nearby events with distanceMeters, isInsideRadius, freshnessScore
- ✅ `geo_intel/services/stats.py` - Places, hourly, weekday, district statistics
- ✅ `geo_intel/services/predictor.py` - Simple statistical predictions (no ML)
- ✅ `geo_intel/services/subscriptions.py` - Alert subscriptions management
- ✅ `geo_intel/services/notifier.py` - Telegram alert delivery
- ✅ `geo_intel/utils/geo_distance.py` - Haversine distance calculation
- ✅ `geo_intel/utils/freshness.py` - Freshness scoring

### Backend Endpoints
- ✅ GET /api/geo/health
- ✅ GET /api/geo/map
- ✅ GET /api/geo/radar?lat=&lng=&radius=
- ✅ GET /api/geo/stats
- ✅ GET /api/geo/stats/places
- ✅ GET /api/geo/stats/hourly
- ✅ GET /api/geo/stats/weekday
- ✅ GET /api/geo/stats/full
- ✅ GET /api/geo/predict
- ✅ POST /api/geo/alerts/subscribe
- ✅ POST /api/geo/alerts/test
- ✅ POST /api/geo/admin/seed

### Frontend
- ✅ RadarPage with Map/List/Stats views
- ✅ GeoMap with radar mode, user pulse marker, radar circle
- ✅ Geolocation support (watchPosition)
- ✅ Radar toggle with radius selector
- ✅ Event highlighting inside radius
- ✅ Ukrainian localization

## User Personas
1. **Analyst** - Uses map and stats to understand geo patterns
2. **Field User** - Uses radar mode to see nearby events in real-time
3. **Admin** - Seeds test data, manages channels

## P0 Features (Done)
- [x] Seed data with gradient density
- [x] Map with markers/clusters
- [x] Radar endpoint with distance calculation
- [x] Stats with hourly/weekday/district breakdown
- [x] Prediction layer (statistical)
- [x] User location tracking
- [x] Radar circle visualization

## P1 Features (Next)
- [ ] Telegram alert subscription flow
- [ ] Proximity alert worker (scheduler)
- [ ] AI summary generation (LLM integration)
- [ ] Heatmap toggle

## P2 Features (Backlog)
- [ ] MTProto Telegram ingestion
- [ ] Temporal playback
- [ ] Predictive zones overlay
- [ ] Mobile PWA support

## Testing Status
- Backend: 100% pass
- Frontend: 100% pass
- Integration: 100% pass
