from pathlib import Path
import streamlit as st
from frontend.visuals import card

with st.container(key="home_hero"):
    left, right = st.columns([1.08, 1], gap="large", vertical_alignment="center")
    with left:
        st.html('<div class="hero-copy"><p class="eyebrow"><span class="gold-line"></span> THE ART OF INFORMED HOSPITALITY</p><h1>Every booking.<br>A clearer<br><em>perspective.</em></h1><p>Hotel cancellation risk intelligence, designed to help you make confident, considered reservation decisions.</p></div>')
        if st.button("Predict Cancellation Risk", type="primary", key="hero_predict", icon=":material/arrow_forward:"):
            st.switch_page("app_pages/prediction.py")
        st.html('<div class="hero-note"><span>01 / BOOKING INTELLIGENCE</span><span>CITY &amp; RESORT HOTELS</span></div>')
    with right:
        with st.container(key="hero_visual"):
            st.image(str(Path(__file__).resolve().parents[1] / "assets/hotel-waterfront.svg"), alt="Original illustration of a waterfront hotel at sunset", width="stretch")
            st.html('<div class="visual-caption"><span>HOSPITALITY, WITH PERSPECTIVE</span><strong>A thoughtful approach<br>to every reservation.</strong></div>')

st.html('<div class="section-intro"><p class="eyebrow">YOUR RESERVATION TOOLKIT</p><h2>Less guesswork. More insight.</h2><p>One focused workspace, from booking details to a considered decision.</p></div>')
for column, (number, title, description) in zip(st.columns(4), [
    ("01", "See risk earlier", "Review each reservation before its final outcome is known."),
    ("02", "Add perspective", "Bring historical-data evidence alongside your team's experience."),
    ("03", "Find clarity", "A straightforward prediction, paired with its estimated probability."),
    ("04", "Stay hotel-focused", "A consistent experience for City and Resort reservations."),
]):
    with column:
        card(number, title, description)
with st.container(key="business_value"):
    left, right = st.columns([2,1], vertical_alignment="center")
    with left:
        st.html('<p class="eyebrow">READY WHEN YOU ARE</p><h2>A better-informed next step.</h2><p>Start with a reservation. Review the estimate. Bring your expertise.</p>')
        st.caption("Decision support, not a guaranteed outcome.")
    with right:
        if st.button("Start a Prediction", type="primary", key="start_prediction", width="stretch"):
            st.switch_page("app_pages/prediction.py")
