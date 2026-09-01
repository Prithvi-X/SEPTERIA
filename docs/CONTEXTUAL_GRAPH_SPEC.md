# SEPTERIA Contextual Personnel Graph Specification (Phase 7)

**Project**: SEPTERIA — AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**SIH Problem Statement**: SIH26186  
**Document**: `docs/CONTEXTUAL_GRAPH_SPEC.md`  
**Technology**: NetworkX + PostgreSQL  
**Status**: IMPLEMENTED & VERIFIED — PHASE 7 COMPLETE

---

> [!IMPORTANT]
> ### Privacy & Ethical Graph Mandate
> 1. **No Peer Health Exposure**: The graph models **contextual relationships** (Unit, Zone, Shift, Duty, Environment, Workload, Trajectory Category). Raw physiological telemetry (HR, PRV, EDA, TEMP, Sleep) is **NEVER** shared across peer nodes or exposed to unauthorized users.
> 2. **Conservative Missing-Data Support**: Values are inferred from contextual cohorts only when personal history is absent, and must be explicitly tagged as `EVIDENCE_STATUS = "INFERRED"` with full provenance. If evidence is insufficient, data remains `MISSING`.
> 3. **Non-Permanent Cold-Start Prior**: Cold-start cohort priors decay dynamically ($w_{\text{prior}} = \max(0, 1 - \frac{d}{3})$) as personal history accumulates over 3 days.
> 4. **Tri-Level RBAC Separation**:
>    - **Soldier View**: Self node and personal operational assignments only.
>    - **Commander View (Authority)**: Aggregated unit patterns and headcount (e.g. 14 personnel affected); zero individual biometrics.
>    - **Medical / Welfare Officer View**: Authorized affected IDs, cohort recovery burden, and operational drivers.

---

## 1. Graph Entity & Relationship Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STRUCTURAL CONTEXT NODES                          │
│                                                                             │
│   [ Unit: BSF-BN-47 ] ◄───────┐                                             │
│   [ Zone: ZONE_2 ]   ◄────────┼──────────┐                                  │
│   [ Shift: Night ]   ◄────────┼──────────┼──────────┐                       │
│   [ Duty: Night Patrol ] ◄────┼──────────┼──────────┼──────────┐            │
└───────────────────────────────┼──────────┼──────────┼──────────┼────────────┘
                                │          │          │          │
                     (BELONGS_TO)│(ASSIGNED)│(ASSIGNED)│(ASSIGNED)│
                                │          │          │          │
┌───────────────────────────────┴──────────┴──────────┴──────────┴────────────┐
│                             PERSONNEL NODES                                 │
│                                                                             │
│   [ Personnel: BSF-47-01 ] ◄────────────────────────► [ Personnel: BSF-47-02 ]
│                 │                                                   │       │
│                 │ (SAME_UNIT + SAME_ZONE + SAME_SHIFT + WORKLOAD)   │       │
│                 │                                                   │       │
│                 ▼                                                   ▼       │
│   [ Personnel: BSF-47-03 ] ◄────────────────────────► [ Personnel: BSF-47-04 ]
│                                                                             │
│   * Peer Edges carry CONTEXTUAL SIMILARITY WEIGHTS (0.0 to 1.0)             │
│   * ZERO raw biometrics or health records are transferred across edges      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Entity Node Definitions
- **`PERSONNEL`**: Soldier node containing `personnel_id`, `unit_id`, `role`, `privacy_scope = RESTRICTED_SELF`.
- **`UNIT`**: Military formation node (e.g. 47th Battalion BSF), `privacy_scope = UNIT`.
- **`ZONE`**: Operational context node (`ZONE_1`, `ZONE_2`, `ZONE_3`), `privacy_scope = PUBLIC`.
- **`SHIFT`**: Shift timing node (`Day`, `Night`, `12-hr Rotation`), `privacy_scope = PUBLIC`.
- **`DUTY`**: Duty specialization node (`Night Patrol`, `Static Guard`, `QRT`), `privacy_scope = PUBLIC`.
- **`ENVIRONMENT`**: Environmental strain node (`High Heat & Dust`, `High Altitude`), `privacy_scope = PUBLIC`.

### Edge Similarity Weights
| Relationship Attribute | Weight Contribution | Operational Rationale |
| :--- | :---: | :--- |
| `SAME_UNIT` | $0.25$ | Shared command, base station, and administrative support. |
| `SAME_ZONE` | $0.15$ | Shared environmental stressors and operational threat level. |
| `SAME_SHIFT` | $0.15$ | Shared circadian alignment and sleep opportunity window. |
| `SAME_DUTY` | $0.15$ | Shared cognitive and physical duty demands. |
| `SAME_ENVIRONMENT` | $0.10$ | Shared climate, altitude, and thermal strain. |
| `SIMILAR_WORKLOAD` | $0.10$ | Matching workload tier (High/Extreme vs Normal). |
| `SIMILAR_RECOVERY_TRAJECTORY`| $0.10$ | Matching autonomic recovery category (Deteriorating/Stable). |
| **Total Composite Weight** | $\mathbf{\sum w_i \in [0.0, 1.0]}$ | Threshold for peer edge creation: $\ge 0.40$. |

---

## 2. Shared-Pattern Detection Engine

The shared-pattern detector evaluates connected operational clusters sharing $(Unit, Zone, Shift, Duty)$:

$$\text{CohortSize} = N_{\text{members}}$$
$$\text{DeterioratingCount} = \sum_{i \in \text{Cohort}} \mathbb{I}(\text{Trajectory}_i = \text{Deteriorating} \lor \text{RecoveryDebt}_i \ge 50)$$

**Trigger Condition**:
$$\text{Trigger} = \begin{cases} \text{True}, & \text{if } \text{DeterioratingCount} \ge \max(3, \lceil 0.40 \times N_{\text{members}} \rceil) \\ \text{False}, & \text{otherwise} \end{cases}$$

### Pattern Output Views:
1. **Command Authority View (Commander)**:
   - Headcount of affected personnel (e.g. 14 of 20).
   - Operational context (Zone 2, Night Patrol).
   - Duration and pattern confidence.
   - **Strict Zero-Biometric Guarantee**: No heart rates, HRV, or medical metrics displayed.
2. **Authorized Welfare View (Medical Officer / Psychologist)**:
   - Affected personnel IDs for targeted welfare review.
   - Average cohort recovery burden score ($68.0 / 100$).
   - Primary operational drivers (Night duty, high heat, consecutive recovery suppression).
   - Actionable follow-up recommendation.

---

## 3. Conservative Contextual Missing-Data Support

When telemetry intervals are missing or corrupted, SEPTERIA follows a strict 3-tier evidence hierarchy:

```
                            [ Query Missing Observation ]
                                          │
                                          ▼
                         [ Personal History Available? ]
                                   (N >= 3 samples)
                                    /           \
                                 YES             NO
                                 /                 \
        [ EVIDENCE_STATUS = PERSONAL_HISTORY ]      [ Contextual Cohort Available? ]
        - Value = Median(Personal Samples)               (N >= 3 peer medians in same
        - Confidence = 0.85                               Unit, Zone, Shift, Duty)
        - is_inferred = False                              /                    \
                                                        YES                      NO
                                                        /                          \
                        [ EVIDENCE_STATUS = INFERRED ]               [ EVIDENCE_STATUS = MISSING ]
                        - Value = Median(Cohort Samples)             - Value = None
                        - Confidence = 0.65                          - Confidence = 0.0
                        - is_inferred = True                         - is_inferred = False
                        - Provenance Logged                          - Never Silently Fill
```

---

## 4. Cold-Start Prior Decay

For newly deployed personnel with $< 3$ days of historical recording:
$$w_{\text{prior}} = \max\left(0.0, 1.0 - \frac{\text{HistoryDays}}{3.0}\right)$$
$$\text{is\_cohort\_prior} = \begin{cases} \text{True}, & \text{if } \text{HistoryDays} < 3 \\ \text{False}, & \text{if } \text{HistoryDays} \ge 3 \end{cases}$$

---

## 5. API Endpoints

- `GET /api/v1/graph/personnel/{id}/context`: Individual graph neighborhood & cold-start status.
- `GET /api/v1/graph/unit/{unit_id}/patterns`: Unit-level command authority pattern summaries.
- `GET /api/v1/graph/shared-patterns`: Multi-unit pattern feed with RBAC-filtered welfare details.
- `POST /api/v1/graph/rebuild`: Deterministic graph reconstruction from authoritative data.
- `GET /api/v1/graph/visualization`: 2D spring layout node/edge coordinates.
- `POST /api/v1/graph/missing-data-support`: Conservative missing-data query endpoint.

---

## 6. Verification & Test Summary

- `backend/tests/test_contextual_graph.py`: **12/12 tests passed**.
- `backend/tests/test_tri_layer_integration.py`: **7/7 tests passed**.
- `ml/tests/`: **11/11 tests passed**.
- **Total Suite Passing**: **30/30 tests (100%)**.
