# Machine Learning System Design & Governance — PatientFlow AI

## Executive Disclaimer

> [!WARNING]
> PatientFlow AI's machine learning models are **operational planning and queue optimization tools**. They do NOT perform clinical diagnosis, medical triage, or patient risk assessment. All datasets used during development are synthetic. Validation against authorized real-world hospital operational data is required prior to any clinical or live hospital deployment.

---

## 1. XGBoost Waiting Time Regression Model

### Problem Framing
Supervised regression predicting individual patient waiting time (`actual_wait_minutes`) from the moment of check-in until consultation start.

### Feature Pipeline
- **Categorical**: `department_id`, `priority` (`NORMAL`, `URGENT`, `EMERGENCY`), `appointment_type` (`WALK_IN`, `APPOINTMENT`, `FOLLOW_UP`).
- **Numerical Operational Features**: `queue_length`, `doctors_available`, `avg_consultation_minutes`, `recent_arrivals_30m`, `recent_completions_30m`, `hour`, `day_of_week`.

### Training Discipline
1. Held-out test set split (80% train/val, 20% test).
2. K-Fold cross-validation during hyperparameter optimization.
3. Performance Metrics reported on held-out test set:
   - Mean Absolute Error (**MAE**)
   - Root Mean Squared Error (**RMSE**)
   - Coefficient of Determination (**R²**)
4. Feature importance extraction saved alongside model artifacts via `joblib`.

---

## 2. LSTM Department Demand Forecasting Model

### Problem Framing
Multivariate time-series forecasting predicting arrival demand per department across multi-step forecast horizons: **1h, 6h, 12h, and 24h ahead**.

### Features & Sequence Windowing
- Inputs: Past 24-hour sequence of `[arrivals, completions, queue_length, avg_wait_minutes, available_doctors, available_beds]`.
- Temporal train/val/test split (no random shuffling to prevent data leakage across time boundaries).
- Scaling fit exclusively on training window.
