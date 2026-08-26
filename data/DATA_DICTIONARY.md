# Data Dictionary — PatientFlow AI

## 1. `queue_training.csv` (XGBoost Waiting Time Dataset)

Target Variable: `actual_wait_minutes` (Continuous Float)

| Column Name | Data Type | Description | Values / Range |
|---|---|---|---|
| `queue_entry_id` | String / UUID | Unique identifier for queue record | `Q10001` - `Q20000` |
| `department_id` | Integer / Categorical | Department code | 1: Emergency, 2: Cardiology, 3: Orthopedics, 4: General Med, 5: ENT, 6: Pediatrics |
| `priority` | String / Categorical | Clinical triage priority level | `NORMAL`, `URGENT`, `EMERGENCY` |
| `appointment_type` | String / Categorical | Type of visit | `WALK_IN`, `APPOINTMENT`, `FOLLOW_UP` |
| `queue_length` | Integer | Total patients ahead in queue at check-in | 0 - 50 |
| `doctors_available` | Integer | Number of active duty doctors in department | 1 - 10 |
| `avg_consultation_minutes` | Float | Rolling avg consultation length for department | 5.0 - 45.0 |
| `recent_arrivals_30m` | Integer | Patient check-ins in the past 30 mins | 0 - 25 |
| `recent_completions_30m` | Integer | Consultations completed in past 30 mins | 0 - 20 |
| `hour` | Integer | Hour of day (24-hour format) | 0 - 23 |
| `day_of_week` | Integer | Day of week | 0 (Monday) - 6 (Sunday) |
| `actual_wait_minutes` | Float | **Target**: Ground truth waiting duration (start - checkin) | 2.0 - 180.0 |

---

## 2. `department_timeseries.csv` (LSTM Demand Forecasting Dataset)

Multivariate sequential dataset aggregated hourly per department.

| Column Name | Data Type | Description | Values / Range |
|---|---|---|---|
| `timestamp` | Datetime (ISO 8601) | Hourly bucket timestamp | `2025-01-01T00:00:00` onwards |
| `department_id` | Integer | Department code | 1 - 6 |
| `arrivals` | Integer | Total patient arrivals in hour | 0 - 60 |
| `completions` | Integer | Total consultations finished in hour | 0 - 50 |
| `queue_length` | Integer | Department queue depth at end of hour | 0 - 70 |
| `avg_wait_minutes` | Float | Average waiting time in hour | 5.0 - 150.0 |
| `available_doctors` | Integer | Active doctors during hour | 1 - 12 |
| `available_beds` | Integer | Unoccupied beds in department wards | 0 - 40 |
