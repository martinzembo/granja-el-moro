// Llamadas a la API que usa el panel de administrador. Espejo 1:1 de
// mobile/lib/features/admin/admin_api.dart — mismos endpoints, mismo
// criterio, para no tener dos superficies de API distintas documentadas
// en dos lugares. Formatea fechas como YYYY-MM-DD (lo que espera el
// backend, ver app/schemas/*.py).
export function formatoFecha(date) {
  return date.toISOString().slice(0, 10)
}

export class AdminApi {
  constructor(api) {
    this.api = api
  }

  crianzas() {
    return this.api.get('/crianzas')
  }

  crearCrianza({ numero, fechaInicio }) {
    return this.api.post('/crianzas', { numero, fecha_inicio: formatoFecha(fechaInicio) })
  }

  galpones() {
    return this.api.get('/galpones')
  }

  crearGalpon({ nombre, capacidadMaxima }) {
    return this.api.post('/galpones', { nombre, capacidad_maxima: capacidadMaxima })
  }

  granjeros() {
    return this.api.get('/usuarios?rol=granjero')
  }

  usuariosPendientes() {
    return this.api.get('/usuarios?activo=false')
  }

  activarUsuario(usuarioId) {
    return this.api.patch(`/usuarios/${usuarioId}/activar`)
  }

  galponesDeCrianza(crianzaId) {
    return this.api.get(`/crianzas/${crianzaId}/galpones`)
  }

  asignarGalpon({ crianzaId, galponId, granjeroId }) {
    return this.api.post(`/crianzas/${crianzaId}/galpones`, {
      galpon_id: galponId,
      granjero_id: granjeroId,
    })
  }

  ingresos(crianzaId, cgId) {
    return this.api.get(`/crianzas/${crianzaId}/galpones/${cgId}/ingresos`)
  }

  registrarIngreso({ crianzaId, cgId, fecha, origen, cantidad, muertosTransporte }) {
    return this.api.post(`/crianzas/${crianzaId}/galpones/${cgId}/ingresos`, {
      fecha: formatoFecha(fecha),
      origen,
      cantidad,
      muertos_transporte: muertosTransporte,
    })
  }

  retiros(crianzaId, cgId) {
    return this.api.get(`/crianzas/${crianzaId}/galpones/${cgId}/retiros`)
  }

  registrarRetiro({ crianzaId, cgId, fecha, remito, transportista, cantidadAves, pesoNeto }) {
    return this.api.post(`/crianzas/${crianzaId}/galpones/${cgId}/retiros`, {
      fecha: formatoFecha(fecha),
      remito,
      transportista,
      cantidad_aves: cantidadAves,
      peso_neto: pesoNeto,
    })
  }

  entregas(crianzaId) {
    return this.api.get(`/crianzas/${crianzaId}/entregas`)
  }

  registrarEntregaAlimento({ crianzaId, fecha, remito, kilos }) {
    return this.api.post(`/crianzas/${crianzaId}/entregas`, {
      tipo_insumo: 'alimento',
      fecha: formatoFecha(fecha),
      remito,
      kilos,
    })
  }

  async cierre(crianzaId) {
    try {
      return await this.api.get(`/crianzas/${crianzaId}/cierre`)
    } catch (e) {
      if (e.statusCode === 404) return null
      throw e
    }
  }

  cerrarCrianza({ crianzaId, fechaCierre, indiceTabla, premios, gasAjuste, ajuste }) {
    return this.api.post(`/crianzas/${crianzaId}/cierre`, {
      fecha_cierre: formatoFecha(fechaCierre),
      indice_tabla: indiceTabla,
      premios,
      gas_ajuste: gasAjuste,
      ajuste,
    })
  }

  resumen(crianzaId) {
    return this.api.get(`/crianzas/${crianzaId}/resumen`)
  }

  alertas(crianzaId, { resuelta } = {}) {
    const query = resuelta === undefined ? '' : `?resuelta=${resuelta}`
    return this.api.get(`/crianzas/${crianzaId}/alertas${query}`)
  }

  resolverAlerta(crianzaId, alertaId) {
    return this.api.patch(`/crianzas/${crianzaId}/alertas/${alertaId}/resolver`)
  }
}
