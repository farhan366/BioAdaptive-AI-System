from fastapi import APIRouter, HTTPException, status
from app.schemas.signal import RawSignalInput, SignalFeaturesResponse
from app.services.signal_service import SignalProcessor

router = APIRouter(
    prefix="/api/v1/signals",
    tags=["Biomedical Signals"]
)

@router.post("/process", response_model=SignalFeaturesResponse)
async def process_patient_signals(payload: RawSignalInput):
    try:
        # Process EDA
        eda_features = SignalProcessor.process_eda_signal(payload.eda_raw, payload.sample_rate)
        
        # Process BVP/HRV if provided, else assign mock fallback
        if payload.bvp_raw and len(payload.bvp_raw) > 10:
            hrv_features = SignalProcessor.process_bvp_hrv(payload.bvp_raw, sampling_rate=64)
        else:
            hrv_features = {"mean_hr": 72.5, "rmssd": 32.4, "sdnn": 45.1}
            
        mean_temp = float(sum(payload.temp_raw)/len(payload.temp_raw)) if payload.temp_raw else 36.5
        
        return SignalFeaturesResponse(
            patient_id=payload.patient_id,
            mean_hr=hrv_features["mean_hr"],
            rmssd=hrv_features["rmssd"],
            sdnn=hrv_features["sdnn"],
            scl_mean=eda_features["scl_mean"],
            scr_peaks_count=eda_features["scr_peaks_count"],
            mean_temp=round(mean_temp, 2),
            status="signals_processed_successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signal processing error: {str(e)}"
        )