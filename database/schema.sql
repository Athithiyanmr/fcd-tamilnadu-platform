-- ============================================================
-- FCD Tamil Nadu Platform — PostGIS Schema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Administrative unit boundaries (state / district / block / forest division)
CREATE TABLE IF NOT EXISTS admin_units (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL,
    unit_type   TEXT NOT NULL CHECK (unit_type IN
                    ('state','district','block','forest_circle',
                     'forest_division','forest_range','custom_aoi')),
    parent_id   UUID REFERENCES admin_units(id),
    source      TEXT,
    district    TEXT,
    state       TEXT DEFAULT 'Tamil Nadu',
    geom        GEOMETRY(MultiPolygon, 4326),
    created_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS admin_units_geom_idx   ON admin_units USING GIST (geom);
CREATE INDEX IF NOT EXISTS admin_units_type_idx   ON admin_units (unit_type);
CREATE INDEX IF NOT EXISTS admin_units_parent_idx ON admin_units (parent_id);

-- FCD processing runs
CREATE TABLE IF NOT EXISTS fcd_runs (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_name           TEXT NOT NULL,
    year               INTEGER NOT NULL,
    start_date         DATE NOT NULL,
    end_date           DATE NOT NULL,
    satellite          TEXT DEFAULT 'Sentinel-2 SR Harmonized',
    cloud_threshold    NUMERIC DEFAULT 1,
    algorithm_version  TEXT DEFAULT '1.0.0',
    status             TEXT DEFAULT 'queued'
                            CHECK (status IN ('queued','running','completed','failed')),
    gee_task_ids       JSONB,
    created_by         TEXT,
    created_at         TIMESTAMPTZ DEFAULT now(),
    completed_at       TIMESTAMPTZ
);

-- COG raster outputs
CREATE TABLE IF NOT EXISTS fcd_rasters (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id       UUID REFERENCES fcd_runs(id) ON DELETE CASCADE,
    aoi_id       UUID REFERENCES admin_units(id),
    year         INTEGER NOT NULL,
    raster_type  TEXT NOT NULL CHECK (raster_type IN ('fcd','change','rgb','qa')),
    cog_url      TEXT NOT NULL,
    tilejson_url TEXT,
    min_value    INTEGER,
    max_value    INTEGER,
    nodata       INTEGER,
    geom         GEOMETRY(MultiPolygon, 4326),
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- FCD class statistics (per run × AOI)
CREATE TABLE IF NOT EXISTS fcd_class_stats (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id        UUID REFERENCES fcd_runs(id) ON DELETE CASCADE,
    aoi_id        UUID REFERENCES admin_units(id),
    year          INTEGER NOT NULL,
    class_code    INTEGER NOT NULL,
    class_name    TEXT NOT NULL,
    area_ha       NUMERIC NOT NULL,
    percent_area  NUMERIC,
    created_at    TIMESTAMPTZ DEFAULT now(),
    UNIQUE (run_id, aoi_id, class_code)
);

-- Class-to-class transition matrix
CREATE TABLE IF NOT EXISTS fcd_transitions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_run_id     UUID REFERENCES fcd_runs(id) ON DELETE CASCADE,
    to_run_id       UUID REFERENCES fcd_runs(id) ON DELETE CASCADE,
    aoi_id          UUID REFERENCES admin_units(id),
    from_class_code INTEGER NOT NULL,
    to_class_code   INTEGER NOT NULL,
    area_ha         NUMERIC NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Carbon sequestration estimates
CREATE TABLE IF NOT EXISTS fcd_carbon_stats (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id        UUID REFERENCES fcd_runs(id) ON DELETE CASCADE,
    aoi_id        UUID REFERENCES admin_units(id),
    year          INTEGER NOT NULL,
    class_code    INTEGER NOT NULL,
    class_name    TEXT NOT NULL,
    area_ha       NUMERIC NOT NULL,
    coef_t_per_ha NUMERIC NOT NULL,
    carbon_t      NUMERIC NOT NULL,
    co2eq_t       NUMERIC NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- Sentinel-2 scene audit log
CREATE TABLE IF NOT EXISTS gee_scene_log (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id           UUID REFERENCES fcd_runs(id) ON DELETE CASCADE,
    aoi_id           UUID REFERENCES admin_units(id),
    image_id         TEXT,
    acquisition_time TIMESTAMPTZ,
    mgrs_tile        TEXT,
    cloud_pct        NUMERIC,
    spacecraft       TEXT
);

-- Report generation jobs
CREATE TABLE IF NOT EXISTS report_jobs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id      UUID REFERENCES fcd_runs(id) ON DELETE CASCADE,
    aoi_id      UUID REFERENCES admin_units(id),
    report_type TEXT CHECK (report_type IN ('state','district','block','forest_division')),
    status      TEXT DEFAULT 'queued',
    pdf_url     TEXT,
    xlsx_url    TEXT,
    created_at  TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

-- Seed: FCD class metadata
INSERT INTO fcd_class_stats (id, run_id, aoi_id, year, class_code, class_name, area_ha, percent_area)
SELECT * FROM (VALUES
    (0, 'Other'),
    (1, 'Water'),
    (2, 'High forest'),
    (3, 'Low forest'),
    (4, 'Grassland'),
    (5, 'Bare land')
) v(code, name)
WHERE FALSE;  -- Template only, no rows inserted
