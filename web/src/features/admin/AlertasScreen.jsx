import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

const EMOJI = { mortandad: '💀', agua: '💧', gas: '🔥', electricidad: '⚡' }

export default function AlertasScreen() {
  const { crianzaId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)

  const [alertas, setAlertas] = useState(null)
  const [error, setError] = useState(false)
  const [resolviendo, setResolviendo] = useState(new Set())

  function cargar() {
    setError(false)
    adminApi
      .alertas(crianzaId)
      .then(setAlertas)
      .catch(() => setError(true))
  }

  useEffect(cargar, [crianzaId])

  async function resolver(alerta) {
    setResolviendo((s) => new Set(s).add(alerta.id))
    try {
      await adminApi.resolverAlerta(crianzaId, alerta.id)
      cargar()
    } catch {
      // se queda como estaba — el usuario puede reintentar
    } finally {
      setResolviendo((s) => {
        const copia = new Set(s)
        copia.delete(alerta.id)
        return copia
      })
    }
  }

  const ordenadas = alertas
    ? [...alertas].sort((a, b) => {
        if (a.resuelta !== b.resuelta) return a.resuelta ? 1 : -1
        return new Date(b.fecha) - new Date(a.fecha)
      })
    : null

  return (
    <div>
      <AppBarPanel title="Alertas" volver />
      <div className="page">
        {error && <p className="vacio">No se pudieron cargar las alertas.</p>}
        {!error && ordenadas === null && <p className="vacio">Cargando…</p>}
        {ordenadas?.length === 0 && <p className="vacio">No hay alertas para esta crianza.</p>}
        {ordenadas?.map((a) => (
          <div key={a.id} className={`card ${a.resuelta ? '' : 'alerta'}`}>
            <div className="card-row">
              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <span className="emoji" style={{ fontSize: '1.6rem' }}>
                  {EMOJI[a.tipo] ?? '🔔'}
                </span>
                <div>
                  <div>{a.descripcion}</div>
                  <div className="subtitulo">{formatoFechaHora(a.fecha)}</div>
                </div>
              </div>
              {a.resuelta ? (
                <span style={{ color: 'var(--verde)', fontSize: '1.3rem' }}>✓</span>
              ) : resolviendo.has(a.id) ? (
                <span className="subtitulo">Resolviendo…</span>
              ) : (
                <button className="btn-texto" onClick={() => resolver(a)}>
                  Resolver
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatoFechaHora(iso) {
  const d = new Date(iso)
  const dia = d.getDate()
  const mes = d.getMonth() + 1
  const anio = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${dia}/${mes}/${anio} ${hh}:${mm}`
}
