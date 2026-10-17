import { useState } from 'react'
import { useAuth } from '../../core/AuthContext'

export default function LoginScreen() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  async function enviar(e) {
    e.preventDefault()
    setError(null)
    setCargando(true)
    try {
      await login(email, password)
    } catch (err) {
      setError(err.message || 'No se pudo conectar con el servidor')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login-card" onSubmit={enviar}>
        <h1>Granja El Moro</h1>
        <p className="subtitulo" style={{ textAlign: 'center', marginTop: '-18px', marginBottom: 24 }}>
          Panel de administrador
        </p>
        {error && <div className="error-banner">{error}</div>}
        <div className="campo">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoCapitalize="none"
            autoCorrect="off"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="campo">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={cargando}>
          {cargando ? 'Ingresando…' : 'Ingresar'}
        </button>
      </form>
    </div>
  )
}
