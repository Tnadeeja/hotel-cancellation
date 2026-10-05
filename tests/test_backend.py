"""Lightweight API and contract checks using the actual saved pipeline."""
from datetime import date
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend import prediction_service
from backend.prediction_service import build_model_input, derive_date_features
from backend.schemas import BookingRequest, COUNTRY_CODES
from src.preprocessing import CATEGORICAL_FEATURES, NUMERICAL_FEATURES, PREDICTOR_FEATURES


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def booking():
    return dict(hotel="City Hotel", lead_time=20, arrival_date="2015-07-05",
                stays_in_weekend_nights=1, stays_in_week_nights=2,
                adults=2, children=0, babies=0, meal="BB", country="PRT",
                market_segment="Direct", distribution_channel="Direct",
                is_repeated_guest=0, previous_cancellations=0,
                previous_bookings_not_canceled=0, reserved_room_type="A",
                deposit_type="No Deposit", agent="240", days_in_waiting_list=0,
                customer_type="Transient", required_car_parking_spaces=0,
                total_of_special_requests=0)


def test_root(client):
    assert client.get("/").status_code == 200


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == dict(status="ok", model_loaded=True,
                                   model_name="Random Forest", strategy="General-only")


@pytest.mark.parametrize("hotel", ["City Hotel", "Resort Hotel"])
def test_prediction(client, booking, hotel):
    booking["hotel"] = hotel
    response = client.post("/predict", json=booking)
    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"prediction", "prediction_label", "cancellation_probability", "model_name", "strategy"}
    assert type(result["prediction"]) is int and result["prediction"] in (0, 1)
    assert result["prediction_label"] == {0: "Not Cancelled", 1: "Cancelled"}[result["prediction"]]
    assert 0 <= result["cancellation_probability"] <= 1
    assert result["model_name"] == "Random Forest" and result["strategy"] == "General-only"


def test_missing_field(client, booking):
    del booking["hotel"]
    assert client.post("/predict", json=booking).status_code == 422


@pytest.mark.parametrize("field,value", [
    ("lead_time", -1), ("adults", -1), ("children", -1), ("babies", -1),
    ("stays_in_week_nights", -1), ("stays_in_weekend_nights", -1),
    ("previous_cancellations", -1), ("previous_bookings_not_canceled", -1),
    ("days_in_waiting_list", -1), ("required_car_parking_spaces", -1),
    ("total_of_special_requests", -1), ("hotel", "Unknown Hotel"),
    ("meal", "unknown"), ("market_segment", "unknown"),
    ("distribution_channel", "unknown"), ("reserved_room_type", "Z"),
    ("deposit_type", "unknown"), ("customer_type", "unknown"),
    ("arrival_date", "2026-02-30"), ("arrival_date", "2015-7-05"),
    ("arrival_date", "2015-07-05T00:00:00"), ("arrival_date", 1436054400),
    ("adults", "2"), ("adults", True), ("children", 0.5), ("adults", None),
    ("is_repeated_guest", True), ("is_repeated_guest", 2),
    ("agent", "240.0"), ("agent", "0240"), ("agent", -1), ("agent", 240),
    ("agent", ""), ("agent", "abc"), ("country", "ZZZ"), ("country", ""),
    ("country", "prt"), ("country", 123),
])
def test_invalid_fields(client, booking, field, value):
    booking[field] = value
    response = client.post("/predict", json=booking)
    assert response.status_code == 422
    assert response.json()["detail"]


def test_zero_guests(client, booking):
    booking.update(adults=0, children=0, babies=0)
    assert client.post("/predict", json=booking).status_code == 422


def test_zero_nights(client, booking):
    booking.update(stays_in_weekend_nights=0, stays_in_week_nights=0)
    assert client.post("/predict", json=booking).status_code == 200


@pytest.mark.parametrize("mode", ["omitted", "null", "new_agent", "source_country"])
def test_optional_inputs(client, booking, mode):
    if mode == "omitted":
        booking.pop("country")
        booking.pop("agent")
    elif mode == "null":
        booking.update(country=None, agent=None)
    elif mode == "new_agent":
        booking["agent"] = "999999"
    else:
        booking["country"] = "CN"
    assert client.post("/predict", json=booking).status_code == 200


@pytest.mark.parametrize("field", ["is_canceled", "reservation_status", "reservation_status_date",
                                    "assigned_room_type", "booking_changes", "company", "adr",
                                    "total_guests", "arrival_date_week_number"])
def test_unexpected_fields(client, booking, field):
    booking[field] = 1
    assert client.post("/predict", json=booking).status_code == 422


def test_engineering_and_schema(booking):
    booking.update(children=1, babies=1, previous_cancellations=1,
                   previous_bookings_not_canceled=3, country=None, agent=None)
    frame = build_model_input(BookingRequest(**booking))
    assert frame.shape == (1, 30)
    assert frame.columns.tolist() == list(PREDICTOR_FEATURES)
    row = frame.iloc[0]
    assert row.total_stay_nights == 3 and row.total_guests == 4
    assert row.family_booking == 1 and row.previous_booking_total == 4
    assert row.previous_cancellation_rate == 0.25
    assert np.isnan(row.country) and np.isnan(row.agent)
    assert all(pd.api.types.is_numeric_dtype(frame[f]) for f in NUMERICAL_FEATURES)
    assert all(frame[f].dtype == object for f in CATEGORICAL_FEATURES)


def test_no_history(booking):
    row = build_model_input(BookingRequest(**booking)).iloc[0]
    assert row.family_booking == 0 and row.previous_cancellation_rate == 0.0


@pytest.mark.parametrize("arrival,week", [(date(2015, 7, 1), 27), (date(2015, 7, 5), 28),
                                         (date(2016, 1, 1), 1), (date(2016, 1, 3), 2),
                                         (date(2017, 1, 1), 1)])
def test_week_convention(arrival, week):
    result = derive_date_features(arrival)
    assert result["arrival_date_week_number"] == week
    assert result["arrival_date_year"] == arrival.year
    assert result["arrival_date_day_of_month"] == arrival.day
    assert result["arrival_date_month"] == ("January" if arrival.month == 1 else "July")


def test_contract_schema(booking):
    assert len(BookingRequest.model_fields) == 22
    assert set(BookingRequest.model_fields) == set(booking)
    assert sum(field.is_required() for field in BookingRequest.model_fields.values()) == 20
    doc = (prediction_service.PROJECT_ROOT / "docs/system_input_output_contract.md").read_text(encoding="utf-8")
    requests = [json.loads(block) for block in re.findall(r"```json\s*(.*?)```", doc, re.S)]
    assert set(requests[2]) == set(BookingRequest.model_fields)
    raw = prediction_service.PROJECT_ROOT / "data/raw/hotel_bookings.csv"
    assert COUNTRY_CODES == set(pd.read_csv(raw, usecols=["country"]).country.dropna())


def test_model_loaded_once(client, booking, monkeypatch):
    def forbidden_load(*args, **kwargs):
        raise AssertionError("Model must not reload during requests")
    monkeypatch.setattr(prediction_service.joblib, "load", forbidden_load)
    assert client.post("/predict", json=booking).status_code == 200
    assert client.get("/health").status_code == 200


def test_missing_artifact(monkeypatch, tmp_path):
    monkeypatch.setattr(prediction_service, "MODEL_PATH", tmp_path / "missing.joblib")
    with pytest.raises(RuntimeError, match="artifact is missing"):
        prediction_service.PredictionService()


def test_internal_failure(client, booking, monkeypatch):
    def broken(*args):
        raise RuntimeError("private internal information")
    monkeypatch.setattr(app.state.prediction_service, "predict", broken)
    response = client.post("/predict", json=booking)
    assert response.status_code == 500
    assert response.json() == {"detail": "Prediction could not be completed."}


def test_malformed_json(client):
    response = client.post("/predict", content="{", headers={"content-type": "application/json"})
    assert response.status_code == 400 and response.json()["error"] == "invalid_json"
