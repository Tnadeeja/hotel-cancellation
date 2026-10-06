"""Run: streamlit run frontend/app.py. Backend: uvicorn backend.app:app --reload.
BACKEND_URL defaults to http://127.0.0.1:8000. No model is loaded here.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from frontend.ui_helpers import render_header, render_sidebar
from frontend.visuals import load_styles

st.set_page_config(page_title="Hotel Cancellation Risk Intelligence", page_icon=":material/hotel:", layout="wide", initial_sidebar_state="expanded")
load_styles()
pages = [
    st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("app_pages/prediction.py", title="Predict Risk", icon=":material/hotel:"),
    st.Page("app_pages/insights.py", title="Model Insights", icon=":material/analytics:"),
    st.Page("app_pages/how_it_works.py", title="How It Works", icon=":material/route:"),
    st.Page("app_pages/about.py", title="About", icon=":material/info:"),
]
page = st.navigation(pages, position="sidebar")
render_sidebar()
render_header(page.title)
page.run()
