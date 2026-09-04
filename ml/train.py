import json
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from ml.dataset_generator import generate_synthetic_dataset

BASE_ML_DIR = Path(__file__).resolve().parent

FEATURE_COLS = [
    "amount",
    "retry_count",
    "failure_count",
    "transaction_frequency_10min",
    "hour_of_day",
    "previous_success_rate",
    "velocity_score",
    "device_trust_score"
]

def train_and_evaluate():
    csv_path = BASE_ML_DIR / "dataset.csv"
    if not csv_path.exists():
        df = generate_synthetic_dataset(5000)
        df.to_csv(csv_path, index=False)
    else:
        df = pd.read_csv(csv_path)

    X = df[FEATURE_COLS]
    y = df["failed"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    # 1. Random Forest Classifier (Primary non-linear failure predictor)
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]

    rf_metrics = {
        "model_name": "Random Forest Classifier",
        "accuracy": round(float(accuracy_score(y_test, rf_preds)), 4),
        "precision": round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, rf_preds)), 4),
        "f1_score": round(float(f1_score(y_test, rf_preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, rf_probs)), 4),
        "feature_importances": {col: round(float(imp), 4) for col, imp in zip(FEATURE_COLS, rf_model.feature_importances_)}
    }

    # 2. Logistic Regression (Baseline Comparison Model)
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    lr_probs = lr_model.predict_proba(X_test)[:, 1]

    lr_metrics = {
        "model_name": "Logistic Regression (Baseline)",
        "accuracy": round(float(accuracy_score(y_test, lr_preds)), 4),
        "precision": round(float(precision_score(y_test, lr_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, lr_preds)), 4),
        "f1_score": round(float(f1_score(y_test, lr_preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, lr_probs)), 4)
    }

    # 3. Isolation Forest (Unsupervised Anomaly Detector)
    iso_model = IsolationForest(contamination=0.08, random_state=42)
    iso_model.fit(X_train)

    # Package Models
    model_bundle = {
        "rf_model": rf_model,
        "lr_model": lr_model,
        "iso_model": iso_model,
        "feature_cols": FEATURE_COLS,
        "metrics": {
            "random_forest": rf_metrics,
            "logistic_regression": lr_metrics
        }
    }

    # Save to disk
    model_pkl_path = BASE_ML_DIR / "model.pkl"
    with open(model_pkl_path, "wb") as f:
        pickle.dump(model_bundle, f)

    metrics_json_path = BASE_ML_DIR / "ml_metrics.json"
    with open(metrics_json_path, "w") as f:
        json.dump(model_bundle["metrics"], f, indent=2)

    print("=== MODEL TRAINING COMPLETE ===")
    print(f"Random Forest - Accuracy: {rf_metrics['accuracy']*100:.1f}%, F1: {rf_metrics['f1_score']:.3f}, ROC-AUC: {rf_metrics['roc_auc']:.3f}")
    print(f"Logistic Regression - Accuracy: {lr_metrics['accuracy']*100:.1f}%, F1: {lr_metrics['f1_score']:.3f}")
    print(f"Saved model bundle to {model_pkl_path}")

    return model_bundle

if __name__ == "__main__":
    train_and_evaluate()
