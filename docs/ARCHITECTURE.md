# Architecture & System Design — PatientFlow AI

## System Overview

PatientFlow AI is built as a **production-grade modular monolith**. It avoids microservices, message brokers, and container complexity to ensure zero setup friction while delivering clean, defensible software engineering practices.

```
+-----------------------------------------------------------------------------------+
|                                 NEXT.JS FRONTEND                                  |
|   (App Router, TypeScript, React, Tailwind CSS, Recharts, React Hook Form + Zod)  |
+-----------------------------------------------------------------------------------+
                                         |
                                         | HTTP REST APIs (JSON)
                                         v
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND SYSTEM                               |
|                                                                                   |
|  +----------------+  +-----------------+  +-----------------+  +---------------+  |
|  | Auth Service   |  | Queue Service   |  | Bed Service     |  | ML Inference  |  |
|  | (JWT + Argon2) |  | (Token/State)   |  | (State Trans.)  |  | (XGB/LSTM)    |  |
|  +----------------+  +-----------------+  +-----------------+  +---------------+  |
|          |                    |                    |                   |          |
|          +--------------------+--------------------+-------------------+          |
|                                         |                                         |
|                                         v                                         |
|                       SQLAlchemy 2.x ORM + Alembic                                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                               POSTGRESQL DATABASE                                 |
|  (users, patients, doctors, departments, wards, beds, appointments, queue_entries)|
+-----------------------------------------------------------------------------------+
```

## Core Modules & Boundaries

1. **Authentication & Authorization (`api/auth.py`, `services/auth.py`)**:
   - Argon2 password hashing.
   - JWT access + refresh tokens.
   - Centralized RBAC dependency (`require_role()`).

2. **Queue Management (`api/queue.py`, `services/queue.py`)**:
   - Atomic check-in transaction.
   - Concurrency-safe token generation using database locking (`SELECT ... FOR UPDATE`).
   - Ground truth calculation: `actual_wait_minutes = consultation_start - check_in_time`.

3. **Bed Management (`api/beds.py`, `services/beds.py`)**:
   - State machine: `AVAILABLE` -> `OCCUPIED` -> `CLEANING` -> `MAINTENANCE` -> `AVAILABLE`.
   - Prevents illegal state transitions via database transactions.

4. **Machine Learning Serving (`api/ml.py`, `services/ml.py`)**:
   - Offline trained model artifacts loaded via `joblib`.
   - Real-time feature extraction directly from PostgreSQL queries.
   - Persistence of every prediction into `model_predictions` audit table.
