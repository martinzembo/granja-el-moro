import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import '../../core/usuario.dart';
import 'admin_api.dart';

/// Cuentas que se autoregistraron desde "Creá una cuenta" en el login y
/// todavía no fueron habilitadas — pedido del docente de la cátedra: antes
/// el registro activaba la cuenta solo, ahora hace falta este paso para
/// evitar que cualquiera con el link de la app quede cargado como
/// granjero sin que el administrador se entere (ver
/// app/api/routers/auth.py, `register`).
class UsuariosPendientesScreen extends StatefulWidget {
  const UsuariosPendientesScreen({super.key});

  @override
  State<UsuariosPendientesScreen> createState() => _UsuariosPendientesScreenState();
}

class _UsuariosPendientesScreenState extends State<UsuariosPendientesScreen> {
  late AdminApi _api;
  late Future<List<Usuario>> _pendientes;
  final Set<int> _activando = {};

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _pendientes = _api.usuariosPendientes();
  }

  Future<void> _refrescar() async {
    setState(() {
      _pendientes = _api.usuariosPendientes();
    });
    await _pendientes;
  }

  Future<void> _activar(Usuario usuario) async {
    setState(() => _activando.add(usuario.id));
    try {
      await _api.activarUsuario(usuario.id);
      await _refrescar();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${usuario.nombre} ya puede ingresar.')),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo conectar con el servidor')),
      );
    } finally {
      if (mounted) setState(() => _activando.remove(usuario.id));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cuentas pendientes')),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<List<Usuario>>(
          future: _pendientes,
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
                    child: Center(child: Text('No se pudieron cargar. Deslizá para reintentar.')),
                  ),
                ],
              );
            }
            final pendientes = snapshot.data ?? [];
            if (pendientes.isEmpty) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: const [
                  Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('No hay cuentas esperando aprobación.')),
                  ),
                ],
              );
            }
            return ListView.builder(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(8),
              itemCount: pendientes.length,
              itemBuilder: (context, i) {
                final usuario = pendientes[i];
                final activando = _activando.contains(usuario.id);
                return Card(
                  color: Colors.orange.shade50,
                  child: ListTile(
                    leading: const Icon(Icons.person_add_alt),
                    title: Text(usuario.nombre),
                    subtitle: Text(usuario.email),
                    trailing: activando
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : FilledButton(
                            onPressed: () => _activar(usuario),
                            child: const Text('Activar'),
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
