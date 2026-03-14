"""
LLM Service — powers the AI Climate Analyst feature.

Supports:
- Anthropic (Claude) — default
- OpenAI (GPT-4o)   — fallback

All responses are cached in Supabase to avoid repeat API calls
for the same location/year/variable combination.
"""
import hashlib
import json
from typing import Optional

from config import settings
from db.supabase_client import get_supabase


SYSTEM_PROMPT = """You are an expert climate scientist and science communicator.
Your job is to explain climate data anomalies in clear, compelling language
that is scientifically accurate but accessible to a general audience.
When given climate data, you:
1. Explain WHAT happened (the data)
2. Explain WHY it happened (the science)
3. Explain the consequences and broader context
Keep responses to 2-3 short paragraphs. Do not use bullet points.
Be specific about the location and time period. Make it vivid and memorable."""


def _make_cache_key(variable: str, lat: float, lon: float,
                    year: int, question: Optional[str] = None) -> str:
    raw = f"{variable}:{lat:.1f}:{lon:.1f}:{year}:{question or ''}"
    return hashlib.md5(raw.encode()).hexdigest()


def _get_cached(cache_key: str) -> Optional[str]:
    try:
        sb = get_supabase()
        result = sb.table("anomaly_explanations") \
                   .select("llm_response") \
                   .eq("cache_key", cache_key) \
                   .single() \
                   .execute()
        if result.data:
            return result.data["llm_response"]
    except Exception:
        pass
    return None


def _save_to_cache(cache_key: str, variable: str, lat: float,
                   lon: float, year: int, response: str) -> None:
    try:
        sb = get_supabase()
        sb.table("anomaly_explanations").upsert({
            "cache_key":    cache_key,
            "variable":     variable,
            "lat":          lat,
            "lon":          lon,
            "year":         year,
            "llm_response": response,
        }).execute()
    except Exception:
        pass  # Cache failure should not break the response


def _call_anthropic(prompt: str) -> str:
    import anthropic  # type: ignore
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    msg = client.messages.create(
        model=settings.llm_model,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _call_openai(prompt: str) -> str:
    from openai import OpenAI  # type: ignore
    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=600,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
    )
    return resp.choices[0].message.content


def explain_anomaly(
    variable:    str,
    lat:         float,
    lon:         float,
    year:        int,
    value:       Optional[float] = None,
    anomaly:     Optional[float] = None,
    baseline:    Optional[float] = None,
    question:    Optional[str]   = None,
) -> str:
    """
    Generate (or retrieve cached) AI explanation for a climate data point.

    question: optional follow-up question from the user.
    """
    cache_key = _make_cache_key(variable, lat, lon, year, question)
    cached = _get_cached(cache_key)
    if cached:
        return cached

    # Build the prompt
    var_labels = {
        "temperature":        ("Surface Temperature", "°C"),
        "wind_speed":         ("10m Wind Speed",      "m/s"),
        "precipitation":      ("Total Precipitation", "mm/month"),
        "sea_level_pressure": ("Sea Level Pressure",  "hPa"),
        "humidity":           ("Relative Humidity",   "%"),
    }
    var_name, unit = var_labels.get(variable, (variable, ""))

    parts = [
        f"Location: {lat:.2f}°N, {lon:.2f}°E",
        f"Time: {year}",
        f"Variable: {var_name}",
    ]
    if value is not None:
        parts.append(f"Observed value: {value:.1f} {unit}")
    if baseline is not None:
        parts.append(f"Historical baseline (1980–2010 mean): {baseline:.1f} {unit}")
    if anomaly is not None:
        direction = "above" if anomaly > 0 else "below"
        parts.append(f"Anomaly: {abs(anomaly):.1f} {unit} {direction} baseline")

    data_context = "\n".join(parts)

    if question:
        prompt = (f"Climate data context:\n{data_context}\n\n"
                  f"User question: {question}\n\n"
                  f"Please answer this question about the climate data above.")
    else:
        prompt = (f"Explain the following climate data observation:\n\n{data_context}\n\n"
                  f"Provide a clear scientific explanation of what happened, "
                  f"why, and the broader significance.")

    # Try configured provider, fall back to other
    try:
        if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            response = _call_anthropic(prompt)
        elif settings.openai_api_key:
            response = _call_openai(prompt)
        elif settings.anthropic_api_key:
            response = _call_anthropic(prompt)
        else:
            response = ("AI analysis unavailable. Please add ANTHROPIC_API_KEY or "
                        "OPENAI_API_KEY to your .env file to enable this feature.")
    except Exception as e:
        response = f"AI analysis temporarily unavailable: {str(e)[:100]}"

    _save_to_cache(cache_key, variable, lat, lon, year, response)
    return response
