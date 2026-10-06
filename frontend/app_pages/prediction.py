"""Prediction page: same 22-field contract and HTTP-only prediction flow."""
from datetime import date
import os
import streamlit as st
from backend.schemas import COUNTRY_CODES
from frontend.ui_helpers import FrontendError, category_options, prepare_payload, request_prediction
from frontend.visuals import page_heading

backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
page_heading("RESERVATION INTELLIGENCE", "Predict Cancellation Risk", "Enter booking information to estimate the likelihood of cancellation.")

SCENARIO_FIELDS = {
    "lead_time": "Lead Time",
    "stays_in_weekend_nights": "Weekend Nights",
    "stays_in_week_nights": "Week Nights",
    "adults": "Adults",
    "children": "Children",
    "babies": "Babies",
    "deposit_type": "Deposit Type",
    "market_segment": "Market Segment",
    "distribution_channel": "Distribution Channel",
    "previous_cancellations": "Previous Cancellations",
    "previous_bookings_not_canceled": "Previous Non-cancelled Bookings",
    "days_in_waiting_list": "Days on Waiting List",
    "required_car_parking_spaces": "Required Parking Spaces",
    "total_of_special_requests": "Special Requests",
}
SCENARIO_UNITS = {
    "lead_time": " days",
    "stays_in_weekend_nights": " nights",
    "stays_in_week_nights": " nights",
    "days_in_waiting_list": " days",
}
ORIGINAL_WIDGET_KEYS = (
    "hotel", "arrival_date", "lead_time", "stays_in_weekend_nights", "stays_in_week_nights",
    "adults", "children", "babies", "meal", "country", "market_segment",
    "distribution_channel", "agent", "reserved_room_type", "customer_type", "deposit_type",
    "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled",
    "days_in_waiting_list", "required_car_parking_spaces", "total_of_special_requests",
)


def clear_scenario_state(clear_widgets=True):
    for key in ("scenario_payload", "scenario_result", "scenario_message"):
        st.session_state.pop(key, None)
    if clear_widgets:
        for field in SCENARIO_FIELDS:
            st.session_state.pop(f"scenario_{field}", None)


def reset_scenario():
    original = st.session_state.get("original_payload")
    if original:
        for field in SCENARIO_FIELDS:
            st.session_state[f"scenario_{field}"] = original[field]
    clear_scenario_state(clear_widgets=False)


def start_new_prediction():
    for key in ("prediction_result", "original_payload", "original_result", "scroll_to_prediction_result"):
        st.session_state.pop(key, None)
    clear_scenario_state()
    for key in ORIGINAL_WIDGET_KEYS:
        st.session_state.pop(key, None)


def changed_scenario_fields(original, scenario):
    return {field: (original[field], scenario[field]) for field in SCENARIO_FIELDS if original[field] != scenario[field]}

values = {}

def count(field, label, default=0, help=None):
    values[field] = st.number_input(label, min_value=0, value=default, step=1, key=field, help=help)

def category(field, label, help=None):
    values[field] = st.selectbox(label, category_options(field), key=field, help=help)

with st.form("booking_form", border=False):
    with st.container(border=True, key="booking_card_1"):
        st.subheader("Hotel & Arrival")
        a, b, c = st.columns(3)
        with a:
            category("hotel", "Hotel Type")
        with b:
            values["arrival_date"] = st.date_input("Arrival Date", value=date.today(),
                min_value=date.min, max_value=date.max, key="arrival_date", format="YYYY-MM-DD")
        with c:
            count("lead_time", "Lead Time (days)", help="Use the booking's recorded lead time, not the days remaining from today.")

    left_card, right_card = st.columns(2)
    with left_card:
        with st.container(border=True, key="booking_card_2"):
            st.subheader("Stay Details")
            a, b = st.columns(2)
            with a:
                count("stays_in_weekend_nights", "Weekend Nights")
            with b:
                count("stays_in_week_nights", "Week Nights")
            st.caption("A booking with zero stay nights is allowed.")
    
    with right_card:
        with st.container(border=True, key="booking_card_3"):
            st.subheader("Guest Details")
            a, b = st.columns(2)
            with a:
                count("adults", "Adults", default=2)
            with b:
                count("children", "Children")
            with b:
                count("babies", "Babies")
    
    left_card, right_card = st.columns(2)
    with left_card:
        with st.container(border=True, key="booking_card_4"):
            st.subheader("Booking Source")
            a, b = st.columns(2)
            with a:
                category("meal", "Meal Plan")
                category("market_segment", "Market Segment")
            with b:
                values["country"] = st.selectbox("Country Code", [None, *sorted(COUNTRY_CODES)],
                    format_func=lambda value: "Unknown / not provided" if value is None else value,
                    key="country", help="Type to search the country codes used in booking records.")
                category("distribution_channel", "Distribution Channel")
            with b:
                values["agent"] = st.text_input("Agent Code (optional)", key="agent",
                    help="Whole-number code such as 240, without decimal points or leading zeros. Leave blank if unknown.")
    
    with right_card:
        with st.container(border=True, key="booking_card_5"):
            st.subheader("Reservation Details")
            a, b = st.columns(2)
            with a:
                category("reserved_room_type", "Reserved Room Type", help="Use the reserved room code, not the room ultimately assigned.")
                category("customer_type", "Customer Type")
            with b:
                category("deposit_type", "Deposit Type", help="Use payment information known at the time of this assessment.")
                repeated = st.radio("Repeated Guest?", ["No", "Yes"], horizontal=True, key="is_repeated_guest")
                values["is_repeated_guest"] = 1 if repeated == "Yes" else 0
    
    left_card, right_card = st.columns(2)
    with left_card:
        with st.container(border=True, key="booking_card_6"):
            st.subheader("Previous Booking History")
            a, b = st.columns(2)
            with a:
                count("previous_cancellations", "Previous Cancellations")
            with b:
                count("previous_bookings_not_canceled", "Previous Non-cancelled Bookings")
            with b:
                count("days_in_waiting_list", "Days on Waiting List", help="Use the known waiting duration once the booking is confirmed.")
    
    with right_card:
        with st.container(border=True, key="booking_card_7"):
            st.subheader("Requests & Parking")
            a, b = st.columns(2)
            with a:
                count("required_car_parking_spaces", "Required Parking Spaces")
            with b:
                count("total_of_special_requests", "Special Request Count")
    submitted = st.form_submit_button("Predict Cancellation Risk", type="primary", width="stretch")

if submitted:
    # Clear the previous result before a new attempt so a failure cannot show stale output.
    st.session_state.pop("prediction_result", None)
    st.session_state.pop("original_payload", None)
    st.session_state.pop("original_result", None)
    clear_scenario_state()
    try:
        payload = prepare_payload(values)
        with st.spinner("Checking this booking…"):
            result = request_prediction(backend_url, payload)
        st.session_state["prediction_result"] = (result, payload)
        st.session_state["original_payload"] = payload
        st.session_state["original_result"] = result
        st.session_state["scroll_to_prediction_result"] = True
    except FrontendError as exc:
        st.error(str(exc))

saved = st.session_state.get("prediction_result")
if saved:
    result, payload = saved
    st.session_state.setdefault("original_payload", payload)
    st.session_state.setdefault("original_result", result)
    is_cancelled = result["prediction"] == 1
    result_class = "cancelled" if is_cancelled else "not-cancelled"
    result_key = "result_panel_cancelled" if is_cancelled else "result_panel_not_cancelled"
    result_icon = "&times;" if is_cancelled else "&#10003;"
    probability_percent = result["cancellation_probability"] * 100
    page_tone = {
        "accent": "#B4232C" if is_cancelled else "#237A4B",
        "deep": "#5F1117" if is_cancelled else "#0F4A2B",
        "wash": "#F9DADC" if is_cancelled else "#DDF3E5",
        "glow": "#EF8E95" if is_cancelled else "#82C99E",
    }
    st.html(
        f"""<style>
        [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at 88% 12%, {page_tone['glow']} 0, transparent 30%),
                linear-gradient(145deg, #fff 0%, {page_tone['wash']} 48%, {page_tone['accent']} 145%);
            background-attachment: fixed;
            transition: background .55s ease;
        }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {page_tone['deep']} 0%, #081B22 100%);
            box-shadow: 8px 0 30px {page_tone['accent']}33;
            transition: background .55s ease;
        }}
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            border-right: 2px solid {page_tone['glow']};
        }}
        .page-heading {{ border-bottom-color: {page_tone['accent']}66; }}
        .page-heading .eyebrow {{ color: {page_tone['deep']}; }}
        </style>"""
    )
    with st.container(border=True, key=result_key):
        st.subheader("Booking Cancellation Prediction")
        st.caption("Estimate for the submitted booking")
        a, b = st.columns(2)
        with a:
            st.html(
                f'<div class="prediction-state {result_class}">'
                f'<span class="result-seal" aria-hidden="true">{result_icon}</span>'
                f'<div><small>Prediction</small>'
                f'<strong>{result["prediction_label"]}</strong></div></div>'
            )
        with b:
            st.html(
                f'<div class="probability-state {result_class}">'
                f'<small>Cancellation Probability</small>'
                f'<strong>{result["cancellation_probability"]:.1%}</strong></div>'
            )
        st.html(
            f'<div class="result-progress {result_class}" role="progressbar" '
            f'aria-label="Cancellation probability" aria-valuemin="0" '
            f'aria-valuemax="100" aria-valuenow="{probability_percent:.1f}">'
            f'<span style="width:{probability_percent:.1f}%"></span></div>'
        )
        st.caption(f"Model: {result['model_name']} · Strategy: {result['strategy']}")
        st.write("This result is a decision-support estimate and does not guarantee whether a booking will actually be cancelled.")
        with st.container(border=False):
            st.markdown("**Booking summary**")
            guests = payload["adults"] + payload["children"] + payload["babies"]
            nights = payload["stays_in_weekend_nights"] + payload["stays_in_week_nights"]
            st.write(f"{payload['hotel']} · Arrival: {payload['arrival_date']} · Guests: {guests} · Stay nights: {nights} · Lead time: {payload['lead_time']} days")

    if st.session_state.pop("scroll_to_prediction_result", False):
        st.iframe(
            f"""
            <script>
                window.setTimeout(() => {{
                    const result = window.parent.document.querySelector('.st-key-{result_key}');
                    if (result) result.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}, 180);
            </script>
            """,
            height=1,
        )

    with st.expander("Scenario Explorer", expanded=False):
        st.html(
            '<div class="scenario-intro"><span>WHAT-IF COMPARISON</span>'
            '<h3>Explore a hypothetical booking</h3>'
            '<p>Adjust selected booking details and compare how the model responds to a hypothetical scenario.</p>'
            '<strong>This is a model-based scenario comparison, not a causal recommendation or guarantee.</strong></div>'
        )

        scenario_values = {}
        for field in SCENARIO_FIELDS:
            st.session_state.setdefault(f"scenario_{field}", payload[field])

        def scenario_count(field):
            scenario_values[field] = st.number_input(
                SCENARIO_FIELDS[field], min_value=0, step=1,
                key=f"scenario_{field}",
            )

        def scenario_category(field):
            options = category_options(field)
            scenario_values[field] = st.selectbox(
                SCENARIO_FIELDS[field], options,
                key=f"scenario_{field}",
            )

        with st.form("scenario_form", border=False):
            with st.container(border=True, key="scenario_editor"):
                st.markdown("**Scenario booking details**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    scenario_count("lead_time")
                    scenario_count("stays_in_weekend_nights")
                    scenario_count("stays_in_week_nights")
                    scenario_count("adults")
                    scenario_count("children")
                with col2:
                    scenario_count("babies")
                    scenario_category("deposit_type")
                    scenario_category("market_segment")
                    scenario_category("distribution_channel")
                    scenario_count("previous_cancellations")
                with col3:
                    scenario_count("previous_bookings_not_canceled")
                    scenario_count("days_in_waiting_list")
                    scenario_count("required_car_parking_spaces")
                    scenario_count("total_of_special_requests")
                compare_scenario = st.form_submit_button("Compare Scenario", type="primary", width="stretch")

        if compare_scenario:
            scenario_candidate = dict(payload)
            scenario_candidate.update(scenario_values)
            clear_scenario_state(clear_widgets=False)
            try:
                scenario_payload = prepare_payload(scenario_candidate)
                changes = changed_scenario_fields(payload, scenario_payload)
                if not changes:
                    st.session_state["scenario_message"] = "No scenario changes selected."
                else:
                    with st.spinner("Comparing the hypothetical scenario..."):
                        scenario_result = request_prediction(backend_url, scenario_payload)
                    st.session_state["scenario_payload"] = scenario_payload
                    st.session_state["scenario_result"] = scenario_result
                    st.session_state.pop("scenario_message", None)
            except FrontendError as exc:
                st.error(str(exc))

        if message := st.session_state.get("scenario_message"):
            st.info(message)

        scenario_payload = st.session_state.get("scenario_payload")
        scenario_result = st.session_state.get("scenario_result")
        if scenario_payload and scenario_result:
            original_result = st.session_state["original_result"]
            difference = scenario_result["cancellation_probability"] - original_result["cancellation_probability"]
            with st.container(border=True, key="scenario_comparison"):
                st.subheader("Original Booking vs Scenario")
                original_col, scenario_col = st.columns(2)
                with original_col:
                    st.markdown("#### Original Booking")
                    st.metric("Prediction", original_result["prediction_label"])
                    st.metric("Cancellation Probability", f"{original_result['cancellation_probability']:.1%}")
                    st.caption(f"Model: {original_result['model_name']} · Strategy: {original_result['strategy']}")
                with scenario_col:
                    st.markdown("#### Scenario")
                    st.metric("Prediction", scenario_result["prediction_label"])
                    st.metric("Cancellation Probability", f"{scenario_result['cancellation_probability']:.1%}")
                    st.caption(f"Model: {scenario_result['model_name']} · Strategy: {scenario_result['strategy']}")
                st.metric(
                    "Change in model-estimated cancellation probability",
                    f"{difference * 100:+.1f} percentage points",
                )
                st.caption("Scenario probability minus original probability.")

                st.markdown("#### Changed booking details")
                for field, (old_value, new_value) in changed_scenario_fields(payload, scenario_payload).items():
                    unit = SCENARIO_UNITS.get(field, "")
                    st.write(f"**{SCENARIO_FIELDS[field]}:** {old_value}{unit} → {new_value}{unit}")

                st.info(
                    "Scenario Explorer shows how the trained model responds when selected booking inputs are changed. "
                    "It does not establish that those changes would cause a booking to cancel or remain active."
                )

        reset_col, new_col = st.columns(2)
        with reset_col:
            st.button("Reset Scenario", on_click=reset_scenario, width="stretch", key="reset_scenario")
        with new_col:
            st.button("Start New Prediction", on_click=start_new_prediction, width="stretch", key="start_new_prediction")

with st.expander("About this prediction"):
    st.write("**Model:** Random Forest  \n**Strategy:** General-only")
    st.write("Purpose: early hotel booking cancellation risk prediction. Predictions support staff decisions and are not guaranteed outcomes.")
