import { apiBaseUrl } from './config'

/** Espejo de ApiException en mobile/lib/core/api_client.dart: el mensaje
 * ya viene armado en español desde el backend (FastAPI manda
 * {"detail": "..."} en los errores), así que se puede mostrar directo. */
export class ApiException extends Error {
  constructor(statusCode, message) {
    super(message)
    this.statusCode = statusCode
  }
}

async function procesar(resp) {
  if (resp.status === 204) return null
  const texto = await resp.text()
  const data = texto ? JSON.parse(texto) : null

  if (resp.ok) return data

  let mensaje = `Error inesperado (${resp.status})`
  const detail = data?.detail
  if (typeof detail === 'string') {
    // Errores "de negocio" (HTTPException), ya en español.
    mensaje = detail
  } else if (Array.isArray(detail) && detail.length > 0) {
    // Errores de validación de Pydantic: lista de objetos con "msg" (en
    // inglés, sin traducir — casos que ya deberían frenarse en el form).
    mensaje = detail[0]?.msg ?? JSON.stringify(detail)
  } else if (detail) {
    mensaje = String(detail)
  }
  throw new ApiException(resp.status, mensaje)
}

function headers(token, auth) {
  const h = { 'Content-Type': 'application/json' }
  if (auth && token) h['Authorization'] = `Bearer ${token}`
  return h
}

/** Wrapper fino sobre fetch, mismo criterio que ApiClient en mobile. */
export class ApiClient {
  constructor(token) {
    this.token = token
  }

  async get(path, { auth = true } = {}) {
    const resp = await fetch(`${apiBaseUrl}${path}`, { headers: headers(this.token, auth) })
    return procesar(resp)
  }

  async post(path, body, { auth = true } = {}) {
    const resp = await fetch(`${apiBaseUrl}${path}`, {
      method: 'POST',
      headers: headers(this.token, auth),
      body: JSON.stringify(body),
    })
    return procesar(resp)
  }

  async patch(path, body, { auth = true } = {}) {
    const resp = await fetch(`${apiBaseUrl}${path}`, {
      method: 'PATCH',
      headers: headers(this.token, auth),
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
    return procesar(resp)
  }
}
