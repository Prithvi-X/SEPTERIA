import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../models/personnel_models.dart';

class RecoveryScreen extends StatefulWidget {
  const RecoveryScreen({super.key});

  @override
  State<RecoveryScreen> createState() => _RecoveryScreenState();
}

class _RecoveryScreenState extends State<RecoveryScreen> {
  final ApiService _apiService = ApiService();
  PhysiologicalTrendResponseModel? _trendsData;
  SignalQualitySummaryModel? _qualityData;
  PersonalStateModel? _personalState;
  bool _isLoading = true;
  String? _errorMessage;
  String _selectedScenario = 'A';

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
      final trends = await _apiService.getPhysiologicalTrends(days: 7);
      
      SignalQualitySummaryModel? quality;
      try {
        quality = await _apiService.getQualitySummary();
      } catch (_) {}

      PersonalStateModel? state;
      try {
        state = await _apiService.getPersonalState();
      } catch (_) {}

      setState(() {
        _trendsData = trends;
        _qualityData = quality;
        _personalState = state;
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

  Future<void> _runScenario(String code) async {
    setState(() {
      _isLoading = true;
    });
    try {
      await _apiService.triggerDemoScenario(code);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Synthetic Scenario $code executed successfully!'),
          backgroundColor: const Color(0xFF10B981),
        ),
      );
      await _fetchData();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed: ${e.toString()}'),
          backgroundColor: Colors.redAccent,
        ),
      );
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Trends & Recovery'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            onPressed: _fetchData,
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
                        const Icon(Icons.error_outline, color: Colors.redAccent, size: 40),
                        const SizedBox(height: 12),
                        Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _fetchData, child: const Text('Retry')),
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

                      // 1. Personal State & Recovery Trajectory Card (Phase 5)
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
                                    'PERSONAL RECOVERY STATE',
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF38BDF8),
                                      letterSpacing: 0.8,
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                                    decoration: BoxDecoration(
                                      color: _personalState?.trajectories.overallDirection == 'IMPROVING'
                                          ? const Color(0x3310B981)
                                          : _personalState?.trajectories.overallDirection == 'DETERIORATING'
                                              ? const Color(0x33EF4444)
                                              : const Color(0x3338BDF8),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      _personalState?.trajectories.overallDirection ?? 'STABLE',
                                      style: TextStyle(
                                        fontSize: 10,
                                        color: _personalState?.trajectories.overallDirection == 'IMPROVING'
                                            ? const Color(0xFF34D399)
                                            : _personalState?.trajectories.overallDirection == 'DETERIORATING'
                                                ? const Color(0xFFF87171)
                                                : const Color(0xFF38BDF8),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              
                              // Recovery Burden Score Bar
                              if (_personalState != null) ...[
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      'Recovery Strain Indicator: ${_personalState!.recoveryDebt.recoveryBurdenScore.toInt()} / 100',
                                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white),
                                    ),
                                    Text(
                                      _personalState!.recoveryDebt.recoveryBurdenScore > 50 ? 'Needs Attention' : 'Stable Equilibrium',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w600,
                                        color: _personalState!.recoveryDebt.recoveryBurdenScore > 50
                                            ? const Color(0xFFFBBF24)
                                            : const Color(0xFF34D399),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(4),
                                  child: LinearProgressIndicator(
                                    value: (_personalState!.recoveryDebt.recoveryBurdenScore / 100.0).clamp(0.05, 1.0),
                                    minHeight: 8,
                                    backgroundColor: const Color(0xFF334155),
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                      _personalState!.recoveryDebt.recoveryBurdenScore > 50
                                          ? const Color(0xFFF59E0B)
                                          : const Color(0xFF10B981),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 10),
                                Text(
                                  _personalState!.attributionSummary,
                                  style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8), height: 1.3),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),

                      // 2. Personal Baseline Comparison Grid
                      if (_personalState != null && _personalState!.deviations.isNotEmpty) ...[
                        const Text(
                          'PERSONAL BASELINE COMPARISONS',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF94A3B8),
                            letterSpacing: 0.8,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: _buildBaselineCard(
                                label: 'HRV (rMSSD)',
                                observed: '${_personalState!.deviations["hrv"]?.observed?.toInt() ?? 52} ms',
                                baseline: 'Baseline: ${_personalState!.deviations["hrv"]?.baselineMedian.toInt() ?? 55} ms',
                                devPct: _personalState!.deviations["hrv"]?.relativeDeviationPct,
                                icon: Icons.waves,
                                iconColor: const Color(0xFF38BDF8),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: _buildBaselineCard(
                                label: 'Sleep Hours',
                                observed: '${_personalState!.deviations["sleep"]?.observed?.toStringAsFixed(1) ?? "7.0"} hrs',
                                baseline: 'Baseline: ${_personalState!.deviations["sleep"]?.baselineMedian.toStringAsFixed(1) ?? "7.1"} hrs',
                                devPct: _personalState!.deviations["sleep"]?.relativeDeviationPct,
                                icon: Icons.bedtime,
                                iconColor: const Color(0xFFA78BFA),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            Expanded(
                              child: _buildBaselineCard(
                                label: 'Resting HR',
                                observed: '${_personalState!.deviations["resting_hr"]?.observed?.toInt() ?? 61} bpm',
                                baseline: 'Baseline: ${_personalState!.deviations["resting_hr"]?.baselineMedian.toInt() ?? 60} bpm',
                                devPct: _personalState!.deviations["resting_hr"]?.relativeDeviationPct,
                                icon: Icons.favorite,
                                iconColor: const Color(0xFFEF4444),
                                isInverse: true,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: _buildBaselineCard(
                                label: 'Activity Index',
                                observed: '${_personalState!.deviations["activity"]?.observed?.toInt() ?? 6800}',
                                baseline: 'Baseline: ${_personalState!.deviations["activity"]?.baselineMedian.toInt() ?? 7000}',
                                devPct: _personalState!.deviations["activity"]?.relativeDeviationPct,
                                icon: Icons.directions_walk,
                                iconColor: const Color(0xFF34D399),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 14),
                      ],

                      // 3. Signal Quality & Gap Banner
                      if (_qualityData != null && _qualityData!.missingIntervals.isNotEmpty) ...[
                        Card(
                          color: const Color(0xFF2A1E1E),
                          shape: RoundedRectangleBorder(
                            side: const BorderSide(color: Color(0x66EF4444)),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.all(12.0),
                            child: Row(
                              children: [
                                const Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444), size: 20),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Sensor Dropout Detected (${_qualityData!.missingIntervals.first.durationMinutes.toInt()} min gap)',
                                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFFCA5A5)),
                                      ),
                                      const SizedBox(height: 2),
                                      const Text(
                                        'Missing telemetry is tracked explicitly and not falsely reported as continuous.',
                                        style: TextStyle(fontSize: 10, color: Color(0xFFE2E8F0)),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                      ],

                      // 4. Demo Scenario Selector
                      Card(
                        color: const Color(0xFF1E293B),
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Row(
                            children: [
                              const Icon(Icons.science_outlined, color: Color(0xFFA78BFA), size: 18),
                              const SizedBox(width: 8),
                              const Text(
                                'Test Scenario:',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFCBD5E1)),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: DropdownButtonHideUnderline(
                                  child: DropdownButton<String>(
                                    value: _selectedScenario,
                                    dropdownColor: const Color(0xFF0F172A),
                                    isDense: true,
                                    style: const TextStyle(fontSize: 11, color: Colors.white),
                                    items: const [
                                      DropdownMenuItem(value: 'A', child: Text('A: Normal Baseline')),
                                      DropdownMenuItem(value: 'B', child: Text('B: Physical Exertion')),
                                      DropdownMenuItem(value: 'C', child: Text('C: Heat & Exertion')),
                                      DropdownMenuItem(value: 'D', child: Text('D: Recovery Decline')),
                                      DropdownMenuItem(value: 'E', child: Text('E: 20m Missing HRV Gap')),
                                      DropdownMenuItem(value: 'F', child: Text('F: Post-Leave Friction')),
                                      DropdownMenuItem(value: 'G', child: Text('G: Contradictory Signals')),
                                    ],
                                    onChanged: (val) {
                                      if (val != null) {
                                        setState(() {
                                          _selectedScenario = val;
                                        });
                                        _runScenario(val);
                                      }
                                    },
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),

                      // 5. 7-Day Trend Visualizations
                      if (_trendsData != null) ...[
                        const Text(
                          '7-DAY PROGRESSION CHARTS',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF94A3B8),
                            letterSpacing: 0.8,
                          ),
                        ),
                        const SizedBox(height: 12),

                        // HRV Trend Chart Card
                        _buildChartCard(
                          title: 'Heart Rate Variability (HRV ms)',
                          items: _trendsData!.trends,
                          getValue: (t) => t.hrv,
                          unit: 'ms',
                          color: const Color(0xFF38BDF8),
                        ),
                        const SizedBox(height: 12),

                        // Sleep Trend Chart Card
                        _buildChartCard(
                          title: 'Sleep Duration (Hours)',
                          items: _trendsData!.trends,
                          getValue: (t) => t.sleep,
                          unit: 'h',
                          color: const Color(0xFFA78BFA),
                        ),
                        const SizedBox(height: 12),

                        // Activity Trend Chart Card
                        _buildChartCard(
                          title: 'Daily Activity (Steps)',
                          items: _trendsData!.trends,
                          getValue: (t) => t.activity,
                          unit: '',
                          color: const Color(0xFF34D399),
                        ),
                      ],
                    ],
                  ),
                ),
    );
  }

  Widget _buildBaselineCard({
    required String label,
    required String observed,
    required String baseline,
    required double? devPct,
    required IconData icon,
    required Color iconColor,
    bool isInverse = false,
  }) {
    final dev = devPct ?? 0.0;
    final isGood = isInverse ? dev <= 0 : dev >= 0;
    
    return Card(
      color: const Color(0xFF1E293B),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: iconColor, size: 18),
                if (devPct != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1.5),
                    decoration: BoxDecoration(
                      color: isGood ? const Color(0x2210B981) : const Color(0x22EF4444),
                      borderRadius: BorderRadius.circular(3),
                    ),
                    child: Text(
                      '${dev >= 0 ? "+" : ""}${dev.toStringAsFixed(1)}%',
                      style: TextStyle(
                        fontSize: 9,
                        color: isGood ? const Color(0xFF34D399) : const Color(0xFFF87171),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              observed,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFFCBD5E1)),
            ),
            const SizedBox(height: 2),
            Text(
              baseline,
              style: const TextStyle(fontSize: 9, color: Color(0xFF64748B)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChartCard({
    required String title,
    required List<PhysiologicalTrendItemModel> items,
    required double Function(PhysiologicalTrendItemModel) getValue,
    required String unit,
    required Color color,
  }) {
    if (items.isEmpty) return const SizedBox.shrink();

    final values = items.map(getValue).toList();
    final maxVal = values.reduce((a, b) => a > b ? a : b);
    final minVal = values.reduce((a, b) => a < b ? a : b);
    final range = maxVal - minVal == 0 ? 1.0 : maxVal - minVal;

    return Card(
      color: const Color(0xFF1E293B),
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                ),
                Text(
                  '${values.last.toStringAsFixed(1)} $unit',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: color),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 70,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: items.map((item) {
                  final val = getValue(item);
                  final normalized = ((val - minVal) / range).clamp(0.2, 1.0);
                  final dateLabel = DateFormat('E').format(item.timestamp);
                  final isInferred = item.evidenceStatus == 'INFERRED';

                  return Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Container(
                            height: 48 * normalized,
                            decoration: BoxDecoration(
                              color: isInferred
                                  ? const Color(0xFFF59E0B).withOpacity(0.85)
                                  : color.withOpacity(0.85),
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            dateLabel,
                            style: const TextStyle(fontSize: 9, color: Color(0xFF64748B)),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
