import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('drinkoo_user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(false)

  const login = useCallback(async (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)

    const { data } = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('drinkoo_token', data.access_token)

    const { data: me } = await api.get('/auth/me')
    localStorage.setItem('drinkoo_user', JSON.stringify(me))
    setUser(me)
    return me
  }, [])

  const signup = useCallback(async (email, password, fullName) => {
    await api.post('/auth/signup', { email, password, full_name: fullName })
    return login(email, password)
  }, [login])

  const logout = useCallback(() => {
    localStorage.removeItem('drinkoo_token')
    localStorage.removeItem('drinkoo_user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
