from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ── Request models ──────────────────────────────────────────────────────────

class ClimateQuery(BaseModel):
    lat:      float = Field(..., ge=-90,  le=90)
    lon:      float = Field(..., ge=-180, le=180)
    year:     int   = Field(..., ge=1950, le=2024)
    month:    int   = Field(..., ge=1,    le=12)
    variable: str   = Field(..., description="temperature | wind_speed | precipitation | ...")


class AIExplainRequest(BaseModel):
    variable: str
    lat:      float
    lon:      float
    year:     int
    value:    Optional[float] = None
    anomaly:  Optional[float] = None
    question: Optional[str]  = None   # free-form follow-up


class ForecastQuery(BaseModel):
    lat:         float
    lon:         float
    variable:    str
    target_year: int = 2045


class AnalogueQuery(BaseModel):
    lat:         float
    lon:         float
    variable:    str
    target_year: int = 2050


# ── Response models ─────────────────────────────────────────────────────────

class HeatmapResponse(BaseModel):
    lats:   List[float]
    lons:   List[float]
    values: List[float]


class TimeseriesResponse(BaseModel):
    years:           List[int]
    values:          List[float]
    forecast_years:  List[int]
    forecast_values: List[float]
    forecast_upper:  List[float]
    forecast_lower:  List[float]


class RCPScenario(BaseModel):
    years:  List[int]
    values: List[float]
    upper:  List[float]
    lower:  List[float]


class Stats(BaseModel):
    current_value:  str
    baseline_mean:  str
    anomaly:        str
    projected_2045: str
    record_year:    str
    rcp26_proj:     str
    rcp45_proj:     str
    rcp85_proj:     str


class AIMetric(BaseModel):
    value: str
    label: str


class AIExplanation(BaseModel):
    paragraph1: str
    paragraph2: str
    metrics:    List[AIMetric] = []


class AnalogueCity(BaseModel):
    city:        str
    lat:         float
    lon:         float
    meta:        str
    match_score: int


class FullClimateResponse(BaseModel):
    stats:         Stats
    heatmap:       HeatmapResponse
    timeseries:    TimeseriesResponse
    rcp_scenarios: Dict[str, RCPScenario]
    analogues:     List[AnalogueCity]
    ai_explanation: AIExplanation


class ForecastResponse(BaseModel):
    years:  List[int]
    values: List[float]
    upper:  List[float]
    lower:  List[float]


class AIResponse(BaseModel):
    explanation: str
    cached:      bool = False


class UploadResponse(BaseModel):
    dataset_id: str
    filename:   str
    variables:  List[str]
    time_range: Dict[str, Any]
    file_url:   str
