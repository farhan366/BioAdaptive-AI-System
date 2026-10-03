from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.schemas.prediction import PredictionInput, PredictionResponse
from app.services.ml_service import ClinicalEngine

router = APIRouter(
    prefix="/api/v1/predictions",
    tags=["AI Clinical Decision Engine"]
)

@router.post("/predict-stage", response_model=PredictionResponse)
async def predict_patient_stage(payload: PredictionInput):
    try:
        res = ClinicalEngine.predict_stage(
            mean_hr=payload.mean_hr,
            rmssd=payload.rmssd,
            scl_mean=payload.scl_mean,
            stress_score=payload.stress_score
        )
        
        return PredictionResponse(
            patient_id=payload.patient_id,
            predicted_stage=res["predicted_stage"],
            stage_label=res["stage_label"],
            confidence_score=res["confidence_score"],
            physiological_score=res["physiological_score"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction Engine Failure: {str(e)}"
        )