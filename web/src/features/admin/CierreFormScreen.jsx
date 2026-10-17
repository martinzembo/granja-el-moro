import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

/** El cierre es irreversible (bloquea toda carga nueva para la crianza),
 * así que insiste en confirmación antes del POST — espejo de
 * mobile/lib/features/admin/cierre_form_screen.dart. indice_tabla/premios/
 * gas_ajuste/ajuste los provee la integradora, no los calcula el sistema. */
export default function CierreFormScreen() {
  const { crianzaId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [crianza, setCrianza] = useState(null)
  const [fechaCierre, setFechaCierre] = useState(() => new Date().toISOString().slice(0, 10))
  const [indiceTabla, setIndiceTabla] = useState('')
  const [premios, setPremios] = useState('0')
  const [gasAjuste, setGasAjuste] = useState('0')
  const [ajuste, setAjuste] = useState('0')
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState(null)
  const [resultado, setResultado] = useState(null)

  useEffect(() => {
    adminApi.crianzas().then((lista) => setCrianza(lista.find((c) => String(c.id) === crianzaId)))
  }, [crianzaId])

  function num(texto) {
    const n = Number(String(texto).replace(',', '.'))
    return Number.isNaN(n) ? 0 : n
  }

  const precioXPolloEstimado = num(indiceTabla) + num(premios) + num(gasAjuste) + num(ajuste)

  async function confirmarYCerrar(e) {
    e.preventDefault()
    if (indiceTabla === '') {
      setError('Ingresá el índice de tabla')
      return
    }
    const confirmado = window.confirm(
      `Se va a cerrar la Crianza #${crianza?.numero} con precio x pollo de $${precioXPolloEstimado.toFixed(2)}. ` +
        'Esta acción no se puede deshacer: después del cierre no se admite más carga de datos para esta crianza.',
    )
    if (!confirmado) return

    setError(null)
    setGuardando(true)
    try {
      const data = await adminApi.cerrarCrianza({
        crianzaId,
        fechaCierre: new Date(`${fechaCierre}T00:00:00`),
        indiceTabla: num(indiceTabla),
        premios: num(premios),
        gasAjuste: num(gasAjuste),
        ajuste: num(ajuste),
      })
      setResultado(data)
    } catch (err) {
      setError(err.message || 'No se pudo conectar con el servidor')
    } finally {
      setGuardando(false)
    }
  }

  if (resultado) {
    return (
      <div>
        <AppBarPanel title="Crianza cerrada" />
        <div className="page">
          <div className="card">
            <FilaResultado etiqueta="Aves entregadas" valor={resultado.total_aves_entregadas} />
            <FilaResultado etiqueta="Peso total" valor={`${Number(resultado.peso_total).toFixed(1)} kg`} />
            <FilaResultado etiqueta="IE promedio" valor={Number(resultado.ie_promedio).toFixed(2)} />
            <FilaResultado etiqueta="Precio x pollo" valor={`$${Number(resultado.precio_x_pollo).toFixed(2)}`} />
            <hr style={{ margin: '10px 0', border: 'none', borderTop: '1px solid var(--borde)' }} />
            <FilaResultado etiqueta="Monto total" valor={`$${Number(resultado.monto_total).toFixed(2)}`} destacado />
          </div>
          <button
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
            onClick={() => navigate(`/crianzas/${crianzaId}`, { replace: true })}
          >
            Listo
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <AppBarPanel title={`Cerrar Crianza #${crianza?.numero ?? ''}`} volver />
      <div className="page">
        <form className="form" onSubmit={confirmarYCerrar}>
          <div className="card" style={{ background: '#fff8e1' }}>
            Antes de cerrar, asegurate de haber cargado todos los retiros a faena y las entregas de
            alimento de esta crianza — después del cierre no se puede agregar más.
          </div>
          {error && <div className="error-banner">{error}</div>}
          <div className="campo">
            <label htmlFor="fechaCierre">Fecha de cierre</label>
            <input
              id="fechaCierre"
              type="date"
              value={fechaCierre}
              onChange={(e) => setFechaCierre(e.target.value)}
              required
            />
          </div>
          <p className="campo-ayuda" style={{ marginBottom: 16 }}>
            Estos cuatro valores los provee la integradora — se cargan tal cual, no los calcula el sistema.
          </p>
          <div className="campo">
            <label htmlFor="indiceTabla">Índice de tabla</label>
            <input
              id="indiceTabla"
              type="number"
              step="0.01"
              value={indiceTabla}
              onChange={(e) => setIndiceTabla(e.target.value)}
              required
            />
          </div>
          <div className="campo">
            <label htmlFor="premios">Premios</label>
            <input id="premios" type="number" step="0.01" value={premios} onChange={(e) => setPremios(e.target.value)} />
          </div>
          <div className="campo">
            <label htmlFor="gasAjuste">Ajuste por gas</label>
            <input
              id="gasAjuste"
              type="number"
              step="0.01"
              value={gasAjuste}
              onChange={(e) => setGasAjuste(e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="ajuste">Ajuste general</label>
            <input id="ajuste" type="number" step="0.01" value={ajuste} onChange={(e) => setAjuste(e.target.value)} />
          </div>
          <div className="card card-row">
            <span>Precio x pollo estimado</span>
            <strong style={{ fontSize: '1.2rem' }}>${precioXPolloEstimado.toFixed(2)}</strong>
          </div>
          <button className="btn btn-peligro" style={{ width: '100%', justifyContent: 'center' }} disabled={guardando}>
            {guardando ? 'Cerrando…' : 'Cerrar crianza'}
          </button>
        </form>
      </div>
    </div>
  )
}

function FilaResultado({ etiqueta, valor, destacado = false }) {
  return (
    <div className="card-row" style={{ padding: '4px 0', fontWeight: destacado ? 700 : 400 }}>
      <span>{etiqueta}</span>
      <span>{valor}</span>
    </div>
  )
}
