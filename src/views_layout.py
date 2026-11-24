"""
AgroOrbit - Layout Shell, Landing Hero, 3-Step Wizard, and Loader
Implements a calm, progressive flow:
  Landing -> Wizard (Step 1: Plot -> Step 2: Soil & Crop -> Step 3: Priority) -> Loading -> Results
"""

import math
from typing import Dict, Any, Optional
import streamlit as st
from streamlit_folium import st_folium

from src import config
from src.design_system import (
    get_tokens,
    get_logo_base64,
    svg_icon,
    build_rotation_ring_svg,
)
from src.crops_data import CROPS_DATABASE
from src.egypt_governorates import EGYPT_GOVERNORATES, get_governorate_choices
from src.governorate_analyzer import rank_governorates, build_orbital_folium_map
from src.nasa_client import nasa_client
from src.decision_engine import decision_engine


def _nearest_governorate(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Find closest registered Egyptian governorate center to given coordinates."""
    best = None
    best_dist = float("inf")
    for g in EGYPT_GOVERNORATES.values():
        d = math.hypot(lat - g["lat"], lon - g["lon"])
        if d < best_dist:
            best_dist = d
            best = g
    return best


def _go_to(page: str, step: Optional[int] = None):
    """Switch top-level route cleanly and sync URL query param."""
    st.session_state.page = page
    if step is not None:
        st.session_state.wizard_step = step
    st.query_params["page"] = page


def _toggle_theme():
    """Toggle dark/light theme cleanly via callback."""
    curr = st.session_state.get("theme_mode", "dark")
    st.session_state.theme_mode = "light" if curr == "dark" else "dark"


# =============================================================================
# 1. Persistent Top Navigation Bar (Sleek Edge-to-Edge SaaS Header)
# =============================================================================
def render_navbar(dark_mode: bool = False):
    """Render slim edge-to-edge top header matching crisp modern web apps."""
    t = get_tokens(dark_mode)
    current_page = st.session_state.get("page", "landing")
    has_results = st.session_state.get("strategies_result") is not None
    logo_uri = get_logo_base64()

    with st.container(key="ao_navbar"):
        left_group, right_group = st.columns([3.2, 1.4], vertical_alignment="center")

        with left_group:
            with st.container(horizontal=True, wrap=False, horizontal_alignment="left", vertical_alignment="center", gap="small"):
                logo_img = (
                    f'<img src="{logo_uri}" alt="AgroOrbit" '
                    f'style="width:26px;height:26px;object-fit:contain;border-radius:6px;" />'
                    if logo_uri else svg_icon("sprout", 20)
                )
                st.markdown(
                    f'<div style="display:inline-flex;align-items:center;gap:8px;white-space:nowrap;padding-inline-end:16px;margin-inline-end:8px;border-inline-end:1px solid {t["hairline"]};">'
                    f'{logo_img}'
                    f'<span class="ao-mono" style="font-size:15.5px;font-weight:600;color:{t["accent"]};">AgroOrbit</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                routes = [
                    ("landing", "الرئيسية", ":material/home:"),
                    ("governorates", "المحافظات", ":material/map:"),
                    ("library", "المكتبة", ":material/menu_book:"),
                ]
                if has_results:
                    routes.append(("results", "النتائج", ":material/analytics:"))

                for route_id, label, icon_name in routes:
                    is_active = (current_page == route_id) or (
                        route_id == "landing" and current_page == "wizard" and not has_results
                    )
                    wrap_key = "ao_nav_active" if is_active else f"ao_nav_{route_id}"
                    with st.container(key=wrap_key):
                        st.button(
                            label,
                            icon=icon_name,
                            key=f"nav_btn_{route_id}",
                            type="secondary",
                            width="content",
                            on_click=_go_to,
                            args=(route_id,),
                        )

        with right_group:
            with st.container(horizontal=True, wrap=False, horizontal_alignment="right", vertical_alignment="center", gap="small"):
                theme_label = "ليلي" if not dark_mode else "نهاري"
                theme_icon = ":material/dark_mode:" if not dark_mode else ":material/light_mode:"
                with st.container(key="ao_nav_theme"):
                    st.button(
                        theme_label,
                        icon=theme_icon,
                        key="nav_theme_toggle",
                        type="secondary",
                        width="content",
                        on_click=_toggle_theme,
                    )

                cta_label = "تعديل التحليل" if current_page == "results" else "ابدأ التحليل"
                with st.container(key="ao_nav_cta"):
                    st.button(
                        cta_label,
                        key="nav_cta_btn",
                        type="primary",
                        width="content",
                        on_click=_go_to,
                        args=("wizard", 1),
                    )


# =============================================================================
# 2. Landing Page (Asymmetric Hero + Crop Rotation Ring Moment + 3 Crisp Cards)
# =============================================================================
def render_landing_page(dark_mode: bool = False):
    """Render bright first-impression hero with asymmetric split and Rotation Ring."""
    t = get_tokens(dark_mode)

    preview_res = st.session_state.get("strategies_result")
    if preview_res is None:
        preview_tel = st.session_state.telemetry
        preview_res = decision_engine.generate_all_strategies(
            soil_type="loam",
            previous_crop_id="maize",
            nasa_telemetry=preview_tel,
            priority_water=5,
            priority_soil=3,
            priority_profit=2,
        )

    water_strat = preview_res.get("strategy_3_water_resilience", {})
    preview_timeline = water_strat.get("timeline", [])
    water_pct = water_strat.get("metrics", {}).get("water_savings_pct", 28.0)

    ring_svg = build_rotation_ring_svg(
        timeline=preview_timeline,
        center_value=f"+{water_pct:.0f}%",
        center_label="توفير مياه متوقع",
        dark_mode=dark_mode,
        size_px=276,
        show_legend=True,
    )

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    col_copy, col_visual = st.columns([1.15, 1.0], vertical_alignment="center", gap="large")

    with col_copy:
        st.markdown(
            f"""
            <div class="ao-enter">
                <div style="margin-bottom: 16px;">
                    <span class="ao-tag ao-tag-accent">
                        <span class="ao-dot" style="background:{t['accent']};"></span>
                        <span>بيانات <bdi dir="ltr">NASA POWER</bdi> و <bdi dir="ltr">SMAP</bdi> · 27 محافظة</span>
                    </span>
                </div>
                <h1 class="ao-hero-title" style="font-size: 46px; font-weight: 600; line-height: 1.25; margin-bottom: 16px; color: {t['text_primary']};">
                    اعرف تزرع إيه في أرضك الموسم الجاي
                </h1>
                <p style="font-size: 17px; line-height: 1.7; color: {t['text_secondary']}; max-width: 34rem; margin-bottom: 24px;">
                    بنقرأ بيانات الأقمار الصناعية عن حرارة ورطوبة وتربة مكانك، ونطلعلك 3 خطط زراعة لـ 3 مواسم متتالية بالتوفير المتوقع في مياه الري وشكاير السماد.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn_c1, btn_c2, _ = st.columns([1.1, 1.25, 0.85], gap="small")
        with btn_c1:
            st.button(
                "ابدأ تحليل أرضك",
                key="hero_start_wizard",
                type="primary",
                width="stretch",
                on_click=_go_to,
                args=("wizard", 1),
            )
        with btn_c2:
            st.button(
                "شوف ترتيب المحافظات",
                key="hero_go_govs",
                type="secondary",
                width="stretch",
                on_click=_go_to,
                args=("governorates",),
            )

    with col_visual:
        st.markdown(
            f'<div class="ao-card ao-enter" style="padding: 28px 24px; display:flex; justify-content:center; align-items:center;">'
            f'{ring_svg}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 36px;"></div>', unsafe_allow_html=True)

    # 3 Value Cards with crisp semantic icon wells (Sky Telemetry, Emerald Growth, Harvest Gold Reports)
    c1, c2, c3 = st.columns(3, gap="medium")
    cards = [
        (
            "map-pin",
            t["sky_teal"],
            t["sky_tint"],
            "بيانات مكانك الدقيقة",
            "سحب 15 يوم من قياسات الحرارة، الإشعاع الشمسي، ورطوبة التربة الجذرية لإحداثيات أرضك من ناسا.",
        ),
        (
            "sprout",
            t["accent"],
            t["accent_tint"],
            "3 خطط مقارنة",
            "خطة لتجديد خصوبة التربة بالبقوليات، وخطة لتوفير المياه في الحرارة العالية، مقارنة بنمطك الحالي.",
        ),
        (
            "file-text",
            t["wheat_gold"],
            t["wheat_tint"],
            "ملخص صوتي وتقرير للطباعة",
            "اسمع التوصية بالعامية المصرية أونلاين أو احفظ التقرير الرسمي <bdi dir='ltr'>PDF</bdi> لمشاركته في الجمعية الزراعية.",
        ),
    ]
    for col, (icon_name, fg_col, bg_col, title, desc) in zip((c1, c2, c3), cards):
        with col:
            st.markdown(
                f"""
                <div class="ao-card-compact" style="height:100%;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                        <span class="ao-icon-box" style="background:{bg_col};color:{fg_col};">
                            {svg_icon(icon_name, 17)}
                        </span>
                        <span style="font-size:15px;font-weight:600;color:{t['text_primary']};">{title}</span>
                    </div>
                    <p style="font-size:14px;line-height:1.65;color:{t['text_secondary']};margin:0;">
                        {desc}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid {t['hairline']}; display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; font-size:13px; color:{t['text_muted']};">
            <span>مصادر البيانات: <bdi dir="ltr">NASA POWER · NASA SMAP · GADM 4.1</bdi></span>
            <span>فريق <bdi dir="ltr">Nova Squad NASA</bdi></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# 3. 3-Step Guided Wizard
# =============================================================================
def _render_stepper(step: int):
    """Render quiet 3-step RTL progress indicator."""
    labels = ["1 · مكان الأرض", "2 · الأرض والمحصول السابق", "3 · أولويتك"]
    items = []
    for idx, lbl in enumerate(labels, start=1):
        track_cls = "ao-step-track ao-step-track-active" if idx <= step else "ao-step-track"
        lbl_cls = "ao-step-label ao-step-label-active" if idx == step else "ao-step-label"
        items.append(
            f'<div class="ao-step-item">'
            f'<div class="{track_cls}"></div>'
            f'<div class="{lbl_cls}">{lbl}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="ao-stepper">{"".join(items)}</div>', unsafe_allow_html=True)


def render_wizard_page(dark_mode: bool = True):
    """Render the 3-step input wizard so user never faces cluttered forms."""
    t = get_tokens(dark_mode)
    step = st.session_state.get("wizard_step", 1)

    st.markdown('<div class="ao-enter" style="max-width: 960px; margin: 0 auto;">', unsafe_allow_html=True)
    _render_stepper(step)

    if step == 1:
        _render_wizard_step_location(t, dark_mode)
    elif step == 2:
        _render_wizard_step_soil_crop(t, dark_mode)
    else:
        _render_wizard_step_priority(t, dark_mode)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_wizard_step_location(t: Dict[str, str], dark_mode: bool):
    """Step 1: Select plot location via dropdown, map click, GPS control, or optional coordinates."""
    st.markdown(
        f"""
        <h2 style="font-size: 28px; margin-bottom: 4px;">أرضك فين</h2>
        <p style="font-size: 15px; color:{t['text_secondary']}; margin-bottom: 20px;">
            دوس على الخريطة، أو اختار المحافظة، أو اضغط علامة الموقع <bdi dir="ltr">GPS</bdi> أعلى يسار الخريطة
        </p>
        """,
        unsafe_allow_html=True,
    )

    gov_choices = get_governorate_choices()
    current_gov_id = st.session_state.get("selected_gov_id", "cairo")
    gov_keys = list(gov_choices.keys())
    default_idx = gov_keys.index(current_gov_id) if current_gov_id in gov_keys else 0

    sel_col, info_col = st.columns([1.4, 1.0], vertical_alignment="bottom")
    with sel_col:
        chosen_gov = st.selectbox(
            "المحافظة",
            options=gov_keys,
            index=default_idx,
            format_func=lambda x: EGYPT_GOVERNORATES[x]["name_ar"],
            key="wiz_gov_select",
        )
        if chosen_gov != st.session_state.get("selected_gov_id"):
            st.session_state.selected_gov_id = chosen_gov
            gov_obj = EGYPT_GOVERNORATES[chosen_gov]
            st.session_state.latitude = gov_obj["lat"]
            st.session_state.longitude = gov_obj["lon"]
            st.session_state.soil_type = gov_obj.get("dominant_soil", st.session_state.soil_type)
            st.rerun()

    with info_col:
        lat_val = st.session_state.latitude
        lon_val = st.session_state.longitude
        gov_display = EGYPT_GOVERNORATES.get(st.session_state.get("selected_gov_id", ""), {}).get("name_ar", "")
        st.markdown(
            f'<div class="ao-card-compact" style="padding: 10px 14px; display:flex; align-items:center; justify-content:space-between; gap:8px;">'
            f'<span style="font-size:13px; color:{t["text_muted"]};">{gov_display}</span>'
            f'<span class="ao-mono" style="font-size:13px; color:{t["text_primary"]};">{lat_val:.4f}, {lon_val:.4f}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    ranked_default = rank_governorates(st.session_state.gov_telemetry, "composite_score", dark_mode=dark_mode)
    farm_map = build_orbital_folium_map(
        center_lat=st.session_state.latitude,
        center_lon=st.session_state.longitude,
        ranked_govs=ranked_default,
        criterion_key="composite_score",
        selected_farm_coords=(st.session_state.latitude, st.session_state.longitude),
        selected_gov_id=st.session_state.get("selected_gov_id"),
        dark_mode=dark_mode,
        zoom_start=7,
    )

    map_interaction = st_folium(
        farm_map,
        height=440,
        use_container_width=True,
        returned_objects=["last_clicked"],
        key="wizard_map_selector",
    )

    if map_interaction and map_interaction.get("last_clicked"):
        new_lat = round(map_interaction["last_clicked"]["lat"], 4)
        new_lon = round(map_interaction["last_clicked"]["lng"], 4)
        if abs(new_lat - st.session_state.latitude) > 0.001 or abs(new_lon - st.session_state.longitude) > 0.001:
            st.session_state.latitude = new_lat
            st.session_state.longitude = new_lon
            nearest = _nearest_governorate(new_lat, new_lon)
            if nearest:
                st.session_state.selected_gov_id = nearest["id"]
            st.rerun()

    with st.expander("إدخال الإحداثيات يدوياً", expanded=False):
        c_lat, c_lon = st.columns(2)
        with c_lat:
            man_lat = st.number_input("خط العرض (Latitude)", value=float(st.session_state.latitude), format="%.4f", step=0.01)
        with c_lon:
            man_lon = st.number_input("خط الطول (Longitude)", value=float(st.session_state.longitude), format="%.4f", step=0.01)
        if abs(man_lat - st.session_state.latitude) > 0.0001 or abs(man_lon - st.session_state.longitude) > 0.0001:
            st.session_state.latitude = man_lat
            st.session_state.longitude = man_lon
            nearest = _nearest_governorate(man_lat, man_lon)
            if nearest:
                st.session_state.selected_gov_id = nearest["id"]

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("التالي", key="wiz_step1_next", type="primary", width="content"):
            st.session_state.wizard_step = 2
            st.rerun()


def _render_wizard_step_soil_crop(t: Dict[str, str], dark_mode: bool):
    """Step 2: Visual soil texture cards + pill selection for previous crop + plot acreage."""
    st.markdown(
        f"""
        <h2 style="font-size: 28px; margin-bottom: 4px;">نوع التربة والمحصول السابق</h2>
        <p style="font-size: 15px; color:{t['text_secondary']}; margin-bottom: 24px;">
            اختار طبيعة تربة الأرض وآخر محصول اتزرع فيها عشان نكسر دورة الآفات ونضبط احتياج النيتروجين
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<div style="font-size:14px; font-weight:500; color:{t["text_primary"]}; margin-bottom:8px;">نوع التربة</div>', unsafe_allow_html=True)

    soil_cards = [
        ("clay", "طينية", "الدلتا والوادي، احتفاظ عالي بالماء"),
        ("loam", "طميية", "تربة متوازنة الصرف والتهوية"),
        ("sandy", "رملية", "أراضي الاستصلاح والري بالتنقيط"),
        ("calcareous", "جيرية", "الساحل الشمالي والترب الكلسية"),
    ]
    current_soil = st.session_state.get("soil_type", "clay")

    with st.container(key="soil_cards_grid"):
        s_cols = st.columns(4, gap="small")
        for col, (sid, title, desc) in zip(s_cols, soil_cards):
            with col:
                is_sel = (current_soil == sid)
                btn_type = "primary" if is_sel else "secondary"
                if st.button(f"**{title}**  \n\n{desc}", key=f"soil_card_{sid}", type=btn_type, width="stretch", wrap=True):
                    st.session_state.soil_type = sid
                    st.rerun()

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:14px; font-weight:500; color:{t["text_primary"]}; margin-bottom:8px;">اتزرع إيه آخر موسم</div>', unsafe_allow_html=True)

    crop_keys = list(CROPS_DATABASE.keys())
    current_crop = st.session_state.get("previous_crop", "maize")
    chosen_crop = st.pills(
        "المحصول السابق",
        options=crop_keys,
        default=current_crop if current_crop in crop_keys else crop_keys[0],
        selection_mode="single",
        required=True,
        format_func=lambda cid: CROPS_DATABASE[cid]["name_ar"],
        label_visibility="collapsed",
        key="wiz_prev_crop_pills",
    )
    if chosen_crop and chosen_crop != st.session_state.previous_crop:
        st.session_state.previous_crop = chosen_crop

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
    area_col, hint_col = st.columns([1.0, 1.5], vertical_alignment="center")
    with area_col:
        area_val = st.number_input(
            "مساحة الأرض (فدان)",
            min_value=0.5,
            max_value=500.0,
            value=float(st.session_state.get("farm_area", 5.0)),
            step=0.5,
            format="%.1f",
            key="wiz_farm_area",
        )
        st.session_state.farm_area = area_val
    with hint_col:
        st.markdown(
            f'<div style="font-size:13px; color:{t["text_muted"]}; padding-top: 20px;">'
            f'بنحسب بيها توفير المياه بالمتر المكعب وشكاير اليوريا في صفحة التوفير.'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("رجوع", key="wiz_step2_back", type="secondary", width="content"):
            st.session_state.wizard_step = 1
            st.rerun()
        if st.button("التالي", key="wiz_step2_next", type="primary", width="content"):
            st.session_state.wizard_step = 3
            st.rerun()


def _render_wizard_step_priority(t: Dict[str, str], dark_mode: bool):
    """Step 3: Select farm priority profile with optional custom weight sliders."""
    st.markdown(
        f"""
        <h2 style="font-size: 28px; margin-bottom: 4px;">إيه أهم حاجة ليك الموسم ده</h2>
        <p style="font-size: 15px; color:{t['text_secondary']}; margin-bottom: 24px;">
            اختيارك بيرتب الأولوية في التوصية الرئيسية مع عرض البدائل للمقارنة
        </p>
        """,
        unsafe_allow_html=True,
    )

    prios = [
        ("water", "توفير المياه", "أرضي على بير أو آخر الترعة ومحتاج أقل مقنن مائي", (5, 3, 2)),
        ("soil", "صحة التربة", "الأرض مجهدة ومحتاجة راحة وتثبيت نيتروجين طبيعي", (3, 5, 2)),
        ("profit", "أعلى عائد اقتصادي", "أولويتي المحاصيل التعاقدية والعائد السريع من الفدان", (2, 3, 5)),
    ]
    current_prio = st.session_state.get("priority_preset", "soil")

    with st.container(key="prio_cards_grid"):
        p_cols = st.columns(3, gap="medium")
        for col, (pid, title, desc, weights) in zip(p_cols, prios):
            with col:
                is_sel = (current_prio == pid)
                btn_type = "primary" if is_sel else "secondary"
                if st.button(f"**{title}**  \n\n{desc}", key=f"prio_card_{pid}", type=btn_type, width="stretch", wrap=True):
                    st.session_state.priority_preset = pid
                    st.session_state.p_water, st.session_state.p_soil, st.session_state.p_profit = weights
                    st.rerun()

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    with st.expander("ضبط الأوزان بالتفصيل", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.p_water = st.slider("أولوية توفير المياه", 1, 5, int(st.session_state.get("p_water", 3)))
        with c2:
            st.session_state.p_soil = st.slider("أولوية خصوبة التربة", 1, 5, int(st.session_state.get("p_soil", 5)))
        with c3:
            st.session_state.p_profit = st.slider("أولوية العائد المادي", 1, 5, int(st.session_state.get("p_profit", 2)))

    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("رجوع", key="wiz_step3_back", type="secondary", width="content"):
            st.session_state.wizard_step = 2
            st.rerun()
        if st.button("اعرض الخطة", key="wiz_step3_submit", type="primary", width="content"):
            _go_to("loading")
            st.rerun()


# =============================================================================
# 4. Transparent Loading Transition (Real Progress Steps)
# =============================================================================
def render_loading_page(dark_mode: bool = True):
    """Run live NASA query and decision computation while showing real progress."""
    t = get_tokens(dark_mode)
    lat = st.session_state.latitude
    lon = st.session_state.longitude
    gov_id = st.session_state.get("selected_gov_id", "")
    gov_name = EGYPT_GOVERNORATES.get(gov_id, {}).get("name_ar", "موقع مخصص")

    st.markdown('<div style="max-width: 520px; margin: 48px auto;">', unsafe_allow_html=True)
    st.markdown(f'<h2 style="font-size: 24px; margin-bottom: 20px;">بنجهّز خطتك</h2>', unsafe_allow_html=True)

    status_slot = st.empty()

    def _draw_progress(step1_done: bool, step2_done: bool, step3_done: bool):
        def _row(done: bool, text: str) -> str:
            icon = (
                f'<span style="color:{t["positive"]};display:inline-flex;">{svg_icon("check", 16)}</span>'
                if done else
                f'<span class="ao-dot" style="background:{t["text_muted"]};width:8px;height:8px;margin:4px;"></span>'
            )
            col = t["text_primary"] if done else t["text_muted"]
            return (
                f'<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid {t["hairline"]};">'
                f'{icon}<span style="font-size:15px;color:{col};">{text}</span></div>'
            )

        status_slot.markdown(
            f'<div class="ao-card">'
            f'{_row(step1_done, f"تم تحديد موقع الأرض: {gov_name}")}'
            f'{_row(step2_done, "سحب 15 يوم من قياسات NASA POWER لإحداثياتك")}'
            f'{_row(step3_done, "حساب الخطط الثلاث وتقدير توفير المياه والسماد")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    _draw_progress(True, False, False)

    telemetry = nasa_client.fetch_point_telemetry(
        lat, lon, days=15, timeout=6, allow_network=True
    )
    st.session_state.telemetry = telemetry
    _draw_progress(True, True, False)

    res = decision_engine.generate_all_strategies(
        soil_type=st.session_state.soil_type,
        previous_crop_id=st.session_state.previous_crop,
        nasa_telemetry=telemetry,
        priority_water=int(st.session_state.get("p_water", 3)),
        priority_soil=int(st.session_state.get("p_soil", 5)),
        priority_profit=int(st.session_state.get("p_profit", 2)),
    )
    res["metadata"]["latitude"] = lat
    res["metadata"]["longitude"] = lon
    res["metadata"]["governorate_ar"] = gov_name
    res["metadata"]["area_feddan"] = float(st.session_state.get("farm_area", 5.0))
    st.session_state.strategies_result = res

    _draw_progress(True, True, True)
    st.markdown("</div>", unsafe_allow_html=True)

    _go_to("results")
    st.rerun()
