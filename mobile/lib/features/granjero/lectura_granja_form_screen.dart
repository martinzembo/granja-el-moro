import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import 'granjero_api.dart';

/// Carga diaria de gas y electricidad de toda la granja (un solo medidor de
/// cada uno, no por galpón — la ventana horaria 08:00-08:00 va fija, no se
/// le pide al granjero). Cualquier granjero asignado a la crianza puede
/// cargar esto, no solo el de un galpón puntual.
class LecturaGranjaFormScreen extends StatefulWidget {
  const LecturaGranjaFormScreen({super.key, required this.crianzaId});

  final int crianzaId;

  @override
  State<LecturaGranjaFormScreen> createState() => _LecturaGranjaFormScreenState();
}

class _LecturaGranjaFormScreenState extends State<LecturaGranjaFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _gasCtrl = TextEditingController();
  final _activaCtrl = TextEditingController();
  final _reactivaCtrl = TextEditingController();
  bool _guardando = false;

  @override
  void dispose() {
    _gasCtrl.dispose();
    _activaCtrl.dispose();
    _reactivaCtrl.dispose();
    super.dispose();
  }

  String? _validarNumero(String? v) {
    if (v == null || v.isEmpty) return 'Ingresá la lectura del medidor';
    if (double.tryParse(v.replaceAll(',', '.')) == null) return 'Tiene que ser un número';
    return null;
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _guardando = true);
    final api = GranjeroApi(context.read<AuthService>().api);
    try {
      await api.cargarLecturaGranja(
        crianzaId: widget.crianzaId,
        fecha: DateTime.now(),
        lecturaGas: double.parse(_gasCtrl.text.replaceAll(',', '.')),
        lecturaElectricidadActiva: double.parse(_activaCtrl.text.replaceAll(',', '.')),
        lecturaElectricidadReactiva: double.parse(_reactivaCtrl.text.replaceAll(',', '.')),
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
      appBar: AppBar(title: const Text('Gas y electricidad de hoy')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Ventana de 08:00 a 08:00 del día siguiente, como siempre.',
                style: TextStyle(color: Colors.black54),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _gasCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Medidor de gas (m³)',
                  border: OutlineInputBorder(),
                ),
                validator: _validarNumero,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _activaCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Medidor de luz — activa (kWh)',
                  border: OutlineInputBorder(),
                ),
                validator: _validarNumero,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _reactivaCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Medidor de luz — reactiva (kvarh)',
                  border: OutlineInputBorder(),
                ),
                validator: _validarNumero,
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
