import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "queue_training.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, "xgboost_wait_time.joblib")


def train_xgboost_model():
    print("[+] Loading synthetic dataset from:", DATA_PATH)
    df = pd.read_csv(DATA_PATH)

    # Preprocessing & Feature Encoding
    priority_map = {"NORMAL": 0, "URGENT": 1, "EMERGENCY": 2}
    app_type_map = {"WALK_IN": 0, "APPOINTMENT": 1, "FOLLOW_UP": 2}

    df["priority_encoded"] = df["priority"].map(priority_map)
    df["app_type_encoded"] = df["appointment_type"].map(app_type_map)

    features = [
        "department_id", "priority_encoded", "app_type_encoded",
        "queue_length", "doctors_available", "avg_consultation_minutes",
        "recent_arrivals_30m", "recent_completions_30m", "hour", "day_of_week"
    ]
    target = "actual_wait_minutes"

    X = df[features]
    y = df[target]

    # Train / Test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    print(f"[+] Training XGBoost Regressor on {len(X_train)} samples...")
    model = xgb.XGBRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )

    model.fit(X_train, y_train)

    # Evaluation on held-out test set
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("==========================================")
    print("XGBoost Waiting Time Prediction Metrics:")
    print(f"  MAE  (Mean Absolute Error):  {mae:.3f} minutes")
    print(f"  RMSE (Root Mean Sq Error):   {rmse:.3f} minutes")
    print(f"  R^2  (Coeff of Determin.):  {r2:.3f}")
    print("==========================================")

    # Save model artifact and feature metadata
    artifact = {
        "model": model,
        "features": features,
        "metrics": {"mae": mae, "rmse": rmse, "r2": r2},
        "model_version": "v1.0.0-xgboost",
    }
    joblib.dump(artifact, MODEL_SAVE_PATH)
    print(f"[SUCCESS] Model artifact saved to: {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train_xgboost_model()
