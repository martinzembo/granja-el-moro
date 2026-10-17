import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

export default function RegistrarEntregaFormScreen() {
  const { crianzaId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [fecha, setFecha] = useState(() => new Date().toISOString().slice(0, 10))
  const [remito, setRemito] = useState('')
  const [kilos, setKilos] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)

  async function enviar(e) {
    e.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await adminApi.registrarEntregaAlimento({
        crianzaId,
        fecha: new Date(`${fecha}T00:00:00`),
        remito,
        kilos: Number(kilos),
      })
      navigate(`/crianzas/${crianzaId}`, { replace: true })
    } catch (err) {
      setError(err.message || 'No se pudo conectar con el servidor')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div>
      <AppBarPanel title="Entrega de alimento" volver />
      <div className="page">
        <form className="form" onSubmit={enviar}>
          {error && <div className="error-banner">{error}</div>}
          <div className="campo">
            <label htmlFor="fecha">Fecha</label>
            <input id="fecha" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
          </div>
          <div className="campo">
            <label htmlFor="remito">N° de remito</label>
            <input id="remito" value={remito} onChange={(e) => setRemito(e.target.value)} required />
          </div>
          <div className="campo">
            <label htmlFor="kilos">Kilos</label>
            <input
              id="kilos"
              type="number"
              step="0.01"
              min="0"
              value={kilos}
              onChange={(e) => setKilos(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar'}
          </button>
        </form>
      </div>
    </div>
  )
}
