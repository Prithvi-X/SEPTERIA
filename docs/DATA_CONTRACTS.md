# SEPTERIA Shared Data Contracts (SIH26186)

This document defines the core data schemas shared between Backend, Authority Web, Personnel Mobile, and ML modules.

---

## 1. Core Entities

### Personnel
```typescript
interface Personnel {
  id: string;            // Unique UUID / Internal ID
  personnel_id: string;  // Official identifier e.g., CRPF-88219
  force: string;         // CRPF, BSF, ITBP, CISF, SSB, Assam Rifles
  unit_id: string;       // e.g., BSF-BN-47
  role: string;          // Operational duty/rank e.g., Head Constable (GD)
  posting: string;       // Primary base location
  status: string;        // ACTIVE | ON_LEAVE | TRANSITION | DEPLOYED
}
```

### OperationalContext
```typescript
interface OperationalContext {
  zone: string;          // Zone 1 | Zone 2 | Zone 3
  duty_type: string;     // Patrol, Static, Night Duty, QRT
  shift: string;         // Day, Night, 12-hr
  location: string;      // Geographic Sector
  environment: string;   // High Heat, Extreme Cold, Arid, Standard
  start_time: string;    // ISO 8601 Timestamp
  end_time?: string;     // Scheduled End Timestamp (if temporary)
  temporary: boolean;    // True if temporary deployment
  auto_revert: boolean;  // True if context reverts upon expiry
}
```

### WellnessRecord
```typescript
interface WellnessRecord {
  timestamp: string;     // ISO 8601
  fatigue: number;       // 1 (Well rested) to 5 (Exhausted)
  stress: number;        // 1 (Calm) to 5 (High acute stress)
  mood: number;          // 1 (Low) to 5 (Positive)
  sleep_quality: number; // 1 (Poor) to 5 (Restful)
  notes?: string;        // Private voluntary notes
  evidence_status: string; // OBSERVED
}
```

### PhysiologicalRecord
```typescript
interface PhysiologicalRecord {
  timestamp: string;     // ISO 8601
  hr: number;            // Heart Rate in bpm
  hrv: number;           // rMSSD in ms
  resting_hr: number;    // Resting HR in bpm
  sleep: number;         // Sleep duration in hours
  activity: number;      // Step count or exertion index
  respiration?: number;  // Breaths/min
  temperature?: number;  // Skin/body temp in °C
  signal_quality: number;// 0.0 to 1.0
  evidence_status: string;// OBSERVED
}
```

### Prediction
```typescript
interface Prediction {
  risk_level: "LOW" | "MODERATE" | "HIGH";
  confidence: number;    // 0.0 to 1.0
  trajectory: "STABLE" | "IMPROVING" | "DETERIORATING";
  contributing_factors: Array<{ factor: string; impact: number; description?: string }>;
  evidence_status: "INFERRED";
  model_version: string; // e.g., xgb-proto-v1.0
}
```

### Recommendation
```typescript
interface Recommendation {
  type: string;          // REST_ADVISORY | WELFARE_CHECK | DUTY_ROTATION
  priority: "ROUTINE" | "PRIORITY" | "URGENT";
  explanation: string;   // Reason for recommended welfare action
  status: "PENDING" | "ACKNOWLEDGED" | "IN_PROGRESS" | "COMPLETED" | "DISMISSED";
}
```

---

## 2. Evidence Status Taxonomy

| Status | Definition | Example |
| :--- | :--- | :--- |
| `OBSERVED` | Directly measured from an authorized sensor or self-reported by personnel. | Raw HR reading, submitted wellness rating. |
| `DERIVED` | Statistically computed from observed records. | Rolling 7-day HRV baseline deviation, 14-day sleep deficit. |
| `INFERRED` | Estimated by trained ML models or contextual graph. | Predicted stress risk score, cold-start prior. |
| `UNCERTAIN` | Signal quality or confidence is below required threshold. | Wearable noise artifact, insufficient data history. |
