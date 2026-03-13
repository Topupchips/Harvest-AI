# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WorldScout is a web application that converts Google Maps locations into interactive 3D worlds using the World Labs API. Users click on a 3D map to select a location, which captures satellite imagery from 4 cardinal directions and generates an explorable 3D world.

## Development Commands

### Backend (FastAPI)
```bash
cd backend
source venv/bin/activate  # venv already exists
uvicorn main:app --reload --port 8000
```

### Frontend (React + Vite + Tailwind v4)
```bash
cd frontend
npm run dev      # Dev server on http://localhost:5173
npm run build    # Production build
```

Both servers must run simultaneously. The frontend proxies `/api/*` requests to the backend on port 8000.

## Environment Setup

Copy `.env.example` to `.env` in both directories:
- `backend/.env`:
  - `WORLDLABS_API_KEY` - World Labs API key
  - `OPENAI_API_KEY` - OpenAI API key (optional, for GPT-4o)
  - `GEMINI_API_KEY` - Google Gemini API key (for AI-powered natural object placement)
- `frontend/.env`: `VITE_GOOGLE_MAPS_API_KEY` - Google Maps API key (requires Maps JavaScript API, Static Maps API, and Geocoding API)

## Architecture

### Frontend → Backend Flow
1. **MapView** renders Google Maps 3D (`gmp-map-3d` web component) with photorealistic tiles
2. User clicks location on map → **LocationPopup** shows place name via reverse geocoding
3. User confirms → **App.jsx** fetches 4 satellite images at headings [0°, 90°, 180°, 270°] via Static Maps API
4. Images + azimuths sent to `POST /api/generate-world-multi` via Vite proxy
5. Backend uploads all images to World Labs, generates multi-image world, polls until complete
6. Frontend displays generated world in **WorldViewer** iframe

### Backend Endpoints
- `POST /generate-world`: Single-image world generation
- `POST /generate-world-multi`: Multi-image world generation with azimuth angles (primary flow)
  - Supports optional `product_image`, `product_position`, `product_scale` for adding products to scenes
- `POST /describe-image`: GPT-4o vision for product description
- `POST /remove-background`: Remove background from product images
- `GET /health`: Health check

### Product Placement (AI-Powered)
When a product image is provided to `/generate-world-multi`:
1. **Gemini Compositing**: Sends both the background scene and product image to Gemini 3 Pro (gemini-3-pro-image-preview)
2. **Natural Placement**: Gemini generates a new image with the product naturally placed in the scene with proper lighting, shadows, and perspective
3. **Fallback**: If `GEMINI_API_KEY` is not set, uses simple rembg background removal + compositing

Debug images are saved to `backend/debug_images/` for inspection.

### Key Frontend Components
- `App.jsx`: State machine (IDLE → LOCATION_SELECTED → GENERATING → VIEWING)
- `MapView.jsx`: Google Maps 3D initialization, handles `gmp-click` events for location selection
- `LocationPopup.jsx`: Shows selected location name/address, triggers generation
- `services/geocoding.js`: Reverse geocoding + location description generation
- `services/api.js`: Axios wrapper with `generateWorld` and `generateWorldMulti`

### API Proxy
Vite dev server proxies `/api/*` to `localhost:8000` with path rewrite (see `vite.config.js`). Example: `/api/generate-world-multi` → `POST http://localhost:8000/generate-world-multi`.

## World Labs API Flow

### Single Image
1. `POST /media-assets:prepare_upload` → signed URL + media_asset_id
2. `PUT` image bytes to signed URL
3. `POST /worlds:generate` with `type: "image"` → operation_id
4. Poll `GET /operations/{id}` until `done: true` → world_marble_url

### Multi-Image (Primary Flow)
1. Upload each image via prepare_upload + PUT (same as above)
2. `POST /worlds:generate` with `type: "multi-image"` and array of `{azimuth, media_asset_id}` pairs
3. Poll `GET /operations/{id}` → world_marble_url
