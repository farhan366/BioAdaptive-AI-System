from typing import Dict, Any, Optional

class ISOMusicEngine:
    """
    Bio-Adaptive Closed-Loop ISO-Principle Intervention Engine.
    Implements:
    1. Dynamic ISO-Entrainment BPM mapping.
    2. Autonomic Recovery Index (ARI) evaluation for 180s windows.
    3. Clinical Fail-Safe: Triggers guided breathing if ARI < 0.20 across consecutive tracks.
    """

    @staticmethod
    def calculate_ari(
        pre_rmssd: float,
        post_rmssd: float,
        pre_scl: float,
        post_scl: float,
        w_hrv: float = 0.5,
        w_eda: float = 0.5
    ) -> float:
        """
        Computes the composite Autonomic Recovery Index (ARI):
        ARI = w_hrv * Delta_RMSSD_180 + w_eda * Delta_SCL_180
        Returns score clamped between 0.0 and 1.0.
        """
        eps = 1e-6
        # Normalized relative recovery increments
        delta_rmssd = max(0.0, (post_rmssd - pre_rmssd) / (pre_rmssd + eps))
        delta_scl = max(0.0, (pre_scl - post_scl) / (pre_scl + eps))

        # Clamp individual component contributions to 1.0 to avoid unbounded distortion
        delta_rmssd_norm = min(1.0, delta_rmssd)
        delta_scl_norm = min(1.0, delta_scl)

        ari = (w_hrv * delta_rmssd_norm) + (w_eda * delta_scl_norm)
        return round(float(ari), 3)

    @classmethod
    def evaluate_closed_loop_recovery(
        cls,
        consecutive_failed_tracks: int,
        ari_score: float,
        current_hr: float
    ) -> Dict[str, Any]:
        """
        Safety & Closed-Loop Controller:
        Monitors recovery threshold (ARI >= 0.50).
        Enforces Clinical Fail-Safe if ARI < 0.20 for > 1 consecutive cycle.
        """
        recovery_success = ari_score >= 0.50

        # Clinical Fail-Safe Condition
        if consecutive_failed_tracks >= 2 and ari_score < 0.20:
            return {
                "fail_safe_triggered": True,
                "recovery_success": False,
                "ari_score": ari_score,
                "action": "ABORT_AUDIO_INTERVENTION",
                "therapeutic_mode": "GUIDED_RESONANCE_BREATHING",
                "pacer_rate": "4-7-8 Breathing Cadence (0.1 Hz Paced Respiration)",
                "alert_caregiver": True,
                "clinical_rationale": "Sustained autonomic resistance or paradoxical arousal detected (ARI < 0.20 across 2 intervention cycles)."
            }

        return {
            "fail_safe_triggered": False,
            "recovery_success": recovery_success,
            "ari_score": ari_score,
            "action": "MAINTAIN_OR_MODULATE_TRACK" if recovery_success else "SHIFT_ACOUSTIC_FREQUENCY",
            "alert_caregiver": False
        }

    @classmethod
    def recommend_therapy(
        cls, 
        stage: int, 
        current_hr: float,
        consecutive_failures: int = 0,
        last_ari: Optional[float] = None
    ) -> Dict[str, Any]:
        
        # Check fail-safe before recommending music
        if last_ari is not None:
            safety_status = cls.evaluate_closed_loop_recovery(consecutive_failures, last_ari, current_hr)
            if safety_status["fail_safe_triggered"]:
                return safety_status

        # Dynamic ISO-Principle Acoustic Prescription
        if stage == 0:
            target_bpm = 60
            track_name = "Homeostasis Ambient Soundscape"
            freq_shift = "Delta Anchor (2.0 - 4.0 Hz)"
            duration_sec = 180
            dsp_instruction = "Preserve resting autonomic tone. Flat harmonic equalization."
            exploratory_binaural = False

        elif stage == 1:
            # Stage 1: Acute Panic / Anxiety
            target_bpm = 60
            track_name = "ISO-Entrainment Deceleration Phase I"
            freq_shift = "Alpha Layering (8.0 - 12.0 Hz) [Exploratory Arm]"
            duration_sec = 180
            dsp_instruction = f"Apply Low-Pass filter @ 1000Hz. Real-time tempo ramp from {int(current_hr)} BPM down to {target_bpm} BPM over 180s."
            exploratory_binaural = True

        elif stage == 2:
            # Stage 2: High Autonomic Stress
            target_bpm = max(65, int(current_hr * 0.82))
            track_name = "Harmonic Parasympathetic Engagement"
            freq_shift = "Theta Resonance (4.5 - 7.0 Hz)"
            duration_sec = 180
            dsp_instruction = f"Apply gentle notch attenuation at high-mid bands. Moderate tempo ramp down to {target_bpm} BPM."
            exploratory_binaural = False

        else:
            # Stage 3: Depressive / Low-Arousal Drift (Rule-based Heuristic)
            target_bpm = 75
            track_name = "Resonance Mood-Elevation Soundscape"
            freq_shift = "Low-Beta Coherence (13.0 - 15.0 Hz)"
            duration_sec = 240
            dsp_instruction = "Gradual valence elevation, ascending harmonic progressions to counteract psychomotor hypo-arousal."
            exploratory_binaural = False

        return {
            "fail_safe_triggered": False,
            "current_hr": current_hr,
            "target_bpm": target_bpm,
            "recommended_track": track_name,
            "frequency_shift": freq_shift,
            "exploratory_binaural_active": exploratory_binaural,
            "session_duration_sec": duration_sec,
            "dsp_instruction": dsp_instruction
        }