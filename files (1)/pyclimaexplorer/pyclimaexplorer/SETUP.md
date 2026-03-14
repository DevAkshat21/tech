# PyClimaExplorer — Complete Setup Guide

This guide assumes you know nothing. Follow every step in order.
Do not skip any step — each one is required for the next to work.

---

## What You Are Building

```
Landing Page  →  Explore Page  →  Results Page
(space + globe)  (globe + controls)  (heatmap + AI + forecasts)
```

Your computer will run two servers simultaneously:
- **Frontend** (Streamlit) on port `8501` — the website
- **Backend** (FastAPI) on port `8000` — the data engine

---

## Part 1 — Prerequisites

### 1.1 Install Python 3.11

Download from: https://www.python.org/downloads/

When installing on Windows, **check the box that says "Add Python to PATH"**.

Verify it worked — open a terminal and run:
```bash
python --version
# Should print: Python 3.11.x
```

> **What is a terminal?**
> - Windows: press `Win + R`, type `cmd`, press Enter
> - Mac: press `Cmd + Space`, type `Terminal`, press Enter

### 1.2 Install Git

Download from: https://git-scm.com/downloads

Verify:
```bash
git --version
# Should print: git version 2.x.x
```

### 1.3 Install Node.js (required only for Three.js globe in development)

Download LTS version from: https://nodejs.org/

---

## Part 2 — Get the Project

### 2.1 Clone the repository

```bash
git clone https://github.com/<your-username>/pyclimaexplorer.git
cd pyclimaexplorer
```

After cloning, your folder structure looks like this:
```
pyclimaexplorer/
├── frontend/          ← Streamlit website
│   ├── app.py         ← Entry point (run this)
│   ├── components/    ← Landing, Explore, Results pages
│   ├── utils/         ← API client
│   └── requirements.txt
├── backend/           ← FastAPI data engine
│   ├── main.py        ← Entry point (run this)
│   ├── routers/       ← API endpoints
│   ├── services/      ← Data processing logic
│   ├── db/            ← Supabase connection
│   ├── models/        ← Request/response schemas
│   └── requirements.txt
├── supabase/
│   └── schema.sql     ← Run this in Supabase
├── data/              ← Put your .nc files here
└── .env.example       ← Copy this to .env
```

---

## Part 3 — Install Python Dependencies

You will create two separate virtual environments — one for frontend, one for backend.
This keeps their dependencies isolated.

### 3.1 Backend dependencies

```bash
cd backend

# Create a virtual environment named "venv"
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Your terminal prompt should now show (venv) at the start

# Install all required packages
pip install -r requirements.txt
```

> **Prophet installation note:** Prophet sometimes needs extra steps.
> If `pip install -r requirements.txt` fails on Prophet, run:
> ```bash
> pip install pystan==2.19.1.1
> pip install prophet
> ```

### 3.2 Frontend dependencies

Open a **second terminal window** (keep the backend one open):

```bash
cd frontend

python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

---

## Part 4 — Supabase Setup

Supabase is your database + file storage. It is free for this project.

### 4.1 Create a Supabase account

Go to: https://supabase.com → Click "Start your project" → Sign up with GitHub

### 4.2 Create a new project

1. Click "New Project"
2. Give it a name: `pyclimaexplorer`
3. Set a strong database password (save it somewhere)
4. Choose a region close to you
5. Click "Create new project" — wait ~2 minutes for it to boot

### 4.3 Get your API keys

In your Supabase project:
1. Click the gear icon (⚙️) in the left sidebar → "Settings"
2. Click "API" in the submenu
3. You will see:
   - **Project URL** — looks like `https://abcdefgh.supabase.co`
   - **anon public** key — a long string starting with `eyJ...`
   - **service_role** key — another long string (keep this secret)

Copy all three. You will need them in Step 5.

### 4.4 Create the database tables

1. In Supabase, click "SQL Editor" in the left sidebar
2. Click "New query"
3. Open the file `supabase/schema.sql` from this project
4. Copy the entire contents and paste it into the SQL editor
5. Click "Run" (or press `Ctrl+Enter`)
6. You should see "Success. No rows returned"

### 4.5 Create the storage bucket

1. Click "Storage" in the left sidebar
2. Click "New bucket"
3. Name it exactly: `climate-datasets`
4. Toggle "Public bucket" to OFF (keep files private)
5. Click "Save"

---

## Part 5 — Configure Environment Variables

### 5.1 Create your .env file

In the project root folder:
```bash
# Mac/Linux:
cp .env.example .env

# Windows:
copy .env.example .env
```

### 5.2 Fill in the .env file

Open `.env` in any text editor (Notepad, VS Code, etc.) and replace every `<YOUR_VALUE>`:

```env
SUPABASE_URL=https://abcdefgh.supabase.co      ← paste your Project URL
SUPABASE_ANON_KEY=eyJhbG...                     ← paste your anon key
SUPABASE_SERVICE_KEY=eyJhbG...                  ← paste your service_role key

ANTHROPIC_API_KEY=sk-ant-...                    ← see Step 5.3
OPENAI_API_KEY=sk-...                           ← optional

LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-20241022

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
DATA_DIR=../data
```

**Important:** The `.env` file must be placed in the `backend/` folder:
```bash
cp .env backend/.env
```
Also copy it to the frontend folder:
```bash
cp .env frontend/.env
```

### 5.3 Get an Anthropic API key (for AI Analyst feature)

1. Go to: https://console.anthropic.com/
2. Sign up / log in
3. Click "API Keys" → "Create Key"
4. Copy the key (starts with `sk-ant-`)
5. Paste it into your `.env` file

> **Cost note:** The AI Analyst uses Claude Haiku which costs about $0.001 per explanation.
> Responses are cached in Supabase so each unique location/year is only called once.

---

## Part 6 — Get Climate Data

The app works without data files (it shows placeholder charts), but real
visualizations require actual NetCDF (.nc) files.

### Option A — Download a small test dataset (recommended to start)

ERA5 provides free climate data. The easiest way to get a small sample:

1. Go to: https://cds.climate.copernicus.eu/
2. Create a free account
3. Go to: "ERA5-Land monthly averaged data from 1950 to present"
4. Select:
   - Variable: "2m temperature"
   - Year: 2000 to 2024
   - Month: all
   - Format: NetCDF
5. Download and place the file in the `data/` folder

Rename it to: `data/era5_temperature.nc`

### Option B — Use the built-in sample generator (instant, no download)

Run this script to generate a synthetic NetCDF file for testing:

```bash
cd backend
python -c "
import numpy as np
import xarray as xr
import pandas as pd

lats  = np.arange(-90, 91, 2.5)
lons  = np.arange(-180, 181, 2.5)
times = pd.date_range('1950-01', '2024-12', freq='MS')

np.random.seed(42)
data = (
    20 - np.abs(lats[:, None, None]) * 0.3
    + np.random.randn(len(lats), len(lons), len(times)) * 2
    + np.arange(len(times))[None, None, :] * 0.002
)

ds = xr.Dataset(
    {'t2m': (['lat','lon','time'], data)},
    coords={'lat': lats, 'lon': lons, 'time': times}
)
ds['t2m'].attrs['units'] = 'degC'
ds.to_netcdf('../data/era5_temperature.nc')
print('Sample data created: data/era5_temperature.nc')
"
```

---

## Part 7 — Run the Application

You need **two terminals open at the same time**.

### Terminal 1 — Start the Backend

```bash
cd backend
source venv/bin/activate    # Mac/Linux
# OR
venv\Scripts\activate       # Windows

uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ PyClimaExplorer backend starting
```

Verify it's working: open http://localhost:8000/health in your browser.
You should see: `{"status":"ok","version":"1.0.0"}`

### Terminal 2 — Start the Frontend

```bash
cd frontend
source venv/bin/activate    # Mac/Linux
# OR
venv\Scripts\activate       # Windows

streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Your browser should open automatically. If not, go to: http://localhost:8501

---

## Part 8 — Verify Everything Works

Walk through the full user flow:

1. **Landing page** loads with spinning 3D globe and "Explore" button
2. Click **Explore** → globe moves left, control panel appears right
3. Select a location (e.g., Paris, France), year 2010, Temperature
4. Click **Load Data**
5. **Results page** shows:
   - Global heatmap (if .nc file is present, otherwise placeholder)
   - Time series chart with forecast
   - AI Analyst panel with explanation
   - Climate analogue cities
   - RCP scenario comparison
   - Stats cards

---

## Part 9 — Troubleshooting

### "ModuleNotFoundError: No module named 'xarray'"
You forgot to activate your virtual environment. Run:
```bash
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
```

### "Connection refused" on Load Data
The backend is not running. Open Terminal 1 and start uvicorn (Step 7).

### Globe not showing / blank white box
Three.js requires an internet connection to load from CDN.
Make sure you're connected to the internet.

### "SUPABASE_URL must be set"
Your `.env` file is missing or in the wrong location.
Make sure it is inside the `backend/` folder.

### Prophet installation fails on Windows
```bash
pip install pystan==2.19.1.1
pip install prophet==1.1.5
```
If it still fails, comment out `from prophet import Prophet` in
`services/forecast_service.py` — it will fall back to linear regression.

### Port 8000 or 8501 already in use
```bash
# Kill whatever is using the port
# Mac/Linux:
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

---

## Part 10 — Deployment (Hackathon Demo)

To show the app to judges without them installing anything:

### Deploy Frontend to Streamlit Cloud (free)

1. Push your code to GitHub (see README.md)
2. Go to: https://share.streamlit.io/
3. Sign in with GitHub
4. Click "New app"
5. Select your repo → Branch: `main` → Main file: `frontend/app.py`
6. Click "Advanced settings" → add your environment variables
7. Click "Deploy"

### Deploy Backend to Railway (free tier)

1. Go to: https://railway.app/
2. "New Project" → "Deploy from GitHub"
3. Select your repo
4. Set root directory to `backend`
5. Add environment variables from your `.env`
6. Railway auto-detects FastAPI and deploys

After deploying backend, update `BACKEND_URL` in Streamlit Cloud settings
to your Railway URL (e.g., `https://pyclimaexplorer-backend.up.railway.app`).

---

## Quick Reference — Common Commands

```bash
# Start backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Start frontend
cd frontend && source venv/bin/activate && streamlit run app.py

# Backend API docs (auto-generated)
open http://localhost:8000/docs

# Test backend health
curl http://localhost:8000/health

# Generate sample data
cd backend && python -c "import scripts.generate_sample_data"
```

---

## Architecture Summary

```
Browser
  │
  ▼
Streamlit (port 8501)          ← frontend/app.py
  │  Renders pages via HTML/CSS
  │  Calls backend API via httpx
  │
  ▼
FastAPI (port 8000)            ← backend/main.py
  │  Receives requests
  │  Loads .nc files with Xarray
  │  Processes data with NumPy/Pandas
  │  Generates Plotly figures
  │  Runs Prophet forecasts
  │  Calls LLM API for AI explanations
  │  Caches responses in Supabase
  │
  ├──► Supabase PostgreSQL     ← dataset metadata, AI cache, saved views
  ├──► Supabase Storage        ← .nc files (uploaded by users)
  └──► LLM API (Anthropic)     ← AI anomaly explanations
```

That's everything. Good luck at TECHNEX 2026! 🚀
