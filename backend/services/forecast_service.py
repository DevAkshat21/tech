"""
Forecast Service — generates climate predictions using Facebook Prophet.

Prophet is perfect for climate data: it handles trend, seasonality,
and uncertainty bands automatically. We feed it annual mean values
and ask it to forecast 20 years ahead.

RCP scenarios are approximated by adjusting the trend slope:
- RCP 2.6: low slope (emissions peak and decline)
- RCP 4.5: medium slope (stabilisation)
- RCP 8.5: high slope (business-as-usual)
"""
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict


def _run_prophet(years: List[int], values: List[float],
                 periods: int = 25) -> Dict:
    """
    Run Prophet forecast. Returns years, predicted values, upper/lower bounds.
    """
    try:
        from prophet import Prophet  # type: ignore
    except ImportError:
        # Graceful degradation if Prophet not installed
        return _linear_forecast(years, values, periods)

    df = pd.DataFrame({"ds": pd.to_datetime([f"{y}-06-01" for y in years]),
                       "y":  values})
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.3,
        interval_width=0.9,
    )
    model.fit(df)

    last_year = max(years)
    future_dates = pd.date_range(
        start=f"{last_year + 1}-06-01", periods=periods, freq="YS"
    )
    future_df = pd.DataFrame({"ds": future_dates})
    forecast  = model.predict(future_df)

    return {
        "years":  [d.year for d in future_dates],
        "values": [round(v, 2) for v in forecast["yhat"].tolist()],
        "upper":  [round(v, 2) for v in forecast["yhat_upper"].tolist()],
        "lower":  [round(v, 2) for v in forecast["yhat_lower"].tolist()],
    }


def _linear_forecast(years: List[int], values: List[float],
                     periods: int = 25) -> Dict:
    """
    Fallback linear regression forecast when Prophet is unavailable.
    Uses numpy polyfit (degree 1).
    """
    x = np.array(years, dtype=float)
    y = np.array(values, dtype=float)

    # Remove NaN
    valid = np.isfinite(y)
    x, y = x[valid], y[valid]

    coeffs = np.polyfit(x, y, 1)
    slope, intercept = coeffs

    last_year    = int(max(years))
    future_years = list(range(last_year + 1, last_year + periods + 1))
    fx     = np.array(future_years, dtype=float)
    preds  = (slope * fx + intercept).tolist()

    residuals = y - np.polyval(coeffs, x)
    std       = float(np.std(residuals)) * 1.645  # 90% CI

    return {
        "years":  future_years,
        "values": [round(v, 2) for v in preds],
        "upper":  [round(v + std, 2) for v in preds],
        "lower":  [round(v - std, 2) for v in preds],
    }


def forecast_timeseries(years: List[int], values: List[float],
                        periods: int = 25) -> Dict:
    """Public entry point for standard forecast."""
    return _run_prophet(years, values, periods)


def generate_rcp_scenarios(years: List[int], values: List[float]) -> Dict[str, Dict]:
    """
    Generate 3 RCP scenario forecasts by adjusting the base trend.

    Strategy: run base forecast, then scale the trend component
    by scenario multipliers derived from IPCC AR6 projections.
    """
    base = _linear_forecast(years, values, periods=len(range(max(years) + 1, 2046)))

    # Approximate IPCC warming rate multipliers vs baseline trend
    scenario_slopes = {"rcp_26": 0.5, "rcp_45": 1.0, "rcp_85": 2.2}

    # Compute baseline slope from history
    x = np.array(years[-30:], dtype=float)  # last 30 years
    y = np.array(values[-30:], dtype=float)
    valid = np.isfinite(y)
    base_slope = float(np.polyfit(x[valid], y[valid], 1)[0]) if valid.sum() > 2 else 0.02
    last_val   = float(values[-1]) if values else 14.0

    results = {}
    hist_years = list(range(1950, min(years[-1] + 1, 2025)))

    for scenario, multiplier in scenario_slopes.items():
        fc_years  = list(range(max(years) + 1, 2046))
        slope     = base_slope * multiplier
        std_scale = 0.3 + multiplier * 0.15
        fc_vals   = [last_val + slope * (i + 1) for i in range(len(fc_years))]
        fc_upper  = [v + std_scale for v in fc_vals]
        fc_lower  = [v - std_scale * 0.6 for v in fc_vals]

        # Combine historical + forecast
        all_years  = hist_years + fc_years
        hist_slice = values[:len(hist_years)]
        all_vals   = list(hist_slice) + fc_vals
        all_upper  = list(hist_slice) + fc_upper
        all_lower  = list(hist_slice) + fc_lower

        results[scenario] = {
            "years":  all_years,
            "values": [round(v, 2) for v in all_vals],
            "upper":  [round(v, 2) for v in all_upper],
            "lower":  [round(v, 2) for v in all_lower],
        }

    return results
