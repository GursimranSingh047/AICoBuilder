import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'

import AppLayout   from './components/Layout/AppLayout'
import Dashboard   from './pages/Dashboard'
import Generator   from './pages/Generator'
import Chat        from './pages/Chat'
import Suggestions from './pages/Suggestions'
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
          {/* Auth pages */}
          <Route path="/login"  element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* App pages – sidebar layout, no auth wall (optional auth) */}
          <Route element={<AppLayout />}>
            <Route index                      element={<Dashboard />} />
            <Route path="generator"           element={<Generator />} />
            <Route path="chat"                element={<Chat />} />
            <Route path="suggestions"         element={<Suggestions />} />
            <Route path="projects/:id"        element={<ProjectViewer />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
