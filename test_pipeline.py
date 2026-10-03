import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.services.ml_service import ClinicalEngine
from app.services.music_service import ISOMusicEngine

def run_system_health_check():
    print("=" * 60)
    print("🧠 1. CHECKING XGBOOST MODEL & INFERENCE PIPELINE")
    print("=" * 60)

    # Test Case A: Acute Stress Condition (Elevated EDA + DASS Anxiety Trait)
    prediction_stress = ClinicalEngine.predict_stage(
        eda_val=4.5,
        temp_val=30.2,
        eda_baseline_mean=1.2,
        eda_baseline_std=0.4,
        temp_baseline_mean=32.0,
        temp_baseline_std=0.6,
        rmssd=18.0,
        acc_magnitude=0.1,
        dass_anxiety=16,
        dass_stress=18,
        dass_depression=4
    )
    print("⚡ Case A (High Stress / Anxiety):")
    print(f"  - Predicted Stage: {prediction_stress['predicted_stage']} ({prediction_stress['stage_label']})")
    print(f"  - Confidence: {prediction_stress['confidence_score']}")
    print(f"  - Biomarker Focus: {prediction_stress['dominant_biomarker']}")
    print(f"  - Shifted Threshold: {prediction_stress['shifted_threshold_used']}")

    # Test Case B: Stage 3 (Depressive Drift - Decoupled Heuristic)
    prediction_dep = ClinicalEngine.predict_stage(
        eda_val=0.15,
        temp_val=31.5,
        rmssd=14.0,           # Suppressed HRV flatline
        acc_magnitude=0.05,
        dass_anxiety=3,
        dass_stress=5,
        dass_depression=17    # High DASS-D
    )
    print("\n🌧️ Case B (Stage 3 Depressive Drift):")
    print(f"  - Predicted Stage: {prediction_dep['predicted_stage']} ({prediction_dep['stage_label']})")
    print(f"  - Dominant Biomarker: {prediction_dep['dominant_biomarker']}")

    print("\n" + "=" * 60)
    print("🎵 2. CHECKING ISO-MUSIC RECOMMENDATION & ARI")
    print("=" * 60)

    # Recommend track for Stage 2 (HR = 92 bpm)
    rec = ISOMusicEngine.recommend_therapy(stage=prediction_stress['predicted_stage'], current_hr=92.0)
    print(f"  - Track Selected: {rec['recommended_track']}")
    print(f"  - Tempo Deceleration Target: {rec['target_bpm']} BPM")
    print(f"  - DSP Instruction: {rec['dsp_instruction']}")

    # Test Autonomic Recovery Index (ARI) calculation
    # Scenario: SCL drops, RMSSD recovers
    ari_success = ISOMusicEngine.calculate_ari(pre_rmssd=20.0, post_rmssd=36.0, pre_scl=4.5, post_scl=2.1)
    print(f"\n  - Autonomic Recovery Index (ARI) [Post-Intervention]: {ari_success}")
    
    status = ISOMusicEngine.evaluate_closed_loop_recovery(consecutive_failed_tracks=0, ari_score=ari_success, current_hr=78.0)
    print(f"  - Closed-Loop Recovery Status: {'SUCCESS' if status['recovery_success'] else 'FAILED'}")

    print("\n" + "=" * 60)
    print("🚨 3. CHECKING CLINICAL FAIL-SAFE LOGIC")
    print("=" * 60)

    # Scenario: 2 consecutive failed tracks with ARI < 0.20
    fail_safe_check = ISOMusicEngine.recommend_therapy(
        stage=2, 
        current_hr=95.0, 
        consecutive_failures=2, 
        last_ari=0.12
    )
    print(f"  - Fail-Safe Triggered: {fail_safe_check['fail_safe_triggered']}")
    if fail_safe_check['fail_safe_triggered']:
        print(f"  - Override Action: {fail_safe_check['action']}")
        print(f"  - Pacer Cadence: {fail_safe_check['pacer_rate']}")
        print(f"  - Caregiver Notification: {fail_safe_check['alert_caregiver']}")

if __name__ == "__main__":
    run_system_health_check()