import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';

class AlertasScreen extends StatefulWidget {
  const AlertasScreen({super.key, required this.crianzaId});

  final int crianzaId;

  @override
  State<AlertasScreen> createState() => _AlertasScreenState();
}

class _AlertasScreenState extends State<AlertasScreen> {
  late AdminApi _api;
  late Future<List<Alerta>> _alertas;

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _alertas = _api.alertas(widget.crianzaId);
  }

  Future<void> _refrescar() async {
    setState(() => _alertas = _api.alertas(widget.crianzaId));
    await _alertas;
  }

  Future<void> _resolver(Alerta alerta) async {
    await _api.resolverAlerta(widget.crianzaId, alerta.id);
    await _refrescar();
  }

  IconData _icono(String tipo) {
    switch (tipo) {
      case 'mortandad':
        return Icons.warning_amber;
      case 'agua':
        return Icons.water_drop;
      case 'gas':
        return Icons.local_fire_department;
      case 'electricidad':
        return Icons.bolt;
      default:
        return Icons.notifications;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Alertas')),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<List<Alerta>>(
          future: _alertas,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return const Center(child: Text('No se pudieron cargar las alertas'));
            }
            final alertas = snapshot.data ?? [];
            if (alertas.isEmpty) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: const [
                  Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('No hay alertas para esta crianza.')),
                  ),
                ],
              );
            }
            // sin resolver primero, más recientes primero
            final ordenadas = [...alertas]
              ..sort((a, b) {
                if (a.resuelta != b.resuelta) return a.resuelta ? 1 : -1;
                return b.fecha.compareTo(a.fecha);
              });
            return ListView.builder(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(8),
              itemCount: ordenadas.length,
              itemBuilder: (context, i) {
                final alerta = ordenadas[i];
                return Card(
                  color: alerta.resuelta ? null : Colors.orange.shade50,
                  child: ListTile(
                    leading: Icon(_icono(alerta.tipo), color: alerta.resuelta ? Colors.grey : Colors.deepOrange),
                    title: Text(alerta.descripcion),
                    subtitle: Text(
                      '${alerta.fecha.day}/${alerta.fecha.month}/${alerta.fecha.year} ${alerta.fecha.hour.toString().padLeft(2, '0')}:${alerta.fecha.minute.toString().padLeft(2, '0')}',
                    ),
                    trailing: alerta.resuelta
                        ? const Icon(Icons.check_circle, color: Colors.green)
                        : TextButton(onPressed: () => _resolver(alerta), child: const Text('Resolver')),
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
