from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import joblib
from fastapi import FastAPI
from backend.app.routers.behavioral import router as behavioral_router
from backend.app.routers.prediction import create_prediction_router
from backend.app.routers.documents import router as documents_router
from backend.app.database import Base, engine
from backend.app.models.document_chunk import DocumentChunk
from backend.app.routers.intelligence import router as intelligence_router

app = FastAPI(
    title="Next-Gen Credit Intelligence API",
    description="Explainable credit risk assessment API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml" / "artifacts" / "credit_risk_model.pkl"

model = joblib.load(MODEL_PATH)

Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {
        "message": "Next-Gen Credit Intelligence API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


app.include_router(create_prediction_router(model))
app.include_router(behavioral_router)
app.include_router(documents_router)
app.include_router(intelligence_router)