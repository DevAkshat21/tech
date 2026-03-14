-- ============================================================
-- PyClimaExplorer — Supabase Database Schema
-- Run this entire file in the Supabase SQL Editor:
--   Dashboard → SQL Editor → New Query → paste → Run
-- ============================================================

-- Enable UUID generation
create extension if not exists "pgcrypto";

-- ── Table: datasets ──────────────────────────────────────────────────────
-- Stores metadata for each NetCDF dataset (pre-loaded or user-uploaded)
create table if not exists datasets (
    id           uuid primary key default gen_random_uuid(),
    name         text not null,
    source       text not null default 'user_upload',
                   -- 'era5' | 'cesm' | 'cmip6' | 'user_upload'
    variables    text[] default '{}',
    time_start   text,
    time_end     text,
    file_url     text,
    uploaded_by  uuid references auth.users(id) on delete set null,
    created_at   timestamptz default now()
);

-- ── Table: saved_views ───────────────────────────────────────────────────
-- Stores a user's current explore/results configuration for sharing
create table if not exists saved_views (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid references auth.users(id) on delete set null,
    location_name   text,
    lat             float,
    lon             float,
    variable        text,
    year            integer,
    month           integer,
    chart_type      text default 'heatmap',
    permalink_slug  text unique,
    created_at      timestamptz default now()
);

-- ── Table: anomaly_explanations (LLM response cache) ────────────────────
-- Caches AI analyst responses so we don't make repeat LLM API calls
-- for the same location/year/variable combination.
create table if not exists anomaly_explanations (
    id           uuid primary key default gen_random_uuid(),
    cache_key    text unique not null,  -- MD5 of variable:lat:lon:year:question
    variable     text not null,
    lat          float not null,
    lon          float not null,
    year         integer not null,
    llm_response text not null,
    cached_at    timestamptz default now()
);

-- ── Row Level Security ────────────────────────────────────────────────────
-- Enable RLS on all tables (best practice — prevents data leaks)
alter table datasets              enable row level security;
alter table saved_views           enable row level security;
alter table anomaly_explanations  enable row level security;

-- Datasets: anyone can read pre-loaded datasets
create policy "public read datasets"
    on datasets for select
    using (true);

-- Datasets: only authenticated users can insert
create policy "authenticated insert datasets"
    on datasets for insert
    with check (auth.role() = 'authenticated' or source = 'era5' or source = 'cesm');

-- Saved views: users can read/write their own views
create policy "users read own views"
    on saved_views for select
    using (user_id = auth.uid() or permalink_slug is not null);

create policy "users insert own views"
    on saved_views for insert
    with check (user_id = auth.uid());

-- Anomaly cache: anyone can read (it's cached data, not PII)
create policy "public read explanations"
    on anomaly_explanations for select
    using (true);

-- Only service role can insert (via backend with service key)
create policy "service insert explanations"
    on anomaly_explanations for insert
    with check (true);

-- ── Storage bucket ────────────────────────────────────────────────────────
-- Create via Supabase Dashboard → Storage → New Bucket
-- Name: climate-datasets
-- Public: false (use signed URLs)
-- Max file size: 500MB
-- Allowed mime types: application/octet-stream

-- ── Indexes for performance ───────────────────────────────────────────────
create index if not exists idx_explanations_cache_key
    on anomaly_explanations(cache_key);

create index if not exists idx_explanations_variable_loc
    on anomaly_explanations(variable, lat, lon, year);

create index if not exists idx_datasets_source
    on datasets(source);

-- ── Seed pre-loaded dataset metadata (optional) ──────────────────────────
-- Uncomment and modify once you've uploaded ERA5 files to Storage:
/*
insert into datasets (name, source, variables, time_start, time_end, file_url)
values
    ('ERA5 Surface Temperature 1950-2024', 'era5',
     array['temperature'], '1950-01-01', '2024-12-31',
     'https://<your-project>.supabase.co/storage/v1/object/public/climate-datasets/era5_temperature.nc'),
    ('ERA5 Wind Speed 1950-2024', 'era5',
     array['wind_speed'], '1950-01-01', '2024-12-31',
     'https://<your-project>.supabase.co/storage/v1/object/public/climate-datasets/era5_wind.nc');
*/
