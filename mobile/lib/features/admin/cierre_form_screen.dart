import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';
import 'nueva_crianza_form_screen.dart' show formatoFechaLegible;

/// El cierre es irreversible (bloquea toda carga nueva para la crianza), así
/// que esta pantalla insiste en la confirmación antes de mandar el POST.
///
/// indice_tabla/premios/gas_ajuste/ajuste son datos que provee la
/// integradora — el admin los tipea tal cual se los pasan, el sistema no
/// los calcula (ver docs/modelo-datos.md, sección Alertas... y CierreCrianza).
class CierreFormScreen extends StatefulWidget {
  const CierreFormScreen({super.key, required this.crianza});

  final Crianza crianza;

  @override
  State<CierreFormScreen> createState() => _CierreFormScreenState();
}

class _CierreFormScreenState extends State<CierreFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _indiceTablaCtrl = TextEditingController();
  final _premiosCtrl = TextEditingController(text: '0');
  final _gasAjusteCtrl = TextEditingController(text: '0');
  final _ajusteCtrl = TextEditingController(text: '0');
  DateTime _fechaCierre = DateTime.now();
  bool _guardando = false;

  double? _num(String texto) => double.tryParse(texto.trim().replaceAll(',', '.'));

  double get _precioXPolloEstimado {
    return (_num(_indiceTablaCtrl.text) ?? 0) +
        (_num(_premiosCtrl.text) ?? 0) +
        (_num(_gasAjusteCtrl.text) ?? 0) +
        (_num(_ajusteCtrl.text) ?? 0);
  }

  @override
  void initState() {
    super.initState();
    for (final ctrl in [_indiceTablaCtrl, _premiosCtrl, _gasAjusteCtrl, _ajusteCtrl]) {
      ctrl.addListener(() => setState(() {}));
    }
  }

  @override
  void dispose() {
    _indiceTablaCtrl.dispose();
    _premiosCtrl.dispose();
    _gasAjusteCtrl.dispose();
    _ajusteCtrl.dispose();
    super.dispose();
  }

  Future<void> _elegirFecha() async {
    final elegida = await showDatePicker(
      context: context,
      initialDate: _fechaCierre,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (elegida != null) setState(() => _fechaCierre = elegida);
  }

  String? _validarNumero(String? v) {
    if (v == null || v.isEmpty) return 'Ingresá un valor';
    if (_num(v) == null) return 'Tiene que ser un número';
    return null;
  }

  Future<void> _confirmarYCerrar() async {
    if (!_formKey.currentState!.validate()) return;

    final confirmado = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Cerrar esta crianza?'),
        content: Text(
          'Se va a cerrar la Crianza #${widget.crianza.numero} con precio x pollo de '
          '\$${_precioXPolloEstimado.toStringAsFixed(2)}. Esta acción no se puede deshacer: '
          'después del cierre no se admite más carga de datos para esta crianza.',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Confirmar cierre')),
        ],
      ),
    );
    if (confirmado != true) return;
    if (!mounted) return;

    setState(() => _guardando = true);
    final api = AdminApi(context.read<AuthService>().api);
    try {
      final resultado = await api.cerrarCrianza(
        crianzaId: widget.crianza.id,
        fechaCierre: _fechaCierre,
        indiceTabla: _num(_indiceTablaCtrl.text)!,
        premios: _num(_premiosCtrl.text)!,
        gasAjuste: _num(_gasAjusteCtrl.text)!,
        ajuste: _num(_ajusteCtrl.text)!,
      );
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Crianza cerrada'),
          content: _ResumenLiquidacion(resultado),
          actions: [
            FilledButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Listo')),
          ],
        ),
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
      appBar: AppBar(title: Text('Cerrar Crianza #${widget.crianza.numero}')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              Card(
                color: Colors.amber.shade50,
                child: const Padding(
                  padding: EdgeInsets.all(12),
                  child: Text(
                    'Antes de cerrar, asegurate de haber cargado todos los retiros a faena '
                    'y las entregas de alimento de esta crianza — después del cierre no se '
                    'puede agregar más.',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Fecha de cierre'),
                subtitle: Text(formatoFechaLegible(_fechaCierre)),
                trailing: const Icon(Icons.calendar_today),
                onTap: _elegirFecha,
              ),
              const SizedBox(height: 8),
              Text(
                'Estos cuatro valores los provee la integradora — se cargan tal cual, '
                'no los calcula el sistema.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _indiceTablaCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Índice de tabla', border: OutlineInputBorder()),
                validator: _validarNumero,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _premiosCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Premios', border: OutlineInputBorder()),
                validator: _validarNumero,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _gasAjusteCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Ajuste por gas', border: OutlineInputBorder()),
                validator: _validarNumero,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _ajusteCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Ajuste general', border: OutlineInputBorder()),
                validator: _validarNumero,
              ),
              const SizedBox(height: 20),
              Card(
                child: ListTile(
                  title: const Text('Precio x pollo estimado'),
                  trailing: Text(
                    '\$${_precioXPolloEstimado.toStringAsFixed(2)}',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              FilledButton(
                style: FilledButton.styleFrom(backgroundColor: Colors.red.shade700),
                onPressed: _guardando ? null : _confirmarYCerrar,
                child: _guardando
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Cerrar crianza'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ResumenLiquidacion extends StatelessWidget {
  const _ResumenLiquidacion(this.cierre);

  final CierreCrianza cierre;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _fila('Aves entregadas', '${cierre.totalAvesEntregadas}'),
        _fila('Peso total', '${cierre.pesoTotal.toStringAsFixed(1)} kg'),
        _fila('IE promedio', cierre.iePromedio.toStringAsFixed(2)),
        _fila('Precio x pollo', '\$${cierre.precioXPollo.toStringAsFixed(2)}'),
        const Divider(),
        _fila('Monto total', '\$${cierre.montoTotal.toStringAsFixed(2)}', destacado: true),
      ],
    );
  }

  Widget _fila(String etiqueta, String valor, {bool destacado = false}) {
    final estilo = destacado ? const TextStyle(fontWeight: FontWeight.bold) : null;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(etiqueta, style: estilo), Text(valor, style: estilo)],
      ),
    );
  }
}
