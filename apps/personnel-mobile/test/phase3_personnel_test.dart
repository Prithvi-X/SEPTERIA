import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:septeria_personnel_mobile/models/personnel_models.dart';
import 'package:septeria_personnel_mobile/screens/privacy_screen.dart';
import 'package:septeria_personnel_mobile/screens/voice_checkin_screen.dart';
import 'package:septeria_personnel_mobile/screens/wellness_screen.dart';
import 'package:septeria_personnel_mobile/screens/support_screen.dart';
import 'package:septeria_personnel_mobile/core/theme.dart';

void main() {
  group('Phase 3 Personnel Models Serialization Tests', () {
    test('PersonnelMeModel correctly parses JSON with authoritative context & countdown', () {
      final json = {
        'id': 'p-1047-uuid',
        'personnel_id': 'P-1047',
        'force': 'BSF',
        'unit_id': 'BSF-BN-47',
        'role': 'Constable / GD (Synthetic Demo)',
        'rank': 'Constable / GD',
        'posting': 'Border Outpost Tanot',
        'status': 'DEPLOYED',
        'authoritative_context': {
          'zone': 'Zone 2',
          'duty_type': 'Border Patrol',
          'shift': 'Night (20:00 - 04:00)',
          'location': 'Tanot Forward Line B',
          'environment': 'High Heat / Extreme Arid',
          'temporary': true,
          'remaining_duration_formatted': '5d 14h remaining',
          'remaining_seconds': 482400,
          'end_time': '2026-09-05T10:00:00Z',
        },
        'leave_status': 'POST_LEAVE_TRANSITION',
        'post_leave_day_count': 3,
        'post_leave_total_days': 14,
        'return_date': '2026-08-27T10:00:00Z',
        'data_classification': 'SYNTHETIC_DEMO_DATA',
      };

      final model = PersonnelMeModel.fromJson(json);

      expect(model.personnelId, 'P-1047');
      expect(model.force, 'BSF');
      expect(model.unitId, 'BSF-BN-47');
      expect(model.status, 'DEPLOYED');
      expect(model.authoritativeContext.zone, 'Zone 2');
      expect(model.authoritativeContext.dutyType, 'Border Patrol');
      expect(model.authoritativeContext.temporary, true);
      expect(model.authoritativeContext.remainingDurationFormatted, '5d 14h remaining');
      expect(model.leaveStatus, 'POST_LEAVE_TRANSITION');
      expect(model.postLeaveDayCount, 3);
      expect(model.postLeaveTotalDays, 14);
    });

    test('WellnessRecordModel correctly parses JSON', () {
      final json = {
        'id': 'w-1',
        'personnel_id': 'P-1047',
        'timestamp': '2026-08-29T10:00:00Z',
        'stress': 4,
        'fatigue': 4,
        'sleep_quality': 2,
        'mood': 3,
        'workload': 5,
        'notes': 'Night shift test',
        'evidence_status': 'OBSERVED',
      };

      final model = WellnessRecordModel.fromJson(json);

      expect(model.stress, 4);
      expect(model.fatigue, 4);
      expect(model.sleepQuality, 2);
      expect(model.mood, 3);
      expect(model.workload, 5);
      expect(model.evidenceStatus, 'OBSERVED');
    });

    test('SupportRequestModel correctly parses JSON', () {
      final json = {
        'id': 's-1',
        'personnel_id': 'P-1047',
        'urgency': 'MODERATE',
        'note': 'Request confidential check-in',
        'status': 'PENDING',
        'created_at': '2026-08-29T10:00:00Z',
      };

      final model = SupportRequestModel.fromJson(json);

      expect(model.urgency, 'MODERATE');
      expect(model.note, 'Request confidential check-in');
      expect(model.status, 'PENDING');
    });
  });

  group('Phase 3 Mobile Screen Widget Tests', () {
    testWidgets('PrivacyScreen renders all policy sections and RBAC disclosures', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: const PrivacyScreen(),
        ),
      );

      expect(find.text('Privacy & Data Center'), findsOneWidget);
      expect(find.text('Your Data & Privacy Rights'), findsOneWidget);
      expect(find.text('1. Authoritative Operational Context'), findsOneWidget);
      expect(find.text('2. Voluntary Self-Reporting'), findsOneWidget);
      expect(find.text('3. Data Visibility & Access Matrix'), findsOneWidget);
      expect(find.text('4. Confidential Welfare Support'), findsOneWidget);
    });

    testWidgets('VoiceCheckInScreen renders consent disclosure and controls', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: const VoiceCheckInScreen(),
        ),
      );

      expect(find.text('Voice Check-in (Voluntary)'), findsOneWidget);
      expect(find.text('OPTIONAL VOICE CHECK-IN'), findsOneWidget);
      expect(find.text('I voluntarily consent to record a voice check-in sample.'), findsOneWidget);
      expect(find.byType(Checkbox), findsOneWidget);
    });

    testWidgets('WellnessScreen renders 1-5 scale selectors and submit action', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: const WellnessScreen(),
        ),
      );

      expect(find.text('Voluntary Wellness Check-in'), findsOneWidget);
      expect(find.text('Stress Level'), findsOneWidget);
      expect(find.text('Fatigue / Exhaustion'), findsOneWidget);
      expect(find.text('Sleep Quality'), findsOneWidget);
      expect(find.text('Overall Mood'), findsOneWidget);
      expect(find.text('Workload Manageability'), findsOneWidget);
      expect(find.text('Submit Check-in'), findsOneWidget);
    });

    testWidgets('SupportScreen renders urgency selectors and submit action', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: const SupportScreen(),
        ),
      );

      expect(find.text('Welfare & Support Request'), findsOneWidget);
      expect(find.text('CONFIDENTIAL WELFARE ASSISTANCE'), findsOneWidget);
      expect(find.text('ROUTINE'), findsOneWidget);
      expect(find.text('MODERATE'), findsOneWidget);
      expect(find.text('PRIORITY'), findsOneWidget);
      expect(find.text('Submit Welfare Request'), findsOneWidget);
    });
  });
}
