-- ============================================================
-- FCD Tamil Nadu Platform — Admin Unit Boundary Seeds
-- Seeds the 38 Tamil Nadu districts into admin_units.
-- Geometries are NULL here; load actual MultiPolygons via ogr2ogr:
--
--   ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=fcd user=postgres" \
--     tamilnadu_districts.shp -nln admin_units_import -overwrite
--
--   UPDATE admin_units a
--      SET geom = ST_Multi(ST_Transform(i.wkb_geometry, 4326))
--     FROM admin_units_import i
--    WHERE LOWER(a.name) = LOWER(i.district_nm);
-- ============================================================

-- State-level row first
INSERT INTO admin_units (name, unit_type, state, source)
VALUES ('Tamil Nadu', 'state', 'Tamil Nadu', 'LGDS')
ON CONFLICT DO NOTHING;

-- 38 Districts (2023 delimitation)
INSERT INTO admin_units (name, unit_type, state, district, source) VALUES
  ('Ariyalur',         'district', 'Tamil Nadu', 'Ariyalur',         'LGDS'),
  ('Chengalpattu',     'district', 'Tamil Nadu', 'Chengalpattu',     'LGDS'),
  ('Chennai',          'district', 'Tamil Nadu', 'Chennai',          'LGDS'),
  ('Coimbatore',       'district', 'Tamil Nadu', 'Coimbatore',       'LGDS'),
  ('Cuddalore',        'district', 'Tamil Nadu', 'Cuddalore',        'LGDS'),
  ('Dharmapuri',       'district', 'Tamil Nadu', 'Dharmapuri',       'LGDS'),
  ('Dindigul',         'district', 'Tamil Nadu', 'Dindigul',         'LGDS'),
  ('Erode',            'district', 'Tamil Nadu', 'Erode',            'LGDS'),
  ('Kallakurichi',     'district', 'Tamil Nadu', 'Kallakurichi',     'LGDS'),
  ('Kancheepuram',     'district', 'Tamil Nadu', 'Kancheepuram',     'LGDS'),
  ('Kanyakumari',      'district', 'Tamil Nadu', 'Kanyakumari',      'LGDS'),
  ('Karur',            'district', 'Tamil Nadu', 'Karur',            'LGDS'),
  ('Krishnagiri',      'district', 'Tamil Nadu', 'Krishnagiri',      'LGDS'),
  ('Madurai',          'district', 'Tamil Nadu', 'Madurai',          'LGDS'),
  ('Mayiladuthurai',   'district', 'Tamil Nadu', 'Mayiladuthurai',   'LGDS'),
  ('Nagapattinam',     'district', 'Tamil Nadu', 'Nagapattinam',     'LGDS'),
  ('Namakkal',         'district', 'Tamil Nadu', 'Namakkal',         'LGDS'),
  ('Nilgiris',         'district', 'Tamil Nadu', 'The Nilgiris',     'LGDS'),
  ('Perambalur',       'district', 'Tamil Nadu', 'Perambalur',       'LGDS'),
  ('Pudukkottai',      'district', 'Tamil Nadu', 'Pudukkottai',      'LGDS'),
  ('Ramanathapuram',   'district', 'Tamil Nadu', 'Ramanathapuram',   'LGDS'),
  ('Ranipet',          'district', 'Tamil Nadu', 'Ranipet',          'LGDS'),
  ('Salem',            'district', 'Tamil Nadu', 'Salem',            'LGDS'),
  ('Sivaganga',        'district', 'Tamil Nadu', 'Sivaganga',        'LGDS'),
  ('Tenkasi',          'district', 'Tamil Nadu', 'Tenkasi',          'LGDS'),
  ('Thanjavur',        'district', 'Tamil Nadu', 'Thanjavur',        'LGDS'),
  ('Theni',            'district', 'Tamil Nadu', 'Theni',            'LGDS'),
  ('Thoothukudi',      'district', 'Tamil Nadu', 'Thoothukudi',      'LGDS'),
  ('Tiruchirappalli',  'district', 'Tamil Nadu', 'Tiruchirappalli',  'LGDS'),
  ('Tirunelveli',      'district', 'Tamil Nadu', 'Tirunelveli',      'LGDS'),
  ('Tirupattur',       'district', 'Tamil Nadu', 'Tirupattur',       'LGDS'),
  ('Tiruppur',         'district', 'Tamil Nadu', 'Tiruppur',         'LGDS'),
  ('Tiruvallur',       'district', 'Tamil Nadu', 'Tiruvallur',       'LGDS'),
  ('Tiruvannamalai',   'district', 'Tamil Nadu', 'Tiruvannamalai',   'LGDS'),
  ('Tiruvarur',        'district', 'Tamil Nadu', 'Tiruvarur',        'LGDS'),
  ('Vellore',          'district', 'Tamil Nadu', 'Vellore',          'LGDS'),
  ('Villupuram',       'district', 'Tamil Nadu', 'Villupuram',       'LGDS'),
  ('Virudhunagar',     'district', 'Tamil Nadu', 'Virudhunagar',     'LGDS')
ON CONFLICT DO NOTHING;
