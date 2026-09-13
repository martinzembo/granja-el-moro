import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/auth_service.dart';

/// Registro público — siempre crea un granjero (ver AuthService.registrarGranjero
/// y docs/modelo-datos.md: el rol admin no se autoregistra). Al confirmar,
/// deja la sesión iniciada directo, sin pasar por la pantalla de login.
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmarCtrl = TextEditingController();
  bool _passwordVisible = false;
  bool _confirmarVisible = false;
  bool _registrando = false;

  static final _emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmarCtrl.dispose();
    super.dispose();
  }

  Future<void> _registrar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _registrando = true);
    try {
      await context.read<AuthService>().registrarGranjero(
            _nombreCtrl.text.trim(),
            _emailCtrl.text.trim(),
            _passwordCtrl.text,
          );
      // AuthService ya quedó autenticado (notifyListeners cambia lo que
      // muestra _Portal en app.dart) — pero esta pantalla se abrió con un
      // push desde el login, así que sigue "encima" en la pila de
      // navegación hasta que la saquemos. Sin este pop, quedaría tapando
      // la pantalla nueva aunque el login ya haya funcionado.
      if (!mounted) return;
      Navigator.of(context).popUntil((route) => route.isFirst);
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo conectar con el servidor')),
      );
    } finally {
      if (mounted) setState(() => _registrando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Crear cuenta')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Esta cuenta va a ser de granjero — para cargar los datos '
                    'diarios de tu galpón. Si necesitás una cuenta de '
                    'administrador, pedísela al dueño de la granja.',
                    style: TextStyle(color: Colors.black54),
                  ),
                  const SizedBox(height: 24),
                  TextFormField(
                    controller: _nombreCtrl,
                    textCapitalization: TextCapitalization.words,
                    decoration: const InputDecoration(labelText: 'Nombre', border: OutlineInputBorder()),
                    validator: (v) => (v == null || v.trim().isEmpty) ? 'Ingresá tu nombre' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _emailCtrl,
                    keyboardType: TextInputType.emailAddress,
                    autocorrect: false,
                    decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'Ingresá tu email';
                      if (!_emailRegex.hasMatch(v.trim())) return 'Ese email no parece válido';
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _passwordCtrl,
                    obscureText: !_passwordVisible,
                    decoration: InputDecoration(
                      labelText: 'Contraseña',
                      border: const OutlineInputBorder(),
                      helperText: 'Mínimo 8 caracteres',
                      suffixIcon: IconButton(
                        icon: Icon(_passwordVisible ? Icons.visibility_off : Icons.visibility),
                        onPressed: () => setState(() => _passwordVisible = !_passwordVisible),
                      ),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return 'Ingresá una contraseña';
                      if (v.length < 8) return 'Tiene que tener al menos 8 caracteres';
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _confirmarCtrl,
                    obscureText: !_confirmarVisible,
                    decoration: InputDecoration(
                      labelText: 'Confirmar contraseña',
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: Icon(_confirmarVisible ? Icons.visibility_off : Icons.visibility),
                        onPressed: () => setState(() => _confirmarVisible = !_confirmarVisible),
                      ),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return 'Confirmá tu contraseña';
                      if (v != _passwordCtrl.text) return 'No coincide con la contraseña';
                      return null;
                    },
                    onFieldSubmitted: (_) => _registrar(),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _registrando ? null : _registrar,
                    child: _registrando
                        ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                        : const Text('Crear cuenta'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
