from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.session import engine, Base

# Import all routers
from app.routers import signals, patients, predictions, recommendations

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BioAdaptive AI System",
    description="Bioadaptive Closed-Loop Stress and Physiological Stage Monitoring API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(signals.router)
app.include_router(patients.router)
app.include_router(predictions.router)
app.include_router(recommendations.router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "system": "BioAdaptive AI Engine",
        "version": "1.0.0"
    }

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "signal_processing": "ready",
            "ml_engine": "ready",
            "music_engine": "ready"
        }
    }