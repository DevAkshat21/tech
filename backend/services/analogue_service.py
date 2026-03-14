"""
Climate Analogue Finder

For a given city and target future year, find current cities worldwide
that already have the same climate profile.

Method:
1. Compute a 12-element "climate signature" (monthly mean values) for the
   target city projected to target_year.
2. Compare against signatures of candidate cities using cosine similarity.
3. Return top-N closest matches.

This is the "London 2050 = Barcelona today" feature.
"""
import numpy as np
from typing import List, Dict
from scipy.spatial.distance import cosine  # type: ignore


# ── Candidate cities database (lat, lon, display name) ─────────────────────
# In production you'd compute signatures from actual data for all of these.
# Here we provide a representative set with pre-computed approximate
# annual temperature baselines (expandable per variable).
CANDIDATE_CITIES = [
    {"city": "Barcelona, Spain",     "lat": 41.38,  "lon":   2.17, "base_temp": 18.5},
    {"city": "Porto, Portugal",      "lat": 41.15,  "lon":  -8.61, "base_temp": 17.2},
    {"city": "Milan, Italy",         "lat": 45.46,  "lon":   9.19, "base_temp": 15.8},
    {"city": "Istanbul, Turkey",     "lat": 41.01,  "lon":  28.95, "base_temp": 15.0},
    {"city": "Madrid, Spain",        "lat": 40.42,  "lon":  -3.70, "base_temp": 15.5},
    {"city": "Athens, Greece",       "lat": 37.98,  "lon":  23.73, "base_temp": 19.5},
    {"city": "Lisbon, Portugal",     "lat": 38.72,  "lon":  -9.14, "base_temp": 17.8},
    {"city": "Marseille, France",    "lat": 43.30,  "lon":   5.37, "base_temp": 15.5},
    {"city": "Rome, Italy",          "lat": 41.90,  "lon":  12.50, "base_temp": 16.2},
    {"city": "Valencia, Spain",      "lat": 39.47,  "lon":  -0.38, "base_temp": 18.8},
    {"city": "Casablanca, Morocco",  "lat": 33.57,  "lon":  -7.59, "base_temp": 18.3},
    {"city": "Tunis, Tunisia",       "lat": 36.82,  "lon":  10.17, "base_temp": 19.1},
    {"city": "Tel Aviv, Israel",     "lat": 32.09,  "lon":  34.78, "base_temp": 20.5},
    {"city": "Seville, Spain",       "lat": 37.39,  "lon":  -5.99, "base_temp": 19.2},
    {"city": "Cape Town, S. Africa", "lat":-33.93,  "lon":  18.42, "base_temp": 17.5},
    {"city": "Los Angeles, USA",     "lat": 34.05,  "lon": -118.24,"base_temp": 18.9},
    {"city": "San Francisco, USA",   "lat": 37.77,  "lon": -122.42,"base_temp": 14.5},
    {"city": "Sydney, Australia",    "lat":-33.87,  "lon": 151.21, "base_temp": 18.1},
    {"city": "Buenos Aires, Argentina","lat":-34.60,"lon":  -58.38,"base_temp": 18.4},
    {"city": "Tromsø, Norway",       "lat": 69.65,  "lon":  18.96, "base_temp":  3.5},
    {"city": "Lerwick, Scotland",    "lat": 60.15,  "lon":  -1.15, "base_temp":  7.8},
    {"city": "Faroe Islands",        "lat": 62.00,  "lon":  -6.79, "base_temp":  6.5},
    {"city": "Murmansk, Russia",     "lat": 68.97,  "lon":  33.09, "base_temp":  0.5},
    {"city": "Reykjavik, Iceland",   "lat": 64.13,  "lon": -21.93, "base_temp":  5.4},
    {"city": "Bergen, Norway",       "lat": 60.39,  "lon":   5.33, "base_temp":  8.1},
    {"city": "Shanghai, China",      "lat": 31.23,  "lon": 121.47, "base_temp": 16.7},
    {"city": "Beijing, China",       "lat": 39.91,  "lon": 116.39, "base_temp": 12.5},
    {"city": "Mumbai, India",        "lat": 19.07,  "lon":  72.88, "base_temp": 27.2},
    {"city": "Tokyo, Japan",         "lat": 35.68,  "lon": 139.69, "base_temp": 15.4},
]

# Seasonal amplitude pattern (used to approximate monthly signatures
# when we don't have full NetCDF data for all candidates)
def _approximate_signature(base_temp: float, lat: float) -> np.ndarray:
    """
    Approximate a 12-month temperature signature for a city
    given its annual mean and latitude (seasonal amplitude proxy).
    """
    # Amplitude: larger at higher latitudes, smaller near equator
    amplitude = max(2.0, min(20.0, abs(lat) * 0.4))
    months = np.arange(12)
    # Northern hemisphere: peak in July (month 6, index 6)
    # Southern hemisphere: peak in January (month 0, index 0)
    peak = 6 if lat >= 0 else 0
    sig = base_temp + amplitude * np.cos((months - peak) * 2 * np.pi / 12)
    return sig


def find_analogues(
    target_lat: float,
    target_lon: float,
    target_signature: np.ndarray,
    n_results: int = 5,
    exclude_radius_km: float = 500.0,
) -> List[Dict]:
    """
    Find cities whose current climate profile matches the target signature.

    target_signature: 12-element array of monthly means for target location
                      projected to future year.
    Returns list of dicts with city info and match scores.
    """
    results = []

    for city in CANDIDATE_CITIES:
        # Skip cities too close to the target (they'd trivially match)
        dist_km = _haversine(target_lat, target_lon, city["lat"], city["lon"])
        if dist_km < exclude_radius_km:
            continue

        # Build city signature
        city_sig = _approximate_signature(city["base_temp"], city["lat"])

        # Cosine similarity (1 - cosine distance)
        try:
            sim = 1.0 - cosine(target_signature, city_sig)
        except Exception:
            continue

        # Convert to 0-100 match score
        match_score = max(0, min(100, int(sim * 100)))

        results.append({
            "city":        city["city"],
            "lat":         city["lat"],
            "lon":         city["lon"],
            "meta":        f"{city['base_temp']:.1f}°C annual avg",
            "match_score": match_score,
            "distance_km": round(dist_km),
        })

    # Sort by match score descending, return top N
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:n_results]


def compute_future_signature(
    current_signature: np.ndarray,
    warming_delta: float,
) -> np.ndarray:
    """
    Apply a uniform warming delta to project a city's signature into the future.
    In a full implementation, RCP-specific deltas would come from model output.
    """
    return current_signature + warming_delta


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi  = np.radians(lat2 - lat1)
    dlam  = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2)**2
    return 2 * R * np.arcsin(np.sqrt(a))
