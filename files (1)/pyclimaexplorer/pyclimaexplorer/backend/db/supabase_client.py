"""
Supabase client factory.

Provides two clients:
- get_supabase()         → uses anon key  (safe for most reads/writes with RLS)
- get_supabase_admin()   → uses service key (bypasses RLS — backend only, never frontend)
"""
from functools import lru_cache
from supabase import create_client, Client  # type: ignore
from config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env"
        )
    return create_client(settings.supabase_url, settings.supabase_anon_key)


@lru_cache(maxsize=1)
def get_supabase_admin() -> Client:
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env"
        )
    return create_client(settings.supabase_url, settings.supabase_service_key)


# ── Storage helpers ────────────────────────────────────────────────────────

STORAGE_BUCKET = "climate-datasets"


def upload_nc_file(filename: str, file_bytes: bytes) -> str:
    """
    Upload a NetCDF file to Supabase Storage.
    Returns the public URL.
    """
    sb = get_supabase_admin()
    path = f"uploads/{filename}"
    sb.storage.from_(STORAGE_BUCKET).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": "application/octet-stream", "upsert": "true"},
    )
    url_response = sb.storage.from_(STORAGE_BUCKET).get_public_url(path)
    return url_response


def save_dataset_metadata(metadata: dict) -> dict:
    """Save dataset metadata to the datasets table."""
    sb = get_supabase()
    result = sb.table("datasets").insert(metadata).execute()
    return result.data[0] if result.data else {}


def get_datasets() -> list:
    """List all available datasets from the DB."""
    sb = get_supabase()
    result = sb.table("datasets").select("*").order("created_at", desc=True).execute()
    return result.data or []


def save_view(view_data: dict) -> dict:
    """Save a user's current view as a shareable permalink."""
    sb = get_supabase()
    result = sb.table("saved_views").insert(view_data).execute()
    return result.data[0] if result.data else {}
