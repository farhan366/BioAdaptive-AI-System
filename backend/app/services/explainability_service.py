from typing import Dict, Any, List

class SHAPExplainer:
    """
    Computes feature contribution and impact factors for AI predictions.
    Mimics TreeSHAP / SHAP Values output structure for clinical interpretability.
    """

    @staticmethod
    def explain_prediction(
        mean_hr: float, 
        rmssd: float, 
        scl_mean: float, 
        stress_score: int
    ) -> List[Dict[str, Any]]:
        
        # Base values / baseline averages
        base_hr = 70.0
        base_rmssd = 45.0
        base_scl = 0.15
        
        # Compute contribution direction & value
        hr_impact = (mean_hr - base_hr) * 0.03
        rmssd_impact = (base_rmssd - rmssd) * 0.02
        scl_impact = (scl_mean - base_scl) * 2.5
        dass_impact = stress_score * 0.02

        shap_values = [
            {
                "feature": "Heart Rate (HR)",
                "value": mean_hr,
                "contribution": round(hr_impact, 3),
                "effect": "Increased Stress" if hr_impact > 0 else "Reduced Stress"
            },
            {
                "feature": "Skin Conductance Level (SCL/EDA)",
                "value": scl_mean,
                "contribution": round(scl_impact, 3),
                "effect": "Elevated Arousal" if scl_impact > 0 else "Normal Arousal"
            },
            {
                "feature": "HR Variability (RMSSD)",
                "value": rmssd,
                "contribution": round(rmssd_impact, 3),
                "effect": "Vagal Suppression" if rmssd_impact > 0 else "Healthy Vagal Tone"
            },
            {
                "feature": "DASS Stress Assessment",
                "value": stress_score,
                "contribution": round(dass_impact, 3),
                "effect": "Baseline Psychological Burden" if dass_impact > 0 else "Normal Baseline"
            }
        ]
        
        # Sort features by impact magnitude
        return sorted(shap_values, key=lambda x: abs(x["contribution"]), reverse=True)