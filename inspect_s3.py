import os
import pickle
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import classification_report, confusion_matrix
import glob
from ml.model_training.train import extract_authentic_signals_from_subject

def diagnose_subject_s3():
    wesad_dir = os.path.join("ml", "data", "WESAD")
    pkl_files = sorted(glob.glob(os.path.join(wesad_dir, "*.pkl")))

    print("🔍 Extracting signals across all subjects to isolate S3...")
    subject_data = {}
    for pkl_file in pkl_files:
        sub_name = os.path.basename(pkl_file).split('.')[0]
        X_sub, y_sub = extract_authentic_signals_from_subject(pkl_file)
        if X_sub is not None:
            subject_data[sub_name] = (X_sub, y_sub)

    if 'S3' not in subject_data:
        print("❌ S3 not found!")
        return

    X_s3, y_s3 = subject_data['S3']
    print("\n==================================================")
    print("📊 1. S3 RAW CLASS DISTRIBUTION (1-Sec Instances)")
    print("==================================================")
    unique, counts = np.unique(y_s3, return_counts=True)
    for u, c in zip(unique, counts):
        lbl = {0: 'Baseline', 1: 'Mild', 2: 'Stress'}.get(u)
        print(f"  Class {u} ({lbl}): {c} instances ({c/len(y_s3)*100:.1f}%)")

    # Inspect Feature Statistics of S3
    print("\n==================================================")
    print("📈 2. S3 CALIBRATED FEATURE SUMMARY (Z-Scores)")
    print("==================================================")
    print(X_s3.describe().T[['mean', 'std', 'min', 'max']])

    # Compare With & Without Class Balancing for S3
    train_subs = [s for s in subject_data.keys() if s != 'S3']
    X_train = pd.concat([subject_data[s][0] for s in train_subs], ignore_index=True)
    y_train = np.concatenate([subject_data[s][1] for s in train_subs])

    # Experiment A: With Balanced Weights
    weights_balanced = compute_sample_weight('balanced', y_train)
    clf_balanced = XGBClassifier(n_estimators=140, max_depth=5, learning_rate=0.05, random_state=42, eval_metric='mlogloss')
    clf_balanced.fit(X_train, y_train, sample_weight=weights_balanced)
    preds_balanced = clf_balanced.predict(X_s3)

    # Experiment B: Without Balanced Weights (Standard)
    clf_standard = XGBClassifier(n_estimators=140, max_depth=5, learning_rate=0.05, random_state=42, eval_metric='mlogloss')
    clf_standard.fit(X_train, y_train)
    preds_standard = clf_standard.predict(X_s3)

    print("\n==================================================")
    print("⚖️ 3. S3 COMPARATIVE CONFUSION MATRIX")
    print("==================================================")
    print("--- [A] With Class Balancing ---")
    print(confusion_matrix(y_s3, preds_balanced))
    print(classification_report(y_s3, preds_balanced, target_names=['Baseline', 'Mild', 'Stress']))

    print("--- [B] Without Class Balancing (Standard) ---")
    print(confusion_matrix(y_s3, preds_standard))
    print(classification_report(y_s3, preds_standard, target_names=['Baseline', 'Mild', 'Stress']))

if __name__ == "__main__":
    diagnose_subject_s3()