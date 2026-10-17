import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

export default function NuevaCrianzaFormScreen() {
  const { api } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [numero, setNumero] = useState('')
  const [fechaInicio, setFechaInicio] = useState(() => new Date().toISOString().slice(0, 10))
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)

  async function enviar(e) {
    e.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      const creada = await adminApi.crearCrianza({
        numero: Number(numero),
        fechaInicio: new Date(`${fechaInicio}T00:00:00`),
      })
      navigate(`/crianzas/${creada.id}`, { replace: true })
    } catch (err) {
      setError(err.message || 'No se pudo conectar con el servidor')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div>
      <AppBarPanel title="Nueva crianza" volver />
      <div className="page">
        <form className="form" onSubmit={enviar}>
          {error && <div className="error-banner">{error}</div>}
          <div className="campo">
            <label htmlFor="numero">Número de crianza</label>
            <input
              id="numero"
              type="number"
              min="1"
              value={numero}
              onChange={(e) => setNumero(e.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label htmlFor="fecha">Fecha de inicio</label>
            <input
              id="fecha"
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary" disabled={enviando}>
            {enviando ? 'Creando…' : 'Crear crianza'}
          </button>
        </form>
      </div>
    </div>
  )
}
