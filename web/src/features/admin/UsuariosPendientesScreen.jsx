import { useEffect, useState } from 'react'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

/** Cuentas autoregistradas sin habilitar — pedido del docente de la
 * cátedra, ver app/api/routers/auth.py `register`. Espejo de
 * mobile/lib/features/admin/usuarios_pendientes_screen.dart. */
export default function UsuariosPendientesScreen() {
  const { api } = useAuth()
  const adminApi = new AdminApi(api)

  const [pendientes, setPendientes] = useState(null)
  const [error, setError] = useState(false)
  const [activando, setActivando] = useState(new Set())
  const [mensaje, setMensaje] = useState(null)

  function cargar() {
    setError(false)
    adminApi
      .usuariosPendientes()
      .then(setPendientes)
      .catch(() => setError(true))
  }

  useEffect(cargar, [])

  async function activar(usuario) {
    setActivando((s) => new Set(s).add(usuario.id))
    setMensaje(null)
    try {
      await adminApi.activarUsuario(usuario.id)
      cargar()
      setMensaje(`${usuario.nombre} ya puede ingresar.`)
    } catch (err) {
      setMensaje(err.message || 'No se pudo conectar con el servidor')
    } finally {
      setActivando((s) => {
        const copia = new Set(s)
        copia.delete(usuario.id)
        return copia
      })
    }
  }

  return (
    <div>
      <AppBarPanel title="Cuentas pendientes" volver />
      <div className="page">
        {mensaje && <div className="error-banner" style={{ background: 'var(--verde-claro)', borderColor: 'var(--verde)', color: 'var(--verde)' }}>{mensaje}</div>}
        {error && <p className="vacio">No se pudieron cargar.</p>}
        {!error && pendientes === null && <p className="vacio">Cargando…</p>}
        {pendientes?.length === 0 && <p className="vacio">No hay cuentas esperando aprobación.</p>}
        {pendientes?.map((u) => (
          <div key={u.id} className="card alerta card-row">
            <div>
              <div className="titulo">👤 {u.nombre}</div>
              <div className="subtitulo">{u.email}</div>
            </div>
            {activando.has(u.id) ? (
              <span className="subtitulo">Activando…</span>
            ) : (
              <button className="btn btn-primary" onClick={() => activar(u)}>
                Activar
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
