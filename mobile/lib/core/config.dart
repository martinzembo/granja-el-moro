/// URL base de la API. En desarrollo, con el celular conectado por USB,
/// `adb reverse tcp:8000 tcp:8000` hace que "localhost:8000" en el celular
/// apunte al backend corriendo en la PC — ver CLAUDE.md sección Mobile.
const String apiBaseUrl = 'http://localhost:8000';
