/**
 * SEPTERIA API Client (Phase 2)
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://septeria-production.up.railway.app/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('septeria_token') : null;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData = null;
    try {
      errorData = await response.json();
    } catch {
      // Ignored if non-json
    }
    const message = errorData?.detail || errorData?.message || `Request failed with status ${response.status}`;
    throw new ApiError(response.status, message, errorData);
  }

  return response.json();
}

export interface ZoneDistribution {
  zone_1: number;
  zone_2: number;
  zone_3: number;
  standard: number;
}

export interface DashboardMetrics {
  total_personnel: number;
  active_units: number;
  active_deployments: number;
  zone_distribution: ZoneDistribution;
  active_temporary_assignments: number;
  personnel_in_transition: number;
  last_updated: string;
  data_classification: string;
}

export interface PersonnelItem {
  id: string;
  personnel_id: string;
  user_id?: string;
  force: string;
  unit_id: string;
  role: string;
  rank?: string;
  posting: string;
  status: string;
  active_context_id?: string;
  current_zone: string;
  current_duty: string;
  current_shift: string;
  current_location: string;
  current_environment: string;
  is_temporary_deployment: boolean;
  remaining_duration_formatted?: string;
  remaining_seconds?: number;
  assignment_end_time?: string;
  leave_status: string;
  post_leave_day_count?: number;
  post_leave_total_days: number;
  return_date?: string;
  created_at: string;
  updated_at: string;
}

export interface OperationalContextItem {
  id: string;
  name?: string;
  personnel_id?: string;
  unit_id?: string;
  zone: string;
  duty_type: string;
  shift: string;
  location: string;
  environment: string;
  start_time: string;
  end_time?: string;
  temporary: boolean;
  auto_revert: boolean;
  status: string;
  previous_context_snapshot?: any;
  notes?: string;
  source: string;
  created_at: string;
  remaining_duration_formatted?: string;
  remaining_seconds?: number;
  is_active: boolean;
}

export interface PersonnelDetail extends PersonnelItem {
  active_context?: OperationalContextItem;
  recent_assignments: OperationalContextItem[];
  leave_events: Array<{
    id: string;
    personnel_id: string;
    leave_type: string;
    leave_start_date?: string;
    leave_end_date: string;
    return_date: string;
    transition_days_total: number;
    status: string;
    recorded_by: string;
    created_at: string;
  }>;
}

export interface UnitItem {
  id: string;
  code: string;
  name: string;
  force: string;
  location: string;
  zone: string;
  personnel_count: number;
}

export interface BulkAssignmentRequest {
  assignment_name: string;
  unit_id?: string;
  personnel_ids?: string[];
  zone: string;
  duty_type: string;
  shift: string;
  location: string;
  environment: string;
  duration_days: number;
  auto_revert: boolean;
  notes?: string;
}

export interface BulkAssignmentResult {
  status: string;
  updated_count: number;
  message: string;
  affected_unit?: string;
  assignment_name: string;
  zone: string;
  auto_revert: boolean;
  end_time?: string;
}

export interface AuditLogItem {
  id: string;
  actor_id: string;
  actor_role: string;
  action: string;
  object_type: string;
  object_id?: string;
  details: Record<string, any>;
  timestamp: string;
  outcome: string;
}

export interface MultimodalAssessment {
  personnel_id?: string;
  advisory_welfare_state: string;
  composite_welfare_score: number;
  multimodal_confidence: number;
  evidence_agreement_score: number;
  is_evidence_conflict: boolean;
  conflict_details?: string;
  contributing_streams: Array<{
    stream: string;
    score?: number;
    weight?: number;
    context?: string;
    z_autonomic?: number;
    direction?: string;
    sleep_deficit_hours?: number;
    summary?: string;
    quality?: number;
    status?: string;
  }>;
  voice_evidence_included: boolean;
  voice_summary?: string;
  graph_evidence_included: boolean;
  graph_summary?: string;
  recommended_action: string;
  action_urgency?: string;
  disclaimer?: string;
}

export interface UnitWelfareSummary {
  unit_id: string;
  total_evaluated: number;
  welfare_state_counts: Record<string, number>;
  primary_contributing_factors: string[];
  shared_patterns_detected: Array<{
    pattern_id: string;
    pattern_type: string;
    affected_headcount: number;
    confidence: string;
    summary: string;
  }>;
  command_advisory_text: string;
}

export interface SharedPatternItem {
  pattern_id: string;
  unit_id: string;
  operational_context: Record<string, any>;
  pattern_type: string;
  affected_personnel_count: number;
  duration_days: number;
  confidence_level: string;
  authority_summary: string;
  welfare_details?: Record<string, any>;
  detected_at: string;
}

export interface GraphVisualizationData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    x: number;
    y: number;
    status?: string;
    unit_id?: string;
    zone?: string;
  }>;
  edges: Array<{
    source: string;
    target: string;
    type: string;
    weight: number;
  }>;
  summary: {
    total_nodes: number;
    total_edges: number;
    total_patterns: number;
  };
}

export interface EdgeFleetOverview {
  total_registered_devices: number;
  active_devices: number;
  offline_devices: number;
  fleet_completeness_pct: number;
  avg_clock_drift_ms: number;
  sources_breakdown: Record<string, number>;
  recent_syncs: Array<{
    device_id: string;
    personnel_id: string;
    source: string;
    sync_status: string;
    last_sync: string;
  }>;
}

export interface SystemHealthAudit {
  system_name: string;
  project_code?: string;
  overall_status?: string;
  status?: string;
  mode?: string;
  claim_boundaries?: {
    clinical_diagnostic_claim: boolean;
    suicide_prediction_claim: boolean;
    capf_field_validation_claim: boolean;
    purpose: string;
  };
  claim_boundaries_verified?: boolean;
  components?: Record<string, any>;
  subsystems?: Record<string, any>;
  timestamp?: string;
  checked_at?: string;
}

export const api = {
  // Health & Auth
  getHealth: () => fetchApi<{ status: string; service: string }>('/health'),
  login: (credentials: { email: string; password: string }) =>
    fetchApi<{ access_token: string; token_type: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
  getMe: () => fetchApi<any>('/auth/me'),

  // Phase 2 Dashboard Metrics
  getDashboardMetrics: () => fetchApi<DashboardMetrics>('/dashboard/metrics'),

  // Phase 2 Units
  getUnits: () => fetchApi<UnitItem[]>('/units/'),

  // Phase 2 Personnel Directory
  getPersonnel: (params: Record<string, string | number | undefined> = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== '') {
        query.append(key, String(val));
      }
    });
    const qs = query.toString();
    return fetchApi<PersonnelItem[]>(`/personnel/${qs ? `?${qs}` : ''}`);
  },
  getPersonnelDetail: (personnelId: string) =>
    fetchApi<PersonnelDetail>(`/personnel/${personnelId}`),

  recordLeaveReturn: (
    personnelId: string,
    data: { leave_type: string; leave_end_date: string; return_date: string }
  ) =>
    fetchApi<{
      status: string;
      message: string;
      personnel_id: string;
      post_leave_day_count: number;
      post_leave_total_days: number;
    }>(`/personnel/${personnelId}/leave-return`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Phase 2 Operational Context & Assignments
  getOperations: (params: Record<string, string | number | undefined> = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== '') {
        query.append(key, String(val));
      }
    });
    const qs = query.toString();
    return fetchApi<OperationalContextItem[]>(`/operations/${qs ? `?${qs}` : ''}`);
  },
  createAssignment: (data: any) =>
    fetchApi<OperationalContextItem>('/operations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  bulkAssign: (data: BulkAssignmentRequest) =>
    fetchApi<BulkAssignmentResult>('/operations/bulk-assign', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  evaluateReversions: () =>
    fetchApi<{ status: string; reverted_count: number; message: string }>('/operations/evaluate-reversions', {
      method: 'POST',
    }),

  // Phase 2 Audit Logs (Admin only)
  getAuditLogs: () => fetchApi<AuditLogItem[]>('/audit-logs/'),

  // Phase 7 Contextual Graph Intelligence
  getUnitPatterns: (unitId: string) =>
    fetchApi<{ unit_id: string; total_shared_patterns: number; patterns: SharedPatternItem[]; view_type: string }>(`/graph/unit/${unitId}/patterns`),
  getAllSharedPatterns: () =>
    fetchApi<{ total_patterns_detected: number; patterns: SharedPatternItem[]; is_welfare_view: boolean }>('/graph/shared-patterns'),
  getGraphVisualization: () =>
    fetchApi<GraphVisualizationData>('/graph/visualization'),
  getPersonnelGraphContext: (personnelId: string) =>
    fetchApi<any>(`/graph/personnel/${personnelId}/context`),

  // Phase 8 Multimodal Welfare Intelligence
  evaluateMultimodal: (payload: any) =>
    fetchApi<MultimodalAssessment>('/welfare/evaluate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getPersonnelWelfare: (personnelId: string) =>
    fetchApi<MultimodalAssessment>(`/welfare/personnel/${personnelId}/current`),
  getUnitWelfareSummary: (unitId: string) =>
    fetchApi<UnitWelfareSummary>(`/welfare/unit/${unitId}/summary`),

  // Phase 9 Edge & Telemetry Fleet Health
  getEdgeOverview: () =>
    fetchApi<EdgeFleetOverview>('/edge/authority/overview'),
  simulateEdgeStream: (scenarioCode: string) =>
    fetchApi<{ status: string; scenario: string; records_ingested: number; sync_status: string }>(`/edge/demo/simulate-stream?scenario=${scenarioCode}`, {
      method: 'POST',
    }),

  // Phase 10 System Administration & Demo Management
  resetDemoState: () =>
    fetchApi<{ status: string; message: string; timestamp: string }>('/system/reset-demo', {
      method: 'POST',
    }),
  getSystemHealthAudit: () =>
    fetchApi<SystemHealthAudit>('/system/health-audit'),
};
