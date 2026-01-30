# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeoMarble is a web application that converts Google Maps 3D views into interactive 3D worlds using the World Labs API. Users navigate a 3D map, capture the viewport, and receive a generated 3D world they can explore.

## Development Commands

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev      # Dev server on http://localhost:5173
npm run build    # Production build
```

Both servers must run simultaneously. The frontend proxies `/api/*` requests to the backend on port 8000.

## Environment Setup

Copy `.env.example` to `.env` in both directories:
- `backend/.env`: `WORLDLABS_API_KEY` - World Labs API key
- `frontend/.env`: `VITE_GOOGLE_MAPS_API_KEY` - Google Maps API key (must have Maps JavaScript API and Static Maps API enabled)

## Architecture

### Frontend → Backend Flow
1. **MapView** renders Google Maps 3D (`gmp-map-3d` web component) with photorealistic tiles
2. User clicks "Generate World" → **App.jsx** captures the viewport using canvas extraction or Static Maps API fallback
3. Image blob sent to `POST /api/generate-world` via Vite proxy
4. Backend orchestrates World Labs API: upload image → generate world → poll until complete
5. Frontend opens the `viewer_url` in a new tab

### Backend Services
- `routes/generate.py`: Single endpoint that validates image and coordinates World Labs flow
- `services/worldlabs.py`: `WorldLabsClient` handles all World Labs API communication (upload, generate, poll)

### Key Frontend Components
- `MapView.jsx`: Google Maps 3D initialization and ref exposure for capture
- `App.jsx`: State machine (IDLE → GENERATING → VIEWING) and viewport capture logic with multiple fallback strategies
- `api.js`: Axios wrapper for backend communication

### API Proxy
Vite dev server proxies `/api/*` to `localhost:8000` (see `vite.config.js`). Frontend calls `/api/generate-world`, which becomes `POST http://localhost:8000/generate-world`.

## World Labs API Flow

1. `POST /media-assets:prepare_upload` → get signed URL + media_asset_id
2. `PUT` image bytes to signed URL
3. `POST /worlds:generate` with media_asset_id → get operation_id
4. Poll `GET /operations/{id}` until `done: true` → returns world_marble_url
