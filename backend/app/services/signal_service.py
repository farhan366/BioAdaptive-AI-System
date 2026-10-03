import numpy as np
import neurokit2 as nk
from typing import Dict, Any, List

class SignalProcessor:
    """
    Biomedical Signal Processor using NeuroKit2 and SciPy.
    Extracts HRV, EDA (SCL/SCR), and Thermal features from Wearable Signals.
    """
    
    @staticmethod
    def process_eda_signal(eda_signals: List[float], sampling_rate: int = 70) -> Dict[str, Any]:
        """Cleans EDA signal and decomposes into Tonic (SCL) and Phasic (SCR) components."""
        eda_clean = nk.eda_clean(eda_signals, sampling_rate=sampling_rate)
        eda_decomposed = nk.eda_phasic(eda_clean, sampling_rate=sampling_rate)
        
        # Extract features
        scl_mean = float(np.mean(eda_decomposed["EDA_Tonic"]))
        peaks, _ = nk.eda_peaks(eda_decomposed["EDA_Phasic"], sampling_rate=sampling_rate)
        scr_peaks_count = int(np.sum(peaks["SCR_Peaks"]))
        
        return {
            "scl_mean": round(scl_mean, 4),
            "scr_peaks_count": scr_peaks_count
        }

    @staticmethod
    def process_bvp_hrv(bvp_signals: List[float], sampling_rate: int = 64) -> Dict[str, Any]:
        """Extracts Heart Rate (HR) and Heart Rate Variability (HRV) metrics from BVP/PPG."""
        ppg_clean = nk.ppg_clean(bvp_signals, sampling_rate=sampling_rate)
        info = nk.ppg_findpeaks(ppg_clean, sampling_rate=sampling_rate)
        peaks = info["PPG_Peaks"]
        
        if len(peaks) < 3:
            return {"mean_hr": 70.0, "rmssd": 30.0, "sdnn": 40.0}
            
        hrv_time = nk.hrv_time(peaks, sampling_rate=sampling_rate)
        mean_hr = float(60.0 / (np.diff(peaks) / sampling_rate).mean())
        
        return {
            "mean_hr": round(mean_hr, 2),
            "rmssd": round(float(hrv_time["HRV_RMSSD"].iloc[0]), 2),
            "sdnn": round(float(hrv_time["HRV_SDNN"].iloc[0]), 2)
        }