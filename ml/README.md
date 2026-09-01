# SEPTERIA Machine Learning (ML) Engine

## Phase 1 Status
Directory structure and contracts established.
AI training and model inference will be implemented in subsequent phases (Phase 9+).

## Directory Structure
- `data/`: Dataset preprocessing, synthetic feature generation, and cohort definitions.
- `features/`: Baseline computation, rolling HRV statistics, workload indices, and zone features.
- `models/`: Trained model binaries (XGBoost, baseline comparators) and metadata.
- `training/`: Training pipelines, subject-wise cross-validation, hyperparameter tuning.
- `inference/`: Real-time prediction pipeline, confidence scoring, evidence tagging.
- `evaluation/`: SHAP explanation generation, performance metrics, confusion matrices.

## Guiding Principles (Build Contract)
- Multimodal stress/recovery risk level: LOW / MODERATE / HIGH.
- Confidence output and SHAP driver explanations with every prediction.
- Clear evidence status tagging: OBSERVED / DERIVED / INFERRED / UNCERTAIN.
- Strictly framed as welfare & stress monitoring; NOT psychiatric diagnosis or suicide prediction.
