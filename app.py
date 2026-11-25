"""
AgroOrbit - Precision Agro-Climatic Decision Support System
Team: Nova Squad NASA | NASA Space Apps Challenge 2026

Refined 4-Stage Progressive Experience:
  Stage 1: Land Profile -> Stage 2: Goals & Constraints (+ 90-Day Climate Sim)
  -> Stage 3: Custom Plans & 12-Month Gantt -> Stage 4: Satellite Maps & Scientific Lab
"""

import streamlit as st

from src.design_system import get_design_system_css
from src.nasa_client import nasa_client
from src.views_layout import (
    render_topbar_and_stepper,
    render_stage1_land,
    render_stage2_goals,
)
from src.views_results import render_stage3_results
from src.views_explore import render_stage4_lab

# =============================================================================
# 1. Page Configuration (Sidebar hidden by Botanical Design System CSS)
# =============================================================================
st.set_page_config(
    page_title="AgroOrbit | أجرواوربت",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# 2. Session State & Route Normalization
# =============================================================================
_LEGACY_ROUTE_MAP = {
    "landing": "stage1",
    "wizard": "stage1",
    "results": "stage3",
    "governorates": "stage4",
    "library": "stage4",
}

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"
if "page" not in st.session_state:
    raw_qp = st.query_params.get("page", "stage1")
    mapped = _LEGACY_ROUTE_MAP.get(raw_qp, raw_qp)
    st.session_state.page = mapped if mapped in ("stage1", "stage2", "stage3", "stage4") else "stage1"

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

if "goal_choice" not in st.session_state:
    st.session_state.goal_choice = "water"
if "p_water" not in st.session_state:
    st.session_state.p_water = 5
if "p_soil" not in st.session_state:
    st.session_state.p_soil = 3
if "p_profit" not in st.session_state:
    st.session_state.p_profit = 2

if "constraint_water" not in st.session_state:
    st.session_state.constraint_water = "limited"
if "constraint_labor" not in st.session_state:
    st.session_state.constraint_labor = "medium"
if "constraint_market" not in st.session_state:
    st.session_state.constraint_market = "local"

if "sim_temp_shift" not in st.session_state:
    st.session_state.sim_temp_shift = 0.0
if "sim_rain_shift" not in st.session_state:
    st.session_state.sim_rain_shift = 0

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
# 3. Apply Botanical Design System & Render Active Stage
# =============================================================================
is_dark = st.session_state.theme_mode == "dark"
st.markdown(get_design_system_css(dark_mode=is_dark), unsafe_allow_html=True)

render_topbar_and_stepper(dark_mode=is_dark)

active_page = st.session_state.page
if active_page == "stage2":
    render_stage2_goals(dark_mode=is_dark)
elif active_page == "stage3":
    render_stage3_results(dark_mode=is_dark)
elif active_page == "stage4":
    render_stage4_lab(dark_mode=is_dark)
else:
    render_stage1_land(dark_mode=is_dark)
