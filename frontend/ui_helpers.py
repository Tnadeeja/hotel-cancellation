"""Request serialization and HTTP handling; no model or preprocessing access."""
from datetime import date
from typing import get_args

import httpx
from pydantic import ValidationError

from backend.schemas import BookingRequest, PredictionResponse


class FrontendError(Exception):
    """A message suitable for hotel staff."""


def category_options(field: str) -> tuple:
    return get_args(BookingRequest.model_fields[field].annotation)


def prepare_payload(values: dict) -> dict:
    payload = dict(values)
    arrival = payload.get("arrival_date")
    if type(arrival) is date:
        payload["arrival_date"] = arrival.isoformat()
    payload["agent"] = payload.get("agent") or None
    if sum(payload.get(field, 0) for field in ("adults", "children", "babies")) == 0:
        raise FrontendError("At least one guest is required.")
    try:
        return BookingRequest.model_validate(payload).model_dump(mode="json")
    except ValidationError as exc:
        messages = []
        for error in exc.errors():
            field = " ".join(str(item).replace("_", " ") for item in error["loc"])
            messages.append(f"{field.capitalize()}: {error['msg']}" if field else error["msg"])
        raise FrontendError("Please check the booking details. " + " ".join(messages)) from None


def request_prediction(backend_url: str, payload: dict) -> dict:
    try:
        response = httpx.post(f"{backend_url.rstrip('/')}/predict", json=payload, timeout=20.0)
    except httpx.TimeoutException:
        raise FrontendError("The prediction request timed out. Please try again.") from None
    except httpx.RequestError:
        raise FrontendError("Cannot connect to the prediction service. Please check that the backend is running.") from None
    if response.status_code == 422:
        try:
            details = response.json().get("detail", [])
            messages = []
            if isinstance(details, list):
                for detail in details:
                    if isinstance(detail, dict) and isinstance(detail.get("msg"), str):
                        fields = [str(part).replace("_", " ") for part in detail.get("loc", []) if part != "body"]
                        messages.append(f"{' '.join(fields).capitalize()}: {detail['msg']}")
            message = " ".join(messages) or "Please check the booking details and try again."
        except (ValueError, AttributeError, TypeError):
            message = "Please check the booking details and try again."
        raise FrontendError(message)
    if response.status_code >= 500:
        raise FrontendError("The prediction service could not complete the request. Please try again later.")
    if response.status_code != 200:
        raise FrontendError("The prediction service returned an unexpected response. Please try again.")
    try:
        result = response.json()
        if not isinstance(result, dict) or set(result) != set(PredictionResponse.model_fields):
            raise ValueError("Unexpected response fields")
        validated = PredictionResponse.model_validate(result)
        if validated.prediction_label != {0: "Not Cancelled", 1: "Cancelled"}[validated.prediction]:
            raise ValueError("Inconsistent prediction label")
        return validated.model_dump()
    except (ValueError, TypeError):
        raise FrontendError("The prediction service returned an invalid result. Please try again later.") from None


def backend_connected(backend_url: str) -> bool:
    try:
        response = httpx.get(f"{backend_url.rstrip('/')}/health", timeout=3.0)
        result = response.json()
        return response.status_code == 200 and result.get("model_loaded") is True and result.get("status") == "ok"
    except (httpx.RequestError, ValueError, AttributeError):
        return False
