-- =====================================================
-- FCD Tamil Nadu Platform — PostGIS Schema
-- =====================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
pgCREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ── Administrative units ──────────────────────────
CREATE TABLE IF NOT EXISTS admin_units (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        TEXT NOT NULL,
  name_local  TEXT,
  unit_type   TEXT NOT NULL CHECK (
                unit_type IN ('state','district','block','taluk',
                              'forest_circle','forest_division',
                              'forest_range','custom_aoi')
              ),
  parent_id   UUID REFERENCES admin_units(id),
  area_ha     NUMERIC,
  source      TEXT,
  geom        GEOMETRY(MultiPolygon, 4326),
  created_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX admin_units_geom_idx  ON admin_units USING GIST (geom);
CREATE INDEX admin_units_type_idx  ON admin_units (unit_type);
CREATE INDEX admin_units_parent_idx ON admin_units (parent_id);

-- ── FCD processing runs ───────────────────────────
CREATE TABLE IF NOT EXISTS fcd_runs (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  run_name          TEXT NOT NULL,
  year              INTEGER NOT NULL,
  start_date        DATE NOT NULL,
  end_date          DATE NOT NULL,
  satellite         TEXT DEFAULT 'Sentinel-2 L2A',
  cloud_threshold   NUMERIC DEFAULT 1,
  algorithm_version TEXT NOT NULL DEFAULT '1.0.0',
  ndvi_lo           NUMERIC DEFAULT 0.25,
  ndvi_hi           NUMERIC DEFAULT 0.45,
  ndwi_hi           NUMERIC DEFAULT 0.2,
  bi_hi             NUMERIC DEFAULT 2.0,
  si_lo             NUMERIC DEFAULT 0.92,
  si_hi             NUMERIC DEFAULT 0.95,
  status            TEXT DEFAULT 'queued' CHECK (
                      status IN ('queued','running','completed','failed')
                    ),
  created_by        TEXT,
  created_at        TIMESTAMPTZ DEFAULT now(),
  completed_at      TIMESTAMPTZ
);

-- ── COG raster registry ───────────────────────────
CREATE TABLE IF NOT EXISTS fcd_rasters (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  run_id       UUID REFERENCES fcd_runs(id),
  aoi_id       UUID REFERENCES admin_units(id),
  year         INTEGER NOT NULL,
  raster_type  TEXT CHECK (raster_type IN ('fcd','change','rgb','ndvi','qa')),
  cog_url      TEXT NOT NULL,
  tilejson_url TEXT,
  min_value    INTEGER,
  max_value    INTEGER,
  nodata       INTEGER DEFAULT 255,
  geom         GEOMETRY(MultiPolygon, 4326),
  file_size_mb NUMERIC,
  created_at   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX fcd_rasters_run_idx ON fcd_rasters (run_id);
CREATE INDEX fcd_rasters_aoi_idx ON fcd_rasters (aoi_id);

-- ── FCD class statistics ──────────────────────────
CREATE TABLE IF NOT EXISTS fcd_class_stats (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  run_id       UUID REFERENCES fcd_runs(id),
  aoi_id       UUID REFERENCES admin_units(id),
  year         INTEGER NOT NULL,
  class_code   INTEGER NOT NULL,
  class_name   TEXT NOT NULL,
  area_ha      NUMERIC NOT NULL,
  percent_area NUMERIC,
  pixel_count  BIGINT,
  created_at   TIMESTAMPTZ DEFAULT now(),
  UNIQUE (run_id, aoi_id, year, class_code)
);
CREATE INDEX fcd_class_stats_aoi_idx ON fcd_class_stats (aoi_id, year);

-- ── Transition matrix ─────────────────────────────
CREATE TABLE IF NOT EXISTS fcd_transitions (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  from_run_id     UUID REFERENCES fcd_runs(id),
  to_run_id       UUID REFERENCES fcd_runs(id),
  aoi_id          UUID REFERENCES admin_units(id),
  from_class_code INTEGER NOT NULL,
  to_class_code   INTEGER NOT NULL,
  area_ha         NUMERIC NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE (from_run_id, to_run_id, aoi_id, from_class_code, to_class_code)
);

-- ── Carbon sequestration stats ────────────────────
CREATE TABLE IF NOT EXISTS fcd_carbon_stats (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  run_id          UUID REFERENCES fcd_runs(id),
  aoi_id          UUID REFERENCES admin_units(id),
  year            INTEGER NOT NULL,
  class_code      INTEGER NOT NULL,
  class_name      TEXT NOT NULL,
  area_ha         NUMERIC NOT NULL,
  coef_t_per_ha   NUMERIC NOT NULL,
  carbon_t        NUMERIC NOT NULL,
  co2eq_t         NUMERIC NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE (run_id, aoi_id, year, class_code)
);

-- ── Sentinel-2 scene log ──────────────────────────
CREATE TABLE IF NOT EXISTS sentinel_scene_log (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  run_id           UUID REFERENCES fcd_runs(id),
  aoi_id           UUID REFERENCES admin_units(id),
  scene_id         TEXT NOT NULL,
  acquisition_time TIMESTAMPTZ,
  mgrs_tile        TEXT,
  cloud_pct        NUMERIC,
  spacecraft       TEXT,
  stac_url         TEXT,
  created_at       TIMESTAMPTZ DEFAULT now()
);

-- ── Report jobs ───────────────────────────────────
CREATE TABLE IF NOT EXISTS report_jobs (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  run_id      UUID REFERENCES fcd_runs(id),
  aoi_id      UUID REFERENCES admin_units(id),
  report_type TEXT CHECK (report_type IN ('district','block','forest_division','state')),
  status      TEXT DEFAULT 'queued' CHECK (status IN ('queued','running','completed','failed')),
  pdf_url     TEXT,
  xlsx_url    TEXT,
  created_at  TIMESTAMPTZ DEFAULT now(),
  completed_at TIMESTAMPTZ
);
