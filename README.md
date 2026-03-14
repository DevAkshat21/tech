# 🌍 PyClimaExplorer

> Interactive climate data visualization platform — TECHNEX 2026, IIT(BHU)
> Team TriArch

A full-stack web application for exploring global climate datasets.
Upload any NetCDF (.nc) file and get instant interactive heatmaps,
time-series analysis, AI-powered anomaly explanations, and 20-year forecasts.

---

## Features

- **3D Interactive Globe** — rotating Earth with location pins
- **Global Heatmaps** — animated choropleth maps for temperature, wind, precipitation
- **Time-Series Analysis** — 74 years of historical data with Prophet-based forecasts to 2045
- **AI Climate Analyst** — click any anomaly, get an instant LLM explanation of what happened and why
- **Climate Analogue Finder** — "Paris 2050 will feel like Barcelona today"
- **Emissions Scenarios** — RCP 2.6 / 4.5 / 8.5 comparison charts
- **Upload Your Own Data** — drop any ERA5, CESM, or CMIP6 NetCDF file

## Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | Streamlit + Three.js + Plotly     |
| Backend    | FastAPI (Python)                  |
| Database   | Supabase (PostgreSQL)             |
| Storage    | Supabase Storage                  |
| Data       | Xarray + NumPy + Pandas           |
| Forecasting| Prophet + SciPy                   |
| AI         | Claude (Anthropic) / GPT-4o       |

## Setup

See [SETUP.md](SETUP.md) for the complete step-by-step guide.

Quick start:
```bash
# Terminal 1 — Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && pip install -r requirements.txt
streamlit run app.py
```

## Data Sources

- [ERA5 Reanalysis](https://cds.climate.copernicus.eu/) — ECMWF
- [CESM Large Ensemble](https://www.cesm.ucar.edu/projects/community-projects/LENS/)
- [CMIP6](https://pcmdi.llnl.gov/CMIP6/)

## License

MIT
