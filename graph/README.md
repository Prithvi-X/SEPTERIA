# SEPTERIA Contextual Personnel Graph

## Phase 1 Status
Directory structure and contracts established.
Contextual Personnel Graph construction and analysis will be implemented in Phase 10.

## Directory Structure
- `construction/`: Graph builder using NetworkX, mapping shared operational contexts (unit, shift, zone, workload).
- `features/`: Contextual similarity features, cold-start priors, neighborhood embeddings.
- `analysis/`: Shared-pattern detection across co-deployed units, cautious imputation for missing sensor data.

## Guiding Principles (Build Contract)
- The graph represents operational context relationships, NOT raw peer medical or physiological data sharing.
- Privacy-first: aggregate trends and context similarities only.
