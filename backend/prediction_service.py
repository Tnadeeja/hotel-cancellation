"""Load the trusted project artifact once per service; never train at inference."""
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.utils.validation import check_is_fitted

from backend.schemas import BookingRequest, PredictionResponse
from src.preprocessing import (
    CATEGORICAL_FEATURES, EXCLUDED_FEATURES, PREDICTOR_FEATURES, TARGET,
    engineer_features,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "final_random_forest_pipeline.joblib"
MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")


def derive_date_features(arrival: date) -> dict:
    jan1 = date(arrival.year, 1, 1)
    day_offset = (arrival - jan1).days
    sunday_index = (jan1.weekday() + 1) % 7
    return {
        "arrival_date_year": arrival.year,
        "arrival_date_month": MONTHS[arrival.month - 1],
        "arrival_date_week_number": 1 + (day_offset + sunday_index) // 7,
        "arrival_date_day_of_month": arrival.day,
    }


def build_model_input(booking: BookingRequest) -> pd.DataFrame:
    values = booking.model_dump()
    arrival = values.pop("arrival_date")
    values.update(derive_date_features(arrival))
    frame = engineer_features(pd.DataFrame([values]))
    for field in CATEGORICAL_FEATURES:
        # Normalize null representation only; fitted imputation stays in the pipeline.
        column = frame[field].astype(object)
        frame[field] = column.where(column.notna(), np.nan)
    assert len(PREDICTOR_FEATURES) == 30
    assert set(frame.columns) == set(PREDICTOR_FEATURES)
    assert not ({TARGET} | set(EXCLUDED_FEATURES)) & set(frame.columns)
    return frame.loc[:, list(PREDICTOR_FEATURES)]


class PredictionService:
    def __init__(self):
        if not MODEL_PATH.is_file():
            raise RuntimeError("Deployment model artifact is missing. Run notebook 13 locally first.")
        try:
            self.pipeline = joblib.load(MODEL_PATH)
            if list(self.pipeline.named_steps) != ["preprocessor", "classifier"]:
                raise ValueError("Unexpected saved pipeline steps.")
            classifier = self.pipeline.named_steps["classifier"]
            if type(classifier).__name__ != "RandomForestClassifier":
                raise ValueError("Unexpected saved classifier.")
            check_is_fitted(classifier)
            check_is_fitted(self.pipeline.named_steps["preprocessor"])
            if self.pipeline.feature_names_in_.tolist() != list(PREDICTOR_FEATURES):
                raise ValueError("Saved predictor schema differs from the approved schema.")
            classes = classifier.classes_.tolist()
            if len(classes) != 2 or set(classes) != {0, 1}:
                raise ValueError("Expected binary cancellation classes.")
            self.positive_index = classes.index(1)
        except Exception as exc:
            raise RuntimeError("Unable to load the approved deployment pipeline.") from exc

    def predict(self, booking: BookingRequest) -> PredictionResponse:
        model_input = build_model_input(booking)
        prediction = int(self.pipeline.predict(model_input)[0])
        probability = float(self.pipeline.predict_proba(model_input)[0, self.positive_index])
        if prediction not in (0, 1):
            raise ValueError("Invalid model output class.")
        return PredictionResponse(
            prediction=prediction,
            prediction_label="Cancelled" if prediction == 1 else "Not Cancelled",
            cancellation_probability=probability,
        )
