from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database.session import Base

class DASS21Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)
    depression_score = Column(Integer, nullable=False)
    anxiety_score = Column(Integer, nullable=False)
    stress_score = Column(Integer, nullable=False)
    severity_level = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)