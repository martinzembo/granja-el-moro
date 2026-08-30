import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';
import 'nueva_crianza_form_screen.dart' show formatoFechaLegible;
import 'registrar_ingreso_form_screen.dart';
import 'registrar_retiro_form_screen.dart';

class GalponDetailScreen extends StatefulWidget {
  const GalponDetailScreen({super.key, required this.crianzaId, required this.cg, required this.crianzaEnCurso});

  final int crianzaId;
  final CrianzaGalpon cg;

  /// Si la crianza ya está cerrada, no se muestran acciones de carga
  /// (el backend las rechazaría igual, esto solo evita el viaje al server).
  final bool crianzaEnCurso;

  @override
  State<GalponDetailScreen> createState() => _GalponDetailScreenState();
}

class _GalponDetailScreenState extends State<GalponDetailScreen> {
  late AdminApi _api;
  late Future<List<IngresoAves>> _ingresos;
  late Future<List<RetiroCamion>> _retiros;

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _cargar();
  }

  void _cargar() {
    _ingresos = _api.ingresos(widget.crianzaId, widget.cg.id);
    _retiros = _api.retiros(widget.crianzaId, widget.cg.id);
  }

  Future<void> _refrescar() async {
    setState(_cargar);
    await Future.wait([_ingresos, _retiros]);
  }

  Future<void> _agregarIngreso() async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => RegistrarIngresoFormScreen(crianzaId: widget.crianzaId, cgId: widget.cg.id),
      ),
    );
    if (ok == true) await _refrescar();
  }

  Future<void> _agregarRetiro() async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => RegistrarRetiroFormScreen(crianzaId: widget.crianzaId, cgId: widget.cg.id),
      ),
    );
    if (ok == true) await _refrescar();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.cg.galponNombre)),
      floatingActionButton: !widget.crianzaEnCurso
          ? null
          : Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                FloatingActionButton.extended(
                  heroTag: 'ingreso',
                  onPressed: _agregarIngreso,
                  icon: const Icon(Icons.add),
                  label: const Text('Ingreso'),
                ),
                const SizedBox(width: 12),
                FloatingActionButton.extended(
                  heroTag: 'retiro',
                  onPressed: _agregarRetiro,
                  icon: const Icon(Icons.local_shipping),
                  label: const Text('Retiro'),
                ),
              ],
            ),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<List<IngresoAves>>(
          future: _ingresos,
          builder: (context, snapshotIngresos) {
            if (snapshotIngresos.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            final ingresos = snapshotIngresos.data ?? [];
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
                const SizedBox(height: 24),
                Text('Retiros a faena', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                FutureBuilder<List<RetiroCamion>>(
                  future: _retiros,
                  builder: (context, snapshotRetiros) {
                    if (snapshotRetiros.connectionState != ConnectionState.done) {
                      return const Center(child: CircularProgressIndicator());
                    }
                    final retiros = snapshotRetiros.data ?? [];
                    if (retiros.isEmpty) return const Text('Todavía no se cargó ningún retiro.');
                    return Column(
                      children: [
                        for (final retiro in retiros)
                          Card(
                            child: ListTile(
                              title: Text('${retiro.transportista} — ${formatoFechaLegible(retiro.fecha)}'),
                              subtitle: Text(
                                'Remito ${retiro.remito} · ${retiro.cantidadAves} aves · ${retiro.pesoNeto.toStringAsFixed(1)} kg',
                              ),
                            ),
                          ),
                      ],
                    );
                  },
                ),
                // espacio para que el contenido no quede tapado por los FABs
                const SizedBox(height: 72),
              ],
            );
          },
        ),
      ),
    );
  }
}
