# Geo Intelligence / Radar Module PRD

## Original Problem Statement
Розробка повнофункціонального Geo Intelligence модуля з:
- Event Types системою
- Probability Engine
- Event Fusion
- Signal Decay
- Telegram Bot alerts
- AI Summary

## Architecture
- **Backend**: FastAPI + MongoDB + Telegram Bot + LLM (GPT-4o)
- **Frontend**: React + Leaflet + TailwindCSS
- **Schedulers**: Alert Scheduler + Intelligence Scheduler
- **Bot**: @Free_thinker_bot

## Event Types (з severity)
| Type | Icon | Severity | Lifetime |
|------|------|----------|----------|
| virus | 🦠 | 3 | 60 min |
| trash | 🗑️ | 2 | 120 min |
| rain | 🌧️ | 1 | 45 min |
| heavy_rain | ⛈️ | 4 | 90 min |

## Core Features Implemented

### Етап 1 - Geo Core ✅
- Radar API з distanceMeters, isInsideRadius, freshnessScore
- Stats API (places, hourly, weekday, districts)
- Predictions (статистичний прогноз)
- Frontend Radar Mode з pulse marker

### Етап 2 - Delivery Layer ✅
- Telegram Bot (@Free_thinker_bot)
- Geo Alert Scheduler (кожні 60 сек)
- AI Summary (GPT-4o)

### Етап 3 - Intelligence Layer ✅
- **Event Types Config** - severity, lifetime, avoidance radius
- **Probability Engine** - probabilityNow, probabilityTomorrow, repeatabilityScore
- **Event Fusion** - N raw events → 1 fused event (80m, 20min threshold)
- **Signal Decay** - lifecycle (NEW → CONFIRMED → ACTIVE → DECAYING → EXPIRED)

### Backend Services
- `config/event_types.py` - Event types configuration
- `services/probability_repository.py` - Probability DB operations
- `services/probability_engine.py` - Probability calculations
- `services/fusion_repository.py` - Fusion DB operations  
- `services/fusion_engine.py` - Event fusion logic
- `services/fusion_scoring.py` - Confidence & status
- `services/signal_decay.py` - Decay calculations
- `services/intelligence_scheduler.py` - Master scheduler

### API Endpoints
- GET /api/geo/config/event-types
- GET /api/geo/probability
- POST /api/geo/probability/rebuild
- GET /api/geo/fused
- POST /api/geo/fused/rebuild
- POST /api/geo/decay/run

## Intelligence Pipeline
```
Raw Events
    ↓
Event Classifier
    ↓
Event Fusion (80m, 20min)
    ↓
Signal Decay
    ↓
Probability Engine
    ↓
Radar / Risk / Alerts
```

## Testing Status (2026-03-08)
- Backend: 100% (46/46 tests)
- Frontend: 95%
- Intelligence Scheduler: Running

## P0 Features (Done)
- [x] Event Types з severity
- [x] Probability Engine
- [x] Event Fusion
- [x] Signal Decay
- [x] Intelligence Scheduler

## P1 Features (Next)
- [ ] Playback (activity timeline)
- [ ] Risk Map (heatmap by severity)
- [ ] Route Safety Engine
- [ ] Pattern Detection (hotspots, movements)

## P2 Features (Later)
- [ ] MTProto Telegram ingestion
- [ ] Movement Detection
- [ ] Cross-channel validation
