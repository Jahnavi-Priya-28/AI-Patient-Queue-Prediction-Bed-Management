import os
import random
import csv
from datetime import datetime, timedelta

# Set deterministic random seed
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

QUEUE_CSV_PATH = os.path.join(DATA_DIR, "queue_training.csv")
TIMESERIES_CSV_PATH = os.path.join(DATA_DIR, "department_timeseries.csv")


def generate_queue_training_data(num_records=10000):
    print(f"[+] Generating {num_records} synthetic XGBoost queue training records...")
    headers = [
        "queue_entry_id", "department_id", "priority", "appointment_type",
        "queue_length", "doctors_available", "avg_consultation_minutes",
        "recent_arrivals_30m", "recent_completions_30m", "hour", "day_of_week",
        "actual_wait_minutes"
    ]

    priorities = ["NORMAL", "URGENT", "EMERGENCY"]
    priority_weights = [0.75, 0.20, 0.05]

    app_types = ["WALK_IN", "APPOINTMENT", "FOLLOW_UP"]
    app_weights = [0.4, 0.4, 0.2]

    records = []
    for i in range(1, num_records + 1):
        q_id = f"Q{10000 + i}"
        dept_id = random.randint(1, 6)
        priority = random.choices(priorities, weights=priority_weights)[0]
        app_type = random.choices(app_types, weights=app_weights)[0]

        queue_length = random.randint(0, 45)
        doctors_available = random.randint(1, 10)
        avg_consult = round(random.uniform(8.0, 30.0), 1)

        arrivals_30m = random.randint(0, 20)
        completions_30m = random.randint(0, 15)

        hour = random.randint(7, 21) # Hospital operating hours
        day_of_week = random.randint(0, 6)

        # Baseline wait logic + non-linear noise
        p_multiplier = 0.2 if priority == "EMERGENCY" else (0.6 if priority == "URGENT" else 1.0)
        base_wait = (queue_length / max(1, doctors_available)) * avg_consult * p_multiplier
        noise = random.normalvariate(0, 3.5)
        actual_wait = max(2.0, round(base_wait + noise, 2))

        records.append([
            q_id, dept_id, priority, app_type, queue_length, doctors_available,
            avg_consult, arrivals_30m, completions_30m, hour, day_of_week, actual_wait
        ])

    with open(QUEUE_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)

    print(f"[SUCCESS] Saved {num_records} rows to {QUEUE_CSV_PATH}")


def generate_department_timeseries_data(num_hours=2000):
    print(f"[+] Generating department time-series forecasting data ({num_hours} hours x 6 departments)...")
    headers = [
        "timestamp", "department_id", "arrivals", "completions",
        "queue_length", "avg_wait_minutes", "available_doctors", "available_beds"
    ]

    start_date = datetime(2025, 1, 1, 0, 0, 0)
    records = []

    for dept_id in range(1, 7):
        current_queue = random.randint(2, 10)
        for h in range(num_hours):
            ts = start_date + timedelta(hours=h)
            hour_of_day = ts.hour

            # Peak arrival hours 9 AM - 4 PM
            arrival_lambda = 15 if 9 <= hour_of_day <= 16 else 4
            arrivals = max(0, int(random.normalvariate(arrival_lambda, 3)))
            completions = max(0, int(random.normalvariate(arrivals * 0.8, 2)))

            current_queue = max(0, current_queue + arrivals - completions)
            doctors = random.randint(2, 8)
            beds = max(0, 30 - int(current_queue * 0.4))
            avg_wait = round((current_queue / max(1, doctors)) * 12.0 + random.uniform(-2, 2), 1)

            records.append([
                ts.isoformat(), dept_id, arrivals, completions,
                current_queue, avg_wait, doctors, beds
            ])

    with open(TIMESERIES_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)

    print(f"[SUCCESS] Saved time-series records to {TIMESERIES_CSV_PATH}")


if __name__ == "__main__":
    generate_queue_training_data()
    generate_department_timeseries_data()
