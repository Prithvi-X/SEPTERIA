class AppConstants {
  static const String appName = 'SEPTERIA';
  static const String appSubtitle = 'Personnel Welfare & Stress Monitoring';
  static const String sihCode = 'SIH26186';
  
  // Production / Compile-time API URL (--dart-define=API_BASE_URL=https://your-backend.up.railway.app/api/v1)
  static const String envApiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
  static const String defaultApiBaseUrl = 'http://10.0.2.2:8000/api/v1'; // Android emulator localhost
  static const String localApiBaseUrl = 'http://127.0.0.1:8000/api/v1';  // iOS / Web / Desktop Fallback

  // Shared Enums
  static const String rolePersonnel = 'personnel';
}
