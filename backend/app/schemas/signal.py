from pydantic import BaseModel
from typing import List, Optional

class RawSignalInput(BaseModel):
    patient_id: str
    sample_rate: int = 70  # Default 70Hz for WESAD EDA/BVP
    eda_raw: List[float]
    bvp_raw: Optional[List[float]] = None
    temp_raw: Optional[List[float]] = None
    acc_x: Optional[List[float]] = None
    acc_y: Optional[List[float]] = None
    acc_z: Optional[List[float]] = None

class SignalFeaturesResponse(BaseModel):
    patient_id: str
    mean_hr: float
    rmssd: float
    sdnn: float
    scl_mean: float
    scr_peaks_count: int
    mean_temp: float
    status: str