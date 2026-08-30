import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import 'granjero_api.dart';

/// Carga diaria de mortandad + lectura de agua de un galpón. La lectura de
/// agua es la del caudalímetro tal cual se lee (no el consumo ya
/// calculado) — ver docs/modelo-datos.md.
class LecturaGalponFormScreen extends StatefulWidget {
  const LecturaGalponFormScreen({super.key, required this.crianzaId, required this.cgId, required this.galponNombre});

  final int crianzaId;
  final int cgId;
  final String galponNombre;

  @override
  State<LecturaGalponFormScreen> createState() => _LecturaGalponFormScreenState();
}

class _LecturaGalponFormScreenState extends State<LecturaGalponFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _mortandadCtrl = TextEditingController(text: '0');
  final _aguaCtrl = TextEditingController();
  bool _guardando = false;

  @override
  void dispose() {
    _mortandadCtrl.dispose();
    _aguaCtrl.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _guardando = true);
    final api = GranjeroApi(context.read<AuthService>().api);
    try {
      await api.cargarLecturaGalpon(
        crianzaId: widget.crianzaId,
        cgId: widget.cgId,
        fecha: DateTime.now(),
        mortandad: int.parse(_mortandadCtrl.text),
        lecturaAgua: double.parse(_aguaCtrl.text.replaceAll(',', '.')),
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
      appBar: AppBar(title: Text('Datos de hoy — ${widget.galponNombre}')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _mortandadCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Mortandad de hoy',
                  helperText: 'Cantidad de aves muertas hoy en este galpón',
                  border: OutlineInputBorder(),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresá un número (0 si no hubo)';
                  if (int.tryParse(v) == null) return 'Tiene que ser un número entero';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _aguaCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Lectura del caudalímetro',
                  helperText: 'El número que muestra el medidor de agua ahora, tal cual',
                  border: OutlineInputBorder(),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Ingresá la lectura del medidor';
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
