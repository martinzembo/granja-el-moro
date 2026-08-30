import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import '../../core/usuario.dart';
import 'admin_api.dart';
import 'admin_models.dart';

class AsignarGalponFormScreen extends StatefulWidget {
  const AsignarGalponFormScreen({super.key, required this.crianzaId, required this.yaAsignados});

  final int crianzaId;

  /// Ids de galpón ya asignados a esta crianza, para no ofrecerlos de nuevo.
  final Set<int> yaAsignados;

  @override
  State<AsignarGalponFormScreen> createState() => _AsignarGalponFormScreenState();
}

class _AsignarGalponFormScreenState extends State<AsignarGalponFormScreen> {
  late AdminApi _api;
  late Future<(List<Galpon>, List<Usuario>)> _datos;
  Galpon? _galponElegido;
  Usuario? _granjeroElegido;
  bool _guardando = false;

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _datos = _cargarDatos();
  }

  Future<(List<Galpon>, List<Usuario>)> _cargarDatos() async {
    final galpones = await _api.galpones();
    final granjeros = await _api.granjeros();
    return (galpones.where((g) => !widget.yaAsignados.contains(g.id)).toList(), granjeros);
  }

  Future<void> _crearGalponNuevo() async {
    final nombreCtrl = TextEditingController();
    final capacidadCtrl = TextEditingController();
    final creado = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nuevo galpón'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nombreCtrl, decoration: const InputDecoration(labelText: 'Nombre')),
            TextField(
              controller: capacidadCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Capacidad máxima (aves)'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Crear')),
        ],
      ),
    );
    if (creado != true) return;
    final capacidad = int.tryParse(capacidadCtrl.text);
    if (nombreCtrl.text.isEmpty || capacidad == null) return;
    try {
      final galpon = await _api.crearGalpon(nombre: nombreCtrl.text, capacidadMaxima: capacidad);
      setState(() {
        _datos = _cargarDatos();
        _galponElegido = galpon;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    }
  }

  Future<void> _guardar() async {
    if (_galponElegido == null || _granjeroElegido == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Elegí un galpón y un granjero')),
      );
      return;
    }
    setState(() => _guardando = true);
    try {
      await _api.asignarGalpon(
        crianzaId: widget.crianzaId,
        galponId: _galponElegido!.id,
        granjeroId: _granjeroElegido!.id,
      );
      if (!mounted) return;
      Navigator.of(context).pop(true);
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo conectar con el servidor')),
      );
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Asignar galpón')),
      body: FutureBuilder<(List<Galpon>, List<Usuario>)>(
        future: _datos,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return const Center(child: Text('No se pudo cargar la información'));
          }
          final (galpones, granjeros) = snapshot.data!;
          return Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                DropdownButtonFormField<Galpon>(
                  initialValue: _galponElegido,
                  decoration: const InputDecoration(labelText: 'Galpón', border: OutlineInputBorder()),
                  items: galpones
                      .map((g) => DropdownMenuItem(value: g, child: Text(g.nombre)))
                      .toList(),
                  onChanged: (g) => setState(() => _galponElegido = g),
                ),
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton.icon(
                    onPressed: _crearGalponNuevo,
                    icon: const Icon(Icons.add),
                    label: const Text('Crear galpón nuevo'),
                  ),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<Usuario>(
                  initialValue: _granjeroElegido,
                  decoration: const InputDecoration(labelText: 'Granjero responsable', border: OutlineInputBorder()),
                  items: granjeros
                      .map((g) => DropdownMenuItem(value: g, child: Text(g.nombre)))
                      .toList(),
                  onChanged: (g) => setState(() => _granjeroElegido = g),
                ),
                if (granjeros.isEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 8),
                    child: Text(
                      'No hay usuarios con rol granjero registrados todavía.',
                      style: TextStyle(color: Colors.red),
                    ),
                  ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: _guardando ? null : _guardar,
                  child: _guardando
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Asignar'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
