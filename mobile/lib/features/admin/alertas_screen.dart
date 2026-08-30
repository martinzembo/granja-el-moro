import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
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
  final Set<int> _resolviendo = {};

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _alertas = _api.alertas(widget.crianzaId);
  }

  Future<void> _refrescar() async {
    setState(() {
      _alertas = _api.alertas(widget.crianzaId);
    });
    await _alertas;
  }

  Future<void> _resolver(Alerta alerta) async {
    setState(() => _resolviendo.add(alerta.id));
    try {
      await _api.resolverAlerta(widget.crianzaId, alerta.id);
      await _refrescar();
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo conectar con el servidor')),
      );
    } finally {
      if (mounted) setState(() => _resolviendo.remove(alerta.id));
    }
  }

  /// Emoji por tipo — más reconocible de un vistazo que un ícono genérico.
  String _emoji(String tipo) {
    switch (tipo) {
      case 'mortandad':
        return '💀';
      case 'agua':
        return '💧';
      case 'gas':
        return '🔥';
      case 'electricidad':
        return '⚡';
      default:
        return '🔔';
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
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: const [
                  Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('No se pudieron cargar las alertas. Deslizá para reintentar.')),
                  ),
                ],
              );
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
                final resolviendo = _resolviendo.contains(alerta.id);
                return Card(
                  color: alerta.resuelta ? null : Colors.orange.shade50,
                  child: ListTile(
                    leading: Text(_emoji(alerta.tipo), style: const TextStyle(fontSize: 28)),
                    title: Text(alerta.descripcion),
                    subtitle: Text(
                      '${alerta.fecha.day}/${alerta.fecha.month}/${alerta.fecha.year} ${alerta.fecha.hour.toString().padLeft(2, '0')}:${alerta.fecha.minute.toString().padLeft(2, '0')}',
                    ),
                    trailing: alerta.resuelta
                        ? const Icon(Icons.check_circle, color: Colors.green)
                        : resolviendo
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : TextButton(
                                onPressed: () => _resolver(alerta),
                                child: const Text('Resolver'),
                              ),
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
