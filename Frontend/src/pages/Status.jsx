import { useEffect, useState } from 'react'
import api from '../api/client'

function StatusBadge({ value }) {
  const ok = value === 'ok' || value === 'ready' || value === 'healthy'
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
        ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}
    >
      {ok ? '● OK' : '● Issue'}
    </span>
  )
}

export default function Status() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [lastChecked, setLastChecked] = useState(null)

  const fetchStatus = async () => {
    setLoading(true)
    setError('')
    try {
      const { data: d } = await api.get('/status')
      setData(d)
      setLastChecked(new Date())
    } catch (err) {
      setError('Could not reach the DRINKOO API. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const id = setInterval(fetchStatus, 30_000) // auto-refresh every 30s
    return () => clearInterval(id)
  }, [])

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Status</h1>
          <p className="text-gray-500 text-sm mt-1">
            {lastChecked ? `Last checked: ${lastChecked.toLocaleTimeString()}` : 'Checking…'}
          </p>
        </div>
        <button onClick={fetchStatus} disabled={loading} className="btn-secondary text-sm">
          {loading ? 'Refreshing…' : '↻ Refresh'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {error}
        </div>
      )}

      {data && (
        <>
          {/* Overall health banner */}
          <div
            className={`rounded-xl p-5 mb-6 flex items-center gap-4 ${
              data.status === 'healthy'
                ? 'bg-green-50 border border-green-200'
                : 'bg-yellow-50 border border-yellow-200'
            }`}
          >
            <span className="text-3xl">{data.status === 'healthy' ? '✅' : '⚠️'}</span>
            <div>
              <p className={`font-semibold ${data.status === 'healthy' ? 'text-green-800' : 'text-yellow-800'}`}>
                {data.status === 'healthy' ? 'All systems operational' : 'Degraded — some checks failed'}
              </p>
              <p className="text-sm text-gray-500 mt-0.5">
                v{data.version} · {data.environment}
              </p>
            </div>
          </div>

          {/* Check cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Object.entries(data.checks)
              .filter(([k]) => k !== 'database_error')
              .map(([key, value]) => (
                <div key={key} className="card flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wide">{key.replace(/_/g, ' ')}</p>
                    <p className="text-sm font-medium text-gray-800 mt-0.5 truncate max-w-[160px]">{value}</p>
                  </div>
                  <StatusBadge value={value} />
                </div>
              ))}
          </div>

          {data.checks.database_error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-700">
              <span className="font-medium">DB error:</span> {data.checks.database_error}
            </div>
          )}
        </>
      )}

      {loading && !data && (
        <div className="flex items-center justify-center py-16 text-gray-400">
          <div className="text-center">
            <div className="text-3xl mb-2 animate-pulse">🔍</div>
            <p>Checking system health…</p>
          </div>
        </div>
      )}
    </div>
  )
}
