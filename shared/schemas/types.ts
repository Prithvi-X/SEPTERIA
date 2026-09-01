import {
  UserRole,
  OperationalZone,
  EvidenceStatus,
  RiskLevel,
  Trajectory,
  RecommendationPriority,
  RecommendationStatus,
} from '../constants/constants';

export interface Personnel {
  id: string;
  force: string;
  unit_id: string;
  role: string;
  posting: string;
  status: string;
}

export interface OperationalContext {
  zone: OperationalZone | string;
  duty_type: string;
  shift: string;
  location: string;
  environment: string;
  start_time: string;
  end_time?: string | null;
  temporary: boolean;
  auto_revert: boolean;
}

export interface WellnessRecord {
  timestamp: string;
  fatigue: number; // 1-5
  stress: number;  // 1-5
  mood: number;    // 1-5
  sleep_quality: number; // 1-5
  notes?: string | null;
  evidence_status: EvidenceStatus;
}

export interface PhysiologicalRecord {
  timestamp: string;
  hr: number;
  hrv: number;
  resting_hr: number;
  sleep: number;
  activity: number;
  respiration?: number | null;
  temperature?: number | null;
  signal_quality: number;
  evidence_status: EvidenceStatus;
}

export interface Prediction {
  risk_level: RiskLevel;
  confidence: number;
  trajectory: Trajectory;
  contributing_factors: Array<{ factor: string; impact: number; description?: string }>;
  evidence_status: EvidenceStatus;
  model_version?: string;
}

export interface Recommendation {
  type: string;
  priority: RecommendationPriority;
  explanation: string;
  status: RecommendationStatus;
}

export interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
  force?: string | null;
  unit_id?: string | null;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}
