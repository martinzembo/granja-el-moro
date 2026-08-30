import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';
import 'alertas_screen.dart';
import 'asignar_galpon_form_screen.dart';
import 'galpon_detail_screen.dart';

class CrianzaDetailScreen extends StatefulWidget {
  const CrianzaDetailScreen({super.key, required this.crianza});

  final Crianza crianza;

  @override
  State<CrianzaDetailScreen> createState() => _CrianzaDetailScreenState();
}

class _CrianzaDetailScreenState extends State<CrianzaDetailScreen> {
  late AdminApi _api;
  late Future<List<CrianzaGalpon>> _galpones;
  late Future<List<Alerta>> _alertas;

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _cargar();
  }

  void _cargar() {
    _galpones = _api.galponesDeCrianza(widget.crianza.id);
    _alertas = _api.alertas(widget.crianza.id, resuelta: false);
  }

  Future<void> _refrescar() async {
    setState(_cargar);
    await Future.wait([_galpones, _alertas]);
  }

  Future<void> _asignarGalpon(List<CrianzaGalpon> actuales) async {
    final ok = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => AsignarGalponFormScreen(
          crianzaId: widget.crianza.id,
          yaAsignados: actuales.map((cg) => cg.galponId).toSet(),
        ),
      ),
    );
    if (ok == true) await _refrescar();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Crianza #${widget.crianza.numero}')),
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
                            MaterialPageRoute(builder: (_) => AlertasScreen(crianzaId: widget.crianza.id)),
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
                            builder: (_) => GalponDetailScreen(crianzaId: widget.crianza.id, cg: cg),
                          ),
                        );
                        await _refrescar();
                      },
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
