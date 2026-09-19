import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Guarda y recupera el JWT de forma segura: Keychain en iOS,
/// EncryptedSharedPreferences en Android. Nunca se guarda un token
/// (una credencial sensible) en SharedPreferences sin cifrar.
class TokenStorage {
  static const _key = 'access_token';
  final _storage = const FlutterSecureStorage();

  Future<void> guardar(String token) => _storage.write(key: _key, value: token);

  Future<String?> obtener() => _storage.read(key: _key);

  Future<void> borrar() => _storage.delete(key: _key);
}
