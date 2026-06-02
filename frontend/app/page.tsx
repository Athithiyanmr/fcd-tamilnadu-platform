export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      <header className="bg-green-900 text-white px-6 py-4 flex items-center gap-3">
        <span className="text-2xl">🌳</span>
        <div>
          <h1 className="text-lg font-bold leading-tight">
            Tamil Nadu Forest Canopy Density Monitoring Platform
          </h1>
          <p className="text-green-300 text-xs">
            Sentinel-2 · PostGIS · GEE · Tamil Nadu Forest Department
          </p>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-72 bg-gray-900 text-white p-4 flex flex-col gap-4 overflow-y-auto">
          <section>
            <label className="text-xs text-gray-400 uppercase tracking-wider">Year</label>
            <select className="mt-1 w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
              <option>2025</option>
              <option>2020</option>
            </select>
          </section>

          <section>
            <label className="text-xs text-gray-400 uppercase tracking-wider">District</label>
            <select className="mt-1 w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
              <option value="">All Districts</option>
            </select>
          </section>

          <section>
            <label className="text-xs text-gray-400 uppercase tracking-wider">Block / Taluk</label>
            <select className="mt-1 w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
              <option value="">All Blocks</option>
            </select>
          </section>

          <section>
            <label className="text-xs text-gray-400 uppercase tracking-wider">Forest Division</label>
            <select className="mt-1 w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
              <option value="">All Divisions</option>
            </select>
          </section>

          {/* FCD Legend */}
          <section className="mt-4">
            <label className="text-xs text-gray-400 uppercase tracking-wider">FCD Legend</label>
            <div className="mt-2 space-y-1">
              {[
                { color: "#006837", label: "High Forest" },
                { color: "#3ea540", label: "Low Forest" },
                { color: "#baf096", label: "Grassland" },
                { color: "#ad8855", label: "Bare Land" },
                { color: "#3380cc", label: "Water" },
                { color: "#000000", label: "Other" },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-2 text-sm">
                  <span
                    className="w-4 h-4 rounded-sm flex-shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-gray-300">{item.label}</span>
                </div>
              ))}
            </div>
          </section>

          <button className="mt-auto bg-green-700 hover:bg-green-600 text-white rounded px-4 py-2 text-sm font-medium">
            Download Report
          </button>
        </aside>

        {/* Map area placeholder */}
        <div className="flex-1 bg-gray-800 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <p className="text-5xl mb-4">🗺️</p>
            <p className="text-lg font-medium">MapLibre GL map will render here</p>
            <p className="text-sm mt-1">
              Connect your TiTiler + pg_tileserv endpoints to show FCD layers
            </p>
          </div>
        </div>
      </div>

      {/* Stats bar */}
      <footer className="bg-gray-900 text-white px-6 py-3 text-xs text-gray-400 flex gap-6">
        <span>High Forest: — ha</span>
        <span>Low Forest: — ha</span>
        <span>Grassland: — ha</span>
        <span>Bare Land: — ha</span>
        <span>Carbon Stock: — t</span>
      </footer>
    </main>
  );
}
