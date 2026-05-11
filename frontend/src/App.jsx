import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'

import AppLayout   from './components/Layout/AppLayout'
import Landing     from './pages/Landing'
import Dashboard   from './pages/Dashboard'
import Generator   from './pages/Generator'
import Chat        from './pages/Chat'
import Suggestions from './pages/Suggestions'
import Activity    from './pages/Activity'
import Analytics   from './pages/Analytics'
import ProjectViewer from './pages/ProjectViewer'
import Login       from './pages/Login'
import Signup      from './pages/Signup'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return null
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Root redirects to landing */}
          <Route path="/" element={<Navigate to="/landing" replace />} />
          
          {/* Landing page */}
          <Route path="/landing" element={<Landing />} />
          
          {/* Auth pages */}
          <Route path="/login"  element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* App pages – sidebar layout, no auth wall (optional auth) */}
          <Route element={<AppLayout />}>
            <Route path="dashboard"              element={<Dashboard />} />
            <Route path="generator"              element={<Generator />} />
            <Route path="chat"                   element={<Chat />} />
            <Route path="suggestions"            element={<Suggestions />} />
            <Route path="activity"               element={<Activity />} />
            <Route path="analytics"              element={<Analytics />} />
            <Route path="projects/:id"           element={<ProjectViewer />} />
          </Route>

          <Route path="*" element={<Navigate to="/landing" replace />} />
        </Routes>
        
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1a1a23',
              color: '#e2e8f0',
              border: '1px solid #2a2a35',
              borderRadius: '12px',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#1a1a23',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#1a1a23',
              },
            },
          }}
        />
      </BrowserRouter>
    </AuthProvider>
  )
}
