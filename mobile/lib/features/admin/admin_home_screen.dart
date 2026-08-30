import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';
import 'crianza_detail_screen.dart';
import 'nueva_crianza_form_screen.dart';

/// Punto de entrada del flujo del administrador: lista de crianzas, alta de
/// una nueva, y desde ahí se entra a galpones/alertas/cierre de cada una.
class AdminHomeScreen extends StatefulWidget {
  const AdminHomeScreen({super.key});

  @override
  State<AdminHomeScreen> createState() => _AdminHomeScreenState();
}

class _AdminHomeScreenState extends State<AdminHomeScreen> {
  late AdminApi _api;
  late Future<List<Crianza>> _crianzas;

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _crianzas = _api.crianzas();
  }

  Future<void> _refrescar() async {
    setState(() {
      _crianzas = _api.crianzas();
    });
    await _crianzas;
  }

  Future<void> _nuevaCrianza() async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => const NuevaCrianzaFormScreen()),
    );
    if (ok == true) await _refrescar();
  }

  @override
  Widget build(BuildContext context) {
    final usuario = context.watch<AuthService>().usuario!;
    return Scaffold(
      appBar: AppBar(
        title: Text('Hola, ${usuario.nombre}'),
        actions: [
          IconButton(icon: const Icon(Icons.logout), onPressed: () => context.read<AuthService>().logout()),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _nuevaCrianza,
        icon: const Icon(Icons.add),
        label: const Text('Crianza'),
      ),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<List<Crianza>>(
          future: _crianzas,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: const [
                  Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('No se pudo conectar con el servidor. Deslizá para reintentar.')),
                  ),
                ],
              );
            }
            final crianzas = [...snapshot.data ?? []]..sort((a, b) => b.numero.compareTo(a.numero));
            if (crianzas.isEmpty) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: const [
                  Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('Todavía no hay ninguna crianza cargada.')),
                  ),
                ],
              );
            }
            return ListView.builder(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(8),
              itemCount: crianzas.length,
              itemBuilder: (context, i) {
                final crianza = crianzas[i];
                return Card(
                  child: ListTile(
                    title: Text('Crianza #${crianza.numero}'),
                    subtitle: Text('Inicio: ${crianza.fechaInicio.day}/${crianza.fechaInicio.month}/${crianza.fechaInicio.year}'),
                    trailing: Chip(
                      label: Text(crianza.enCurso ? 'En curso' : 'Cerrada'),
                      backgroundColor: crianza.enCurso ? Colors.green.shade100 : Colors.grey.shade300,
                    ),
                    onTap: () async {
                      await Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => CrianzaDetailScreen(crianza: crianza)),
                      );
                      await _refrescar();
                    },
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
