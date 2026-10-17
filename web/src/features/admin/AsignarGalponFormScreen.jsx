import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

export default function AsignarGalponFormScreen() {
  const { crianzaId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [galpones, setGalpones] = useState(null)
  const [granjeros, setGranjeros] = useState(null)
  const [galponId, setGalponId] = useState('')
  const [granjeroId, setGranjeroId] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState(null)

  function cargar() {
    Promise.all([adminApi.galpones(), adminApi.galponesDeCrianza(crianzaId), adminApi.granjeros()]).then(
      ([todos, deEstaCrianza, granjerosData]) => {
        const yaAsignados = new Set(deEstaCrianza.map((cg) => cg.galpon_id))
        setGalpones(todos.filter((g) => !yaAsignados.has(g.id)))
        setGranjeros(granjerosData)
      },
    )
  }

  useEffect(cargar, [crianzaId])

  async function crearGalponNuevo() {
    const nombre = window.prompt('Nombre del galpón nuevo:')
    if (!nombre) return
    const capacidadStr = window.prompt('Capacidad máxima (aves):')
    const capacidad = Number(capacidadStr)
    if (!capacidadStr || Number.isNaN(capacidad)) return
    try {
      const galpon = await adminApi.crearGalpon({ nombre, capacidadMaxima: capacidad })
      cargar()
      setGalponId(String(galpon.id))
    } catch (err) {
      setError(err.message || 'No se pudo crear el galpón')
    }
  }

  async function guardar(e) {
    e.preventDefault()
    if (!galponId || !granjeroId) {
      setError('Elegí un galpón y un granjero')
      return
    }
    setError(null)
    setGuardando(true)
    try {
      await adminApi.asignarGalpon({ crianzaId, galponId: Number(galponId), granjeroId: Number(granjeroId) })
      navigate(`/crianzas/${crianzaId}`, { replace: true })
    } catch (err) {
      setError(err.message || 'No se pudo conectar con el servidor')
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div>
      <AppBarPanel title="Asignar galpón" volver />
      <div className="page">
        {galpones === null || granjeros === null ? (
          <p className="vacio">Cargando…</p>
        ) : (
          <form className="form" onSubmit={guardar}>
            {error && <div className="error-banner">{error}</div>}
            <div className="campo">
              <label htmlFor="galpon">Galpón</label>
              <select id="galpon" value={galponId} onChange={(e) => setGalponId(e.target.value)}>
                <option value="">Elegí un galpón…</option>
                {galpones.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.nombre}
                  </option>
                ))}
              </select>
              <button type="button" className="btn-texto" onClick={crearGalponNuevo}>
                + Crear galpón nuevo
              </button>
            </div>
            <div className="campo">
              <label htmlFor="granjero">Granjero responsable</label>
              <select id="granjero" value={granjeroId} onChange={(e) => setGranjeroId(e.target.value)}>
                <option value="">Elegí un granjero…</option>
                {granjeros.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.nombre}
                  </option>
                ))}
              </select>
              {granjeros.length === 0 && (
                <p className="campo-ayuda" style={{ color: 'var(--rojo)' }}>
                  No hay usuarios con rol granjero registrados todavía.
                </p>
              )}
            </div>
            <button className="btn btn-primary" disabled={guardando}>
              {guardando ? 'Asignando…' : 'Asignar'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
