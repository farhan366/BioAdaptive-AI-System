from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PatientCreate(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    disease_category: Optional[str] = "General"

class PatientResponse(PatientCreate):
    created_at: datetime
    class Config:
        from_attributes = True

class DASS21Input(BaseModel):
    patient_id: str
    answers: List[int] # List of 21 integers (0 to 3)

class DASS21Response(BaseModel):
    assessment_id: int
    patient_id: str
    depression_score: int
    anxiety_score: int
    stress_score: int
    severity_level: str
    timestamp: datetime
    class Config:
        from_attributes = True