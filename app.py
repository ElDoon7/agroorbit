"""
AgroOrbit - Precision Agro-Climatic Decision Support System
Team: Nova Squad NASA | NASA Space Apps Challenge 2026

Calm multi-page flow:
  Landing Hero -> 3-Step Guided Wizard -> NASA Telemetry Loading -> Results Dashboard
  Plus standalone Governorates Ranking Matrix & Agronomic Knowledge Library.
"""

import streamlit as st

from src.design_system import get_design_system_css
from src.nasa_client import nasa_client
from src.views_layout import (
    render_navbar,
    render_landing_page,
    render_wizard_page,
    render_loading_page,
)
from src.views_results import render_results_page
from src.views_explore import render_governorates_page, render_library_page

# =============================================================================
# 1. Page Configuration (Sidebar collapsed & hidden by Design System CSS)
# =============================================================================
st.set_page_config(
    page_title="AgroOrbit | أجرواوربت",
    page_icon="assets/favicon.png" if False else None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# 2. Session State & Initial Route
# =============================================================================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"
if "page" not in st.session_state:
    qp_page = st.query_params.get("page", "landing")
    st.session_state.page = qp_page if qp_page in ("landing", "wizard", "results", "governorates", "library") else "landing"
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "selected_gov_id" not in st.session_state:
    st.session_state.selected_gov_id = "faiyum"
if "latitude" not in st.session_state:
    st.session_state.latitude = 29.3084
if "longitude" not in st.session_state:
    st.session_state.longitude = 30.8428
if "soil_type" not in st.session_state:
    st.session_state.soil_type = "clay"
if "previous_crop" not in st.session_state:
    st.session_state.previous_crop = "maize"
if "farm_area" not in st.session_state:
    st.session_state.farm_area = 5.0
if "priority_preset" not in st.session_state:
    st.session_state.priority_preset = "soil"
if "p_water" not in st.session_state:
    st.session_state.p_water = 3
if "p_soil" not in st.session_state:
    st.session_state.p_soil = 5
if "p_profit" not in st.session_state:
    st.session_state.p_profit = 2

if "telemetry" not in st.session_state:
    st.session_state.telemetry = nasa_client.fetch_point_telemetry(
        st.session_state.latitude,
        st.session_state.longitude,
        days=15,
        timeout=3,
        allow_network=False,
    )
if "gov_telemetry" not in st.session_state:
    st.session_state.gov_telemetry = nasa_client.get_all_governorates_telemetry(force_refresh=False)
if "strategies_result" not in st.session_state:
    st.session_state.strategies_result = None

# =============================================================================
# 3. Apply Design System & Render Active Route
# =============================================================================
is_dark = st.session_state.theme_mode == "dark"
st.markdown(get_design_system_css(dark_mode=is_dark), unsafe_allow_html=True)

render_navbar(dark_mode=is_dark)

active_page = st.session_state.page
if active_page == "landing":
    render_landing_page(dark_mode=is_dark)
elif active_page == "wizard":
    render_wizard_page(dark_mode=is_dark)
elif active_page == "loading":
    render_loading_page(dark_mode=is_dark)
elif active_page == "results":
    render_results_page(dark_mode=is_dark)
elif active_page == "governorates":
    render_governorates_page(dark_mode=is_dark)
elif active_page == "library":
    render_library_page(dark_mode=is_dark)
else:
    render_landing_page(dark_mode=is_dark)
