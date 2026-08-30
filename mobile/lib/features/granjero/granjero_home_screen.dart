import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/auth_service.dart';
import '../../core/date_utils.dart';
import 'granjero_api.dart';
import 'granjero_models.dart';
import 'lectura_galpon_form_screen.dart';
import 'lectura_granja_form_screen.dart';

/// Punto de entrada del flujo del granjero: mortandad + agua de su galpón,
/// y gas/electricidad de toda la granja, ambas con carga diaria (ver
/// docs/plan.md Semana 4-5).
class GranjeroHomeScreen extends StatefulWidget {
  const GranjeroHomeScreen({super.key});

  @override
  State<GranjeroHomeScreen> createState() => _GranjeroHomeScreenState();
}

class _EstadoDia {
  _EstadoDia({this.galponCargado = false, this.granjaCargado = false});
  bool galponCargado;
  bool granjaCargado;
}

class _GranjeroHomeScreenState extends State<GranjeroHomeScreen> {
  late GranjeroApi _api;
  late Future<List<Asignacion>> _asignaciones;
  Asignacion? _asignacionActiva;
  _EstadoDia _estadoDia = _EstadoDia();
  bool _cargandoEstadoDia = false;

  @override
  void initState() {
    super.initState();
    _api = GranjeroApi(context.read<AuthService>().api);
    _asignaciones = _cargarAsignaciones();
  }

  Future<List<Asignacion>> _cargarAsignaciones() async {
    final asignaciones = await _api.misAsignaciones();
    final activa = asignaciones.where((a) => a.enCurso).firstOrNull;
    _asignacionActiva = activa;
    if (activa != null) {
      await _cargarEstadoDelDia(activa);
    }
    return asignaciones;
  }

  Future<void> _cargarEstadoDelDia(Asignacion asignacion) async {
    setState(() => _cargandoEstadoDia = true);
    final hoy = DateTime.now();
    final lecturasGalpon = await _api.lecturasGalpon(asignacion.crianzaId, asignacion.crianzaGalponId);
    final lecturasGranja = await _api.lecturasGranja(asignacion.crianzaId);
    setState(() {
      _estadoDia = _EstadoDia(
        galponCargado: lecturasGalpon.any((l) => esMismoDia(l.fecha, hoy)),
        granjaCargado: lecturasGranja.any((l) => esMismoDia(l.fecha, hoy)),
      );
      _cargandoEstadoDia = false;
    });
  }

  Future<void> _refrescar() async {
    setState(() {
      _asignaciones = _cargarAsignaciones();
    });
    await _asignaciones;
  }

  @override
  Widget build(BuildContext context) {
    final usuario = context.watch<AuthService>().usuario!;
    return Scaffold(
      appBar: AppBar(
        title: Text('Hola, ${usuario.nombre}'),
        actions: [
          IconButton(icon: const Icon(Icons.logout), onPressed: () => context.read<AuthService>().logout()),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refrescar,
        child: FutureBuilder<List<Asignacion>>(
          future: _asignaciones,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return _mensajeCentrado('No se pudo cargar tu información. Deslizá para reintentar.');
            }
            final asignacion = _asignacionActiva;
            if (asignacion == null) {
              return _mensajeCentrado('Todavía no tenés un galpón asignado en una crianza en curso.');
            }
            return _contenido(asignacion);
          },
        ),
      ),
    );
  }

  Widget _mensajeCentrado(String texto) {
    return LayoutBuilder(
      builder: (context, constraints) => SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: ConstrainedBox(
          constraints: BoxConstraints(minHeight: constraints.maxHeight),
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Text(texto, textAlign: TextAlign.center),
            ),
          ),
        ),
      ),
    );
  }

  Widget _contenido(Asignacion asignacion) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          '${asignacion.galponNombre} — Crianza #${asignacion.crianzaNumero}',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (_cargandoEstadoDia)
          const Center(child: Padding(padding: EdgeInsets.all(16), child: CircularProgressIndicator()))
        else ...[
          _tarjetaCarga(
            titulo: 'Mortandad y agua de hoy',
            yaCargado: _estadoDia.galponCargado,
            onCargar: () async {
              final ok = await Navigator.of(context).push<bool>(
                MaterialPageRoute(
                  builder: (_) => LecturaGalponFormScreen(
                    crianzaId: asignacion.crianzaId,
                    cgId: asignacion.crianzaGalponId,
                    galponNombre: asignacion.galponNombre,
                  ),
                ),
              );
              if (ok == true) await _cargarEstadoDelDia(asignacion);
            },
          ),
          const SizedBox(height: 12),
          _tarjetaCarga(
            titulo: 'Gas y electricidad de hoy (toda la granja)',
            yaCargado: _estadoDia.granjaCargado,
            onCargar: () async {
              final ok = await Navigator.of(context).push<bool>(
                MaterialPageRoute(builder: (_) => LecturaGranjaFormScreen(crianzaId: asignacion.crianzaId)),
              );
              if (ok == true) await _cargarEstadoDelDia(asignacion);
            },
          ),
        ],
      ],
    );
  }

  Widget _tarjetaCarga({required String titulo, required bool yaCargado, required VoidCallback onCargar}) {
    return Card(
      child: ListTile(
        leading: Icon(
          yaCargado ? Icons.check_circle : Icons.pending_outlined,
          color: yaCargado ? Colors.green : Colors.orange,
        ),
        title: Text(titulo),
        subtitle: Text(yaCargado ? 'Ya cargado hoy' : 'Todavía no cargaste hoy'),
        trailing: yaCargado ? null : FilledButton(onPressed: onCargar, child: const Text('Cargar')),
      ),
    );
  }
}

extension<T> on Iterable<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
