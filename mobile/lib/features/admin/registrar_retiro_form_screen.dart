import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'nueva_crianza_form_screen.dart' show formatoFechaLegible;

class RegistrarRetiroFormScreen extends StatefulWidget {
  const RegistrarRetiroFormScreen({super.key, required this.crianzaId, required this.cgId});

  final int crianzaId;
  final int cgId;

  @override
  State<RegistrarRetiroFormScreen> createState() => _RegistrarRetiroFormScreenState();
}

class _RegistrarRetiroFormScreenState extends State<RegistrarRetiroFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _remitoCtrl = TextEditingController();
  final _transportistaCtrl = TextEditingController();
  final _cantidadCtrl = TextEditingController();
  final _pesoCtrl = TextEditingController();
  DateTime _fecha = DateTime.now();
  bool _guardando = false;

  @override
  void dispose() {
    _remitoCtrl.dispose();
    _transportistaCtrl.dispose();
    _cantidadCtrl.dispose();
    _pesoCtrl.dispose();
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
      await api.registrarRetiro(
        crianzaId: widget.crianzaId,
        cgId: widget.cgId,
        fecha: _fecha,
        remito: _remitoCtrl.text,
        transportista: _transportistaCtrl.text,
        cantidadAves: int.parse(_cantidadCtrl.text),
        pesoNeto: double.parse(_pesoCtrl.text.replaceAll(',', '.')),
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
      appBar: AppBar(title: const Text('Retiro a faena')),
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
                controller: _transportistaCtrl,
                decoration: const InputDecoration(labelText: 'Transportista', border: OutlineInputBorder()),
                validator: (v) => (v == null || v.isEmpty) ? 'Ingresá el transportista' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _cantidadCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Cantidad de aves', border: OutlineInputBorder()),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresá la cantidad';
                  if (int.tryParse(v) == null) return 'Tiene que ser un número entero';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _pesoCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Peso neto (kg)', border: OutlineInputBorder()),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresá el peso neto';
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
