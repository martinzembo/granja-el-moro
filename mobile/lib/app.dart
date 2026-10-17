import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/auth_service.dart';
import 'core/usuario.dart';
import 'features/admin/admin_en_web_screen.dart';
import 'features/auth/login_screen.dart';
import 'features/granjero/granjero_home_screen.dart';

class GranjaElMoroApp extends StatelessWidget {
  const GranjaElMoroApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthService()..intentarSesionGuardada(),
      child: MaterialApp(
        title: 'Granja El Moro',
        theme: ThemeData(colorSchemeSeed: Colors.green, useMaterial3: true),
        home: const _Portal(),
      ),
    );
  }
}

/// Decide qué pantalla mostrar según el estado de sesión. El granjero tiene
/// su flujo completo acá; el admin ya no — el panel de administrador pasó a
/// ser la versión web (pedido del docente de la cátedra, ver CLAUDE.md
/// sección Web), así que un admin que entra por la app solo ve un aviso
/// (AdminEnWebScreen) en vez del flujo completo que tenía antes.
class _Portal extends StatelessWidget {
  const _Portal();

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    switch (auth.estado) {
      case EstadoAuth.cargando:
        return const Scaffold(body: Center(child: CircularProgressIndicator()));
      case EstadoAuth.noAutenticado:
        return const LoginScreen();
      case EstadoAuth.autenticado:
        return auth.usuario!.rol == RolUsuario.admin
            ? const AdminEnWebScreen()
            : const GranjeroHomeScreen();
    }
  }
}
