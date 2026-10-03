from fastapi import APIRouter, HTTPException
from app.schemas.music import ExplainableRequest, MusicRequest
from app.services.explainability_service import SHAPExplainer
from app.services.music_service import ISOMusicEngine

router = APIRouter(
    prefix="/api/v1/adaptive",
    tags=["Explainable AI & ISO Music Engine"]
)

@router.post("/explain-shap")
async def get_shap_explanation(payload: ExplainableRequest):
    try:
        explanation = SHAPExplainer.explain_prediction(
            mean_hr=payload.mean_hr,
            rmssd=payload.rmssd,
            scl_mean=payload.scl_mean,
            stress_score=payload.stress_score
        )
        return {"shap_feature_contributions": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend-music")
async def recommend_iso_music(payload: MusicRequest):
    try:
        recommendation = ISOMusicEngine.recommend_therapy(
            stage=payload.predicted_stage,
            current_hr=payload.current_hr
        )
        return {
            "patient_id": payload.patient_id,
            "therapy_plan": recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))