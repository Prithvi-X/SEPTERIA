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
  final PageController _pageController = PageController();

  int _stress = 3;
  int _fatigue = 3;
  int _sleepQuality = 3;
  int _mood = 3;
  int _workload = 3;
  final TextEditingController _notesController = TextEditingController();

  bool _isSubmitting = false;
  bool _isComplete = false;
  int _currentPage = 0;
  String? _errorMessage;

  final int _totalPages = 6; // 5 questions + 1 notes

  @override
  void dispose() {
    _notesController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentPage < _totalPages - 1) {
      _pageController.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
    } else {
      _submitCheckIn();
    }
  }

  void _prevPage() {
    if (_currentPage > 0) {
      _pageController.previousPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
    }
  }

  Future<void> _submitCheckIn() async {
    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      await _apiService.submitWellnessCheckIn(
        stress: _stress,
        fatigue: _fatigue,
        sleepQuality: _sleepQuality,
        mood: _mood,
        workload: _workload,
        notes: _notesController.text.trim().isNotEmpty ? _notesController.text.trim() : null,
      );

      setState(() {
        _isComplete = true;
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
  Widget build(BuildContext context) {
    if (_isComplete) {
      return _buildCompleteScreen();
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: const Text('DAILY WELLNESS CHECK-IN', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0)),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Progress Bar
          LinearProgressIndicator(
            value: (_currentPage + 1) / _totalPages,
            backgroundColor: const Color(0xFF1E293B),
            valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF38BDF8)),
            minHeight: 2,
          ),
          
          Expanded(
            child: PageView(
              controller: _pageController,
              physics: const NeverScrollableScrollPhysics(), // Disable swipe to force using buttons
              onPageChanged: (index) {
                setState(() {
                  _currentPage = index;
                });
              },
              children: [
                _buildQuestionPage('Stress', 'How would you rate your current stress level?', _stress, (v) => setState(() => _stress = v)),
                _buildQuestionPage('Fatigue', 'How physically or mentally fatigued are you?', _fatigue, (v) => setState(() => _fatigue = v)),
                _buildQuestionPage('Sleep', 'How was your recent sleep quality?', _sleepQuality, (v) => setState(() => _sleepQuality = v)),
                _buildQuestionPage('Mood', 'How would you rate your general mood today?', _mood, (v) => setState(() => _mood = v)),
                _buildQuestionPage('Workload', 'How manageable is your current workload?', _workload, (v) => setState(() => _workload = v)),
                _buildNotesPage(),
              ],
            ),
          ),
          
          _buildBottomNavigation(),
        ],
      ),
    );
  }

  Widget _buildCompleteScreen() {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.check_circle_outline, color: Color(0xFF10B981), size: 64),
              const SizedBox(height: 24),
              const Text('CHECK-IN COMPLETE', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, letterSpacing: 1.0)),
              const SizedBox(height: 12),
              const Text(
                'Thanks. Your response is part of your private wellness record.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 15, color: Color(0xFF94A3B8), height: 1.4),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isComplete = false;
                    _currentPage = 0;
                    _stress = 3;
                    _fatigue = 3;
                    _sleepQuality = 3;
                    _mood = 3;
                    _workload = 3;
                    _notesController.clear();
                  });
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1E293B),
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
                child: const Text('Submit another', style: TextStyle(color: Colors.white)),
              )
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuestionPage(String category, String question, int currentValue, Function(int) onChanged) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            category.toUpperCase(),
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8), letterSpacing: 1.0),
          ),
          const SizedBox(height: 16),
          Text(
            question,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white, height: 1.3),
          ),
          const SizedBox(height: 48),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List.generate(5, (index) {
              final value = index + 1;
              final isSelected = currentValue == value;
              return GestureDetector(
                onTap: () => onChanged(value),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF1E293B),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155),
                      width: 2,
                    ),
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    value.toString(),
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: isSelected ? const Color(0xFF0F172A) : Colors.white,
                    ),
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: const [
              Text('Very low', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
              Text('Very high', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNotesPage() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            'ADD A PRIVATE NOTE',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8), letterSpacing: 1.0),
          ),
          const SizedBox(height: 16),
          const Text(
            'Anything you\'d like your welfare team to know?',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white, height: 1.3),
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _notesController,
            maxLines: 4,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Optional',
              hintStyle: const TextStyle(color: Color(0xFF475569)),
              filled: true,
              fillColor: const Color(0xFF1E293B),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF38BDF8)),
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (_errorMessage != null)
            Text(_errorMessage!, style: const TextStyle(color: Color(0xFFEF4444), fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildBottomNavigation() {
    return Container(
      padding: const EdgeInsets.all(24.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          if (_currentPage > 0)
            TextButton(
              onPressed: _prevPage,
              child: const Text('Back', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 16)),
            )
          else
            const SizedBox.shrink(),
            
          ElevatedButton(
            onPressed: _isSubmitting ? null : _nextPage,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF38BDF8),
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: _isSubmitting 
              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Color(0xFF0F172A), strokeWidth: 2))
              : Text(_currentPage == _totalPages - 1 ? 'Save / Submit' : 'Next', style: const TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
