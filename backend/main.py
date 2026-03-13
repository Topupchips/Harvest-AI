import os

from dotenv import load_dotenv

# Load .env BEFORE importing modules that read env vars
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.generate import router as generate_router
from routes.data_factory import router as data_factory_router
from routes.vision import router as vision_router
from routes.worlds import router as worlds_router
from services.supabase_client import reset_supabase_client
app = FastAPI(title="WorldScout Backend", version="0.1.0")


@app.on_event("startup")
async def startup_event():
    """Reset Supabase client on startup to ensure fresh credentials from env."""
    reset_supabase_client()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(data_factory_router)
app.include_router(vision_router)
app.include_router(worlds_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
