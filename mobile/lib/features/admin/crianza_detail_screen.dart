import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';
import 'alertas_screen.dart';
import 'asignar_galpon_form_screen.dart';
import 'cierre_form_screen.dart';
import 'galpon_detail_screen.dart';
import 'registrar_entrega_form_screen.dart';

class CrianzaDetailScreen extends StatefulWidget {
  const CrianzaDetailScreen({super.key, required this.crianza});

  final Crianza crianza;

  @override
  State<CrianzaDetailScreen> createState() => _CrianzaDetailScreenState();
}

class _CrianzaDetailScreenState extends State<CrianzaDetailScreen> {
  late AdminApi _api;
  late Crianza _crianza;
  late Future<List<CrianzaGalpon>> _galpones;
  late Future<List<Alerta>> _alertas;
  late Future<List<EntregaInsumo>> _entregas;
  Future<CierreCrianza?>? _cierre;

  @override
  void initState() {
    super.initState();
    _crianza = widget.crianza;
    _api = AdminApi(context.read<AuthService>().api);
    _cargar();
  }

  void _cargar() {
    _galpones = _api.galponesDeCrianza(_crianza.id);
    _alertas = _api.alertas(_crianza.id, resuelta: false);
    _entregas = _api.entregas(_crianza.id);
    _cierre = _crianza.enCurso ? null : _api.cierre(_crianza.id);
  }

  Future<void> _refrescar() async {
    final crianzas = await _api.crianzas();
    setState(() {
      _crianza = crianzas.firstWhere((c) => c.id == _crianza.id, orElse: () => _crianza);
      _cargar();
    });
    await Future.wait([_galpones, _alertas, _entregas, ?_cierre]);
  }

  Future<void> _asignarGalpon(List<CrianzaGalpon> actuales) async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => AsignarGalponFormScreen(
          crianzaId: _crianza.id,
          yaAsignados: actuales.map((cg) => cg.galponId).toSet(),
        ),
      ),
    );
    if (ok == true) await _refrescar();
  }

  Future<void> _agregarEntrega() async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => RegistrarEntregaFormScreen(crianzaId: _crianza.id)),
    );
    if (ok == true) await _refrescar();
  }

  Future<void> _cerrarCrianza() async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => CierreFormScreen(crianza: _crianza)),
    );
    if (ok == true) await _refrescar();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Crianza #${_crianza.numero}'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Center(
              child: Chip(
                label: Text(_crianza.enCurso ? 'En curso' : 'Cerrada'),
                backgroundColor: _crianza.enCurso ? Colors.green.shade100 : Colors.grey.shade300,
              ),
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<List<CrianzaGalpon>>(
          future: _galpones,
          builder: (context, snapshotGalpones) {
            if (snapshotGalpones.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            final galpones = snapshotGalpones.data ?? [];
            return ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              children: [
                if (!_crianza.enCurso) _tarjetaLiquidacion(),
                FutureBuilder<List<Alerta>>(
                  future: _alertas,
                  builder: (context, snapshotAlertas) {
                    final cantidad = snapshotAlertas.data?.length;
                    return Card(
                      color: (cantidad ?? 0) > 0 ? Colors.orange.shade50 : null,
                      child: ListTile(
                        leading: const Icon(Icons.notifications),
                        title: Text(cantidad == null ? 'Alertas' : '$cantidad alerta(s) sin resolver'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () async {
                          await Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => AlertasScreen(crianzaId: _crianza.id)),
                          );
                          await _refrescar();
                        },
                      ),
                    );
                  },
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Galpones', style: Theme.of(context).textTheme.titleMedium),
                    if (_crianza.enCurso)
                      TextButton.icon(
                        onPressed: () => _asignarGalpon(galpones),
                        icon: const Icon(Icons.add),
                        label: const Text('Asignar'),
                      ),
                  ],
                ),
                if (galpones.isEmpty) const Text('Todavía no hay galpones asignados a esta crianza.'),
                for (final cg in galpones)
                  Card(
                    child: ListTile(
                      title: Text(cg.galponNombre),
                      subtitle: Text('Granjero: ${cg.granjeroNombre}'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () async {
                        await Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => GalponDetailScreen(
                              crianzaId: _crianza.id,
                              cg: cg,
                              crianzaEnCurso: _crianza.enCurso,
                            ),
                          ),
                        );
                        await _refrescar();
                      },
                    ),
                  ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Entregas de alimento', style: Theme.of(context).textTheme.titleMedium),
                    if (_crianza.enCurso)
                      TextButton.icon(
                        onPressed: _agregarEntrega,
                        icon: const Icon(Icons.add),
                        label: const Text('Entrega'),
                      ),
                  ],
                ),
                FutureBuilder<List<EntregaInsumo>>(
                  future: _entregas,
                  builder: (context, snapshotEntregas) {
                    if (snapshotEntregas.connectionState != ConnectionState.done) {
                      return const Center(child: CircularProgressIndicator());
                    }
                    final entregas = snapshotEntregas.data ?? [];
                    if (entregas.isEmpty) return const Text('Todavía no se cargó ninguna entrega.');
                    return Column(
                      children: [
                        for (final entrega in entregas)
                          Card(
                            child: ListTile(
                              title: Text('${entrega.kilos.toStringAsFixed(0)} kg — remito ${entrega.remito}'),
                              subtitle: Text(
                                '${entrega.fecha.day}/${entrega.fecha.month}/${entrega.fecha.year}',
                              ),
                            ),
                          ),
                      ],
                    );
                  },
                ),
                if (_crianza.enCurso) ...[
                  const SizedBox(height: 32),
                  FilledButton.icon(
                    style: FilledButton.styleFrom(backgroundColor: Colors.red.shade700),
                    onPressed: _cerrarCrianza,
                    icon: const Icon(Icons.lock),
                    label: const Text('Cerrar crianza'),
                  ),
                ],
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _tarjetaLiquidacion() {
    return FutureBuilder<CierreCrianza?>(
      future: _cierre,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Padding(
            padding: EdgeInsets.all(16),
            child: Center(child: CircularProgressIndicator()),
          );
        }
        final cierre = snapshot.data;
        if (cierre == null) {
          return const Card(child: ListTile(title: Text('Crianza cerrada sin liquidación registrada')));
        }
        return Card(
          color: Colors.blue.shade50,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Liquidación', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Text('Aves entregadas: ${cierre.totalAvesEntregadas}'),
                Text('Peso total: ${cierre.pesoTotal.toStringAsFixed(1)} kg'),
                Text('IE promedio: ${cierre.iePromedio.toStringAsFixed(2)}'),
                Text('Precio x pollo: \$${cierre.precioXPollo.toStringAsFixed(2)}'),
                const SizedBox(height: 4),
                Text(
                  'Monto total: \$${cierre.montoTotal.toStringAsFixed(2)}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
