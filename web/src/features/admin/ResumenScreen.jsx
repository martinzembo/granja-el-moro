import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../../core/AuthContext'
import AppBarPanel from '../../core/AppBarPanel'
import { AdminApi } from './adminApi'

/** "Los números reales, como en el Excel" — espejo de
 * mobile/lib/features/admin/resumen_screen.dart. A propósito no muestra
 * índice de crecimiento/conversión/IE: necesitan peso, que no se conoce
 * hasta el retiro a faena (eso está en la liquidación final). */
export default function ResumenScreen() {
  const { crianzaId } = useParams()
  const { api } = useAuth()
  const adminApi = new AdminApi(api)

  const [resumen, setResumen] = useState(null)
  const [crianza, setCrianza] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    adminApi.crianzas().then((lista) => setCrianza(lista.find((c) => String(c.id) === crianzaId)))
    adminApi
      .resumen(crianzaId)
      .then(setResumen)
      .catch(() => setError(true))
  }, [crianzaId])

  return (
    <div>
      <AppBarPanel title={`Resumen — Crianza #${crianza?.numero ?? ''}`} volver />
      <div className="page">
        {error && <p className="vacio">No se pudo cargar el resumen.</p>}
        {!error && !resumen && <p className="vacio">Cargando…</p>}
        {resumen && (
          <>
            <TarjetaGranja resumen={resumen} />
            {resumen.galpones.length === 0 && (
              <p className="vacio">Todavía no hay galpones asignados a esta crianza.</p>
            )}
            {resumen.galpones.map((g) => (
              <TarjetaGalpon key={g.crianza_galpon_id} galpon={g} />
            ))}
          </>
        )}
      </div>
    </div>
  )
}

function TarjetaGranja({ resumen }) {
  const { granja } = resumen
  return (
    <div className="card" style={{ background: 'var(--verde-claro)' }}>
      <div className="titulo" style={{ marginBottom: 10 }}>
        Granja
      </div>
      <Fila emoji="🌾" texto={`Alimento entregado: ${Number(resumen.alimento_entregado_kg).toFixed(0)} kg`} />
      {granja.fecha === null ? (
        <p style={{ marginTop: 8 }}>Todavía no se cargó ninguna lectura de gas/electricidad.</p>
      ) : (
        <>
          <FilaHoyPromedio emoji="🔥" etiqueta="Gas" hoy={granja.consumo_gas_hoy} promedio={granja.promedio_gas_3_dias} unidad="m³" />
          <FilaHoyPromedio
            emoji="⚡"
            etiqueta="Electricidad activa"
            hoy={granja.consumo_electricidad_activa_hoy}
            promedio={granja.promedio_electricidad_activa_3_dias}
            unidad="kWh"
          />
          <FilaHoyPromedio
            emoji="⚡"
            etiqueta="Electricidad reactiva"
            hoy={granja.consumo_electricidad_reactiva_hoy}
            promedio={granja.promedio_electricidad_reactiva_3_dias}
            unidad="kvarh"
          />
          <p className="subtitulo" style={{ marginTop: 6 }}>
            Última lectura: {formatoFechaCorta(granja.fecha)}
          </p>
        </>
      )}
    </div>
  )
}

function TarjetaGalpon({ galpon: g }) {
  const mortandadPct = g.mortandad_pct * 100
  const mortandadEsperadaPct = g.mortandad_esperada_pct === null ? null : g.mortandad_esperada_pct * 100
  const sobreMortandad = mortandadEsperadaPct !== null && mortandadPct > mortandadEsperadaPct * 1.5

  return (
    <div className="card">
      <div className="card-row">
        <div className="titulo">{g.galpon_nombre}</div>
        <div className="subtitulo">{g.edad_dias === null ? 'Sin ingreso cargado' : `Día ${g.edad_dias} de vida`}</div>
      </div>
      <div className="subtitulo">Granjero: {g.granjero_nombre}</div>
      <hr style={{ margin: '10px 0', border: 'none', borderTop: '1px solid var(--borde)' }} />
      <Fila emoji="🐔" texto={`Aves vivas: ${g.aves_vivas} / ${g.aves_netas} netas`} />
      <p style={{ margin: '4px 0', color: sobreMortandad ? 'var(--rojo)' : undefined, fontWeight: sobreMortandad ? 700 : 400 }}>
        💀{' '}
        {mortandadEsperadaPct === null
          ? `Mortandad acumulada: ${g.mortandad_acumulada} (${mortandadPct.toFixed(2)}%)`
          : `Mortandad acumulada: ${g.mortandad_acumulada} (${mortandadPct.toFixed(2)}%) — esperado ~${mortandadEsperadaPct.toFixed(2)}%`}
      </p>
      <Fila emoji="💧" texto={`Agua acumulada: ${Number(g.agua_acumulada_litros).toFixed(0)} L`} />
      {g.agua_litros_pollo_hoy !== null && (
        <p className="subtitulo" style={{ marginLeft: 26 }}>
          {g.agua_esperada_litros_pollo_hoy === null
            ? `Última lectura: ${g.agua_litros_pollo_hoy.toFixed(3)} L/ave`
            : `Última lectura: ${g.agua_litros_pollo_hoy.toFixed(3)} L/ave — esperado ~${g.agua_esperada_litros_pollo_hoy.toFixed(3)} L/ave`}
        </p>
      )}
    </div>
  )
}

function Fila({ emoji, texto }) {
  return (
    <p style={{ margin: '4px 0' }}>
      <span className="emoji">{emoji}</span> {texto}
    </p>
  )
}

function FilaHoyPromedio({ emoji, etiqueta, hoy, promedio, unidad }) {
  let texto
  if (hoy === null) texto = `${etiqueta}: sin datos suficientes todavía`
  else if (promedio === null) texto = `${etiqueta}: ${hoy.toFixed(1)} ${unidad} hoy`
  else texto = `${etiqueta}: ${hoy.toFixed(1)} ${unidad} hoy — promedio 3 días: ${promedio.toFixed(1)} ${unidad}`
  return <Fila emoji={emoji} texto={texto} />
}

function formatoFechaCorta(fecha) {
  const [anio, mes, dia] = fecha.split('-')
  return `${Number(dia)}/${Number(mes)}/${anio}`
}
