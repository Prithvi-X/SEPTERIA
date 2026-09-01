import 'package:flutter/material.dart';

class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Privacy & Data Center'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header Banner
            Card(
              color: const Color(0xFF1E293B),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(
                        color: Color(0x3338BDF8),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.privacy_tip_outlined, color: Color(0xFF38BDF8), size: 24),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text(
                            'Your Data & Privacy Rights',
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                          SizedBox(height: 2),
                          Text(
                            'SEPTERIA operates on strict least-privilege RBAC standards under MHA protocols.',
                            style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Policy Points
            _buildSection(
              title: '1. Authoritative Operational Context',
              icon: Icons.shield_outlined,
              iconColor: const Color(0xFF38BDF8),
              content:
                  'Your operational posting, unit assignment, tactical duty, shift, environment, and deployment zone are authoritative facts managed by force administration. You do not manually enter these details.',
            ),
            const SizedBox(height: 12),

            _buildSection(
              title: '2. Voluntary Self-Reporting',
              icon: Icons.edit_note,
              iconColor: const Color(0xFF34D399),
              content:
                  'All wellness check-ins (stress, fatigue, sleep quality, mood, workload) and voice check-in samples are 100% voluntary. You may choose if and when to report self-assessments.',
            ),
            const SizedBox(height: 12),

            _buildSection(
              title: '3. Data Visibility & Access Matrix',
              icon: Icons.lock_outline,
              iconColor: const Color(0xFFA78BFA),
              content:
                  '• Unit Commanders: View aggregated operational deployments and duty readiness. They cannot see individual wellness check-in scores.\n• Welfare & Medical Officers: Can view authorized welfare indicators and support requests to facilitate confidential care.\n• You (Personnel): Have full access to your personal trends, operational context, and support requests.',
            ),
            const SizedBox(height: 12),

            _buildSection(
              title: '4. Confidential Welfare Support',
              icon: Icons.handshake_outlined,
              iconColor: const Color(0xFFFBBF24),
              content:
                  'Support requests submitted through this app are routed directly and confidentially to designated Welfare Officers. They do not appear on unit operational noticeboards.',
            ),
            const SizedBox(height: 12),

            _buildSection(
              title: '5. Post-Leave Transition Period',
              icon: Icons.calendar_today_outlined,
              iconColor: const Color(0xFFF97316),
              content:
                  'The 14-day post-leave reintegration period is an administrative contextual state activated upon leave return. It is designed to assist duty adaptation and is not an indicator of personal clinical risk.',
            ),
            const SizedBox(height: 24),

            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0x1A2563EB),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0x4D2563EB)),
              ),
              child: const Text(
                'SIH26186 • SEPTERIA Personnel Operations Architecture • Data Protected by End-to-End Cryptographic JWT Bearer Tokens & TLS Encryption.',
                style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8), height: 1.4),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required IconData icon,
    required Color iconColor,
    required String content,
  }) {
    return Card(
      color: const Color(0xFF1E293B),
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: iconColor, size: 18),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              content,
              style: const TextStyle(fontSize: 11, color: Color(0xFFCBD5E1), height: 1.4),
            ),
          ],
        ),
      ),
    );
  }
}
