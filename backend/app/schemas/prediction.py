from pydantic import BaseModel
from datetime import datetime

class PredictionInput(BaseModel):
    patient_id: str
    mean_hr: float
    rmssd: float
    scl_mean: float
    stress_score: int = 0

class PredictionResponse(BaseModel):
    patient_id: str
    predicted_stage: int
    stage_label: str
    confidence_score: float
    physiological_score: float
    timestamp: datetime