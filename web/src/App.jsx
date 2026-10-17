import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './core/AuthContext'
import LoginScreen from './features/auth/LoginScreen'
import CrianzasListScreen from './features/admin/CrianzasListScreen'
import NuevaCrianzaFormScreen from './features/admin/NuevaCrianzaFormScreen'
import CrianzaDetailScreen from './features/admin/CrianzaDetailScreen'
import AsignarGalponFormScreen from './features/admin/AsignarGalponFormScreen'
import GalponDetailScreen from './features/admin/GalponDetailScreen'
import RegistrarIngresoFormScreen from './features/admin/RegistrarIngresoFormScreen'
import RegistrarRetiroFormScreen from './features/admin/RegistrarRetiroFormScreen'
import RegistrarEntregaFormScreen from './features/admin/RegistrarEntregaFormScreen'
import ResumenScreen from './features/admin/ResumenScreen'
import AlertasScreen from './features/admin/AlertasScreen'
import CierreFormScreen from './features/admin/CierreFormScreen'
import UsuariosPendientesScreen from './features/admin/UsuariosPendientesScreen'

/** Rutea según sesión — espejo de _Portal en mobile/lib/app.dart, pero acá
 * solo hay un rol posible (admin): el panel web reemplaza al admin móvil
 * (ver CLAUDE.md, sección Web), el flujo del granjero sigue siendo
 * exclusivo de la app. */
export default function App() {
  const { estado } = useAuth()

  if (estado === 'cargando') {
    return (
      <div className="centro">
        <p>Cargando…</p>
      </div>
    )
  }

  if (estado === 'noAutenticado') {
    return <LoginScreen />
  }

  return (
    <Routes>
      <Route path="/" element={<CrianzasListScreen />} />
      <Route path="/crianzas/nueva" element={<NuevaCrianzaFormScreen />} />
      <Route path="/crianzas/:crianzaId" element={<CrianzaDetailScreen />} />
      <Route path="/crianzas/:crianzaId/resumen" element={<ResumenScreen />} />
      <Route path="/crianzas/:crianzaId/alertas" element={<AlertasScreen />} />
      <Route path="/crianzas/:crianzaId/cierre" element={<CierreFormScreen />} />
      <Route path="/crianzas/:crianzaId/asignar-galpon" element={<AsignarGalponFormScreen />} />
      <Route path="/crianzas/:crianzaId/entregas/nueva" element={<RegistrarEntregaFormScreen />} />
      <Route path="/crianzas/:crianzaId/galpones/:cgId" element={<GalponDetailScreen />} />
      <Route path="/crianzas/:crianzaId/galpones/:cgId/ingresos/nuevo" element={<RegistrarIngresoFormScreen />} />
      <Route path="/crianzas/:crianzaId/galpones/:cgId/retiros/nuevo" element={<RegistrarRetiroFormScreen />} />
      <Route path="/usuarios-pendientes" element={<UsuariosPendientesScreen />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
