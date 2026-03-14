"""
PyClimaExplorer — FastAPI Backend
Serves all data processing, chart generation, forecasting, and AI endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from routers import climate, ai_analyst, forecast


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown logic."""
    print(f"✅ PyClimaExplorer backend starting — data dir: {settings.data_dir}")
    yield
    print("🛑 Shutting down.")


app = FastAPI(
    title="PyClimaExplorer API",
    description="Climate data processing, visualization, and AI analysis backend.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS: allow Streamlit frontend (localhost:8501) ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "https://*.streamlit.app",
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(climate.router,     prefix="/api/climate",  tags=["Climate Data"])
app.include_router(ai_analyst.router,  prefix="/api/ai",       tags=["AI Analyst"])
app.include_router(forecast.router,    prefix="/api/forecast", tags=["Forecast"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
