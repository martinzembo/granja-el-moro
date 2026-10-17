import { useNavigate } from 'react-router-dom'

/** Barra superior reutilizada en todas las pantallas del panel — título,
 * opcional botón de "volver" y acciones a la derecha. */
export default function AppBarPanel({ title, volver = false, actions = null }) {
  const navigate = useNavigate()
  return (
    <div className="appbar">
      <div className="appbar-left">
        {volver && (
          <button className="appbar-back" onClick={() => navigate(-1)} aria-label="Volver">
            ←
          </button>
        )}
        <h1>{title}</h1>
      </div>
      {actions && <div className="appbar-actions">{actions}</div>}
    </div>
  )
}
