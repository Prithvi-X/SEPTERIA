import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/personnel_models.dart';

class RecoveryScreen extends StatefulWidget {
  const RecoveryScreen({super.key});

  @override
  State<RecoveryScreen> createState() => _RecoveryScreenState();
}

class _RecoveryScreenState extends State<RecoveryScreen> {
  final ApiService _apiService = ApiService();
  PersonalStateModel? _personalState;
  PersonnelMeModel? _data;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final state = await _apiService.getPersonalState();
      final res = await _apiService.getPersonnelMe();

      setState(() {
        _personalState = state;
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
    // Logic for presentation
    final isAmber = (_personalState?.recoveryDebt.recoveryBurdenScore ?? 0) > 50;
    
    // Fallback if data is missing
    final hasEnoughData = _personalState != null && _data != null;
    
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: const Text('My Recovery', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 22, color: Color(0xFF94A3B8)),
            onPressed: _fetchData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
          : _errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.cloud_off, color: Color(0xFFEF4444), size: 40),
                      const SizedBox(height: 12),
                      const Text('Could not load recovery data.', style: TextStyle(color: Color(0xFF94A3B8))),
                      TextButton(onPressed: _fetchData, child: const Text('Retry', style: TextStyle(color: Color(0xFF38BDF8)))),
                    ],
                  ),
                )
              : !hasEnoughData
                ? _buildNotEnoughData()
                : RefreshIndicator(
                    onRefresh: _fetchData,
                    color: const Color(0xFF38BDF8),
                    backgroundColor: const Color(0xFF1E293B),
                    child: SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (isAmber) _buildAttentionState() else _buildStableState(),
                          
                          const SizedBox(height: 24),
                          
                          const Text('7-DAY TREND', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
                          const SizedBox(height: 12),
                          _buildTrendChart(isAmber),

                          const SizedBox(height: 24),

                          const Text('RECENT INDICATORS', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
                          const SizedBox(height: 12),
                          _buildIndicatorRow('Sleep', 'Less than your recent average', Icons.bedtime),
                          const Divider(color: Color(0xFF1E293B)),
                          _buildIndicatorRow('Rest', 'Below your usual range', Icons.favorite_border),
                          const Divider(color: Color(0xFF1E293B)),
                          _buildIndicatorRow('Activity', 'Consistent with deployment', Icons.directions_walk),
                        ],
                      ),
                    ),
                  ),
    );
  }

  Widget _buildStableState() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'RECOVERY LOOKS STABLE',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF10B981)),
        ),
        const SizedBox(height: 12),
        const Text(
          'Your recent indicators are consistent with your usual pattern.',
          style: TextStyle(fontSize: 16, color: Color(0xFFE2E8F0), height: 1.4),
        ),
      ],
    );
  }

  Widget _buildAttentionState() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'RECOVERY NEEDS ATTENTION',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFFF59E0B)),
        ),
        const SizedBox(height: 24),
        const Text(
          'WHAT CHANGED?',
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0),
        ),
        const SizedBox(height: 8),
        Text(
          _personalState?.attributionSummary ?? 'Recovery has been trending lower over the last several days.',
          style: const TextStyle(fontSize: 15, color: Color(0xFFE2E8F0), height: 1.4),
        ),
        const SizedBox(height: 24),
        const Text(
          'WHAT CAN HELP?',
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0),
        ),
        const SizedBox(height: 8),
        const Text(
          'Consider taking advantage of your next available recovery period or completing today\'s wellness check-in.',
          style: TextStyle(fontSize: 15, color: Color(0xFFE2E8F0), height: 1.4),
        ),
      ],
    );
  }

  Widget _buildNotEnoughData() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.data_usage, color: Color(0xFF475569), size: 48),
            SizedBox(height: 16),
            Text(
              'NOT ENOUGH DATA',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8)),
            ),
            SizedBox(height: 8),
            Text(
              'We couldn\'t make a reliable recovery assessment right now.\n\nYour other wellness features are still available.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Color(0xFF64748B), height: 1.4),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrendChart(bool isAmber) {
    return Container(
      height: 120,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Stack(
        children: [
          // Fake simple sparkline for visual representation as requested ("calm line visualization")
          CustomPaint(
            size: Size.infinite,
            painter: _SimpleTrendPainter(color: isAmber ? const Color(0xFFF59E0B) : const Color(0xFF10B981), isDownward: isAmber),
          ),
        ],
      ),
    );
  }

  Widget _buildIndicatorRow(String title, String subtitle, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF38BDF8), size: 24),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SimpleTrendPainter extends CustomPainter {
  final Color color;
  final bool isDownward;

  _SimpleTrendPainter({required this.color, required this.isDownward});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(0.5)
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();
    final step = size.width / 6;
    
    // Generate a smooth curve. If downward, curve goes down over 7 points
    final points = isDownward 
        ? [0.2, 0.25, 0.3, 0.5, 0.7, 0.85, 0.9] // Y values (lower is higher on screen)
        : [0.5, 0.45, 0.5, 0.4, 0.45, 0.5, 0.4];

    path.moveTo(0, size.height * points[0]);
    for (int i = 1; i < 7; i++) {
      final x = step * i;
      final y = size.height * points[i];
      // simplified bezier for visual smoothness
      final prevX = step * (i - 1);
      final prevY = size.height * points[i - 1];
      path.quadraticBezierTo(
        prevX + (x - prevX) / 2, prevY, 
        x, y
      );
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
