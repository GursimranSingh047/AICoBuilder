import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authAPI } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  // Re-hydrate from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('pp_token')
    if (!token) { setLoading(false); return }
    authAPI.me()
      .then(r => setUser(r.data))
      .catch(() => localStorage.removeItem('pp_token'))
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email, password) => {
    const { data } = await authAPI.login({ email, password })
    localStorage.setItem('pp_token', data.access_token)
    setUser(data.user)
    return data
  }, [])

  const signup = useCallback(async (email, username, password) => {
    const { data } = await authAPI.signup({ email, username, password })
    localStorage.setItem('pp_token', data.access_token)
    setUser(data.user)
    return data
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('pp_token')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
