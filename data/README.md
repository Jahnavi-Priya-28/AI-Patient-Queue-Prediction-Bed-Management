# PatientFlow AI — Synthetic Datasets & Data Governance

## Overview

This directory contains synthetic datasets used for model training and forecasting in PatientFlow AI:
1. `queue_training.csv` (~10,000+ records): Operational queue check-ins and waiting times for XGBoost regression training.
2. `department_timeseries.csv` (~10,000+ records): Hourly/department multivariate time series for LSTM demand forecasting.

## Privacy & Synthetic Disclaimer

> [!IMPORTANT]
> **No Real PII / PHI**: All patient IDs, names, timestamps, wait times, and hospital metrics in these datasets are synthetically generated using a deterministic random seed. No actual hospital or patient data is included.

## Data Schema & Governance

Detailed column definitions, data types, value ranges, and generation logic are documented in [`DATA_DICTIONARY.md`](file:///c:/Users/jannu/OneDrive/Desktop/huii/data/DATA_DICTIONARY.md).

## Production Real-Data Swapping Protocol

To replace synthetic data with authorized real-world hospital operational data:
1. Export real hospital queue logs matching the schema in `DATA_DICTIONARY.md`.
2. Place the cleaned CSV files in this `data/` directory.
3. Run `python backend/scripts/train_xgboost.py` and `python backend/scripts/train_lstm.py` to retrain and persist new model weights.
