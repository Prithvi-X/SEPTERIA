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

  bool _isLoadingHistory = true;
  List<SupportRequestModel> _requests = [];

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

  void _openSupportSheet(String title) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
        child: _SupportRequestSheet(title: title, onSubmitted: () {
          Navigator.pop(context);
          _fetchRequests();
        }),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: const Text('Support', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'PRIVATE SUPPORT',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8), letterSpacing: 1.0),
            ),
            const SizedBox(height: 12),
            const Text(
              'Need someone to talk to or help with recovery?',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white, height: 1.3),
            ),
            const SizedBox(height: 32),
            
            _buildSupportOption(
              'Peer Support',
              'Someone from your designated support network',
              Icons.people_outline,
              () => _openSupportSheet('Peer Support'),
            ),
            const SizedBox(height: 12),
            _buildSupportOption(
              'Welfare Officer',
              'Confidential personnel welfare support',
              Icons.support_agent,
              () => _openSupportSheet('Welfare Officer'),
            ),
            const SizedBox(height: 12),
            _buildSupportOption(
              'Medical Support',
              'Authorized medical pathway',
              Icons.medical_services_outlined,
              () => _openSupportSheet('Medical Support'),
            ),

            const SizedBox(height: 48),
            
            if (_requests.isNotEmpty) ...[
              const Text(
                'YOUR REQUESTS',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 1.0),
              ),
              const SizedBox(height: 12),
              ..._requests.map((r) => _buildRequestItem(r)),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildSupportOption(String title, String subtitle, IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFF334155)),
        ),
        child: Row(
          children: [
            Icon(icon, color: const Color(0xFF38BDF8), size: 28),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 4),
                  Text(subtitle, style: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8))),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Color(0xFF64748B)),
          ],
        ),
      ),
    );
  }

  Widget _buildRequestItem(SupportRequestModel req) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0B132B),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                DateFormat('MMM d, yyyy').format(req.createdAt.toLocal()),
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 4),
              Text(
                'Urgency: ${req.urgency}',
                style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
              ),
            ],
          ),
          Text(
            req.status,
            style: TextStyle(
              fontSize: 12, 
              fontWeight: FontWeight.bold, 
              color: req.status == 'SUBMITTED' ? const Color(0xFF38BDF8) : const Color(0xFF10B981)
            ),
          ),
        ],
      ),
    );
  }
}

class _SupportRequestSheet extends StatefulWidget {
  final String title;
  final VoidCallback onSubmitted;

  const _SupportRequestSheet({required this.title, required this.onSubmitted});

  @override
  State<_SupportRequestSheet> createState() => _SupportRequestSheetState();
}

class _SupportRequestSheetState extends State<_SupportRequestSheet> {
  final ApiService _apiService = ApiService();
  String _urgency = 'ROUTINE';
  bool _isSubmitting = false;
  String? _errorMessage;
  bool _isSuccess = false;

  Future<void> _submit() async {
    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      await _apiService.submitSupportRequest(
        urgency: _urgency,
        note: 'Requested via pathway: ${widget.title}',
      );
      setState(() {
        _isSuccess = true;
      });
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) widget.onSubmitted();
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Could not submit request. Please try again.';
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
    if (_isSuccess) {
      return Container(
        padding: const EdgeInsets.all(32),
        height: 250,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.check_circle_outline, color: Color(0xFF10B981), size: 48),
            SizedBox(height: 16),
            Text('REQUEST SENT', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF34D399), letterSpacing: 1.0)),
            SizedBox(height: 12),
            Text('Your request has been routed to the appropriate authorized support channel.', textAlign: TextAlign.center, style: TextStyle(fontSize: 14, color: Colors.white, height: 1.4)),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Request ${widget.title}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
              IconButton(icon: const Icon(Icons.close, color: Color(0xFF64748B)), onPressed: () => Navigator.pop(context)),
            ],
          ),
          const SizedBox(height: 24),
          
          _buildUrgencyOption('ROUTINE', 'I\'d like some support.', _urgency == 'ROUTINE'),
          const SizedBox(height: 12),
          _buildUrgencyOption('PRIORITY', 'I\'d like help soon.', _urgency == 'PRIORITY'),
          const SizedBox(height: 12),
          _buildUrgencyOption('URGENT', 'I need immediate assistance.', _urgency == 'URGENT'),

          const SizedBox(height: 32),

          if (_errorMessage != null) ...[
            Text(_errorMessage!, style: const TextStyle(color: Color(0xFFEF4444), fontSize: 12)),
            const SizedBox(height: 16),
          ],

          ElevatedButton(
            onPressed: _isSubmitting ? null : _submit,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF38BDF8),
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: _isSubmitting
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Color(0xFF0F172A), strokeWidth: 2))
                : const Text('Submit Request', style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildUrgencyOption(String value, String label, bool isSelected) {
    return InkWell(
      onTap: () => setState(() => _urgency = value),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF0F172A) : const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(
              isSelected ? Icons.radio_button_checked : Icons.radio_button_unchecked,
              color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF64748B),
            ),
            const SizedBox(width: 12),
            Text(label, style: const TextStyle(fontSize: 15, color: Colors.white)),
          ],
        ),
      ),
    );
  }
}
