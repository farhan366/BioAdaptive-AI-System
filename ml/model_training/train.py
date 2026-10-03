import os
import glob
import pickle
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

def extract_authentic_signals_from_subject(pkl_path):
    """
    Extracts multimodal wrist biosignals (EDA, TEMP, BVP, ACC) from WESAD subject pkl file.
    Applies uniform aggregation, strict backward causal temporal dynamics, and baseline calibration.
    """
    if not os.path.exists(pkl_path):
        return None, None

    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f, encoding='latin1')

        wrist = data['signal']['wrist']
        eda = wrist['EDA'].flatten()       # 4 Hz
        temp = wrist['TEMP'].flatten()     # 4 Hz
        bvp = wrist['BVP'].flatten()       # 64 Hz
        acc = wrist['ACC']                 # 32 Hz (x, y, z)
        labels = data['label'].flatten()   # 700 Hz

        # 1. Uniform 1-Hz Temporal Aggregation across all streams
        labels_1hz = labels[::700]

        # EDA (4Hz) & TEMP (4Hz): Exact uniform 1-second mean
        eda_len = len(eda) - (len(eda) % 4)
        eda_1hz = eda[:eda_len].reshape(-1, 4).mean(axis=1)

        temp_len = len(temp) - (len(temp) % 4)
        temp_1hz = temp[:temp_len].reshape(-1, 4).mean(axis=1)

        # BVP (64Hz): RMS Energy (Peripheral Vasomotor Amplitude Proxy)
        bvp_len = len(bvp) - (len(bvp) % 64)
        bvp_reshaped = bvp[:bvp_len].reshape(-1, 64)
        bvp_energy_1hz = np.sqrt(np.mean(bvp_reshaped**2, axis=1))

        # ACC (32Hz): Euclidean Vector Magnitude over 1 second
        acc_mag = np.sqrt(np.sum(acc**2, axis=1))
        acc_len = len(acc_mag) - (len(acc_mag) % 32)
        acc_mag_1hz = acc_mag[:acc_len].reshape(-1, 32).mean(axis=1)

        # Synchronize arrays
        min_len = min(len(labels_1hz), len(eda_1hz), len(temp_1hz), len(bvp_energy_1hz), len(acc_mag_1hz))
        labels_aligned = labels_1hz[:min_len]
        eda_aligned = eda_1hz[:min_len]
        temp_aligned = temp_1hz[:min_len]
        bvp_aligned = bvp_energy_1hz[:min_len]
        acc_aligned = acc_mag_1hz[:min_len]

        # Filter target conditions: 1 (Baseline), 2 (Stress), 3 (Amusement/Mild)
        valid_mask = np.isin(labels_aligned, [1, 2, 3])
        y_valid = labels_aligned[valid_mask]
        eda_valid = eda_aligned[valid_mask]
        temp_valid = temp_aligned[valid_mask]
        bvp_valid = bvp_aligned[valid_mask]
        acc_valid = acc_aligned[valid_mask]

        # 2. Causal Baseline Normalization (Calibrated from Resting Baseline condition: Class 1)
        base_mask = (y_valid == 1)
        if np.sum(base_mask) > 10:
            eda_mu, eda_std = np.mean(eda_valid[base_mask]), np.std(eda_valid[base_mask])
            temp_mu, temp_std = np.mean(temp_valid[base_mask]), np.std(temp_valid[base_mask])
            bvp_mu, bvp_std = np.mean(bvp_valid[base_mask]), np.std(bvp_valid[base_mask])
            acc_mu, acc_std = np.mean(acc_valid[base_mask]), np.std(acc_valid[base_mask])
        else:
            eda_mu, eda_std = np.mean(eda_valid), np.std(eda_valid)
            temp_mu, temp_std = np.mean(temp_valid), np.std(temp_valid)
            bvp_mu, bvp_std = np.mean(bvp_valid), np.std(bvp_valid)
            acc_mu, acc_std = np.mean(acc_valid), np.std(acc_valid)

        eps = 1e-6
        eda_z = (eda_valid - eda_mu) / (eda_std + eps)
        temp_z = (temp_valid - temp_mu) / (temp_std + eps)
        bvp_z = (bvp_valid - bvp_mu) / (bvp_std + eps)
        acc_z = (acc_valid - acc_mu) / (acc_std + eps)

        # 3. Strictly Causal Multi-Second Dynamics (Backward-Looking Only)
        eda_series = pd.Series(eda_z)
        temp_series = pd.Series(temp_z)

        # 5-second backward rolling mean (min_periods=1 with causal fill)
        eda_roll_5s = eda_series.rolling(window=5, min_periods=1).mean().values
        temp_roll_5s = temp_series.rolling(window=5, min_periods=1).mean().values

        # Strict Causal First Difference (Past sample only, 0 look-ahead)
        eda_diff_5s = np.diff(eda_roll_5s, prepend=eda_roll_5s[0])
        temp_diff_5s = np.diff(temp_roll_5s, prepend=temp_roll_5s[0])

        X_df = pd.DataFrame({
            'eda_z': eda_z,
            'eda_roll_5s': eda_roll_5s,
            'eda_diff_5s': eda_diff_5s,
            'temp_z': temp_z,
            'temp_roll_5s': temp_roll_5s,
            'temp_diff_5s': temp_diff_5s,
            'bvp_energy_z': bvp_z,
            'acc_mag_z': acc_z
        })

        # Remap WESAD labels: 1 -> 0 (Baseline), 3 -> 1 (Mild/Amusement), 2 -> 2 (Acute Stress)
        label_map = {1: 0, 3: 1, 2: 2}
        y_labels = np.array([label_map[l] for l in y_valid])

        return X_df, y_labels
    except Exception as e:
        print(f"⚠️ Error parsing {pkl_path}: {e}")
        return None, None


def run_rigorous_loso_evaluation():
    wesad_dir = os.path.join("ml", "data", "WESAD")
    pkl_files = sorted(glob.glob(os.path.join(wesad_dir, "*.pkl")))

    if not pkl_files:
        print("⚠️ No .pkl files found in ml/data/WESAD/")
        return

    print(f"🚀 Processing {len(pkl_files)} WESAD Subject files with Strict Causal Dynamics...")
    
    subject_data = {}
    for pkl_file in pkl_files:
        sub_name = os.path.basename(pkl_file).split('.')[0]
        X_sub, y_sub = extract_authentic_signals_from_subject(pkl_file)
        if X_sub is not None and len(X_sub) > 0:
            subject_data[sub_name] = (X_sub, y_sub)
            print(f"  ✓ Processed {sub_name}: {len(X_sub)} instances")

    subjects = list(subject_data.keys())
    loso_accuracies = []
    loso_f1_scores = []
    all_y_true = []
    all_y_pred = []

    print("\n------------------------------------------------------------")
    print("📈 Running LOSO-CV (Class-Balanced & Strictly Causal)...")
    print("------------------------------------------------------------")

    for test_sub in subjects:
        train_subs = [s for s in subjects if s != test_sub]
        
        X_train = pd.concat([subject_data[s][0] for s in train_subs], ignore_index=True)
        y_train = np.concatenate([subject_data[s][1] for s in train_subs])
        
        X_test, y_test = subject_data[test_sub]

        # Compute sample weights to solve class imbalance (Mild class support deficiency)
        train_weights = compute_sample_weight('balanced', y_train)

        clf = XGBClassifier(
            n_estimators=140, 
            max_depth=5, 
            learning_rate=0.05, 
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42, 
            eval_metric='mlogloss'
        )
        clf.fit(X_train, y_train, sample_weight=train_weights)

        preds = clf.predict(X_test)
        
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average='weighted')
        
        loso_accuracies.append(acc)
        loso_f1_scores.append(f1)
        all_y_true.extend(y_test)
        all_y_pred.extend(preds)
        
        print(f"  -> Holdout [{test_sub}]: Accuracy = {acc*100:.2f}%, Weighted F1 = {f1*100:.2f}%")

    print("\n============================================================")
    print("🎯 FINAL CLASS-BALANCED CAUSAL LOSO-CV RESULTS (FOR PAPER)")
    print("============================================================")
    print(f"Mean LOSO Accuracy: {np.mean(loso_accuracies)*100:.2f}% ± {np.std(loso_accuracies)*100:.2f}%")
    print(f"Mean LOSO Weighted F1-Score: {np.mean(loso_f1_scores)*100:.2f}% ± {np.std(loso_f1_scores)*100:.2f}%\n")
    print("Aggregated Classification Report:\n", classification_report(all_y_true, all_y_pred, target_names=['Baseline', 'Mild', 'Stress']))
    print("Overall Confusion Matrix:\n", confusion_matrix(all_y_true, all_y_pred))

    # Retrain and save global production model with balanced weights
    print("\n📦 Updating Global Production Model...")
    X_full = pd.concat([subject_data[s][0] for s in subjects], ignore_index=True)
    y_full = np.concatenate([subject_data[s][1] for s in subjects])
    full_weights = compute_sample_weight('balanced', y_full)

    final_model = XGBClassifier(n_estimators=140, max_depth=5, learning_rate=0.05, random_state=42, eval_metric='mlogloss')
    final_model.fit(X_full, y_full, sample_weight=full_weights)

    save_dir = os.path.join("ml", "saved_models")
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "xgboost_model.pkl")
    joblib.dump(final_model, model_path)
    print(f"✓ Final Production Model saved to: {model_path}")

if __name__ == "__main__":
    run_rigorous_loso_evaluation()