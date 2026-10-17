import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'
import { formatoFechaLegible } from '../../core/dateUtils'

export default function CrianzasListScreen() {
  const { api, usuario, logout } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [crianzas, setCrianzas] = useState(null)
  const [pendientes, setPendientes] = useState(0)
  const [error, setError] = useState(false)

  function cargar() {
    setError(false)
    adminApi
      .crianzas()
      .then((data) => setCrianzas([...data].sort((a, b) => b.numero - a.numero)))
      .catch(() => setError(true))
    adminApi
      .usuariosPendientes()
      .then((data) => setPendientes(data.length))
      .catch(() => {})
  }

  useEffect(cargar, [])

  return (
    <div>
      <AppBarPanel
        title={`Hola, ${usuario.nombre}`}
        actions={
          <>
            <button
              className="appbar-back"
              title="Cuentas pendientes de aprobar"
              onClick={() => navigate('/usuarios-pendientes')}
              style={{ position: 'relative' }}
            >
              👤
              {pendientes > 0 && (
                <span className="badge" style={{ position: 'absolute', top: -2, right: -2 }}>
                  {pendientes}
                </span>
              )}
            </button>
            <button className="appbar-back" title="Cerrar sesión" onClick={logout}>
              ⎋
            </button>
          </>
        }
      />
      <div className="page">
        <div className="seccion-titulo">
          <h2>Crianzas</h2>
          <button className="btn btn-primary" onClick={() => navigate('/crianzas/nueva')}>
            + Crianza
          </button>
        </div>

        {error && <p className="vacio">No se pudo conectar con el servidor.</p>}
        {!error && crianzas === null && <p className="vacio">Cargando…</p>}
        {!error && crianzas?.length === 0 && <p className="vacio">Todavía no hay ninguna crianza cargada.</p>}

        {crianzas?.map((c) => (
          <div key={c.id} className="card clickable" onClick={() => navigate(`/crianzas/${c.id}`)}>
            <div className="card-row">
              <div>
                <div className="titulo">Crianza #{c.numero}</div>
                <div className="subtitulo">Inicio: {formatoFechaLegible(c.fecha_inicio)}</div>
              </div>
              <span className={`chip ${c.estado === 'en_curso' ? '' : 'gris'}`}>
                {c.estado === 'en_curso' ? 'En curso' : 'Cerrada'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
