"""Small shared presentation elements; all dynamic text is escaped."""
from html import escape
from pathlib import Path
import streamlit as st


def load_styles():
    st.html(Path(__file__).with_name("styles.css"))


def page_heading(eyebrow, title, description):
    st.html(f'<div class="page-heading"><p class="eyebrow">{escape(eyebrow)}</p>'
            f'<h1>{escape(title)}</h1><p>{escape(description)}</p></div>')


def card(number, title, description):
    st.html(f'<article class="feature-card"><span class="card-number">{escape(number)}</span>'
            f'<h3>{escape(title)}</h3><p>{escape(description)}</p></article>')
