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
  bool _isRecording = false;
  bool _isSubmitting = false;
  int _secondsRecorded = 0;
  Timer? _timer;
  
  bool _checkComplete = false;
  String? _errorMessage;

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startRecording() {
    setState(() {
      _isRecording = true;
      _secondsRecorded = 0;
      _errorMessage = null;
      _checkComplete = false;
    });

    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _secondsRecorded++;
        if (_secondsRecorded >= 20) {
          _stopRecording();
        }
      });
    });
  }

  void _stopRecording() {
    _timer?.cancel();
    setState(() {
      _isRecording = false;
    });
    if (_secondsRecorded >= 3) {
      _submitVoiceSample();
    } else {
      setState(() {
        _errorMessage = "Not enough usable audio to compare.";
        _secondsRecorded = 0;
      });
    }
  }

  Future<void> _submitVoiceSample() async {
    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      await _apiService.submitVoiceCheckIn(
        consentGiven: true,
        durationSeconds: _secondsRecorded,
      );

      setState(() {
        _checkComplete = true;
      });
    } catch (e) {
      setState(() {
        _errorMessage = "Connection error. Could not submit voice check.";
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
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF94A3B8)),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (_checkComplete) 
                _buildCompleteState()
              else if (_isSubmitting)
                _buildSubmittingState()
              else
                _buildInitialOrRecordingState(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInitialOrRecordingState() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(Icons.mic_none, color: Color(0xFF38BDF8), size: 48),
        const SizedBox(height: 24),
        const Text('OPTIONAL VOICE CHECK-IN', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
        const SizedBox(height: 12),
        if (!_isRecording)
          const Text('Take about 20 seconds.\nThis is voluntary.', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, color: Colors.white, height: 1.4))
        else
          Column(
            children: [
              const Text('Recording...', style: TextStyle(fontSize: 18, color: Colors.white)),
              const SizedBox(height: 8),
              Text(
                '00:${_secondsRecorded.toString().padLeft(2, '0')} / 00:20',
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
              ),
            ],
          ),
        const SizedBox(height: 48),
        
        if (!_isRecording)
          ElevatedButton(
            onPressed: _startRecording,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF38BDF8),
              padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
            ),
            child: const Text('Start voice check', style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold)),
          )
        else
          ElevatedButton(
            onPressed: _stopRecording,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
            ),
            child: const Text('Stop', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          ),
          
        const SizedBox(height: 48),
        
        if (_errorMessage != null)
          Text(_errorMessage!, style: const TextStyle(color: Color(0xFFEF4444), fontSize: 14)),

        const SizedBox(height: 24),
        const Text(
          'Your voice pattern will be compared with your usual pattern when enough personal history exists.\n\nRaw audio is not retained.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.4),
        ),
      ],
    );
  }

  Widget _buildSubmittingState() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: const [
        CircularProgressIndicator(color: Color(0xFF38BDF8)),
        SizedBox(height: 24),
        Text('Processing securely...', style: TextStyle(fontSize: 16, color: Color(0xFF94A3B8))),
      ],
    );
  }

  Widget _buildCompleteState() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(Icons.check_circle_outline, color: Color(0xFF10B981), size: 64),
        const SizedBox(height: 24),
        const Text('VOICE CHECK COMPLETE', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
        const SizedBox(height: 12),
        const Text('No clear change detected.', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, color: Colors.white)),
        const SizedBox(height: 48),
        ElevatedButton(
          onPressed: () => Navigator.of(context).pop(),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF1E293B),
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          ),
          child: const Text('Done', style: TextStyle(color: Colors.white)),
        )
      ],
    );
  }
}
