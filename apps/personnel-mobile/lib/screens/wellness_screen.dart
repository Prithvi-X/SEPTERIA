import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../models/personnel_models.dart';

class WellnessScreen extends StatefulWidget {
  const WellnessScreen({super.key});

  @override
  State<WellnessScreen> createState() => _WellnessScreenState();
}

class _WellnessScreenState extends State<WellnessScreen> {
  final ApiService _apiService = ApiService();

  int _stress = 3;
  int _fatigue = 3;
  int _sleepQuality = 3;
  int _mood = 3;
  int _workload = 3;
  final TextEditingController _notesController = TextEditingController();

  bool _isSubmitting = false;
  bool _isLoadingHistory = true;
  List<WellnessRecordModel> _history = [];
  String? _successMessage;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    setState(() {
      _isLoadingHistory = true;
    });

    try {
      final records = await _apiService.getWellnessHistory();
      setState(() {
        _history = records;
      });
    } catch (e) {
      // Ignored for now or logged
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingHistory = false;
        });
      }
    }
  }

  Future<void> _submitCheckIn() async {
    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final record = await _apiService.submitWellnessCheckIn(
        stress: _stress,
        fatigue: _fatigue,
        sleepQuality: _sleepQuality,
        mood: _mood,
        workload: _workload,
        notes: _notesController.text.trim().isNotEmpty ? _notesController.text.trim() : null,
      );

      setState(() {
        _successMessage = 'Wellness check-in recorded successfully.';
        _history.insert(0, record);
        _notesController.clear();
        _stress = 3;
        _fatigue = 3;
        _sleepQuality = 3;
        _mood = 3;
        _workload = 3;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voluntary Wellness Check-in'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Check-in Form Card
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
                          'DAILY SELF-REPORTING',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF38BDF8),
                            letterSpacing: 0.8,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0x3310B981),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: const Text(
                            'VOLUNTARY & PRIVATE',
                            style: TextStyle(fontSize: 9, color: Color(0xFF34D399), fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'How are you feeling today?',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Quick 1–5 self-assessment to monitor your personal recovery and workload.',
                      style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                    ),
                    const SizedBox(height: 16),

                    if (_successMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: const Color(0x3310B981),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFF059669)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.check_circle, color: Color(0xFF34D399), size: 16),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _successMessage!,
                                style: const TextStyle(color: Color(0xFF34D399), fontSize: 11),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),
                    ],

                    if (_errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: const Color(0x667F1D1D),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFFB91C1C)),
                        ),
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(color: Colors.redAccent, fontSize: 11),
                        ),
                      ),
                      const SizedBox(height: 14),
                    ],

                    // Scale 1: Stress Level
                    _buildScaleSelector(
                      title: 'Stress Level',
                      description: '1: Very Low (Relaxed) • 5: Very High (Intense)',
                      value: _stress,
                      onChanged: (val) => setState(() => _stress = val),
                    ),
                    const SizedBox(height: 14),

                    // Scale 2: Fatigue Level
                    _buildScaleSelector(
                      title: 'Fatigue / Exhaustion',
                      description: '1: Fresh (Energized) • 5: Exhausted (Drained)',
                      value: _fatigue,
                      onChanged: (val) => setState(() => _fatigue = val),
                    ),
                    const SizedBox(height: 14),

                    // Scale 3: Sleep Quality
                    _buildScaleSelector(
                      title: 'Sleep Quality',
                      description: '1: Poor (Restless) • 5: Excellent (Deep)',
                      value: _sleepQuality,
                      onChanged: (val) => setState(() => _sleepQuality = val),
                    ),
                    const SizedBox(height: 14),

                    // Scale 4: Overall Mood
                    _buildScaleSelector(
                      title: 'Overall Mood',
                      description: '1: Distressed • 5: Great (Positive)',
                      value: _mood,
                      onChanged: (val) => setState(() => _mood = val),
                    ),
                    const SizedBox(height: 14),

                    // Scale 5: Workload Manageability
                    _buildScaleSelector(
                      title: 'Workload Manageability',
                      description: '1: Overwhelming • 5: Highly Manageable',
                      value: _workload,
                      onChanged: (val) => setState(() => _workload = val),
                    ),
                    const SizedBox(height: 16),

                    // Optional Notes Field
                    TextFormField(
                      controller: _notesController,
                      maxLines: 2,
                      decoration: InputDecoration(
                        labelText: 'Optional Personal Note (Private)',
                        hintText: 'e.g., Extended night patrol shift in extreme heat.',
                        filled: true,
                        fillColor: const Color(0xFF0F172A),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: const BorderSide(color: Color(0xFF334155)),
                        ),
                      ),
                    ),
                    const SizedBox(height: 18),

                    ElevatedButton.icon(
                      onPressed: _isSubmitting ? null : _submitCheckIn,
                      icon: _isSubmitting
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.send_rounded, size: 16),
                      label: const Text('Submit Check-in'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Wellness Check-in History Section
            const Text(
              'WELLNESS CHECK-IN HISTORY',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: Color(0xFF94A3B8),
                letterSpacing: 0.8,
              ),
            ),
            const SizedBox(height: 12),

            if (_isLoadingHistory)
              const Center(child: Padding(padding: EdgeInsets.all(20.0), child: CircularProgressIndicator()))
            else if (_history.isEmpty)
              Card(
                color: const Color(0xFF1E293B),
                child: const Padding(
                  padding: EdgeInsets.all(20.0),
                  child: Center(
                    child: Text(
                      'No past check-ins recorded yet. Complete your first voluntary check-in above.',
                      style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              )
            else
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _history.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final item = _history[index];
                  final dateStr = DateFormat('dd MMM yyyy • hh:mm a').format(item.timestamp);

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
                              Text(
                                dateStr,
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF38BDF8)),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                decoration: BoxDecoration(
                                  color: const Color(0x3310B981),
                                  borderRadius: BorderRadius.circular(3),
                                ),
                                child: Text(
                                  item.evidenceStatus,
                                  style: const TextStyle(fontSize: 8, color: Color(0xFF34D399), fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              _buildScoreBadge('Stress', item.stress, Colors.redAccent),
                              const SizedBox(width: 6),
                              _buildScoreBadge('Fatigue', item.fatigue, Colors.amber),
                              const SizedBox(width: 6),
                              _buildScoreBadge('Sleep', item.sleepQuality, Colors.purpleAccent),
                              const SizedBox(width: 6),
                              _buildScoreBadge('Mood', item.mood, Colors.blueAccent),
                              const SizedBox(width: 6),
                              _buildScoreBadge('Workload', item.workload, Colors.tealAccent),
                            ],
                          ),
                          if (item.notes != null && item.notes!.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Text(
                              item.notes!,
                              style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: Color(0xFFCBD5E1)),
                            ),
                          ],
                        ],
                      ),
                    ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildScaleSelector({
    required String title,
    required String description,
    required int value,
    required ValueChanged<int> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white),
            ),
            Text(
              '$value / 5',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Text(
          description,
          style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
        ),
        const SizedBox(height: 6),
        Row(
          children: List.generate(5, (index) {
            final score = index + 1;
            final isSelected = score == value;

            return Expanded(
              child: GestureDetector(
                onTap: () => onChanged(score),
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 2.0),
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  decoration: BoxDecoration(
                    color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF0F172A),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155),
                    ),
                  ),
                  child: Center(
                    child: Text(
                      '$score',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        color: isSelected ? Colors.white : const Color(0xFF94A3B8),
                      ),
                    ),
                  ),
                ),
              ),
            );
          }),
        ),
      ],
    );
  }

  Widget _buildScoreBadge(String label, int val, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Text(
        '$label: $val',
        style: const TextStyle(fontSize: 9, color: Color(0xFFCBD5E1)),
      ),
    );
  }
}
