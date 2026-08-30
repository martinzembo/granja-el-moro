import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';

/// Punto de entrada del flujo del administrador. Placeholder — acá van el
/// dashboard de galpones/crianzas, alertas y cierre, ver docs/plan.md
/// Semana 6-7. Pantallas completamente separadas de las del granjero.
class AdminHomeScreen extends StatelessWidget {
  const AdminHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final usuario = context.watch<AuthService>().usuario!;
    return Scaffold(
      appBar: AppBar(
        title: Text('Hola, ${usuario.nombre}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthService>().logout(),
          ),
        ],
      ),
      body: const Center(child: Text('Panel del administrador — próximamente')),
    );
  }
}
