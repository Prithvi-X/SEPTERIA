import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/personnel_models.dart';
import 'login_screen.dart';
import 'privacy_screen.dart';
import 'voice_checkin_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final ApiService _apiService = ApiService();
  PersonnelMeModel? _profile;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final p = await _apiService.getPersonnelMe();
      setState(() {
        _profile = p;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleLogout() async {
    await _apiService.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Personnel Profile'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, color: Colors.redAccent, size: 40),
                        const SizedBox(height: 12),
                        Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _fetchProfile, child: const Text('Retry')),
                      ],
                    ),
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Profile Card
                      Card(
                        color: const Color(0xFF1E293B),
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            children: [
                              Container(
                                width: 56,
                                height: 56,
                                decoration: const BoxDecoration(
                                  color: Color(0x332563EB),
                                  shape: BoxShape.circle,
                                ),
                                child: const Center(
                                  child: Icon(Icons.person, color: Color(0xFF38BDF8), size: 30),
                                ),
                              ),
                              const SizedBox(height: 10),
                              Text(
                                _profile?.personnelId ?? 'P-1047',
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '${_profile?.rank ?? "Constable / GD"} • ${_profile?.force ?? "BSF"}',
                                style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Unit: ${_profile?.unitId ?? "BSF-BN-47"}',
                                style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), fontFamily: 'monospace'),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Administrative Info List
                      Card(
                        color: const Color(0xFF1E293B),
                        child: Padding(
                          padding: const EdgeInsets.all(14.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'ADMINISTRATIVE DETAILS',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8), letterSpacing: 0.8),
                              ),
                              const SizedBox(height: 10),
                              _buildInfoRow('Force / Organization', _profile?.force ?? 'BSF'),
                              const Divider(color: Color(0xFF334155), height: 16),
                              _buildInfoRow('Unit / Battalion', _profile?.unitId ?? 'BSF-BN-47'),
                              const Divider(color: Color(0xFF334155), height: 16),
                              _buildInfoRow('Posting', _profile?.posting ?? 'Border Outpost Tanot'),
                              const Divider(color: Color(0xFF334155), height: 16),
                              _buildInfoRow('Operational Status', _profile?.status ?? 'DEPLOYED'),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Navigation Actions List
                      Card(
                        color: const Color(0xFF1E293B),
                        child: Column(
                          children: [
                            ListTile(
                              leading: const Icon(Icons.privacy_tip_outlined, color: Color(0xFF38BDF8), size: 22),
                              title: const Text('Privacy & Data Center', style: TextStyle(fontSize: 13, color: Colors.white)),
                              subtitle: const Text('View RBAC data boundaries & consent policies', style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8))),
                              trailing: const Icon(Icons.chevron_right, size: 20, color: Color(0xFF64748B)),
                              onTap: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute(builder: (_) => const PrivacyScreen()),
                                );
                              },
                            ),
                            const Divider(color: Color(0xFF334155), height: 1),
                            ListTile(
                              leading: const Icon(Icons.mic_none, color: Color(0xFF34D399), size: 22),
                              title: const Text('Voluntary Voice Check-in', style: TextStyle(fontSize: 13, color: Colors.white)),
                              subtitle: const Text('Record optional natural speech sample', style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8))),
                              trailing: const Icon(Icons.chevron_right, size: 20, color: Color(0xFF64748B)),
                              onTap: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute(builder: (_) => const VoiceCheckInScreen()),
                                );
                              },
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Sign Out Button
                      OutlinedButton.icon(
                        onPressed: _handleLogout,
                        icon: const Icon(Icons.logout, color: Colors.redAccent, size: 18),
                        label: const Text('Sign Out', style: TextStyle(color: Colors.redAccent)),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          side: const BorderSide(color: Color(0xFF7F1D1D)),
                        ),
                      ),
                      const SizedBox(height: 16),

                      const Text(
                        'SEPTERIA Mobile v0.1.0 • SIH26186\nConfidential Personnel Client',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 10, color: Color(0xFF64748B), height: 1.4),
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
        Text(value, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
      ],
    );
  }
}
