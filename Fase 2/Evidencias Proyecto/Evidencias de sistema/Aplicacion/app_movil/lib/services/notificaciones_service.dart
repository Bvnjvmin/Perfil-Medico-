// ignore_for_file: deprecated_member_use
import 'dart:async';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'api_service.dart';
import 'token_storage.dart';

/// Notificaciones push con Firebase Cloud Messaging (HU 9).
///
/// - Al iniciar sesión pide el permiso, obtiene el token de este celular y lo registra en
///   el backend (`POST /dispositivos`).
/// - Al cerrar sesión lo quita (`DELETE /dispositivos/{token}`).
/// - Con la app cerrada o en segundo plano, Android muestra la notificación solo.
/// - Con la app abierta, se muestra un aviso (SnackBar) encima de la pantalla actual.
///
/// Si Firebase no está configurado (falta `google-services.json`), todo esto se desactiva
/// sin romper la app: los avisos siguen viéndose en la pantalla Avisos.
class NotificacionesService {
  NotificacionesService._();
  static final NotificacionesService instance = NotificacionesService._();

  /// Se asigna a `MaterialApp.scaffoldMessengerKey` para poder mostrar avisos desde aquí.
  static final GlobalKey<ScaffoldMessengerState> mensajeroKey =
      GlobalKey<ScaffoldMessengerState>();

  final _api = ApiService();
  final _tokenStorage = TokenStorage();

  bool _firebaseListo = false;
  bool _escuchando = false;
  String? _tokenFcm;

  /// Indica si Firebase se inició bien (hay push disponible).
  bool get disponible => _firebaseListo;

  /// Se llama una vez al abrir la app, desde `main()`.
  Future<void> iniciarFirebase() async {
    try {
      await Firebase.initializeApp();
      _firebaseListo = true;
    } catch (e) {
      debugPrint('Push desactivado: Firebase no está configurado ($e)');
    }
  }

  /// Registra este celular para el usuario con sesión [jwt]. No espera ni lanza errores.
  void registrar(String jwt) => unawaited(_registrar(jwt));

  Future<void> _registrar(String jwt) async {
    if (!_firebaseListo) return;
    try {
      final mensajero = FirebaseMessaging.instance;
      final permiso = await mensajero.requestPermission();
      if (permiso.authorizationStatus == AuthorizationStatus.denied) {
        debugPrint('Push: el usuario no dio permiso para notificaciones');
        return;
      }
      final tokenFcm = await mensajero.getToken();
      if (tokenFcm == null) return;
      _tokenFcm = tokenFcm;
      await _api.registrarDispositivo(jwt, tokenFcm);
      _escuchar();
    } catch (e) {
      debugPrint('Push: no se pudo registrar el dispositivo ($e)');
    }
  }

  void _escuchar() {
    if (_escuchando) return;
    _escuchando = true;
    // Firebase puede cambiar el token del celular: se vuelve a registrar.
    FirebaseMessaging.instance.onTokenRefresh.listen((nuevo) async {
      final jwt = await _tokenStorage.obtener();
      if (jwt == null) return;
      _tokenFcm = nuevo;
      try {
        await _api.registrarDispositivo(jwt, nuevo);
      } catch (e) {
        debugPrint('Push: no se pudo actualizar el token ($e)');
      }
    });
    // Con la app abierta Android no muestra la notificación: se muestra un aviso en pantalla.
    FirebaseMessaging.onMessage.listen(_mostrarEnPrimerPlano);
  }

  void _mostrarEnPrimerPlano(RemoteMessage mensaje) {
    final aviso = mensaje.notification;
    if (aviso == null) return;
    final texto = [
      if (aviso.title != null) aviso.title!,
      if (aviso.body != null) aviso.body!,
    ].join(': ');
    mensajeroKey.currentState
      ?..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(content: Text(texto), duration: const Duration(seconds: 6)),
      );
  }

  /// Quita este celular del usuario (al cerrar sesión). No lanza errores.
  Future<void> quitar(String jwt) async {
    if (!_firebaseListo) return;
    try {
      final tokenFcm =
          _tokenFcm ?? await FirebaseMessaging.instance.getToken();
      if (tokenFcm != null) {
        await _api.quitarDispositivo(jwt, tokenFcm);
      }
      await FirebaseMessaging.instance.deleteToken();
    } catch (e) {
      debugPrint('Push: no se pudo quitar el dispositivo ($e)');
    }
    _tokenFcm = null;
  }
}
