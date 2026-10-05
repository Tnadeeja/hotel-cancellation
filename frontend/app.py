"""From project root: streamlit run frontend/app.py

Run backend separately: uvicorn backend.app:app --reload
Optional environment variable BACKEND_URL defaults to http://127.0.0.1:8000.
"""
from datetime import date
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from backend.schemas import COUNTRY_CODES
from frontend.ui_helpers import (
    FrontendError, backend_connected, category_options, prepare_payload, request_prediction,
)


def main():
    st.set_page_config(page_title="Hotel Cancellation Risk Prediction", page_icon="🏨", layout="wide")
    backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
    st.title("Hotel Cancellation Risk Prediction")
    st.caption("Early booking cancellation risk support for hotel staff")
    st.write("Enter the booking information available before the final outcome is known.")
    with st.sidebar:
        st.subheader("Prediction service")
        if st.button("Check connection"):
            st.session_state["backend_connected"] = backend_connected(backend_url)
        connected = st.session_state.get("backend_connected")
        if connected is True:
            st.success("Backend connected")
        elif connected is False:
            st.warning("Backend unavailable")
        else:
            st.caption("Connection not checked")
        st.caption("Model: Random Forest\n\nStrategy: General-only")

    values = {}

    def count(field, label, default=0, help=None):
        values[field] = st.number_input(label, min_value=0, value=default, step=1, key=field, help=help)

    def category(field, label, help=None):
        values[field] = st.selectbox(label, category_options(field), key=field, help=help)

    with st.form("booking_form"):
        st.subheader("Hotel & Arrival")
        a, b, c = st.columns(3)
        with a:
            category("hotel", "Hotel Type")
        with b:
            values["arrival_date"] = st.date_input("Arrival Date", value=date.today(),
                min_value=date.min, max_value=date.max, key="arrival_date", format="YYYY-MM-DD")
        with c:
            count("lead_time", "Lead Time (days)", help="Use the booking's recorded lead time, not the days remaining from today.")

        st.subheader("Stay Details")
        a, b = st.columns(2)
        with a:
            count("stays_in_weekend_nights", "Weekend Nights")
        with b:
            count("stays_in_week_nights", "Week Nights")
        st.caption("A booking with zero stay nights is allowed.")

        st.subheader("Guest Details")
        a, b, c = st.columns(3)
        with a:
            count("adults", "Adults", default=2)
        with b:
            count("children", "Children")
        with c:
            count("babies", "Babies")

        st.subheader("Booking Channel")
        a, b, c = st.columns(3)
        with a:
            category("meal", "Meal Plan")
            category("market_segment", "Market Segment")
        with b:
            values["country"] = st.selectbox("Country Code", [None, *sorted(COUNTRY_CODES)],
                format_func=lambda value: "Unknown / not provided" if value is None else value,
                key="country", help="Type to search the country codes used in booking records.")
            category("distribution_channel", "Distribution Channel")
        with c:
            values["agent"] = st.text_input("Agent Code (optional)", key="agent",
                help="Whole-number code such as 240, without decimal points or leading zeros. Leave blank if unknown.")

        st.subheader("Reservation Details")
        a, b = st.columns(2)
        with a:
            category("reserved_room_type", "Reserved Room Type", help="Use the reserved room code, not the room ultimately assigned.")
            category("customer_type", "Customer Type")
        with b:
            category("deposit_type", "Deposit Type", help="Use payment information known at the time of this assessment.")
            repeated = st.radio("Repeated Guest?", ["No", "Yes"], horizontal=True, key="is_repeated_guest")
            values["is_repeated_guest"] = 1 if repeated == "Yes" else 0

        st.subheader("Previous Booking History")
        a, b, c = st.columns(3)
        with a:
            count("previous_cancellations", "Previous Cancellations")
        with b:
            count("previous_bookings_not_canceled", "Previous Non-cancelled Bookings")
        with c:
            count("days_in_waiting_list", "Days on Waiting List", help="Use the known waiting duration once the booking is confirmed.")

        st.subheader("Requests & Parking")
        a, b = st.columns(2)
        with a:
            count("required_car_parking_spaces", "Required Parking Spaces")
        with b:
            count("total_of_special_requests", "Special Request Count")
        submitted = st.form_submit_button("Predict Cancellation Risk", type="primary")

    if submitted:
        # Clear the previous result before a new attempt so a failure cannot show stale output.
        st.session_state.pop("prediction_result", None)
        try:
            payload = prepare_payload(values)
            with st.spinner("Checking this booking…"):
                result = request_prediction(backend_url, payload)
            st.session_state["prediction_result"] = (result, payload)
        except FrontendError as exc:
            st.error(str(exc))

    saved = st.session_state.get("prediction_result")
    if saved:
        result, payload = saved
        with st.container(border=True):
            st.subheader("Prediction Result")
            st.caption("Estimate for the submitted booking")
            a, b = st.columns(2)
            with a:
                st.metric("Prediction", result["prediction_label"])
            with b:
                st.metric("Cancellation Probability", f"{result['cancellation_probability']:.1%}")
            st.progress(result["cancellation_probability"])
            st.caption(f"Model: {result['model_name']} · Strategy: {result['strategy']}")
            st.write("This result is a decision-support estimate and does not guarantee whether a booking will actually be cancelled.")
            with st.expander("Submitted booking summary"):
                guests = payload["adults"] + payload["children"] + payload["babies"]
                nights = payload["stays_in_weekend_nights"] + payload["stays_in_week_nights"]
                st.write(f"{payload['hotel']} · Arrival: {payload['arrival_date']} · Guests: {guests} · Stay nights: {nights} · Lead time: {payload['lead_time']} days")

    with st.expander("About this prediction"):
        st.write("**Model:** Random Forest  \n**Strategy:** General-only")
        st.write("Purpose: early hotel booking cancellation risk prediction. Predictions support staff decisions and are not guaranteed outcomes.")


if __name__ == "__main__":
    main()
