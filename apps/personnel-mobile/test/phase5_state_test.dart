import 'package:flutter_test/flutter_test.dart';
import 'package:septeria_personnel_mobile/models/personnel_models.dart';

void main() {
  group('Phase 5 Personal Baseline & State Models Tests', () {
    test('Parse PersonalBaselineModel with robust statistics and quality rating', () {
      final json = {
        'personnel_id': 'P-1047',
        'baselines': {
          'hrv_rmssd': {
            'metric': 'hrv_rmssd',
            'median': 55.0,
            'mad': 5.0,
            'p10': 42.0,
            'p90': 68.0,
            'observation_count': 14,
            'quality_rating': 'GOOD',
            'is_cohort_prior': false,
          },
          'sleep_hours': {
            'metric': 'sleep_hours',
            'median': 7.1,
            'mad': 0.8,
            'p10': 5.5,
            'p90': 8.2,
            'observation_count': 14,
            'quality_rating': 'GOOD',
            'is_cohort_prior': false,
          }
        },
        'last_updated': '2026-08-30T10:00:00.000Z',
      };

      final model = PersonalBaselineModel.fromJson(json);
      expect(model.personnelId, 'P-1047');
      expect(model.baselines['hrv_rmssd']!.median, 55.0);
      expect(model.baselines['hrv_rmssd']!.mad, 5.0);
      expect(model.baselines['hrv_rmssd']!.qualityRating, 'GOOD');
      expect(model.baselines['hrv_rmssd']!.isCohortPrior, false);
      expect(model.baselines['sleep_hours']!.median, 7.1);
    });

    test('Parse PersonalStateModel with deviations, trajectory, and recovery debt', () {
      final json = {
        'personnel_id': 'P-1047',
        'timestamp': '2026-08-30T10:00:00.000Z',
        'operational_zone': 'Zone 2: Border / Remote / Extreme Environment',
        'duty_type': 'Border Patrol',
        'shift': 'Night (20:00 - 04:00)',
        'deviations': {
          'hrv': {
            'metric': 'hrv_rmssd',
            'observed': 42.0,
            'baseline_median': 55.0,
            'baseline_mad': 5.0,
            'absolute_deviation': -13.0,
            'relative_deviation_pct': -23.6,
            'robust_z_score': -1.75,
            'is_missing': false,
          },
          'sleep': {
            'metric': 'sleep_hours',
            'observed': 5.2,
            'baseline_median': 7.1,
            'baseline_mad': 0.8,
            'absolute_deviation': -1.9,
            'relative_deviation_pct': -26.8,
            'robust_z_score': -1.6,
            'is_missing': false,
            'sleep_deficit_hours': 1.9,
          }
        },
        'trajectories': {
          'overall_direction': 'DETERIORATING',
          'overall_summary': 'Multi-signal recovery trajectory indicates accumulating strain.',
          'hrv_trajectory': {
            'metric': 'hrv',
            'direction': 'DETERIORATING',
            'slope': -1.8,
            'volatility': 2.4,
            'interpretation': 'Recovery-related physiological trajectory shows progressive downward shift.'
          },
          'sleep_trajectory': {
            'metric': 'sleep',
            'direction': 'DETERIORATING',
            'slope': -0.4,
            'volatility': 0.8,
            'interpretation': 'Sleep duration shows deficit relative to baseline.'
          }
        },
        'recovery_debt': {
          'recovery_burden_score': 62.0,
          'contributing_factors': [
            'Sleep deficit: 1.9h below baseline (+19.0 pts)',
            'HRV suppression: 23.6% below baseline (+16.9 pts)',
            '3 consecutive high-workload shifts (+9.0 pts)',
          ],
          'subscores': {
            'sleep_contribution': 19.0,
            'hrv_contribution': 16.9,
            'rhr_contribution': 0.0,
            'workload_contribution': 9.0,
            'post_leave_contribution': 0.0,
          },
          'disclaimer': 'Provisional prototype indicator; not a validated clinical instrument.',
        },
        'rebound_status': 'NONE',
        'evidence_quality': 'GOOD',
        'attribution_summary': 'Physiological telemetry within expected baseline resting range.',
      };

      final state = PersonalStateModel.fromJson(json);
      expect(state.personnelId, 'P-1047');
      expect(state.operationalZone, contains('Zone 2'));
      expect(state.deviations['hrv']!.absoluteDeviation, -13.0);
      expect(state.deviations['hrv']!.relativeDeviationPct, -23.6);
      expect(state.deviations['sleep']!.sleepDeficitHours, 1.9);
      expect(state.trajectories.overallDirection, 'DETERIORATING');
      expect(state.recoveryDebt.recoveryBurdenScore, 62.0);
      expect(state.recoveryDebt.contributingFactors.length, 3);
      expect(state.recoveryDebt.disclaimer, contains('Provisional prototype'));
    });
  });
}
