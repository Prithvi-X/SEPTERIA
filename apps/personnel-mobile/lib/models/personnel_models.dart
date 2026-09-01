class AuthoritativeContextModel {
  final String zone;
  final String dutyType;
  final String shift;
  final String location;
  final String environment;
  final bool temporary;
  final String? remainingDurationFormatted;
  final int? remainingSeconds;
  final DateTime? endTime;

  AuthoritativeContextModel({
    required this.zone,
    required this.dutyType,
    required this.shift,
    required this.location,
    required this.environment,
    required this.temporary,
    this.remainingDurationFormatted,
    this.remainingSeconds,
    this.endTime,
  });

  factory AuthoritativeContextModel.fromJson(Map<String, dynamic> json) {
    return AuthoritativeContextModel(
      zone: json['zone'] ?? 'Zone 2',
      dutyType: json['duty_type'] ?? 'Standard Duty',
      shift: json['shift'] ?? 'Day (08:00 - 16:00)',
      location: json['location'] ?? 'Base Station',
      environment: json['environment'] ?? 'Standard Base Environment',
      temporary: json['temporary'] ?? false,
      remainingDurationFormatted: json['remaining_duration_formatted'],
      remainingSeconds: json['remaining_seconds'],
      endTime: json['end_time'] != null ? DateTime.tryParse(json['end_time']) : null,
    );
  }
}

class PersonnelMeModel {
  final String id;
  final String personnelId;
  final String force;
  final String unitId;
  final String role;
  final String? rank;
  final String posting;
  final String status;
  final AuthoritativeContextModel authoritativeContext;
  final String leaveStatus;
  final int? postLeaveDayCount;
  final int postLeaveTotalDays;
  final DateTime? returnDate;
  final String dataClassification;

  PersonnelMeModel({
    required this.id,
    required this.personnelId,
    required this.force,
    required this.unitId,
    required this.role,
    this.rank,
    required this.posting,
    required this.status,
    required this.authoritativeContext,
    required this.leaveStatus,
    this.postLeaveDayCount,
    this.postLeaveTotalDays = 14,
    this.returnDate,
    required this.dataClassification,
  });

  factory PersonnelMeModel.fromJson(Map<String, dynamic> json) {
    return PersonnelMeModel(
      id: json['id'] ?? '',
      personnelId: json['personnel_id'] ?? '',
      force: json['force'] ?? 'BSF',
      unitId: json['unit_id'] ?? '',
      role: json['role'] ?? '',
      rank: json['rank'],
      posting: json['posting'] ?? '',
      status: json['status'] ?? 'ACTIVE',
      authoritativeContext: AuthoritativeContextModel.fromJson(json['authoritative_context'] ?? {}),
      leaveStatus: json['leave_status'] ?? 'NONE',
      postLeaveDayCount: json['post_leave_day_count'],
      postLeaveTotalDays: json['post_leave_total_days'] ?? 14,
      returnDate: json['return_date'] != null ? DateTime.tryParse(json['return_date']) : null,
      dataClassification: json['data_classification'] ?? 'PERSONNEL_PRIVATE',
    );
  }
}

class WellnessRecordModel {
  final String id;
  final String personnelId;
  final DateTime timestamp;
  final int stress;
  final int fatigue;
  final int sleepQuality;
  final int mood;
  final int workload;
  final String? notes;
  final String evidenceStatus;

  WellnessRecordModel({
    required this.id,
    required this.personnelId,
    required this.timestamp,
    required this.stress,
    required this.fatigue,
    required this.sleepQuality,
    required this.mood,
    this.workload = 3,
    this.notes,
    required this.evidenceStatus,
  });

  factory WellnessRecordModel.fromJson(Map<String, dynamic> json) {
    return WellnessRecordModel(
      id: json['id'] ?? '',
      personnelId: json['personnel_id'] ?? '',
      timestamp: DateTime.parse(json['timestamp']),
      stress: json['stress'] ?? 3,
      fatigue: json['fatigue'] ?? 3,
      sleepQuality: json['sleep_quality'] ?? 3,
      mood: json['mood'] ?? 3,
      workload: json['workload'] ?? 3,
      notes: json['notes'],
      evidenceStatus: json['evidence_status'] ?? 'OBSERVED',
    );
  }
}

class PhysiologicalTrendItemModel {
  final String id;
  final DateTime timestamp;
  final double hr;
  final double hrv;
  final double restingHr;
  final double sleep;
  final double activity;
  final double signalQuality;
  final String sqiStatus;
  final String evidenceStatus;
  final String motionContext;
  final bool isReconstructed;

  PhysiologicalTrendItemModel({
    required this.id,
    required this.timestamp,
    required this.hr,
    required this.hrv,
    required this.restingHr,
    required this.sleep,
    required this.activity,
    required this.signalQuality,
    this.sqiStatus = 'GOOD',
    this.evidenceStatus = 'OBSERVED',
    this.motionContext = 'LOW',
    this.isReconstructed = false,
  });

  factory PhysiologicalTrendItemModel.fromJson(Map<String, dynamic> json) {
    return PhysiologicalTrendItemModel(
      id: json['id'] ?? '',
      timestamp: DateTime.parse(json['timestamp']),
      hr: (json['hr'] as num).toDouble(),
      hrv: (json['hrv'] as num).toDouble(),
      restingHr: (json['resting_hr'] as num).toDouble(),
      sleep: (json['sleep'] as num).toDouble(),
      activity: (json['activity'] as num).toDouble(),
      signalQuality: (json['signal_quality'] as num?)?.toDouble() ?? 1.0,
      sqiStatus: json['sqi_status'] ?? 'GOOD',
      evidenceStatus: json['evidence_status'] ?? 'OBSERVED',
      motionContext: json['motion_context'] ?? 'LOW',
      isReconstructed: json['is_reconstructed'] ?? false,
    );
  }
}

class PhysiologicalTrendResponseModel {
  final String personnelId;
  final double latestHr;
  final double latestHrv;
  final double latestRestingHr;
  final double latestSleep;
  final double latestActivity;
  final String overallSqi;
  final double dataCompletenessPct;
  final String attributionSummary;
  final List<PhysiologicalTrendItemModel> trends;
  final String evidenceStatus;

  PhysiologicalTrendResponseModel({
    required this.personnelId,
    required this.latestHr,
    required this.latestHrv,
    required this.latestRestingHr,
    required this.latestSleep,
    required this.latestActivity,
    this.overallSqi = 'GOOD',
    this.dataCompletenessPct = 94.0,
    this.attributionSummary = 'Physiological telemetry within expected baseline resting range.',
    required this.trends,
    required this.evidenceStatus,
  });

  factory PhysiologicalTrendResponseModel.fromJson(Map<String, dynamic> json) {
    var trendsList = json['trends'] as List? ?? [];
    List<PhysiologicalTrendItemModel> parsedTrends =
        trendsList.map((i) => PhysiologicalTrendItemModel.fromJson(i)).toList();

    return PhysiologicalTrendResponseModel(
      personnelId: json['personnel_id'] ?? '',
      latestHr: (json['latest_hr'] as num?)?.toDouble() ?? 72.0,
      latestHrv: (json['latest_hrv'] as num?)?.toDouble() ?? 54.0,
      latestRestingHr: (json['latest_resting_hr'] as num?)?.toDouble() ?? 62.0,
      latestSleep: (json['latest_sleep'] as num?)?.toDouble() ?? 6.8,
      latestActivity: (json['latest_activity'] as num?)?.toDouble() ?? 7200.0,
      overallSqi: json['overall_sqi'] ?? 'GOOD',
      dataCompletenessPct: (json['data_completeness_pct'] as num?)?.toDouble() ?? 94.0,
      attributionSummary: json['attribution_summary'] ?? 'Physiological telemetry within expected baseline resting range.',
      trends: parsedTrends,
      evidenceStatus: json['evidence_status'] ?? 'OBSERVED',
    );
  }
}

class MissingIntervalModel {
  final String id;
  final String personnelId;
  final String signalName;
  final DateTime startTime;
  final DateTime endTime;
  final double durationMinutes;
  final String gapType;
  final bool reconstructed;

  MissingIntervalModel({
    required this.id,
    required this.personnelId,
    required this.signalName,
    required this.startTime,
    required this.endTime,
    required this.durationMinutes,
    required this.gapType,
    required this.reconstructed,
  });

  factory MissingIntervalModel.fromJson(Map<String, dynamic> json) {
    return MissingIntervalModel(
      id: json['id'] ?? '',
      personnelId: json['personnel_id'] ?? '',
      signalName: json['signal_name'] ?? 'hrv',
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      durationMinutes: (json['duration_minutes'] as num).toDouble(),
      gapType: json['gap_type'] ?? 'SHORT_GAP',
      reconstructed: json['reconstructed'] ?? false,
    );
  }
}

class SignalQualitySummaryModel {
  final String personnelId;
  final String overallQuality;
  final double overallCompletenessPct;
  final Map<String, double> completenessBreakdown;
  final Map<String, String> signals;
  final List<MissingIntervalModel> missingIntervals;
  final List<String> contextualWarnings;
  final String attributionSummary;
  final DateTime timestamp;

  SignalQualitySummaryModel({
    required this.personnelId,
    required this.overallQuality,
    required this.overallCompletenessPct,
    required this.completenessBreakdown,
    required this.signals,
    required this.missingIntervals,
    required this.contextualWarnings,
    required this.attributionSummary,
    required this.timestamp,
  });

  factory SignalQualitySummaryModel.fromJson(Map<String, dynamic> json) {
    var intervalsList = json['missing_intervals'] as List? ?? [];
    var breakdownMap = (json['completeness_breakdown'] as Map<String, dynamic>? ?? {})
        .map((k, v) => MapEntry(k, (v as num).toDouble()));
    var signalsMap = (json['signals'] as Map<String, dynamic>? ?? {})
        .map((k, v) => MapEntry(k, v.toString()));
    var warningsList = (json['contextual_warnings'] as List? ?? []).map((e) => e.toString()).toList();

    return SignalQualitySummaryModel(
      personnelId: json['personnel_id'] ?? '',
      overallQuality: json['overall_quality'] ?? 'GOOD',
      overallCompletenessPct: (json['overall_completeness_pct'] as num?)?.toDouble() ?? 94.0,
      completenessBreakdown: breakdownMap,
      signals: signalsMap,
      missingIntervals: intervalsList.map((i) => MissingIntervalModel.fromJson(i)).toList(),
      contextualWarnings: warningsList,
      attributionSummary: json['attribution_summary'] ?? 'Physiological telemetry within expected baseline resting range.',
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toUtc().toIso8601String()),
    );
  }
}

class SupportRequestModel {
  final String id;
  final String personnelId;
  final String urgency;
  final String? note;
  final String status;
  final DateTime createdAt;

  SupportRequestModel({
    required this.id,
    required this.personnelId,
    required this.urgency,
    this.note,
    required this.status,
    required this.createdAt,
  });

  factory SupportRequestModel.fromJson(Map<String, dynamic> json) {
    return SupportRequestModel(
      id: json['id'] ?? '',
      personnelId: json['personnel_id'] ?? '',
      urgency: json['urgency'] ?? 'ROUTINE',
      note: json['note'],
      status: json['status'] ?? 'PENDING',
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class BaselineMetricModel {
  final String metric;
  final double median;
  final double mad;
  final double? p10;
  final double? p90;
  final int observationCount;
  final String qualityRating;
  final bool isCohortPrior;

  BaselineMetricModel({
    required this.metric,
    required this.median,
    required this.mad,
    this.p10,
    this.p90,
    required this.observationCount,
    required this.qualityRating,
    required this.isCohortPrior,
  });

  factory BaselineMetricModel.fromJson(Map<String, dynamic> json) {
    return BaselineMetricModel(
      metric: json['metric'] ?? '',
      median: (json['median'] as num).toDouble(),
      mad: (json['mad'] as num).toDouble(),
      p10: (json['p10'] as num?)?.toDouble(),
      p90: (json['p90'] as num?)?.toDouble(),
      observationCount: json['observation_count'] ?? 0,
      qualityRating: json['quality_rating'] ?? 'GOOD',
      isCohortPrior: json['is_cohort_prior'] ?? false,
    );
  }
}

class PersonalBaselineModel {
  final String personnelId;
  final Map<String, BaselineMetricModel> baselines;
  final DateTime lastUpdated;

  PersonalBaselineModel({
    required this.personnelId,
    required this.baselines,
    required this.lastUpdated,
  });

  factory PersonalBaselineModel.fromJson(Map<String, dynamic> json) {
    var rawMap = json['baselines'] as Map<String, dynamic>? ?? {};
    var converted = rawMap.map((k, v) => MapEntry(k, BaselineMetricModel.fromJson(v as Map<String, dynamic>)));

    return PersonalBaselineModel(
      personnelId: json['personnel_id'] ?? '',
      baselines: converted,
      lastUpdated: DateTime.parse(json['last_updated'] ?? DateTime.now().toUtc().toIso8601String()),
    );
  }
}

class MetricDeviationModel {
  final String metric;
  final double? observed;
  final double baselineMedian;
  final double baselineMad;
  final double? absoluteDeviation;
  final double? relativeDeviationPct;
  final double? robustZScore;
  final bool isMissing;
  final double? sleepDeficitHours;

  MetricDeviationModel({
    required this.metric,
    this.observed,
    required this.baselineMedian,
    required this.baselineMad,
    this.absoluteDeviation,
    this.relativeDeviationPct,
    this.robustZScore,
    required this.isMissing,
    this.sleepDeficitHours,
  });

  factory MetricDeviationModel.fromJson(Map<String, dynamic> json) {
    return MetricDeviationModel(
      metric: json['metric'] ?? '',
      observed: (json['observed'] as num?)?.toDouble(),
      baselineMedian: (json['baseline_median'] as num?)?.toDouble() ?? 0.0,
      baselineMad: (json['baseline_mad'] as num?)?.toDouble() ?? 1.0,
      absoluteDeviation: (json['absolute_deviation'] as num?)?.toDouble(),
      relativeDeviationPct: (json['relative_deviation_pct'] as num?)?.toDouble(),
      robustZScore: (json['robust_z_score'] as num?)?.toDouble(),
      isMissing: json['is_missing'] ?? false,
      sleepDeficitHours: (json['sleep_deficit_hours'] as num?)?.toDouble(),
    );
  }
}

class RecoveryDebtModel {
  final double recoveryBurdenScore;
  final List<String> contributingFactors;
  final Map<String, double> subscores;
  final String disclaimer;

  RecoveryDebtModel({
    required this.recoveryBurdenScore,
    required this.contributingFactors,
    required this.subscores,
    required this.disclaimer,
  });

  factory RecoveryDebtModel.fromJson(Map<String, dynamic> json) {
    var rawSub = json['subscores'] as Map<String, dynamic>? ?? {};
    var factors = (json['contributing_factors'] as List? ?? []).map((e) => e.toString()).toList();
    return RecoveryDebtModel(
      recoveryBurdenScore: (json['recovery_burden_score'] as num?)?.toDouble() ?? 0.0,
      contributingFactors: factors,
      subscores: rawSub.map((k, v) => MapEntry(k, (v as num).toDouble())),
      disclaimer: json['disclaimer'] ?? 'Provisional prototype indicator; not a validated clinical instrument.',
    );
  }
}

class TrajectoryMetricModel {
  final String metric;
  final String direction; // STABLE, IMPROVING, DETERIORATING
  final double slope;
  final double volatility;
  final String interpretation;

  TrajectoryMetricModel({
    required this.metric,
    required this.direction,
    required this.slope,
    required this.volatility,
    required this.interpretation,
  });

  factory TrajectoryMetricModel.fromJson(Map<String, dynamic> json) {
    return TrajectoryMetricModel(
      metric: json['metric'] ?? '',
      direction: json['direction'] ?? 'STABLE',
      slope: (json['slope'] as num?)?.toDouble() ?? 0.0,
      volatility: (json['volatility'] as num?)?.toDouble() ?? 0.0,
      interpretation: json['interpretation'] ?? '',
    );
  }
}

class TrajectorySummaryModel {
  final String overallDirection;
  final String overallSummary;
  final TrajectoryMetricModel? hrvTrajectory;
  final TrajectoryMetricModel? sleepTrajectory;
  final TrajectoryMetricModel? restingHrTrajectory;

  TrajectorySummaryModel({
    required this.overallDirection,
    required this.overallSummary,
    this.hrvTrajectory,
    this.sleepTrajectory,
    this.restingHrTrajectory,
  });

  factory TrajectorySummaryModel.fromJson(Map<String, dynamic> json) {
    return TrajectorySummaryModel(
      overallDirection: json['overall_direction'] ?? 'STABLE',
      overallSummary: json['overall_summary'] ?? 'Physiological recovery trajectory is in stable balance.',
      hrvTrajectory: json['hrv_trajectory'] != null ? TrajectoryMetricModel.fromJson(json['hrv_trajectory']) : null,
      sleepTrajectory: json['sleep_trajectory'] != null ? TrajectoryMetricModel.fromJson(json['sleep_trajectory']) : null,
      restingHrTrajectory: json['resting_hr_trajectory'] != null ? TrajectoryMetricModel.fromJson(json['resting_hr_trajectory']) : null,
    );
  }
}

class PersonalStateModel {
  final String personnelId;
  final DateTime timestamp;
  final String operationalZone;
  final String dutyType;
  final String shift;
  final Map<String, MetricDeviationModel> deviations;
  final TrajectorySummaryModel trajectories;
  final RecoveryDebtModel recoveryDebt;
  final String reboundStatus;
  final String evidenceQuality;
  final String attributionSummary;

  PersonalStateModel({
    required this.personnelId,
    required this.timestamp,
    required this.operationalZone,
    required this.dutyType,
    required this.shift,
    required this.deviations,
    required this.trajectories,
    required this.recoveryDebt,
    required this.reboundStatus,
    required this.evidenceQuality,
    required this.attributionSummary,
  });

  factory PersonalStateModel.fromJson(Map<String, dynamic> json) {
    var rawDevs = json['deviations'] as Map<String, dynamic>? ?? {};
    var devsMap = rawDevs.map((k, v) => MapEntry(k, MetricDeviationModel.fromJson(v as Map<String, dynamic>)));

    return PersonalStateModel(
      personnelId: json['personnel_id'] ?? '',
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toUtc().toIso8601String()),
      operationalZone: json['operational_zone'] ?? 'Zone 2',
      dutyType: json['duty_type'] ?? 'General Duty',
      shift: json['shift'] ?? 'Day (08:00 - 16:00)',
      deviations: devsMap,
      trajectories: TrajectorySummaryModel.fromJson(json['trajectories'] ?? {}),
      recoveryDebt: RecoveryDebtModel.fromJson(json['recovery_debt'] ?? {}),
      reboundStatus: json['rebound_status'] ?? 'NONE',
      evidenceQuality: json['evidence_quality'] ?? 'GOOD',
      attributionSummary: json['attribution_summary'] ?? 'Physiological telemetry within expected baseline resting range.',
    );
  }
}
