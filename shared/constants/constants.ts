export enum UserRole {
  PERSONNEL = 'personnel',
  WELFARE_OFFICER = 'welfare_officer',
  MEDICAL_OFFICER = 'medical_officer',
  COMMANDER = 'commander',
  ADMIN = 'admin',
}

export enum OperationalZone {
  ZONE_1 = 'Zone 1: High-Intensity / Active Operations',
  ZONE_2 = 'Zone 2: Border / Remote / Extreme Environment',
  ZONE_3 = 'Zone 3: Critical Incident / Post-Incident Recovery',
}

export enum EvidenceStatus {
  OBSERVED = 'OBSERVED',
  DERIVED = 'DERIVED',
  INFERRED = 'INFERRED',
  UNCERTAIN = 'UNCERTAIN',
}

export enum RiskLevel {
  LOW = 'LOW',
  MODERATE = 'MODERATE',
  HIGH = 'HIGH',
}

export enum Trajectory {
  STABLE = 'STABLE',
  IMPROVING = 'IMPROVING',
  DETERIORATING = 'DETERIORATING',
}

export enum RecommendationPriority {
  ROUTINE = 'ROUTINE',
  PRIORITY = 'PRIORITY',
  URGENT = 'URGENT',
}

export enum RecommendationStatus {
  PENDING = 'PENDING',
  ACKNOWLEDGED = 'ACKNOWLEDGED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  DISMISSED = 'DISMISSED',
}
