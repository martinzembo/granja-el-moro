import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/auth_service.dart';
import 'core/usuario.dart';
import 'features/admin/admin_home_screen.dart';
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

/// Decide qué pantalla mostrar según el estado de sesión. Una vez logueado,
/// el rol define un flujo de navegación completo y separado — el granjero
/// nunca ve pantallas de administrador, ni viceversa (ver CLAUDE.md, sección
/// Mobile).
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
            ? const AdminHomeScreen()
            : const GranjeroHomeScreen();
    }
  }
}
