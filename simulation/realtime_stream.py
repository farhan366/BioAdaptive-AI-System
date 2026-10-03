import time
import math
import requests
import random

API_URL = "http://127.0.0.1:8000/api/v1"

def generate_synthetic_wesad_window(tick: int):
    """
    Simulates real-time 70Hz continuous PPG/EDA telemetry stream 
    with fluctuating stress artifacts.
    """
    base_hr = 72 + (15 * math.sin(tick * 0.1)) + random.uniform(-2, 2)
    base_eda = 0.15 + (0.2 * max(0, math.sin(tick * 0.08))) + random.uniform(-0.02, 0.02)
    
    # Generate 25 samples for EDA
    eda_raw = [round(base_eda + random.uniform(-0.01, 0.01), 3) for _ in range(25)]
    
    return {
        "patient_id": "P-101",
        "sample_rate": 70,
        "eda_raw": eda_raw,
        "temp_raw": [36.5, 36.6, 36.5, 36.7]
    }

def run_simulation():
    print("🚀 Starting BioAdaptive Telemetry Stream Simulation...")
    print("Connecting to Backend API:", API_URL)
    tick = 0
    
    while True:
        try:
            payload = generate_synthetic_wesad_window(tick)
            
            # 1. Process Signal
            sig_res = requests.post(f"{API_URL}/signals/process", json=payload).json()
            
            # 2. Predict Stage using processed features
            pred_payload = {
                "patient_id": payload["patient_id"],
                "mean_hr": sig_res["mean_hr"],
                "rmssd": sig_res["rmssd"],
                "scl_mean": sig_res["scl_mean"],
                "stress_score": 18
            }
            pred_res = requests.post(f"{API_URL}/predictions/predict-stage", json=pred_payload).json()
            
            # 3. Request Music Recommendation
            music_payload = {
                "patient_id": payload["patient_id"],
                "predicted_stage": pred_res["predicted_stage"],
                "current_hr": sig_res["mean_hr"]
            }
            music_res = requests.post(f"{API_URL}/adaptive/recommend-music", json=music_payload).json()
            
            print(f"[{time.strftime('%H:%M:%S')}] Stream Tick #{tick} | HR: {sig_res['mean_hr']} BPM | "
                  f"Stage: {pred_res['stage_label']} | Target BPM: {music_res['therapy_plan']['target_bpm']}")
            
            tick += 1
            time.sleep(3)  # Stream interval
            
        except KeyboardInterrupt:
            print("\n🛑 Simulation Stopped.")
            break
        except Exception as e:
            print(f"⚠️ Stream Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_simulation()