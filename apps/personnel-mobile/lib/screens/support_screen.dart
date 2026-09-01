import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../models/personnel_models.dart';

class SupportScreen extends StatefulWidget {
  const SupportScreen({super.key});

  @override
  State<SupportScreen> createState() => _SupportScreenState();
}

class _SupportScreenState extends State<SupportScreen> {
  final ApiService _apiService = ApiService();

  String _urgency = 'ROUTINE';
  final TextEditingController _noteController = TextEditingController();

  bool _isSubmitting = false;
  bool _isLoadingHistory = true;
  List<SupportRequestModel> _requests = [];
  String? _successMessage;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchRequests();
  }

  Future<void> _fetchRequests() async {
    setState(() {
      _isLoadingHistory = true;
    });

    try {
      final reqs = await _apiService.getSupportRequests();
      setState(() {
        _requests = reqs;
      });
    } catch (e) {
      // Ignored
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingHistory = false;
        });
      }
    }
  }

  Future<void> _submitSupportRequest() async {
    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final req = await _apiService.submitSupportRequest(
        urgency: _urgency,
        note: _noteController.text.trim().isNotEmpty ? _noteController.text.trim() : null,
      );

      setState(() {
        _successMessage = 'Your support request has been submitted to the authorized welfare team.';
        _requests.insert(0, req);
        _noteController.clear();
        _urgency = 'ROUTINE';
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
    _noteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Welfare & Support Request'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header Info Card
            Card(
              color: const Color(0xFF1E293B),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Icon(Icons.handshake_outlined, color: Color(0xFF38BDF8), size: 22),
                        SizedBox(width: 8),
                        Text(
                          'CONFIDENTIAL WELFARE ASSISTANCE',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF38BDF8),
                            letterSpacing: 0.8,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Request support from designated force Welfare Officers.',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Requests are confidential and routed directly to authorized welfare officers. They are not displayed on unit operational noticeboards.',
                      style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8), height: 1.4),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Request Form Card
            Card(
              color: const Color(0xFF1E293B),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'New Support Request',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 14),

                    if (_successMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
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
                                style: const TextStyle(color: Color(0xFF34D399), fontSize: 11, height: 1.3),
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

                    const Text(
                      'Urgency Level',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFFCBD5E1)),
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        _buildUrgencyChip('ROUTINE', 'Routine Check-in', const Color(0xFF38BDF8)),
                        const SizedBox(width: 8),
                        _buildUrgencyChip('MODERATE', 'Moderate Welfare', const Color(0xFFFBBF24)),
                        const SizedBox(width: 8),
                        _buildUrgencyChip('PRIORITY', 'Priority Care', const Color(0xFFEF4444)),
                      ],
                    ),
                    const SizedBox(height: 16),

                    TextFormField(
                      controller: _noteController,
                      maxLines: 3,
                      decoration: InputDecoration(
                        labelText: 'Details / Nature of Assistance (Optional)',
                        hintText: 'e.g., Request confidential welfare check-in regarding family concerns.',
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
                      onPressed: _isSubmitting ? null : _submitSupportRequest,
                      icon: _isSubmitting
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.send_rounded, size: 16),
                      label: const Text('Submit Welfare Request'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Request History Section
            const Text(
              'MY WELFARE REQUESTS',
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
            else if (_requests.isEmpty)
              Card(
                color: const Color(0xFF1E293B),
                child: const Padding(
                  padding: EdgeInsets.all(20.0),
                  child: Center(
                    child: Text(
                      'No active support requests. Submit a voluntary request above if assistance is needed.',
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
                itemCount: _requests.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final req = _requests[index];
                  final dateStr = DateFormat('dd MMM yyyy • hh:mm a').format(req.createdAt);

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
                                'Urgency: ${req.urgency}',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: req.urgency == 'PRIORITY'
                                      ? const Color(0xFFEF4444)
                                      : req.urgency == 'MODERATE'
                                          ? const Color(0xFFFBBF24)
                                          : const Color(0xFF38BDF8),
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: req.status == 'PENDING'
                                      ? const Color(0x33FBBF24)
                                      : req.status == 'REVIEWED'
                                          ? const Color(0x3338BDF8)
                                          : const Color(0x3310B981),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  'STATUS: ${req.status}',
                                  style: TextStyle(
                                    fontSize: 9,
                                    fontWeight: FontWeight.bold,
                                    color: req.status == 'PENDING'
                                        ? const Color(0xFFFBBF24)
                                        : req.status == 'REVIEWED'
                                            ? const Color(0xFF38BDF8)
                                            : const Color(0xFF34D399),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          if (req.note != null && req.note!.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Text(
                              req.note!,
                              style: const TextStyle(fontSize: 11, color: Color(0xFFCBD5E1)),
                            ),
                          ],
                          const SizedBox(height: 8),
                          Text(
                            'Submitted: $dateStr',
                            style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                          ),
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

  Widget _buildUrgencyChip(String code, String label, Color color) {
    final isSelected = _urgency == code;

    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _urgency = code),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          decoration: BoxDecoration(
            color: isSelected ? color.withOpacity(0.2) : const Color(0xFF0F172A),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isSelected ? color : const Color(0xFF334155),
            ),
          ),
          child: Center(
            child: Text(
              code,
              style: TextStyle(
                fontSize: 10,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? color : const Color(0xFF94A3B8),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
