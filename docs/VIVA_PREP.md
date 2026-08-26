# Viva Defense & Academic Rigor Pack — PatientFlow AI

This document contains defensible answers for viva examiners and academic reviewers evaluating PatientFlow AI.

---

### Q1: Why XGBoost for waiting time prediction instead of Linear Regression or Random Forest?
**Answer**: Waiting time in hospital queues exhibits strong non-linear interactions (e.g., arrival rate interaction with doctor availability and priority tiers). Linear regression fails to capture these non-linearities. While Random Forest is capable, XGBoost uses gradient boosting with tree pruning and regularization (L1/L2) which prevents overfitting on operational outliers, trains faster on tabular data, and provides superior predictive accuracy (lower MAE/RMSE).

### Q2: Why LSTM for department demand forecasting instead of ARIMA or Prophet?
**Answer**: Hospital arrival demand is multivariate and non-stationary. ARIMA assumes linear univariate time-series relationships. Prophet is optimized for daily/weekly additive seasonality but struggles with real-time operational feedback loops (e.g., how bed capacity and completions affect arrivals across 6 departments). LSTM (Long Short-Term Memory) neural networks handle multivariate sequential state vectors and non-linear temporal dependencies across multiple horizon steps (1h, 6h, 12h, 24h).

### Q3: Why did you choose a Modular Monolith instead of Microservices or Docker?
**Answer**: For local grading, evaluation, and viva demonstration, microservices introduce unnecessary operational overhead (distributed tracing, network latency, cross-service transactions, complex deployment scripts). A modular monolith enforces strict domain boundaries inside `services/` and `models/`, running within a single process space. This guarantees ACID transactions for check-ins and bed assignments while remaining simple to set up, run, and defend.

### Q4: Why use polling instead of WebSockets for live queue updates?
**Answer**: At hospital department queue scale (tens to hundreds of updates per hour per ward), short-polling (every 5-15 seconds) is far simpler, highly reliable, stateless, and defense-ready. WebSockets require stateful connection handling, heartbeat pinging, and complex reconnection logic that adds failure modes during demonstrations without measurable gain for human queue updates.

### Q5: How do you handle fallback if the ML inference service fails?
**Answer**: Graceful degradation: If XGBoost model inference fails or model files are missing, the queue service falls back to a deterministic rule-based heuristic (`estimated_wait = (queue_position / active_doctors) * avg_consultation_time`). The application never crashes or blocks check-in.

### Q6: How is data privacy ensured?
**Answer**: Synthetic datasets are generated deterministically with no real patient PII/PHI. Passwords use Argon2 hashing, authentication uses signed JWTs, and audit logs exclude sensitive payloads or tokens.
