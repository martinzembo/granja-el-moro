import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import 'admin_api.dart';
import 'admin_models.dart';

/// "Los números reales, como en el Excel" — pedido del administrador: no
/// solo alertas cuando algo se desvía, sino el estado completo de la
/// crianza en cualquier momento. Reusa exactamente los mismos cálculos que
/// las alertas (ver app/services/resumen.py) para no mostrar un criterio
/// distinto acá que allá.
///
/// A propósito no muestra índice de crecimiento/conversión/IE: esos
/// necesitan peso, que no se conoce hasta que las aves salen a faena — eso
/// ya está en la liquidación final (ver CierreFormScreen).
class ResumenScreen extends StatefulWidget {
  const ResumenScreen({super.key, required this.crianza});

  final Crianza crianza;

  @override
  State<ResumenScreen> createState() => _ResumenScreenState();
}

class _ResumenScreenState extends State<ResumenScreen> {
  late AdminApi _api;
  late Future<ResumenCrianza> _resumen;

  @override
  void initState() {
    super.initState();
    _api = AdminApi(context.read<AuthService>().api);
    _resumen = _api.resumen(widget.crianza.id);
  }

  Future<void> _refrescar() async {
    setState(() {
      _resumen = _api.resumen(widget.crianza.id);
    });
    await _resumen;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Resumen — Crianza #${widget.crianza.numero}')),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<ResumenCrianza>(
          future: _resumen,
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
                    child: Center(child: Text('No se pudo cargar el resumen. Deslizá para reintentar.')),
                  ),
                ],
              );
            }
            final resumen = snapshot.data!;
            return ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(12),
              children: [
                _tarjetaGranja(resumen),
                const SizedBox(height: 12),
                if (resumen.galpones.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('Todavía no hay galpones asignados a esta crianza.'),
                  ),
                for (final galpon in resumen.galpones) ...[
                  _tarjetaGalpon(galpon),
                  const SizedBox(height: 12),
                ],
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _tarjetaGranja(ResumenCrianza resumen) {
    final granja = resumen.granja;
    return Card(
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Granja', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            _fila('🌾', 'Alimento entregado', '${resumen.alimentoEntregadoKg.toStringAsFixed(0)} kg'),
            if (granja.fecha == null)
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: Text('Todavía no se cargó ninguna lectura de gas/electricidad.'),
              )
            else ...[
              _filaHoyPromedio('🔥', 'Gas', granja.consumoGasHoy, granja.promedioGas3Dias, 'm³'),
              _filaHoyPromedio(
                '⚡',
                'Electricidad activa',
                granja.consumoElectricidadActivaHoy,
                granja.promedioElectricidadActiva3Dias,
                'kWh',
              ),
              _filaHoyPromedio(
                '⚡',
                'Electricidad reactiva',
                granja.consumoElectricidadReactivaHoy,
                granja.promedioElectricidadReactiva3Dias,
                'kvarh',
              ),
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  'Última lectura: ${granja.fecha!.day}/${granja.fecha!.month}/${granja.fecha!.year}',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _tarjetaGalpon(ResumenGalpon galpon) {
    final mortandadPct = galpon.mortandadPct * 100;
    final mortandadEsperadaPct = galpon.mortandadEsperadaPct == null
        ? null
        : galpon.mortandadEsperadaPct! * 100;
    final sobreMortandad = mortandadEsperadaPct != null && mortandadPct > mortandadEsperadaPct * 1.5;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(galpon.galponNombre, style: Theme.of(context).textTheme.titleMedium),
                Text(
                  galpon.edadDias == null ? 'Sin ingreso cargado' : 'Día ${galpon.edadDias} de vida',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ],
            ),
            Text('Granjero: ${galpon.granjeroNombre}', style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
            const Divider(height: 20),
            _fila('🐔', 'Aves vivas', '${galpon.avesVivas} / ${galpon.avesNetas} netas'),
            Row(
              children: [
                const Text('💀 ', style: TextStyle(fontSize: 18)),
                Expanded(
                  child: Text(
                    mortandadEsperadaPct == null
                        ? 'Mortandad acumulada: ${galpon.mortandadAcumulada} (${mortandadPct.toStringAsFixed(2)}%)'
                        : 'Mortandad acumulada: ${galpon.mortandadAcumulada} (${mortandadPct.toStringAsFixed(2)}%) '
                            '— esperado ~${mortandadEsperadaPct.toStringAsFixed(2)}%',
                    style: TextStyle(
                      color: sobreMortandad ? Colors.red.shade700 : null,
                      fontWeight: sobreMortandad ? FontWeight.bold : null,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            _fila('💧', 'Agua acumulada', '${galpon.aguaAcumuladaLitros.toStringAsFixed(0)} L'),
            if (galpon.aguaLitrosPolloHoy != null)
              Padding(
                padding: const EdgeInsets.only(left: 26, top: 2),
                child: Text(
                  galpon.aguaEsperadaLitrosPolloHoy == null
                      ? 'Última lectura: ${galpon.aguaLitrosPolloHoy!.toStringAsFixed(3)} L/ave'
                      : 'Última lectura: ${galpon.aguaLitrosPolloHoy!.toStringAsFixed(3)} L/ave '
                          '— esperado ~${galpon.aguaEsperadaLitrosPolloHoy!.toStringAsFixed(3)} L/ave',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _fila(String emoji, String etiqueta, String valor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text('$emoji ', style: const TextStyle(fontSize: 18)),
          Expanded(child: Text('$etiqueta: $valor')),
        ],
      ),
    );
  }

  Widget _filaHoyPromedio(String emoji, String etiqueta, double? hoy, double? promedio, String unidad) {
    final texto = hoy == null
        ? '$etiqueta: sin datos suficientes todavía'
        : promedio == null
            ? '$etiqueta: ${hoy.toStringAsFixed(1)} $unidad hoy'
            : '$etiqueta: ${hoy.toStringAsFixed(1)} $unidad hoy — promedio 3 días: ${promedio.toStringAsFixed(1)} $unidad';
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text('$emoji ', style: const TextStyle(fontSize: 18)),
          Expanded(child: Text(texto)),
        ],
      ),
    );
  }
}
