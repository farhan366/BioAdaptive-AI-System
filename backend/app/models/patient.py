from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.session import Base

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    disease_category = Column(String, default="General")
    created_at = Column(DateTime, default=datetime.utcnow)