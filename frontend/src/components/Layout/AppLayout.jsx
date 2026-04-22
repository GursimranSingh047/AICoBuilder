import React, { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import { healthAPI } from '../../api/client'
import { Wifi, WifiOff } from 'lucide-react'

export default function AppLayout() {
  const [online, setOnline] = useState(null)

  useEffect(() => {
    healthAPI.check()
      .then(() => setOnline(true))
      .catch(() => setOnline(false))
  }, [])

  return (
    <div className="flex h-screen overflow-hidden bg-surface-DEFAULT">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Backend status bar */}
        {online === false && (
          <div className="flex items-center gap-2 px-4 py-2 bg-rose/10 border-b border-rose/20 text-rose text-xs">
            <WifiOff size={13} />
            Backend offline — start FastAPI on <code className="font-mono">http://127.0.0.1:8000</code>
          </div>
        )}
        {online === true && (
          <div className="flex items-center gap-2 px-4 py-1.5 bg-emerald/5 border-b border-emerald/10 text-emerald/70 text-[11px]">
            <Wifi size={12} />
            Connected to backend
          </div>
        )}

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-surface-DEFAULT dot-grid">
          <div className="min-h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
