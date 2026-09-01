import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/personnel_models.dart';
import 'recovery_screen.dart';
import 'wellness_screen.dart';
import 'support_screen.dart';
import 'profile_screen.dart';
import 'voice_checkin_screen.dart';
import 'privacy_screen.dart';
import 'login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _tabs = [
    const _HomeDashboardTab(),
    const RecoveryScreen(),
    const WellnessScreen(),
    const SupportScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: _tabs[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        backgroundColor: const Color(0xFF0B132B),
        indicatorColor: const Color(0x3338BDF8),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: Color(0xFF38BDF8)),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.trending_up),
            selectedIcon: Icon(Icons.trending_up, color: Color(0xFF38BDF8)),
            label: 'Recovery',
          ),
          NavigationDestination(
            icon: Icon(Icons.edit_note),
            selectedIcon: Icon(Icons.edit_note, color: Color(0xFF38BDF8)),
            label: 'Wellness',
          ),
          NavigationDestination(
            icon: Icon(Icons.handshake_outlined),
            selectedIcon: Icon(Icons.handshake, color: Color(0xFF38BDF8)),
            label: 'Support',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person, color: Color(0xFF38BDF8)),
            label: 'More',
          ),
        ],
      ),
    );
  }
}

class _HomeDashboardTab extends StatefulWidget {
  const _HomeDashboardTab();

  @override
  State<_HomeDashboardTab> createState() => _HomeDashboardTabState();
}

class _HomeDashboardTabState extends State<_HomeDashboardTab> {
  final ApiService _apiService = ApiService();
  PersonnelMeModel? _data;
  PersonalStateModel? _state;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchHomeData();
  }

  Future<void> _fetchHomeData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final res = await _apiService.getPersonnelMe();
      PersonalStateModel? stateRes;
      try {
        stateRes = await _apiService.getPersonalState();
      } catch (_) {}

      setState(() {
        _data = res;
        _state = stateRes;
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

  @override
  Widget build(BuildContext context) {
    // Determine status logic based on API data
    final isAmber = (_state?.recoveryDebt.recoveryBurdenScore ?? 0) > 50;
    final statusColor = isAmber ? const Color(0xFFF59E0B) : const Color(0xFF10B981);
    final statusTitle = isAmber ? 'NEEDS ATTENTION' : 'STABLE';
    final statusDesc = isAmber 
        ? 'Your recent recovery indicators differ from your usual pattern.' 
        : 'Your recent indicators are consistent with your usual pattern.';

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: const Text('My Recovery', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 22, color: Color(0xFF94A3B8)),
            tooltip: 'Refresh',
            onPressed: _fetchHomeData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
          : _errorMessage != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.cloud_off, color: Color(0xFFEF4444), size: 40),
                        const SizedBox(height: 12),
                        Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 14, color: Color(0xFF94A3B8))),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _fetchHomeData, 
                          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF334155)),
                          child: const Text('Retry Connection', style: TextStyle(color: Colors.white)),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _fetchHomeData,
                  color: const Color(0xFF38BDF8),
                  backgroundColor: const Color(0xFF1E293B),
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Subtle Demo Indicator
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            Text(
                              'DEMO MODE · SYNTHETIC DATA',
                              style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 0.5),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),

                        // Welcome & Duty Context
                        Text(
                          'Good evening, ${_data?.personnelId ?? "P-1047"}',
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                        const SizedBox(height: 16),
                        
                        // Edge Hardware & Sync Status
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E293B),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: const Color(0xFF334155)),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.bluetooth_connected, color: Color(0xFF38BDF8), size: 18),
                                  const SizedBox(width: 8),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: const [
                                      Text(
                                        'DEVICE: Connected',
                                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                                      ),
                                      Text(
                                        'Sync: Just now',
                                        style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF10B981).withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: const Text('SQI: EXCELLENT', style: TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold)),
                              )
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),

                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E293B),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: const Color(0xFF334155)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _data?.authoritativeContext.dutyType ?? 'Night Patrol',
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${_data?.authoritativeContext.zone ?? "Zone 2"} · ${_data?.authoritativeContext.location ?? "Tanot Forward Sector"}',
                                style: const TextStyle(fontSize: 14, color: Color(0xFF94A3B8)),
                              ),
                              const SizedBox(height: 12),
                              const Divider(color: Color(0xFF334155)),
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  const Icon(Icons.timer_outlined, size: 16, color: Color(0xFF38BDF8)),
                                  const SizedBox(width: 8),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text('Temporary assignment', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: Color(0xFFE2E8F0))),
                                      const SizedBox(height: 2),
                                      Text(_data?.authoritativeContext.remainingDurationFormatted ?? '5d 13h remaining', style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
                                    ],
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 32),

                        // Your Recovery
                        const Text('YOUR RECOVERY', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
                        const SizedBox(height: 12),
                        
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E293B),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: const Color(0xFF334155)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    width: 10,
                                    height: 10,
                                    decoration: BoxDecoration(color: statusColor, shape: BoxShape.circle),
                                  ),
                                  const SizedBox(width: 10),
                                  Text(
                                    statusTitle,
                                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: statusColor, letterSpacing: 0.5),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(statusDesc, style: const TextStyle(fontSize: 14, color: Color(0xFFE2E8F0), height: 1.4)),
                              const SizedBox(height: 16),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  _buildCompactTrend(
                                    'HRV', 
                                    '${_state?.deviations['hrv']?.observed?.toStringAsFixed(0) ?? '52'}ms',
                                    isAmber ? Icons.arrow_downward : Icons.arrow_forward, 
                                    isAmber ? const Color(0xFFEF4444) : const Color(0xFF94A3B8)
                                  ),
                                  _buildCompactTrend(
                                    'Sleep', 
                                    '${_state?.deviations['sleep']?.observed?.toStringAsFixed(1) ?? '6.2'}h',
                                    isAmber ? Icons.arrow_downward : Icons.arrow_upward, 
                                    isAmber ? const Color(0xFFEF4444) : const Color(0xFF10B981)
                                  ),
                                  _buildCompactTrend(
                                    'Resting HR', 
                                    '${_state?.deviations['resting_hr']?.observed?.toStringAsFixed(0) ?? '65'}bpm',
                                    isAmber ? Icons.arrow_upward : Icons.arrow_forward, 
                                    isAmber ? const Color(0xFFF59E0B) : const Color(0xFF94A3B8)
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 32),

                        // Actions
                        const Text('WHAT YOU CAN DO', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
                        const SizedBox(height: 12),
                        
                        _buildActionRow(
                          icon: Icons.trending_up, 
                          title: 'View recovery', 
                          onTap: () {
                            final homeState = context.findAncestorStateOfType<_HomeScreenState>();
                            homeState?.setState(() => homeState._currentIndex = 1);
                          }
                        ),
                        const SizedBox(height: 8),
                        _buildActionRow(
                          icon: Icons.edit_note, 
                          title: 'Daily wellness check-in', 
                          onTap: () {
                            final homeState = context.findAncestorStateOfType<_HomeScreenState>();
                            homeState?.setState(() => homeState._currentIndex = 2);
                          }
                        ),

                        const SizedBox(height: 32),

                        const Text('NEED SUPPORT?', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
                        const SizedBox(height: 12),
                        
                        _buildActionRow(
                          icon: Icons.handshake_outlined, 
                          title: 'Request confidential support', 
                          onTap: () {
                            final homeState = context.findAncestorStateOfType<_HomeScreenState>();
                            homeState?.setState(() => homeState._currentIndex = 3);
                          }
                        ),

                        const SizedBox(height: 32),

                        // Voice
                        Center(
                          child: TextButton.icon(
                            onPressed: () {
                              Navigator.of(context).push(MaterialPageRoute(builder: (_) => const VoiceCheckInScreen()));
                            },
                            icon: const Icon(Icons.mic_none, size: 18, color: Color(0xFF94A3B8)),
                            label: const Text('Voice check-in', style: TextStyle(fontSize: 14, color: Color(0xFF94A3B8))),
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildCompactTrend(String label, IconData icon, Color color) {
    return Row(
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
        const SizedBox(width: 4),
        Icon(icon, size: 14, color: color),
      ],
    );
  }

  Widget _buildActionRow({required IconData icon, required String title, required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFF334155)),
        ),
        child: Row(
          children: [
            Icon(icon, size: 20, color: const Color(0xFF38BDF8)),
            const SizedBox(width: 16),
            Expanded(
              child: Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Colors.white)),
            ),
            const Icon(Icons.chevron_right, size: 20, color: Color(0xFF64748B)),
          ],
        ),
      ),
    );
  }
}
