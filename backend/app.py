"""Run from project root: uvicorn backend.app:app --reload"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.prediction_service import PredictionService
from backend.schemas import BookingRequest, PredictionResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prediction_service = PredictionService()
    yield


app = FastAPI(title="Hotel Cancellation Risk Prediction API", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # Preserve field/type/message details without echoing the booking payload.
    details = [
        {"loc": error["loc"], "type": error["type"], "msg": error["msg"]}
        for error in exc.errors()
    ]
    malformed = any(error["type"] == "json_invalid" for error in details)
    return JSONResponse(status_code=400 if malformed else 422, content={
        "error": "invalid_json" if malformed else "validation_error", "detail": details,
    })


def get_service(request: Request) -> PredictionService:
    service = getattr(request.app.state, "prediction_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="Prediction model is unavailable.")
    return service


@app.get("/")
def root():
    return {
        "service": "Hotel Cancellation Risk Prediction API",
        "description": "Predict cancellation using the frozen General Random Forest pipeline.",
        "endpoints": ["GET /", "GET /health", "POST /predict"],
    }


@app.get("/health")
def health(request: Request):
    get_service(request)
    return {"status": "ok", "model_loaded": True,
            "model_name": "Random Forest", "strategy": "General-only"}


@app.post("/predict", response_model=PredictionResponse)
def predict(booking: BookingRequest, request: Request):
    service = get_service(request)
    try:
        return service.predict(booking)
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction could not be completed.") from None
