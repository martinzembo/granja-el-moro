import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';

/// Pedido del docente de la cátedra: el panel de administrador pasó a ser
/// la versión web (ver web/, y CLAUDE.md sección Web) — la app móvil ya no
/// es la herramienta de trabajo del admin. Esta pantalla reemplaza al flujo
/// de admin que había acá antes (sigue en el repo, en
/// features/admin/admin_home_screen.dart y el resto de ese directorio, por
/// si hace falta retomarlo, pero ya no está enganchado desde app.dart).
class AdminEnWebScreen extends StatelessWidget {
  const AdminEnWebScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final usuario = context.watch<AuthService>().usuario!;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('💻', style: TextStyle(fontSize: 56)),
                const SizedBox(height: 16),
                Text(
                  'Hola, ${usuario.nombre}',
                  style: Theme.of(context).textTheme.titleLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                const Text(
                  'El panel de administrador ahora es la versión web — '
                  'abrilo desde una computadora para gestionar crianzas, '
                  'galpones, alertas y cierres.',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                FilledButton.icon(
                  onPressed: () => context.read<AuthService>().logout(),
                  icon: const Icon(Icons.logout),
                  label: const Text('Cerrar sesión'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
