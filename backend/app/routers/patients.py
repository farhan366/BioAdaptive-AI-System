from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.patient import Patient
from app.models.assessment import DASS21Assessment
from app.schemas.patient import PatientCreate, PatientResponse, DASS21Input, DASS21Response
from app.services.dass_service import DASSEngine

router = APIRouter(
    prefix="/api/v1/patients",
    tags=["Patients & DASS-21"]
)

@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def register_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_in.patient_id).first()
    if db_patient:
        raise HTTPException(status_code=400, detail="Patient ID already exists.")
    
    new_patient = Patient(
        patient_id=patient_in.patient_id,
        name=patient_in.name,
        age=patient_in.age,
        gender=patient_in.gender,
        disease_category=patient_in.disease_category
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.post("/dass-assessment", response_model=DASS21Response)
def submit_dass_assessment(assessment_in: DASS21Input, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.patient_id == assessment_in.patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    
    try:
        scores = DASSEngine.calculate_scores(assessment_in.answers)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    new_assessment = DASS21Assessment(
        patient_id=assessment_in.patient_id,
        depression_score=scores["depression_score"],
        anxiety_score=scores["anxiety_score"],
        stress_score=scores["stress_score"],
        severity_level=scores["severity_level"]
    )
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    return new_assessment