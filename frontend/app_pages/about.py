import streamlit as st
from frontend.visuals import page_heading

page_heading("BUILT FOR INFORMED RESERVATIONS", "About the project", "Early Hotel Booking Cancellation Risk Prediction")
a, b = st.columns(2)
with a:
    with st.container(border=True):
        st.subheader("Purpose")
        st.write("Support hotel reservation decision-making using booking information available before the final outcome is known.")
        st.caption("The historical data is retrospective; exact booking-creation values are not guaranteed. Deposit and waiting-list details must be available at the assessment point.")
with b:
    with st.container(border=True):
        st.subheader("Dataset & system")
        st.write("**Dataset:** Hotel Booking Demand dataset")
        st.write("Streamlit frontend · FastAPI backend · Scikit-learn preprocessing · Random Forest classifier")
st.subheader("Final model & system stack")
for column, name in zip(st.columns(4), ["Streamlit", "FastAPI", "Scikit-learn", "Random Forest"]):
    with column:
        with st.container(border=True):
            st.markdown(f"**{name}**")
st.caption("Final model: Random Forest ? General-only strategy. Both hotel types use the same model.")
st.subheader("Limitations")
st.markdown("- Predictions are decision support, not guarantees.\n- Performance is based on the project dataset.\n- The model depends on valid booking information.\n- Operational conditions may differ from historical data.")
st.subheader("Project Team")
team_members = (
    ("Weerasinghe K.A.T.N", "IT23581470"),
    ("De Silva H.S.S", "IT23562042"),
    ("Wijesinghe H P V", "IT23577374"),
    ("Ruksala G V R", "IT23606074"),
)
for column, (name, registration_number) in zip(st.columns(4), team_members):
    with column:
        with st.container(border=True, key=f"team_{registration_number}"):
            st.markdown(f"**{name}**")
            st.caption(registration_number)
