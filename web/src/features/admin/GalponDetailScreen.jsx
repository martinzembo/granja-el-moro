import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'
import { formatoFechaLegible } from '../../core/dateUtils'

export default function GalponDetailScreen() {
  const { crianzaId, cgId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)
  const navigate = useNavigate()

  const [cg, setCg] = useState(null)
  const [enCurso, setEnCurso] = useState(true)
  const [ingresos, setIngresos] = useState(null)
  const [retiros, setRetiros] = useState(null)

  function cargar() {
    adminApi.galponesDeCrianza(crianzaId).then((lista) => setCg(lista.find((x) => String(x.id) === cgId)))
    adminApi.crianzas().then((lista) => {
      const c = lista.find((x) => String(x.id) === crianzaId)
      setEnCurso(c ? c.estado === 'en_curso' : true)
    })
    adminApi.ingresos(crianzaId, cgId).then(setIngresos)
    adminApi.retiros(crianzaId, cgId).then(setRetiros)
  }

  useEffect(cargar, [crianzaId, cgId])

  const totalNeto = ingresos?.reduce((acc, i) => acc + i.cantidad_neta, 0) ?? 0

  return (
    <div>
      <AppBarPanel title={cg?.galpon_nombre ?? 'Galpón'} volver />
      <div className="page">
        {cg && (
          <div className="card" style={{ background: '#eeeee4' }}>
            <div className="titulo">Granjero: {cg.granjero_nombre}</div>
            <div className="subtitulo">Total de aves netas ingresadas: {totalNeto}</div>
          </div>
        )}

        <div className="seccion-titulo">
          <h2>Ingresos de pollitos BB</h2>
          {enCurso && (
            <button className="btn-texto" onClick={() => navigate(`/crianzas/${crianzaId}/galpones/${cgId}/ingresos/nuevo`)}>
              + Ingreso
            </button>
          )}
        </div>
        {ingresos === null && <p className="vacio">Cargando…</p>}
        {ingresos?.length === 0 && <p className="vacio">Todavía no se cargó ningún ingreso.</p>}
        {ingresos?.map((ing, i) => (
          <div key={i} className="card">
            <div className="titulo">
              {ing.origen} — {formatoFechaLegible(ing.fecha)}
            </div>
            <div className="subtitulo">
              Despachadas: {ing.cantidad} · Muertas en transporte: {ing.muertos_transporte} · Netas:{' '}
              {ing.cantidad_neta}
            </div>
          </div>
        ))}

        <div className="seccion-titulo">
          <h2>Retiros a faena</h2>
          {enCurso && (
            <button className="btn-texto" onClick={() => navigate(`/crianzas/${crianzaId}/galpones/${cgId}/retiros/nuevo`)}>
              + Retiro
            </button>
          )}
        </div>
        {retiros === null && <p className="vacio">Cargando…</p>}
        {retiros?.length === 0 && <p className="vacio">Todavía no se cargó ningún retiro.</p>}
        {retiros?.map((r, i) => (
          <div key={i} className="card">
            <div className="titulo">
              {r.transportista} — {formatoFechaLegible(r.fecha)}
            </div>
            <div className="subtitulo">
              Remito {r.remito} · {r.cantidad_aves} aves · {Number(r.peso_neto).toFixed(1)} kg
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
