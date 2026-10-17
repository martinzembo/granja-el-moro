import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { ApiClient } from './apiClient'

const STORAGE_KEY = 'granja-el-moro.token'

const AuthContext = createContext(null)

/** Sesión del admin logueado. Guarda el JWT en localStorage para no pedir
 * login cada vez que se recarga la página — espejo de AuthService en
 * mobile/lib/core/auth_service.dart, pero el panel web es solo para el
 * rol admin (ver CLAUDE.md, sección Web: el flujo del granjero sigue
 * siendo exclusivo de la app). */
export function AuthProvider({ children }) {
  const [token, setToken] = useState(null)
  const [usuario, setUsuario] = useState(null)
  // 'cargando' | 'autenticado' | 'noAutenticado'
  const [estado, setEstado] = useState('cargando')

  useEffect(() => {
    const guardado = localStorage.getItem(STORAGE_KEY)
    if (!guardado) {
      setEstado('noAutenticado')
      return
    }
    new ApiClient(guardado)
      .get('/auth/me')
      .then((data) => {
        if (data.rol !== 'admin') {
          // El panel web es solo para administradores — si por algún
          // motivo hay un token de granjero guardado, no sirve acá.
          throw new Error('rol no admin')
        }
        setToken(guardado)
        setUsuario(data)
        setEstado('autenticado')
      })
      .catch(() => {
        localStorage.removeItem(STORAGE_KEY)
        setEstado('noAutenticado')
      })
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await new ApiClient().post('/auth/login', { email, password }, { auth: false })
    const nuevoToken = data.access_token
    const me = await new ApiClient(nuevoToken).get('/auth/me')
    if (me.rol !== 'admin') {
      throw new Error(
        'Esta cuenta no es de administrador — el panel web es solo para administradores. Usá la app móvil.',
      )
    }
    localStorage.setItem(STORAGE_KEY, nuevoToken)
    setToken(nuevoToken)
    setUsuario(me)
    setEstado('autenticado')
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    setToken(null)
    setUsuario(null)
    setEstado('noAutenticado')
  }, [])

  const api = new ApiClient(token)

  return (
    <AuthContext.Provider value={{ estado, usuario, token, login, logout, api }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth() tiene que usarse dentro de <AuthProvider>')
  return ctx
}
