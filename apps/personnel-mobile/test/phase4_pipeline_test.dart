import 'package:flutter_test/flutter_test.dart';
import 'package:septeria_personnel_mobile/models/personnel_models.dart';

void main() {
  group('Phase 4 Data Ingestion & Quality Pipeline Tests', () {
    test('Parse PhysiologicalTrendResponseModel with SQI and evidence status', () {
      final json = {
        'personnel_id': 'P-1047',
        'latest_hr': 74.0,
        'latest_hrv': 52.0,
        'latest_resting_hr': 61.0,
        'latest_sleep': 7.1,
        'latest_activity': 6800.0,
        'overall_sqi': 'GOOD',
        'data_completeness_pct': 94.0,
        'attribution_summary': 'Physiological telemetry within expected baseline resting range.',
        'evidence_status': 'OBSERVED',
        'trends': [
          {
            'id': 't1',
            'timestamp': '2026-08-30T10:00:00.000Z',
            'hr': 72.0,
            'hrv': 55.0,
            'resting_hr': 60.0,
            'sleep': 7.0,
            'activity': 5000.0,
            'signal_quality': 0.95,
            'sqi_status': 'GOOD',
            'evidence_status': 'OBSERVED',
            'motion_context': 'MODERATE',
            'is_reconstructed': false,
          },
          {
            'id': 't2-inferred',
            'timestamp': '2026-08-30T10:05:00.000Z',
            'hr': 73.0,
            'hrv': 54.0,
            'resting_hr': 60.0,
            'sleep': 7.0,
            'activity': 5100.0,
            'signal_quality': 0.70,
            'sqi_status': 'FAIR',
            'evidence_status': 'INFERRED',
            'motion_context': 'MODERATE',
            'is_reconstructed': true,
          }
        ]
      };

      final model = PhysiologicalTrendResponseModel.fromJson(json);
      expect(model.personnelId, 'P-1047');
      expect(model.overallSqi, 'GOOD');
      expect(model.dataCompletenessPct, 94.0);
      expect(model.trends.length, 2);
      expect(model.trends[0].evidenceStatus, 'OBSERVED');
      expect(model.trends[0].isReconstructed, false);
      expect(model.trends[1].evidenceStatus, 'INFERRED');
      expect(model.trends[1].isReconstructed, true);
    });

    test('Parse SignalQualitySummaryModel with missing intervals', () {
      final json = {
        'personnel_id': 'P-1047',
        'overall_quality': 'FAIR',
        'overall_completeness_pct': 88.0,
        'completeness_breakdown': {
          'physiological': 88.0,
          'wellness': 100.0,
          'operational': 100.0,
          'environmental': 85.0,
        },
        'signals': {
          'hr': 'GOOD',
          'hrv': 'FAIR',
          'sleep': 'GOOD',
          'activity': 'GOOD',
        },
        'missing_intervals': [
          {
            'id': 'gap-1',
            'personnel_id': 'P-1047',
            'signal_name': 'hrv',
            'start_time': '2026-08-30T08:00:00.000Z',
            'end_time': '2026-08-30T08:20:00.000Z',
            'duration_minutes': 20.0,
            'gap_type': 'LONG_GAP',
            'reconstructed': false,
          }
        ],
        'contextual_warnings': [
          'HRV missing segment detected (20 min).'
        ],
        'attribution_summary': 'Physiological elevation is consistent with physical exertion; psychological attribution reduced.',
        'timestamp': '2026-08-30T10:00:00.000Z',
      };

      final summary = SignalQualitySummaryModel.fromJson(json);
      expect(summary.personnelId, 'P-1047');
      expect(summary.overallQuality, 'FAIR');
      expect(summary.overallCompletenessPct, 88.0);
      expect(summary.missingIntervals.length, 1);
      expect(summary.missingIntervals.first.durationMinutes, 20.0);
      expect(summary.missingIntervals.first.gapType, 'LONG_GAP');
      expect(summary.contextualWarnings.first, contains('HRV missing segment'));
      expect(summary.attributionSummary, contains('physical exertion'));
    });
  });
}
