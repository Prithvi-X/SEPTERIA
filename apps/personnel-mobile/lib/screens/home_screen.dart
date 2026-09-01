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
      body: _tabs[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        backgroundColor: const Color(0xFF0B132B),
        indicatorColor: const Color(0x4D2563EB),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: Color(0xFF38BDF8)),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.trending_up),
            selectedIcon: Icon(Icons.trending_up, color: Color(0xFF38BDF8)),
            label: 'My Trends',
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
            label: 'Profile',
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
      setState(() {
        _data = res;
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('SEPTERIA • My Recovery'),
        actions: [
          IconButton(
            icon: const Icon(Icons.privacy_tip_outlined, size: 20),
            tooltip: 'Privacy Center',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const PrivacyScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            tooltip: 'Refresh',
            onPressed: _fetchHomeData,
          ),
          IconButton(
            icon: const Icon(Icons.logout, size: 20),
            tooltip: 'Sign Out',
            onPressed: () async {
              await _apiService.logout();
              if (mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                  (route) => false,
                );
              }
            },
          ),
        ],
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
                        const Icon(Icons.cloud_off, color: Colors.redAccent, size: 40),
                        const SizedBox(height: 12),
                        Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _fetchHomeData, child: const Text('Retry Connection')),
                        const SizedBox(height: 12),
                        OutlinedButton.icon(
                          icon: const Icon(Icons.logout, size: 16),
                          label: const Text('Sign Out & Re-Login'),
                          onPressed: () async {
                            await _apiService.logout();
                            if (mounted) {
                              Navigator.of(context).pushAndRemoveUntil(
                                MaterialPageRoute(builder: (_) => const LoginScreen()),
                                (route) => false,
                              );
                            }
                          },
                        ),
                      ],
                    ),
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Synthetic Demonstration Data Banner
                      Container(
                        margin: const EdgeInsets.only(bottom: 14),
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0x33F59E0B),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0x66F59E0B)),
                        ),
                        child: Row(
                          children: const [
                            Icon(Icons.info_outline, color: Color(0xFFFCD34D), size: 14),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'DEMO MODE • SYNTHETIC DEMONSTRATION DATA (SIH26186)',
                                style: TextStyle(
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFFFCD34D),
                                  letterSpacing: 0.4,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),

                      // User Welcome Banner
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Jawan ${_data?.personnelId ?? "P-1047"}',
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              Text(
                                '${_data?.rank ?? "Constable / GD"} • ${_data?.force ?? "BSF"} (${_data?.unitId ?? "Unit 47"})',
                                style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0x3310B981),
                              borderRadius: BorderRadius.circular(6),
                              border: Border.all(color: const Color(0xFF059669)),
                            ),
                            child: const Text(
                              'ACTIVE DUTY',
                              style: TextStyle(fontSize: 10, color: Color(0xFF34D399), fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Card 0: Edge Hardware & Sync Status (Phase 9)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0F172A),
                          borderRadius: BorderRadius.circular(10),
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
                                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white),
                                    ),
                                    Text(
                                      'Tactical Band v1 • BLE',
                                      style: TextStyle(fontSize: 9, color: Color(0xFF94A3B8)),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            Row(
                              children: [
                                const Icon(Icons.check_circle_outline, color: Color(0xFF34D399), size: 16),
                                const SizedBox(width: 6),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.end,
                                  children: const [
                                    Text(
                                      'SYNC: Synced',
                                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF34D399)),
                                    ),
                                    Text(
                                      'Updated Just Now',
                                      style: TextStyle(fontSize: 9, color: Color(0xFF64748B)),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Card 1: Authoritative Operational Context (Read-Only)
                      Card(
                        color: const Color(0xFF1E293B),
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                    'AUTHORITATIVE OPERATIONAL CONTEXT',
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      letterSpacing: 0.8,
                                      color: Color(0xFF38BDF8),
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: const Color(0x2238BDF8),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: const Text(
                                      'READ-ONLY',
                                      style: TextStyle(fontSize: 8, color: Color(0xFF38BDF8), fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 10),
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: _data?.authoritativeContext.zone.contains('1') == true
                                          ? const Color(0x33EF4444)
                                          : _data?.authoritativeContext.zone.contains('2') == true
                                              ? const Color(0x33F59E0B)
                                              : const Color(0x33A855F7),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      _data?.authoritativeContext.zone ?? 'Zone 2',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: _data?.authoritativeContext.zone.contains('1') == true
                                            ? const Color(0xFFFCA5A5)
                                            : _data?.authoritativeContext.zone.contains('2') == true
                                                ? const Color(0xFFFCD34D)
                                                : const Color(0xFFD8B4FE),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _data?.authoritativeContext.zone.contains('2') == true
                                          ? 'Border / Remote / Extreme Environment'
                                          : _data?.authoritativeContext.zone.contains('1') == true
                                              ? 'Active Operations / QRT Sector'
                                              : 'Incident Recovery Context',
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Duty: ${_data?.authoritativeContext.dutyType ?? "Border Patrol"} • Shift: ${_data?.authoritativeContext.shift ?? "Night (20:00 - 04:00)"}',
                                style: const TextStyle(fontSize: 12, color: Color(0xFFCBD5E1)),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Location: ${_data?.authoritativeContext.location ?? "Tanot Forward Line B"} (${_data?.authoritativeContext.environment ?? "High Heat / Extreme Arid"})',
                                style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                              ),
                              const SizedBox(height: 10),
                              const Text(
                                'Context managed by authorized force administration.',
                                style: TextStyle(fontSize: 10, fontStyle: FontStyle.italic, color: Color(0xFF64748B)),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Card 2: Active Temporary Assignment Countdown (If Active)
                      if (_data?.authoritativeContext.temporary == true) ...[
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: const Color(0x2A7C3AED),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFF7C3AED)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.timer_outlined, color: Color(0xFFA78BFA), size: 28),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'TEMPORARY ASSIGNMENT ACTIVE',
                                      style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFFA78BFA), letterSpacing: 0.6),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      _data?.authoritativeContext.remainingDurationFormatted ?? '5d 14h remaining',
                                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white, fontFamily: 'monospace'),
                                    ),
                                    const SizedBox(height: 2),
                                    const Text(
                                      'Auto-reverts to baseline station upon expiry.',
                                      style: TextStyle(fontSize: 10, color: Color(0xFFCBD5E1)),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),
                      ],

                      // Card 3: Post-Leave Transition Period (If Active)
                      if (_data?.leaveStatus == 'POST_LEAVE_TRANSITION') ...[
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: const Color(0x2AF59E0B),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFF59E0B)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                    'POST-LEAVE TRANSITION',
                                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFFBBF24), letterSpacing: 0.6),
                                  ),
                                  Text(
                                    'DAY ${_data?.postLeaveDayCount ?? 3} / 14',
                                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              ClipRRect(
                                borderRadius: BorderRadius.circular(4),
                                child: LinearProgressIndicator(
                                  value: ((_data?.postLeaveDayCount ?? 3) / 14.0).clamp(0.0, 1.0),
                                  backgroundColor: const Color(0xFF334155),
                                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFBBF24)),
                                  minHeight: 6,
                                ),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'Contextual reintegration window activated following leave return. Assisting gradual duty adaptation.',
                                style: TextStyle(fontSize: 11, color: Color(0xFFCBD5E1)),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),
                      ],

                      // Card 4: Daily Wellness Summary & Quick Action
                      Card(
                        color: const Color(0xFF1E293B),
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'TODAY\'S VOLUNTARY WELLNESS',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF34D399), letterSpacing: 0.8),
                              ),
                              const SizedBox(height: 10),
                              Row(
                                children: [
                                  Container(
                                    width: 44,
                                    height: 44,
                                    decoration: const BoxDecoration(
                                      color: Color(0x3334D399),
                                      shape: BoxShape.circle,
                                    ),
                                    child: const Center(
                                      child: Icon(Icons.favorite, color: Color(0xFF34D399), size: 22),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: const [
                                        Text(
                                          'Recovery Equilibrium Observed',
                                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white),
                                        ),
                                        SizedBox(height: 2),
                                        Text(
                                          'Keep track of fatigue and workload adaptation.',
                                          style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 14),
                              ElevatedButton.icon(
                                onPressed: () {
                                  // Switch to Wellness Tab
                                  final homeState = context.findAncestorStateOfType<_HomeScreenState>();
                                  if (homeState != null) {
                                    homeState.setState(() {
                                      homeState._currentIndex = 2; // Wellness Tab
                                    });
                                  }
                                },
                                icon: const Icon(Icons.edit_note, size: 16),
                                label: const Text('Complete Daily Wellness Check-in'),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Card 5: Private Contextual Recovery Guidance (Static Placeholder)
                      Card(
                        color: const Color(0xFF1E293B),
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: const [
                                  Text(
                                    'PRIVATE RECOVERY GUIDANCE',
                                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8), letterSpacing: 0.8),
                                  ),
                                  Text(
                                    'DEMO REMINDERS',
                                    style: TextStyle(fontSize: 9, color: Color(0xFF64748B), fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                '• High-Heat Sector: Ensure consistent electrolyte hydration during day shifts.\n• Night Duty Adaptation: Maintain dark, quiet rest intervals between rotations.',
                                style: TextStyle(fontSize: 11, color: Color(0xFFCBD5E1), height: 1.4),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Quick Action Buttons
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute(builder: (_) => const VoiceCheckInScreen()),
                                );
                              },
                              icon: const Icon(Icons.mic_none, size: 16, color: Color(0xFF38BDF8)),
                              label: const Text('Voice Check-in', style: TextStyle(fontSize: 11, color: Color(0xFF38BDF8))),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 10),
                                side: const BorderSide(color: Color(0xFF2563EB)),
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () {
                                final homeState = context.findAncestorStateOfType<_HomeScreenState>();
                                if (homeState != null) {
                                  homeState.setState(() {
                                    homeState._currentIndex = 3; // Support Tab
                                  });
                                }
                              },
                              icon: const Icon(Icons.handshake_outlined, size: 16, color: Color(0xFFFBBF24)),
                              label: const Text('Welfare Support', style: TextStyle(fontSize: 11, color: Color(0xFFFBBF24))),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 10),
                                side: const BorderSide(color: Color(0xFFD97706)),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
    );
  }
}
