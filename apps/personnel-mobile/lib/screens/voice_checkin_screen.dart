import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class VoiceCheckInScreen extends StatefulWidget {
  const VoiceCheckInScreen({super.key});

  @override
  State<VoiceCheckInScreen> createState() => _VoiceCheckInScreenState();
}

class _VoiceCheckInScreenState extends State<VoiceCheckInScreen> {
  final ApiService _apiService = ApiService();
  bool _consentGiven = false;
  bool _isRecording = false;
  bool _hasRecorded = false;
  int _secondsRecorded = 0;
  Timer? _timer;
  bool _isSubmitting = false;
  String? _statusMessage;
  String? _errorMessage;

  void _toggleRecording() {
    if (!_consentGiven) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please accept the voluntary consent before recording.'),
          backgroundColor: Colors.amber,
        ),
      );
      return;
    }

    if (_isRecording) {
      _stopRecording();
    } else {
      _startRecording();
    }
  }

  void _startRecording() {
    setState(() {
      _isRecording = true;
      _hasRecorded = false;
      _secondsRecorded = 0;
      _statusMessage = null;
      _errorMessage = null;
    });

    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _secondsRecorded++;
        if (_secondsRecorded >= 30) {
          _stopRecording();
        }
      });
    });
  }

  void _stopRecording() {
    _timer?.cancel();
    setState(() {
      _isRecording = false;
      _hasRecorded = _secondsRecorded >= 3;
    });
  }

  void _resetRecording() {
    _timer?.cancel();
    setState(() {
      _isRecording = false;
      _hasRecorded = false;
      _secondsRecorded = 0;
      _statusMessage = null;
    });
  }

  Future<void> _submitVoiceSample() async {
    if (!_hasRecorded) return;

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final res = await _apiService.submitVoiceCheckIn(
        consentGiven: _consentGiven,
        durationSeconds: _secondsRecorded,
      );

      setState(() {
        _statusMessage = res['message'] ?? 'Voice check-in sample submitted successfully.';
        _hasRecorded = false;
        _secondsRecorded = 0;
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
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Check-in (Voluntary)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Consent & Purpose Box
            Card(
              color: const Color(0xFF1E293B),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Icon(Icons.mic, color: Color(0xFF38BDF8), size: 22),
                        SizedBox(width: 8),
                        Text(
                          'OPTIONAL VOICE CHECK-IN',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF38BDF8),
                            letterSpacing: 0.8,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      'Record a short 20–30 second natural speech sample for optional wellness analysis.',
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      '• Strictly voluntary and confidential.\n• No background recording is ever performed.\n• Audio samples are not accessible to unit commanders.\n• Used exclusively for private recovery guidance.',
                      style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8), height: 1.4),
                    ),
                    const Divider(color: Color(0xFF334155), height: 20),
                    Row(
                      children: [
                        Checkbox(
                          value: _consentGiven,
                          activeColor: const Color(0xFF2563EB),
                          onChanged: (val) {
                            setState(() {
                              _consentGiven = val ?? false;
                            });
                          },
                        ),
                        const Expanded(
                          child: Text(
                            'I voluntarily consent to record a voice check-in sample.',
                            style: TextStyle(fontSize: 11, color: Colors.white),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            if (_statusMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0x3310B981),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF059669)),
                ),
                child: Text(
                  _statusMessage!,
                  style: const TextStyle(color: Color(0xFF34D399), fontSize: 12),
                ),
              ),
              const SizedBox(height: 16),
            ],

            if (_errorMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0x667F1D1D),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFB91C1C)),
                ),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(color: Colors.redAccent, fontSize: 12),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Recording Controls Area
            Center(
              child: Column(
                children: [
                  GestureDetector(
                    onTap: _isSubmitting ? null : _toggleRecording,
                    child: Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isRecording
                            ? const Color(0xFFEF4444)
                            : _consentGiven
                                ? const Color(0xFF2563EB)
                                : const Color(0xFF334155),
                        boxShadow: _isRecording
                            ? [
                                BoxShadow(
                                  color: Colors.red.withOpacity(0.4),
                                  blurRadius: 20,
                                  spreadRadius: 6,
                                ),
                              ]
                            : [],
                      ),
                      child: Icon(
                        _isRecording ? Icons.stop : Icons.mic,
                        color: Colors.white,
                        size: 44,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _isRecording
                        ? 'Recording: 00:${_secondsRecorded.toString().padLeft(2, '0')} / 00:30'
                        : _hasRecorded
                            ? 'Sample Recorded (${_secondsRecorded}s)'
                            : 'Tap to Record Speech Sample',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: _isRecording ? Colors.redAccent : const Color(0xFF94A3B8),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Prompt Reading Assistance
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0x221E293B),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'SUGGESTED READING PROMPT (OPTIONAL):',
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                  ),
                  SizedBox(height: 6),
                  Text(
                    '"I am completing my regular duty shift. Today the operational terrain was normal and I am feeling focused for the upcoming rotation."',
                    style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: Color(0xFFCBD5E1)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            if (_hasRecorded) ...[
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _resetRecording,
                      icon: const Icon(Icons.refresh, size: 16),
                      label: const Text('Re-record'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _isSubmitting ? null : _submitVoiceSample,
                      icon: _isSubmitting
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.check, size: 16),
                      label: const Text('Submit Sample'),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
