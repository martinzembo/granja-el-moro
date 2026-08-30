/// Formatea a 'yyyy-MM-dd', el formato que espera el backend (Pydantic `date`).
String formatoFecha(DateTime d) {
  final anio = d.year.toString().padLeft(4, '0');
  final mes = d.month.toString().padLeft(2, '0');
  final dia = d.day.toString().padLeft(2, '0');
  return '$anio-$mes-$dia';
}

/// true si dos DateTime caen en el mismo día calendario (ignora la hora).
bool esMismoDia(DateTime a, DateTime b) {
  return a.year == b.year && a.month == b.month && a.day == b.day;
}
