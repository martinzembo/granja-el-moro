import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'
import { formatoFechaLegible } from '../../core/dateUtils'

export default function CrianzaDetailScreen() {
  const { crianzaId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [crianza, setCrianza] = useState(null)
  const [galpones, setGalpones] = useState(null)
  const [alertasSinResolver, setAlertasSinResolver] = useState(null)
  const [entregas, setEntregas] = useState(null)
  // undefined = todavía no se pidió / está cargando; null = confirmado
  // que no hay liquidación cargada; objeto = la liquidación.
  const [cierre, setCierre] = useState(undefined)

  function cargar() {
    adminApi.crianzas().then((data) => setCrianza(data.find((c) => String(c.id) === crianzaId)))
    adminApi.galponesDeCrianza(crianzaId).then(setGalpones)
    adminApi.alertas(crianzaId, { resuelta: false }).then(setAlertasSinResolver)
    adminApi.entregas(crianzaId).then(setEntregas)
  }

  useEffect(cargar, [crianzaId])

  useEffect(() => {
    if (crianza && crianza.estado !== 'en_curso') {
      adminApi.cierre(crianzaId).then(setCierre)
    }
  }, [crianza, crianzaId])

  if (!crianza) {
    return (
      <div>
        <AppBarPanel title="Crianza" volver />
        <div className="page">
          <p className="vacio">Cargando…</p>
        </div>
      </div>
    )
  }

  const enCurso = crianza.estado === 'en_curso'

  return (
    <div>
      <AppBarPanel
        title={`Crianza #${crianza.numero}`}
        volver
        actions={<span className={`chip ${enCurso ? '' : 'gris'}`}>{enCurso ? 'En curso' : 'Cerrada'}</span>}
      />
      <div className="page">
        {!enCurso && (
          <TarjetaLiquidacion cierre={cierre} />
        )}

        <div
          className="card clickable card-row"
          onClick={() => navigate(`/crianzas/${crianzaId}/resumen`)}
        >
          <div>
            <div className="titulo">📊 Resumen</div>
            <div className="subtitulo">Edad, mortandad, agua, alimento y gas/electricidad al día</div>
          </div>
          <span>›</span>
        </div>

        <div
          className={`card clickable card-row ${alertasSinResolver?.length ? 'alerta' : ''}`}
          onClick={() => navigate(`/crianzas/${crianzaId}/alertas`)}
        >
          <div className="titulo">
            🔔 {alertasSinResolver === null ? 'Alertas' : `${alertasSinResolver.length} alerta(s) sin resolver`}
          </div>
          <span>›</span>
        </div>

        <div className="seccion-titulo">
          <h2>Galpones</h2>
          {enCurso && (
            <button className="btn-texto" onClick={() => navigate(`/crianzas/${crianzaId}/asignar-galpon`)}>
              + Asignar
            </button>
          )}
        </div>
        {galpones === null && <p className="vacio">Cargando…</p>}
        {galpones?.length === 0 && <p className="vacio">Todavía no hay galpones asignados a esta crianza.</p>}
        {galpones?.map((cg) => (
          <div
            key={cg.id}
            className="card clickable card-row"
            onClick={() => navigate(`/crianzas/${crianzaId}/galpones/${cg.id}`)}
          >
            <div>
              <div className="titulo">{cg.galpon_nombre}</div>
              <div className="subtitulo">Granjero: {cg.granjero_nombre}</div>
            </div>
            <span>›</span>
          </div>
        ))}

        <div className="seccion-titulo">
          <h2>Entregas de alimento</h2>
          {enCurso && (
            <button className="btn-texto" onClick={() => navigate(`/crianzas/${crianzaId}/entregas/nueva`)}>
              + Entrega
            </button>
          )}
        </div>
        {entregas === null && <p className="vacio">Cargando…</p>}
        {entregas?.length === 0 && <p className="vacio">Todavía no se cargó ninguna entrega.</p>}
        {entregas?.map((e, i) => (
          <div key={i} className="card">
            <div className="titulo">{Number(e.kilos).toFixed(0)} kg — remito {e.remito}</div>
            <div className="subtitulo">{formatoFechaLegible(e.fecha)}</div>
          </div>
        ))}

        {enCurso && (
          <button
            className="btn btn-peligro"
            style={{ width: '100%', justifyContent: 'center', marginTop: 24 }}
            onClick={() => navigate(`/crianzas/${crianzaId}/cierre`)}
          >
            🔒 Cerrar crianza
          </button>
        )}
      </div>
    </div>
  )
}

function TarjetaLiquidacion({ cierre }) {
  if (cierre === null) {
    return (
      <div className="card">
        <div className="titulo">Crianza cerrada sin liquidación registrada</div>
      </div>
    )
  }
  if (cierre === undefined) {
    return (
      <div className="card">
        <p className="vacio">Cargando liquidación…</p>
      </div>
    )
  }
  return (
    <div className="card" style={{ background: 'var(--verde-claro)' }}>
      <div className="titulo" style={{ marginBottom: 8 }}>
        Liquidación
      </div>
      <p style={{ margin: '4px 0' }}>Aves entregadas: {cierre.total_aves_entregadas}</p>
      <p style={{ margin: '4px 0' }}>Peso total: {Number(cierre.peso_total).toFixed(1)} kg</p>
      <p style={{ margin: '4px 0' }}>IE promedio: {Number(cierre.ie_promedio).toFixed(2)}</p>
      <p style={{ margin: '4px 0' }}>Precio x pollo: ${Number(cierre.precio_x_pollo).toFixed(2)}</p>
      <p style={{ margin: '8px 0 0', fontWeight: 700 }}>
        Monto total: ${Number(cierre.monto_total).toFixed(2)}
      </p>
    </div>
  )
}
