/// URL base de la API. Por defecto "localhost:8000" para desarrollo: con
/// el celular conectado por USB, `adb reverse tcp:8000 tcp:8000` hace que
/// eso apunte al backend corriendo en la PC (ver CLAUDE.md sección
/// Mobile). Para el build real que usa el granjero (backend corriendo en
/// la notebook de la granja, no en una PC de desarrollo) se pisa en
/// tiempo de compilación, sin tocar este archivo:
///
///   flutter build apk --release --dart-define=API_BASE_URL=http://IP-DE-LA-NOTEBOOK:8000
const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);
