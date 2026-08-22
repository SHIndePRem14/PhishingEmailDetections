"""Trains the PhishGuard TF-IDF + Logistic Regression phishing classifier.

Usage:
    python scripts/train_model.py [path_to_csv]

Loads a labeled CSV (columns: text, label), cleans the text, trains a
TF-IDF vectorizer and Logistic Regression classifier, evaluates it, and
saves the model + vectorizer + metrics to ml_models/.
"""

import json
import os
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app.services.text_preprocessing import clean_text  # noqa: E402

DEFAULT_DATASET = os.path.join(BASE_DIR, "dataset", "phishing_emails.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "phishing_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")


def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")

    df = pd.read_csv(path)

    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'text' and 'label' columns")

    df = df.dropna(subset=["text", "label"])
    df["label"] = df["label"].str.strip().str.lower()
    df = df[df["label"].isin(["phishing", "legitimate"])]

    if df.empty:
        raise ValueError("Dataset has no valid rows after cleaning")

    return df


def main():
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET

    print(f"[1/9] Loading dataset from: {dataset_path}")
    df = load_dataset(dataset_path)
    print(f"      Loaded {len(df)} rows")

    print("[2/9] Cleaning text...")
    df["clean_text"] = df["text"].apply(clean_text)

    print("[3/9] Splitting train/test sets (80/20)...")
    x_train, x_test, y_train, y_test = train_test_split(
        df["clean_text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    print("[4/9] Fitting TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    print("[5/9] Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(x_train_vec, y_train)

    print("[6/9] Evaluating model...")
    y_pred = model.predict(x_test_vec)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label="phishing", zero_division=0)
    recall = recall_score(y_test, y_pred, pos_label="phishing", zero_division=0)
    f1 = f1_score(y_test, y_pred, pos_label="phishing", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=["legitimate", "phishing"])

    print("[7/9] Saving model and vectorizer...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print("[8/9] Saving metrics...")
    metrics = {
        "model_name": "phishing_model.pkl",
        "algorithm": "TF-IDF + Logistic Regression",
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm.tolist(),
        "train_size": len(x_train),
        "test_size": len(x_test),
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print("[9/9] Done.\n")
    print("=" * 50)
    print("TRAINING RESULTS")
    print("=" * 50)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Confusion Matrix (rows=actual, cols=predicted [legit, phishing]):\n{cm}")
    print("=" * 50)
    print(f"Model saved to:      {MODEL_PATH}")
    print(f"Vectorizer saved to: {VECTORIZER_PATH}")
    print(f"Metrics saved to:    {METRICS_PATH}")


if __name__ == "__main__":
    main()
