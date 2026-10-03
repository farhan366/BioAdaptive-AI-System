from pydantic import BaseModel
from typing import List, Any

class ExplainableRequest(BaseModel):
    mean_hr: float
    rmssd: float
    scl_mean: float
    stress_score: int = 0

class MusicRequest(BaseModel):
    patient_id: str
    predicted_stage: int
    current_hr: float