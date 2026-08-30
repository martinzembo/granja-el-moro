import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';
import 'nueva_crianza_form_screen.dart' show formatoFechaLegible;
import 'registrar_ingreso_form_screen.dart';

class GalponDetailScreen extends StatefulWidget {
  const GalponDetailScreen({super.key, required this.crianzaId, required this.cg});

  final int crianzaId;
  final CrianzaGalpon cg;

  @override
  State<GalponDetailScreen> createState() => _GalponDetailScreenState();
}

class _GalponDetailScreenState extends State<GalponDetailScreen> {
  late AdminApi _api;
  late Future<List<IngresoAves>> _ingresos;

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _ingresos = _api.ingresos(widget.crianzaId, widget.cg.id);
  }

  Future<void> _refrescar() async {
    setState(() => _ingresos = _api.ingresos(widget.crianzaId, widget.cg.id));
    await _ingresos;
  }

  Future<void> _agregarIngreso() async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => RegistrarIngresoFormScreen(crianzaId: widget.crianzaId, cgId: widget.cg.id),
      ),
    );
    if (ok == true) await _refrescar();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.cg.galponNombre)),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _agregarIngreso,
        icon: const Icon(Icons.add),
        label: const Text('Ingreso'),
      ),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<List<IngresoAves>>(
          future: _ingresos,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            final ingresos = snapshot.data ?? [];
            final totalNeto = ingresos.fold<int>(0, (acc, i) => acc + i.cantidadNeta);
            return ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              children: [
                Card(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text('Granjero: ${widget.cg.granjeroNombre}'),
                    subtitle: Text('Total de aves netas ingresadas: $totalNeto'),
                  ),
                ),
                const SizedBox(height: 16),
                Text('Ingresos de pollitos BB', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                if (ingresos.isEmpty) const Text('Todavía no se cargó ningún ingreso.'),
                for (final ingreso in ingresos)
                  Card(
                    child: ListTile(
                      title: Text('${ingreso.origen} — ${formatoFechaLegible(ingreso.fecha)}'),
                      subtitle: Text(
                        'Despachadas: ${ingreso.cantidad} · Muertas en transporte: ${ingreso.muertosTransporte} · Netas: ${ingreso.cantidadNeta}',
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }
}
