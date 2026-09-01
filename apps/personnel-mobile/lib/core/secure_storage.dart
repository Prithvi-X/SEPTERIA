import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  static final SecureStorageService _instance = SecureStorageService._internal();
  factory SecureStorageService() => _instance;
  SecureStorageService._internal();

  final _storage = const FlutterSecureStorage();
  final Map<String, String> _memoryFallback = {};

  static const String _keyToken = 'jwt_token';
  static const String _keyUserId = 'user_id';
  static const String _keyUserRole = 'user_role';
  static const String _keyUserEmail = 'user_email';

  Future<void> saveAuthData({
    required String token,
    required String userId,
    required String role,
    required String email,
  }) async {
    _memoryFallback[_keyToken] = token;
    _memoryFallback[_keyUserId] = userId;
    _memoryFallback[_keyUserRole] = role;
    _memoryFallback[_keyUserEmail] = email;
    try {
      await _storage.write(key: _keyToken, value: token);
      await _storage.write(key: _keyUserId, value: userId);
      await _storage.write(key: _keyUserRole, value: role);
      await _storage.write(key: _keyUserEmail, value: email);
    } catch (_) {}
  }

  Future<String?> getToken() async {
    try {
      final val = await _storage.read(key: _keyToken);
      if (val != null && val.isNotEmpty) return val;
    } catch (_) {}
    return _memoryFallback[_keyToken];
  }

  Future<String?> getUserId() async {
    try {
      final val = await _storage.read(key: _keyUserId);
      if (val != null && val.isNotEmpty) return val;
    } catch (_) {}
    return _memoryFallback[_keyUserId];
  }

  Future<String?> getUserRole() async {
    try {
      final val = await _storage.read(key: _keyUserRole);
      if (val != null && val.isNotEmpty) return val;
    } catch (_) {}
    return _memoryFallback[_keyUserRole];
  }

  Future<String?> getUserEmail() async {
    try {
      final val = await _storage.read(key: _keyUserEmail);
      if (val != null && val.isNotEmpty) return val;
    } catch (_) {}
    return _memoryFallback[_keyUserEmail];
  }

  Future<void> clearAuthData() async {
    _memoryFallback.clear();
    try {
      await _storage.delete(key: _keyToken);
      await _storage.delete(key: _keyUserId);
      await _storage.delete(key: _keyUserRole);
      await _storage.delete(key: _keyUserEmail);
    } catch (_) {}
  }

  Future<bool> hasValidSession() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}
