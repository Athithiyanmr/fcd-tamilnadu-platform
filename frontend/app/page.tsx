export default function Home() {
  return (
    <main style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>

      {/* Header */}
      <header style={{
        background: '#14532d',
        color: '#fff',
        padding: '14px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
      }}>
        <span style={{ fontSize: 28 }}>🌳</span>
        <div>
          <h1 style={{ margin: 0, fontSize: 17, fontWeight: 700 }}>
            Tamil Nadu Forest Canopy Density Monitoring Platform
          </h1>
          <p style={{ margin: 0, fontSize: 12, color: '#86efac' }}>
            Sentinel-2 · PostGIS · Google Earth Engine · Tamil Nadu Forest Department
          </p>
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1 }}>

        {/* Sidebar */}
        <aside style={{
          width: 280,
          background: '#1f2937',
          color: '#fff',
          padding: 16,
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
          overflowY: 'auto',
        }}>
          <div>
            <label style={{ fontSize: 11, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 1 }}>Year</label>
            <select style={sidebarSelect}>
              <option>2025</option>
              <option>2020</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: 11, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 1 }}>District</label>
            <select style={sidebarSelect}>
              <option value="">All Districts</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: 11, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 1 }}>Block / Taluk</label>
            <select style={sidebarSelect}>
              <option value="">All Blocks</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: 11, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 1 }}>Forest Division</label>
            <select style={sidebarSelect}>
              <option value="">All Divisions</option>
            </select>
          </div>

          {/* Legend */}
          <div style={{ marginTop: 8 }}>
            <label style={{ fontSize: 11, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 1 }}>FCD Legend</label>
            <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {LEGEND.map((item) => (
                <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
                  <span style={{ width: 16, height: 16, borderRadius: 3, background: item.color, flexShrink: 0 }} />
                  <span style={{ color: '#d1d5db' }}>{item.label}</span>
                </div>
              ))}
            </div>
          </div>

          <button style={{
            marginTop: 'auto',
            background: '#15803d',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '10px 16px',
            fontSize: 13,
            fontWeight: 600,
            cursor: 'pointer',
          }}>
            📅 Download Report
          </button>
        </aside>

        {/* Map placeholder */}
        <div style={{
          flex: 1,
          background: '#111827',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 12,
          color: '#6b7280',
        }}>
          <span style={{ fontSize: 56 }}>🗺️</span>
          <p style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>MapLibre GL map loads here</p>
          <p style={{ fontSize: 13, margin: 0 }}>
            Connect TiTiler (:8080) + pg_tileserv (:7800) to render FCD layers
          </p>
          <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
            <a href="http://localhost:8000/docs"
               style={apiBadge}>
              📚 API Docs
            </a>
            <a href="http://localhost:8080"
               style={apiBadge}>
              🌍 TiTiler
            </a>
            <a href="http://localhost:7800"
               style={apiBadge}>
              🔷 pg_tileserv
            </a>
          </div>
        </div>
      </div>

      {/* Stats footer */}
      <footer style={{
        background: '#1f2937',
        color: '#9ca3af',
        padding: '10px 24px',
        fontSize: 12,
        display: 'flex',
        gap: 24,
        flexWrap: 'wrap',
      }}>
        <span>🌲 High Forest: — ha</span>
        <span>🌿 Low Forest: — ha</span>
        <span>🌾 Grassland: — ha</span>
        <span>🏜️ Bare Land: — ha</span>
        <span>🌊 Carbon Stock: — t</span>
        <span style={{ marginLeft: 'auto' }}>
          FCD Tamil Nadu Platform v1.0.0
        </span>
      </footer>

    </main>
  );
}

const sidebarSelect: React.CSSProperties = {
  marginTop: 4,
  width: '100%',
  background: '#374151',
  border: '1px solid #4b5563',
  borderRadius: 6,
  padding: '8px 10px',
  fontSize: 13,
  color: '#f9fafb',
};

const apiBadge: React.CSSProperties = {
  background: '#374151',
  color: '#d1d5db',
  padding: '6px 14px',
  borderRadius: 6,
  fontSize: 12,
  textDecoration: 'none',
  border: '1px solid #4b5563',
};

const LEGEND = [
  { color: '#006837', label: 'High Forest' },
  { color: '#3ea540', label: 'Low Forest' },
  { color: '#baf096', label: 'Grassland' },
  { color: '#ad8855', label: 'Bare Land' },
  { color: '#3380cc', label: 'Water' },
  { color: '#000000', label: 'Other / No Data' },
];
