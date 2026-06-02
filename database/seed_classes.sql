-- =====================================================
-- FCD Class definitions and carbon coefficients
-- =====================================================

CREATE TABLE IF NOT EXISTS fcd_class_definitions (
  code          INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,
  color_hex     TEXT NOT NULL,
  coef_t_per_ha NUMERIC NOT NULL DEFAULT 0,
  description   TEXT
);

INSERT INTO fcd_class_definitions (code, name, color_hex, coef_t_per_ha, description) VALUES
  (0, 'Other',       '#000000', 0,      'Unclassified or cloud shadow'),
  (1, 'Water',       '#3380cc', 0,      'Water bodies — NDWI > 0.2'),
  (2, 'High forest', '#006837', 104.58, 'Dense forest canopy — NDVI > 0.45'),
  (3, 'Low forest',  '#3ea540', 90.18,  'Open / degraded forest — NDVI 0.25–0.45'),
  (4, 'Grassland',   '#baf096', 60.64,  'Grass and scrub — NDVI > 0.25'),
  (5, 'Bare land',   '#ad8855', 0,      'Bare soil / built-up — NDVI < 0.25')
ON CONFLICT (code) DO NOTHING;
