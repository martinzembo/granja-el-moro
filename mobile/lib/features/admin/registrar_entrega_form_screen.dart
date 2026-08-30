import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'nueva_crianza_form_screen.dart' show formatoFechaLegible;

/// Solo alimento por ahora — cáscara de girasol/arroz queda para más
/// adelante si hace falta (ver docs/modelo-datos.md).
class RegistrarEntregaFormScreen extends StatefulWidget {
  const RegistrarEntregaFormScreen({super.key, required this.crianzaId});

  final int crianzaId;

  @override
  State<RegistrarEntregaFormScreen> createState() => _RegistrarEntregaFormScreenState();
}

class _RegistrarEntregaFormScreenState extends State<RegistrarEntregaFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _remitoCtrl = TextEditingController();
  final _kilosCtrl = TextEditingController();
  DateTime _fecha = DateTime.now();
  bool _guardando = false;

  @override
  void dispose() {
    _remitoCtrl.dispose();
    _kilosCtrl.dispose();
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
      await api.registrarEntregaAlimento(
        crianzaId: widget.crianzaId,
        fecha: _fecha,
        remito: _remitoCtrl.text,
        kilos: double.parse(_kilosCtrl.text.replaceAll(',', '.')),
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
      appBar: AppBar(title: const Text('Entrega de alimento')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Fecha'),
                subtitle: Text(formatoFechaLegible(_fecha)),
                trailing: const Icon(Icons.calendar_today),
                onTap: _elegirFecha,
              ),
              TextFormField(
                controller: _remitoCtrl,
                decoration: const InputDecoration(labelText: 'N° de remito', border: OutlineInputBorder()),
                validator: (v) => (v == null || v.isEmpty) ? 'Ingresá el remito' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _kilosCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Kilos', border: OutlineInputBorder()),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresá los kilos';
                  if (double.tryParse(v.replaceAll(',', '.')) == null) return 'Tiene que ser un número';
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
