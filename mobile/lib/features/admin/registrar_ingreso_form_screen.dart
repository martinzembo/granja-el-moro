import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'nueva_crianza_form_screen.dart' show formatoFechaLegible;

class RegistrarIngresoFormScreen extends StatefulWidget {
  const RegistrarIngresoFormScreen({super.key, required this.crianzaId, required this.cgId});

  final int crianzaId;
  final int cgId;

  @override
  State<RegistrarIngresoFormScreen> createState() => _RegistrarIngresoFormScreenState();
}

class _RegistrarIngresoFormScreenState extends State<RegistrarIngresoFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _origenCtrl = TextEditingController();
  final _cantidadCtrl = TextEditingController();
  final _muertosCtrl = TextEditingController(text: '0');
  DateTime _fecha = DateTime.now();
  bool _guardando = false;

  @override
  void dispose() {
    _origenCtrl.dispose();
    _cantidadCtrl.dispose();
    _muertosCtrl.dispose();
    super.dispose();
  }

  Future<void> _elegirFecha() async {
    final elegida = await showDatePicker(
      context: context,
      initialDate: _fecha,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (elegida != null) setState(() => _fecha = elegida);
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _guardando = true);
    final api = AdminApi(context.read<AuthService>().api);
    try {
      await api.registrarIngreso(
        crianzaId: widget.crianzaId,
        cgId: widget.cgId,
        fecha: _fecha,
        origen: _origenCtrl.text,
        cantidad: int.parse(_cantidadCtrl.text),
        muertosTransporte: int.parse(_muertosCtrl.text),
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
      appBar: AppBar(title: const Text('Ingreso de pollitos BB')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Fecha de ingreso'),
                subtitle: Text(formatoFechaLegible(_fecha)),
                trailing: const Icon(Icons.calendar_today),
                onTap: _elegirFecha,
              ),
              TextFormField(
                controller: _origenCtrl,
                decoration: const InputDecoration(
                  labelText: 'Origen',
                  helperText: 'Línea genética o granja de reproductoras (ej. Las Violetas)',
                  border: OutlineInputBorder(),
                ),
                validator: (v) => (v == null || v.isEmpty) ? 'Ingresá el origen' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _cantidadCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Cantidad despachada',
                  border: OutlineInputBorder(),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresá la cantidad';
                  if (int.tryParse(v) == null) return 'Tiene que ser un número entero';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _muertosCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Muertos en el transporte',
                  border: OutlineInputBorder(),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresá un número (0 si no hubo)';
                  if (int.tryParse(v) == null) return 'Tiene que ser un número entero';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _guardando ? null : _guardar,
                child: _guardando
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Guardar'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
