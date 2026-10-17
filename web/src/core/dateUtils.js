/** "YYYY-MM-DD" (o un Date/ISO) -> "DD/MM/AAAA", para mostrar. Evita
 * Date.parse en el string "YYYY-MM-DD" a secas porque eso lo interpreta
 * como UTC y puede correr un día según el huso horario del navegador. */
export function formatoFechaLegible(fecha) {
  const str = typeof fecha === 'string' ? fecha : fecha.toISOString()
  const [anio, mes, dia] = str.slice(0, 10).split('-')
  return `${Number(dia)}/${Number(mes)}/${anio}`
}
