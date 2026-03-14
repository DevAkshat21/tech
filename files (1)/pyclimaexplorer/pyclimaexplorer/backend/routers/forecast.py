"""Forecast & analogues router."""
from fastapi import APIRouter, Query
from services.forecast_service import forecast_timeseries
from services.analogue_service import find_analogues, _approximate_signature, compute_future_signature

router = APIRouter()

@router.get("/analogues")
async def get_analogues(
    lat:         float = Query(...),
    lon:         float = Query(...),
    variable:    str   = Query(...),
    target_year: int   = Query(2050),
):
    sig_now    = _approximate_signature(14.0, lat)
    sig_future = compute_future_signature(sig_now, warming_delta=2.0)
    analogues  = find_analogues(lat, lon, sig_future, n_results=4)
    return {"analogues": analogues}
