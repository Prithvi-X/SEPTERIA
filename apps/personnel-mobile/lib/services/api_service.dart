import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../core/secure_storage.dart';
import '../models/user_model.dart';
import '../models/personnel_models.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final SecureStorageService _storage = SecureStorageService();

  String get baseUrl {
    if (AppConstants.envApiBaseUrl.isNotEmpty) {
      return AppConstants.envApiBaseUrl;
    }
    if (kIsWeb) {
      return AppConstants.localApiBaseUrl;
    }
    try {
      if (Platform.isAndroid) {
        return AppConstants.defaultApiBaseUrl;
      }
    } catch (_) {
      // Platform unsupported or testing environment
    }
    return AppConstants.localApiBaseUrl;
  }

  Future<Map<String, String>> _getHeaders({bool withAuth = true}) async {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (withAuth) {
      final token = await _storage.getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  // Health Check
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: await _getHeaders(withAuth: false),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'ok';
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  // Login
  Future<UserModel> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: await _getHeaders(withAuth: false),
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['access_token'] as String;
      final userJson = data['user'] as Map<String, dynamic>;
      final user = UserModel.fromJson(userJson);

      await _storage.saveAuthData(
        token: token,
        userId: user.id,
        role: user.role,
        email: user.email,
      );

      return user;
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Login failed');
    }
  }

  // Get Current Authenticated Personnel & Read-Only Operational Context
  Future<PersonnelMeModel> getPersonnelMe() async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      return PersonnelMeModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch personal profile.');
    }
  }

  // Get Voluntary Wellness Check-in History
  Future<List<WellnessRecordModel>> getWellnessHistory({int limit = 50}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me/wellness?limit=$limit'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List;
      return list.map((item) => WellnessRecordModel.fromJson(item)).toList();
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch wellness history.');
    }
  }

  // Submit Voluntary Wellness Check-in
  Future<WellnessRecordModel> submitWellnessCheckIn({
    required int stress,
    required int fatigue,
    required int sleepQuality,
    required int mood,
    int workload = 3,
    String? notes,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/personnel/me/wellness'),
      headers: await _getHeaders(withAuth: true),
      body: jsonEncode({
        'stress': stress,
        'fatigue': fatigue,
        'sleep_quality': sleepQuality,
        'mood': mood,
        'workload': workload,
        'notes': notes,
      }),
    );

    if (response.statusCode == 201) {
      return WellnessRecordModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to submit wellness check-in.');
    }
  }

  // Get Physiological Recovery Trends
  Future<PhysiologicalTrendResponseModel> getPhysiologicalTrends({int days = 7}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me/trends?days=$days'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      return PhysiologicalTrendResponseModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch physiological trends.');
    }
  }

  // Get Signal Quality & Completeness Summary
  Future<SignalQualitySummaryModel> getQualitySummary() async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me/quality'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      return SignalQualitySummaryModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch signal quality summary.');
    }
  }

  // Trigger Synthetic Demo Scenario
  Future<Map<String, dynamic>> triggerDemoScenario(String scenarioCode) async {
    final response = await http.post(
      Uri.parse('$baseUrl/physiology/demo/scenario'),
      headers: await _getHeaders(withAuth: true),
      body: jsonEncode({
        'scenario_code': scenarioCode,
        'personnel_id': 'P-1047',
        'days': 7,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to trigger demo scenario.');
    }
  }

  // Submit Confidential Welfare Support Request
  Future<SupportRequestModel> submitSupportRequest({
    required String urgency,
    String? note,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/personnel/me/support'),
      headers: await _getHeaders(withAuth: true),
      body: jsonEncode({
        'urgency': urgency,
        'note': note,
      }),
    );

    if (response.statusCode == 201) {
      return SupportRequestModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to submit support request.');
    }
  }

  // Get Support Requests
  Future<List<SupportRequestModel>> getSupportRequests() async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me/support'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List;
      return list.map((item) => SupportRequestModel.fromJson(item)).toList();
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch support requests.');
    }
  }

  // Submit Voice Check-in Consent & Metadata
  Future<Map<String, dynamic>> submitVoiceCheckIn({
    required bool consentGiven,
    int durationSeconds = 20,
    String? notes,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/personnel/me/voice-check-in'),
      headers: await _getHeaders(withAuth: true),
      body: jsonEncode({
        'consent_given': consentGiven,
        'duration_seconds': durationSeconds,
        'notes': notes,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to record voice check-in.');
    }
  }

  // Get Personal Baseline Metrics (Phase 5)
  Future<PersonalBaselineModel> getPersonalBaseline() async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me/baseline'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      return PersonalBaselineModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch personal baseline.');
    }
  }

  // Get Current Personal State Snapshot (Phase 5)
  Future<PersonalStateModel> getPersonalState() async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me/state'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      return PersonalStateModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch personal state snapshot.');
    }
  }

  // Get Multi-Horizon Trajectory Summary (Phase 5)
  Future<TrajectorySummaryModel> getTrajectorySummary() async {
    final response = await http.get(
      Uri.parse('$baseUrl/personnel/me/trajectory'),
      headers: await _getHeaders(withAuth: true),
    );

    if (response.statusCode == 200) {
      return TrajectorySummaryModel.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to fetch trajectory summary.');
    }
  }

  // Logout
  Future<void> logout() async {
    await _storage.clearAuthData();
  }
}
