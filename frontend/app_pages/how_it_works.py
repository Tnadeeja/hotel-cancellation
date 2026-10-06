import streamlit as st
from frontend.visuals import page_heading, card
page_heading("A CLEAR PATH FROM DETAILS TO DECISIONS", "How it works", "Enter the reservation details. The service checks them, calculates the required values, and returns an estimate for your review.")
steps = [
("01", "Booking Details", "Provide the reservation, guest and stay information."),
("02", "Frontend Validation", "Helpful checks catch missing or invalid information."),
("03", "FastAPI Backend", "The prediction service validates the submitted booking."),
("04", "Feature Derivation", "Date components and additional booking values are calculated automatically."),
("05", "Preprocessing", "The saved pipeline prepares booking information consistently."),
("06", "Random Forest", "The frozen model estimates cancellation from the prepared details."),
("07", "Prediction", "Receive a cancellation label and probability."),
("08", "Decision Support", "Review the estimate alongside staff knowledge and current conditions."),
]
for start in (0,4):
    for column, step in zip(st.columns(4),steps[start:start+4]):
        with column: card(*step)
with st.container(border=True):
    st.subheader("One connected service")
    st.write("The interface sends booking details to the backend. The backend handles all calculations and model processing, then returns the result. Hotel staff do not need to enter engineered values or date components.")
    st.caption("At least one guest is required. Zero-night bookings are allowed. Agent and country may be left unknown.")
