import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

export default function RegistrarIngresoFormScreen() {
  const { crianzaId, cgId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [fecha, setFecha] = useState(() => new Date().toISOString().slice(0, 10))
  const [origen, setOrigen] = useState('')
  const [cantidad, setCantidad] = useState('')
  const [muertosTransporte, setMuertosTransporte] = useState('0')
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)

  async function enviar(e) {
    e.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await adminApi.registrarIngreso({
        crianzaId,
        cgId,
        fecha: new Date(`${fecha}T00:00:00`),
        origen,
        cantidad: Number(cantidad),
        muertosTransporte: Number(muertosTransporte),
      })
      navigate(`/crianzas/${crianzaId}/galpones/${cgId}`, { replace: true })
    } catch (err) {
      setError(err.message || 'No se pudo conectar con el servidor')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div>
      <AppBarPanel title="Ingreso de pollitos BB" volver />
      <div className="page">
        <form className="form" onSubmit={enviar}>
          {error && <div className="error-banner">{error}</div>}
          <div className="campo">
            <label htmlFor="fecha">Fecha</label>
            <input id="fecha" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
          </div>
          <div className="campo">
            <label htmlFor="origen">Origen</label>
            <input id="origen" value={origen} onChange={(e) => setOrigen(e.target.value)} required />
            <p className="campo-ayuda">Línea genética o granja de reproductoras (ej. Las Violetas)</p>
          </div>
          <div className="campo">
            <label htmlFor="cantidad">Cantidad despachada</label>
            <input
              id="cantidad"
              type="number"
              min="1"
              value={cantidad}
              onChange={(e) => setCantidad(e.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label htmlFor="muertos">Muertos en el transporte</label>
            <input
              id="muertos"
              type="number"
              min="0"
              value={muertosTransporte}
              onChange={(e) => setMuertosTransporte(e.target.value)}
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
