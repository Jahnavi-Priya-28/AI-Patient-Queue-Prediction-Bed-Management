# PatientFlow AI — AI Patient Queue Prediction & Bed Management System

> **Project ID**: 102 | **Type**: Production-Grade Reference Implementation (Final Year Project)  
> **Core ML**: XGBoost (waiting-time regression) + LSTM (department demand forecasting)  
> **Stack**: Next.js (App Router, TypeScript, Tailwind CSS) + FastAPI (Python 3.13, SQLAlchemy 2.x, Alembic, PostgreSQL)

---

## System Overview

PatientFlow AI is a modular monolithic healthcare operational intelligence platform designed to eliminate hospital waiting room bottlenecks, predict patient waiting times, forecast department demand, and manage ward bed allocations concurrently.

### Key Capabilities

- **Role-Based Workflows**: Tailored portals for **Patient**, **Doctor**, **Receptionist**, and **Admin**.
- **Atomic Queue Check-In**: Concurrency-safe token generation (`SELECT ... FOR UPDATE`), real-time queue positioning, and priority triage (`NORMAL`, `URGENT`, `EMERGENCY`).
- **XGBoost Waiting Time Prediction**: Real-time regression based on operational queue features (queue depth, active doctors, priority, historical consultation duration).
- **LSTM Department Demand Forecasting**: Multi-horizon multivariate time-series forecasting (1h, 6h, 12h, 24h ahead).
- **Atomic Bed Allocation**: State machine tracking bed status (`AVAILABLE`, `OCCUPIED`, `CLEANING`, `MAINTENANCE`) across hospital wards.
- **Audit Logging & Analytics**: Security event logging and live PostgreSQL aggregated operational metrics.

---

## Directory Structure

```
patientflow-ai/
├── frontend/                     # Next.js (App Router, TypeScript, Tailwind CSS)
│   ├── app/                      # Page components & layouts
│   ├── components/               # Reusable UI components
│   ├── lib/                      # API client & Zod schemas
│   └── public/                   # Static assets
├── backend/                      # FastAPI Python Modular Monolith
│   ├── app/                      # Core application code (main, api, services, db, models, ml)
│   ├── alembic/                  # Database migration scripts
│   ├── tests/                    # Pytest test suite
│   ├── .env.example              # Sample environment variables
│   └── requirements.txt          # Python dependencies
├── data/                         # Synthetic datasets & data dictionary
│   ├── DATA_DICTIONARY.md
│   └── README.md
├── ml/                           # Offline ML training scripts & model artifacts
│   ├── xgboost/
│   ├── lstm/
│   └── models/
├── docs/                         # Academic documentation & viva defense
│   ├── ARCHITECTURE.md
│   ├── ML.md
│   └── VIVA_PREP.md
└── README.md                     # Master setup guide
```

---

## Local Development & Setup Instructions

### Prerequisites
- **Node.js**: v18.0.0+
- **Python**: v3.11+ (Python 3.13 supported)
- **PostgreSQL**: Local install running on port `5432`

---

### Step 1: Database Setup
1. Open PostgreSQL CLI (`psql`) or PgAdmin.
2. Create the database:
   ```sql
   CREATE DATABASE patientflow_db;
   ```

---

### Step 2: Backend Setup (FastAPI)
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.env`:
   ```bash
   cp .env.example .env
   ```
5. Apply database migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - Interactive API Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/api/health`

---

### Step 3: Frontend Setup (Next.js)
1. In a new terminal window, navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js dev server:
   ```bash
   npm run dev
   ```
4. Access the web interface at `http://localhost:3000`.

---


---

## Demo Accounts

Authentication uses `EMAIL + PASSWORD`. The backend derives the user's role, organization, permissions, and active status from the authenticated account.

Development seed accounts:

| Portal | Role | Email | Password |
| --- | --- | --- | --- |
| Administration Login | `HOSPITAL_ADMIN` | `admin@example.com` | `AdminPassword123!` |
| Receptionist Login | `RECEPTIONIST` | `reception@example.com` | `ReceptionPassword123!` |
| Doctor Login | `DOCTOR` | `doctor@example.com` | `DoctorPassword123!` |
| Patient Login | `PATIENT` | `patient@example.com` | `PatientPassword123!` |

Public registration creates patient accounts only. Hospital administrators can create staff accounts through the protected `/api/auth/admin/users` endpoint.

Security behavior:

- Login derives the stored backend role; the client never submits or selects a role.
- Inactive users and inactive organizations cannot authenticate.
- Staff analytics are protected from patient accounts.
- Dashboard pages verify the session through `/api/auth/me`; local browser storage is only a cache.
## Testing & Verification

- **Backend Pytest Suite**:
  ```bash
  cd backend
  pytest
  ```

- **Frontend Type Checking / Lint / Build**:
  ```bash
  cd frontend
  npm run type-check
  ```


