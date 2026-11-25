"""
AgroOrbit - Header Navigation, 4-Stage Stepper, Stage 1 & Stage 2 Views
Visual structure & botanical polish aligned with balanced 4-stage progressive flow:
  Topbar (Logo + Lab + Voice Dialog + Day/Night Pill)
  4-Step Ribbon -> Stage 1 (Land Profile) -> Stage 2 (Goals & Constraints + 90-Day Sim)
"""

import math
from typing import Dict, Any, Optional
import folium
from folium.plugins import LocateControl
import streamlit as st
from streamlit_folium import st_folium

from src import config
from src.design_system import get_tokens, get_logo_base64
from src.crops_data import CROPS_DATABASE
from src.egypt_governorates import EGYPT_GOVERNORATES, get_governorate_choices
from src.nasa_client import nasa_client
from src.decision_engine import decision_engine
from src.voice_advisor import generate_voice_script, get_agro_voice_audio


STAGE_ORDER = {
    "stage1": 1,
    "stage2": 2,
    "stage3": 3,
    "stage4": 4,
}


def _nearest_governorate(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Return nearest Egypt governorate record for map clicks or manual lat/lon."""
    best = None
    best_dist = float("inf")
    for gid, gov in EGYPT_GOVERNORATES.items():
        d = math.hypot(lat - gov["lat"], lon - gov["lon"])
        if d < best_dist:
            best_dist = d
            best = gov
    return best


def _go_stage(target_stage: str):
    """Switch active stage cleanly and compute strategies if entering stage3 directly."""
    if target_stage == "stage3":
        ensure_strategies_computed(allow_network=True)
    st.session_state.page = target_stage
    st.query_params["page"] = target_stage


def ensure_strategies_computed(force: bool = False, allow_network: bool = True) -> Dict[str, Any]:
    """Ensure telemetry and 3 crop strategies are computed for current inputs."""
    existing = st.session_state.get("strategies_result")
    lat = float(st.session_state.get("latitude", 29.3084))
    lon = float(st.session_state.get("longitude", 30.8428))
    soil = st.session_state.get("soil_type", "clay")
    prev = st.session_state.get("previous_crop", "maize")
    pw = int(st.session_state.get("p_water", 5))
    ps = int(st.session_state.get("p_soil", 3))
    pp = int(st.session_state.get("p_profit", 2))
    area = float(st.session_state.get("farm_area", 5.0))
    c_water = st.session_state.get("constraint_water", "unlimited")
    t_shift = float(st.session_state.get("sim_temp_shift", 0.0))
    r_shift = int(st.session_state.get("sim_rain_shift", 0))

    sig = (round(lat, 4), round(lon, 4), soil, prev, pw, ps, pp, c_water, t_shift, r_shift)
    if existing and not force and st.session_state.get("_strategies_sig") == sig:
        existing["metadata"]["area_feddan"] = area
        return existing

    gov_id = st.session_state.get("selected_gov_id", "faiyum")
    gov_name = EGYPT_GOVERNORATES.get(gov_id, {}).get("name_ar", "موقع مخصص")

    telemetry = nasa_client.fetch_point_telemetry(
        lat,
        lon,
        days=15,
        timeout=6 if allow_network else 2,
        allow_network=allow_network,
    )
    st.session_state.telemetry = telemetry

    # Apply effective water boost if irrigation water constraint is scarce
    eff_pw = min(5, pw + 1) if c_water == "scarce" else pw

    # Feed scenario-adjusted telemetry into engine if user slid climate offsets
    calc_tel = telemetry
    if t_shift != 0.0 or r_shift != 0:
        calc_tel = dict(telemetry)
        idx_c = dict(telemetry.get("indices", {}))
        idx_c["avg_temp_c"] = round(float(idx_c.get("avg_temp_c", 23.0)) + t_shift, 1)
        idx_c["max_temp_c"] = round(float(idx_c.get("max_temp_c", 31.0)) + t_shift, 1)
        if t_shift >= 2.0:
            idx_c["extreme_heat_days"] = int(idx_c.get("extreme_heat_days", 0)) + 2
        if r_shift < 0:
            base_m = float(idx_c.get("soil_moisture_score", 45.0))
            idx_c["soil_moisture_score"] = max(12.0, round(base_m * (1.0 + r_shift / 160.0), 1))
        calc_tel["indices"] = idx_c

    res = decision_engine.generate_all_strategies(
        soil_type=soil,
        previous_crop_id=prev,
        nasa_telemetry=calc_tel,
        priority_water=eff_pw,
        priority_soil=ps,
        priority_profit=pp,
    )
    res["metadata"]["latitude"] = lat
    res["metadata"]["longitude"] = lon
    res["metadata"]["governorate_ar"] = gov_name
    res["metadata"]["area_feddan"] = area
    res["metadata"]["sim_temp_shift"] = t_shift
    res["metadata"]["sim_rain_shift"] = r_shift

    st.session_state.strategies_result = res
    st.session_state._strategies_sig = sig
    return res


# =============================================================================
# Voice Agro-Advisor Modal (Accessible from any stage via Topbar button)
# =============================================================================
@st.dialog("المستشار الصوتي الزراعي - أجرواوربت", width="large")
def open_voice_dialog():
    """Play Egyptian colloquial agronomic briefings and allow offline MP3 download."""
    is_dark = st.session_state.get("theme_mode", "dark") == "dark"
    t = get_tokens(is_dark)
    res = ensure_strategies_computed(allow_network=False)
    meta = res.get("metadata", {})

    st.markdown(
        f'<p style="font-size:14px;color:{t["mu"]};margin-bottom:14px;">'
        f'اختر موضوع الإحاطة للاستماع إلى شرح التوصيات بالعامية المصرية لحقول <b>{meta.get("governorate_ar", "الفيوم")}</b>'
        f' (<bdi dir="ltr">{meta.get("area_feddan", 5.0):.1f}</bdi> فدان).'
        f'</p>',
        unsafe_allow_html=True,
    )

    briefing_opts = {
        "comprehensive": "الملخص الشامل",
        "soil_health": "صحة التربة واليوريا",
        "water_resilience": "ترشيد المياه والحر",
        "pest_prevention": "كسر دورة الآفات",
    }
    selected_b = st.pills(
        "موضوع الرسالة الصوتية",
        options=list(briefing_opts.keys()),
        default="comprehensive",
        selection_mode="single",
        required=True,
        format_func=lambda k: briefing_opts[k],
        label_visibility="collapsed",
        key="modal_voice_pills",
    )

    script_text = generate_voice_script(selected_b, meta, res)
    with st.spinner("جاري تجهيز الملف الصوتي..."):
        audio_bytes = get_agro_voice_audio(script_text)

    v_col, d_col = st.columns([2.6, 1.0], vertical_alignment="center", gap="small")
    with v_col:
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.info("تعذر توليد الملف الصوتي حالياً، يمكنك قراءة النص الكامل بالأسفل.")
    with d_col:
        if audio_bytes:
            st.download_button(
                label="تحميل الصوت MP3",
                data=audio_bytes,
                file_name=f"agroorbit_voice_{selected_b}.mp3",
                mime="audio/mp3",
                width="stretch",
                key="modal_voice_dl",
            )

    with st.expander("قراءة النص الكامل للرسالة الصوتية", expanded=True):
        st.markdown(
            f'<div class="gf-insight-box" style="line-height:1.85;font-size:14.5px;margin-top:0;">'
            f'{script_text.replace(chr(10), "<br>")}'
            f'</div>',
            unsafe_allow_html=True,
        )


# =============================================================================
# 1. Sticky Topbar & 4-Step Progress Bar
# =============================================================================
def render_topbar_and_stepper(dark_mode: bool = True):
    """Render top brand header, action pills, and 4-step numbered ribbon."""
    t = get_tokens(dark_mode)
    active_page = st.session_state.get("page", "stage1")
    logo_uri = get_logo_base64()

    if logo_uri:
        logo_html = (
            f'<div style="width:48px;height:48px;border-radius:14px;background:{t["surface_alt"]};'
            f'border:1.5px solid {t["ac_border"]};box-shadow:0 4px 16px {t["ac_soft"]};'
            f'display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0;">'
            f'<img src="{logo_uri}" alt="AgroOrbit" style="width:42px;height:42px;object-fit:contain;" />'
            f'</div>'
        )
    else:
        logo_html = (
            f'<div style="width:48px;height:48px;border-radius:14px;background:linear-gradient(135deg,{t["ac"]},{t["ac_dark"]});'
            f'display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:{t["ac_text"]};'
            f'box-shadow:0 4px 16px {t["ac_soft"]};flex-shrink:0;">AO</div>'
        )

    with st.container(key="gf_topbar"):
        brand_col, lab_col, voice_col, theme_col = st.columns(
            [3.8, 1.55, 1.3, 0.9], vertical_alignment="center", gap="small"
        )
        with brand_col:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:14px;">'
                f'{logo_html}'
                f'<div>'
                f'<div style="font-size:19px;font-weight:800;color:{t["tx"]};letter-spacing:-0.2px;line-height:1.25;">'
                f'<bdi dir="ltr">AgroOrbit</bdi> <span style="color:{t["ac"]};font-size:15px;">أجرواوربت</span>'
                f'</div>'
                f'<div style="font-size:12.5px;color:{t["mu"]};margin-top:2px;">'
                f'مستشار الدورة الزراعية الذكي عبر الأقمار الصناعية'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with lab_col:
            with st.container(key="gf_top_lab_btn"):
                if st.button(
                    "الخرائط والمختبر العلمي",
                    icon=":material/public:",
                    key="top_lab_btn",
                    type="secondary",
                    width="stretch",
                ):
                    _go_stage("stage4")
                    st.rerun()

        with voice_col:
            with st.container(key="gf_top_pill_voice"):
                if st.button(
                    "المستشار الصوتي",
                    icon=":material/record_voice_over:",
                    key="top_voice_btn",
                    type="secondary",
                    width="stretch",
                ):
                    open_voice_dialog()

        with theme_col:
            with st.container(key="gf_top_pill_theme"):
                mode_lbl = "نهاري" if dark_mode else "ليلي"
                mode_ico = ":material/light_mode:" if dark_mode else ":material/dark_mode:"
                if st.button(
                    mode_lbl,
                    icon=mode_ico,
                    key="top_theme_toggle",
                    type="secondary",
                    width="stretch",
                ):
                    st.session_state.theme_mode = "light" if dark_mode else "dark"
                    st.rerun()

    # 4-Step Progress Ribbon
    steps = [
        ("stage1", "1", "بيانات الأرض"),
        ("stage2", "2", "الأهداف والقيود"),
        ("stage3", "3", "خطتك المخصصة"),
        ("stage4", "4", "الخرائط والمختبر"),
    ]
    curr_idx = STAGE_ORDER.get(active_page, 1)

    with st.container(key="gf_stepper"):
        cols = st.columns([1.25, 0.22, 1.25, 0.22, 1.25, 0.22, 1.25], vertical_alignment="center", gap="small")
        for idx, (sid, num, label) in enumerate(steps):
            step_num = idx + 1
            col_step = cols[idx * 2]
            is_active = (sid == active_page)
            is_done = (step_num < curr_idx)

            state_cls = "active" if is_active else ("done" if is_done else "idle")
            prefix = "✓" if is_done else num
            btn_label = f"{prefix} · {label}"

            with col_step:
                with st.container(key=f"gf_step_{state_cls}_{sid}"):
                    if st.button(
                        btn_label,
                        key=f"stepper_btn_{sid}",
                        type="secondary",
                        width="stretch",
                    ):
                        _go_stage(sid)
                        st.rerun()

            if idx < len(steps) - 1:
                col_conn = cols[idx * 2 + 1]
                conn_cls = "gf-connector gf-connector-done" if step_num < curr_idx else "gf-connector"
                with col_conn:
                    st.markdown(f'<div class="{conn_cls}"></div>', unsafe_allow_html=True)


# =============================================================================
# 2. Stage 1 — Land Profile (Centered 920px Card, Direct Start Screen)
# =============================================================================
def _render_optional_satellite_picker(t: Dict[str, str], dark_mode: bool):
    """Expandable precision GPS / satellite pinpoint picker inside Stage 1."""
    center_lat = float(st.session_state.get("latitude", 29.3084))
    center_lon = float(st.session_state.get("longitude", 30.8428))

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles=None,
        control_scale=True,
    )
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="صور الأقمار الصناعية",
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Labels",
        name="أسماء المواقع",
        overlay=True,
    ).add_to(m)

    folium.CircleMarker(
        location=[center_lat, center_lon],
        radius=9,
        color=t["ac"],
        weight=3,
        fill=True,
        fill_color=t["ac"],
        fill_opacity=0.85,
        tooltip="موقع الأرض المحدد",
    ).add_to(m)
    LocateControl(auto_start=False, strings={"title": "تحديد موقعي بـ GPS"}).add_to(m)

    map_res = st_folium(
        m,
        height=310,
        use_container_width=True,
        returned_objects=["last_clicked"],
        key="stage1_satellite_picker",
    )
    if map_res and map_res.get("last_clicked"):
        new_lat = round(float(map_res["last_clicked"]["lat"]), 4)
        new_lon = round(float(map_res["last_clicked"]["lng"]), 4)
        if abs(new_lat - center_lat) > 0.001 or abs(new_lon - center_lon) > 0.001:
            st.session_state.latitude = new_lat
            st.session_state.longitude = new_lon
            nearest = _nearest_governorate(new_lat, new_lon)
            if nearest:
                st.session_state.selected_gov_id = nearest["id"]
                st.session_state.soil_type = nearest.get("dominant_soil", st.session_state.soil_type)
            st.session_state.telemetry = nasa_client.fetch_point_telemetry(
                new_lat, new_lon, days=15, timeout=2, allow_network=False
            )
            st.rerun()

    c_lat, c_lon = st.columns(2, gap="small")
    with c_lat:
        man_lat = st.number_input("خط العرض (Lat)", value=center_lat, format="%.4f", step=0.01, key="s1_man_lat")
    with c_lon:
        man_lon = st.number_input("خط الطول (Lon)", value=center_lon, format="%.4f", step=0.01, key="s1_man_lon")
    if abs(man_lat - center_lat) > 0.0001 or abs(man_lon - center_lon) > 0.0001:
        st.session_state.latitude = man_lat
        st.session_state.longitude = man_lon
        nearest = _nearest_governorate(man_lat, man_lon)
        if nearest:
            st.session_state.selected_gov_id = nearest["id"]
        st.session_state.telemetry = nasa_client.fetch_point_telemetry(
            man_lat, man_lon, days=15, timeout=2, allow_network=False
        )
        st.rerun()


def render_stage1_land(dark_mode: bool = True):
    """Render Stage 1 Land Profile Card inside centered 920px layout."""
    t = get_tokens(dark_mode)
    st.markdown('<div class="gf-animate">', unsafe_allow_html=True)

    with st.container(key="gf_centered_stage"):
        st.markdown(
            f'<span class="gf-step-tag">المرحلة 1 من 3 • تعريف الحقل</span>'
            f'<h1 style="font-size:25px;font-weight:800;margin-bottom:4px;color:{t["tx"]};">حدثنا عن أرضك وظروفها الحالية</h1>'
            f'<p style="font-size:14.5px;color:{t["mu"]};margin-bottom:16px;">'
            f'اختر المحافظة والمساحة والمحصول السابق لنقيس التربة والرطوبة والحرارة مباشرة من الأقمار الصناعية دون تعقيد.'
            f'</p>',
            unsafe_allow_html=True,
        )

        gov_choices = get_governorate_choices()
        gov_keys = list(gov_choices.keys())
        curr_gov = st.session_state.get("selected_gov_id", "faiyum")
        if curr_gov not in gov_keys:
            curr_gov = gov_keys[0]

        soil_keys = list(config.SOIL_TYPES.keys())
        curr_soil = st.session_state.get("soil_type", "clay")
        if curr_soil not in soil_keys:
            curr_soil = soil_keys[0]

        crop_keys = list(CROPS_DATABASE.keys())
        curr_prev = st.session_state.get("previous_crop", "maize")
        if curr_prev not in crop_keys:
            curr_prev = crop_keys[0]

        # 2x2 Main Input Grid
        r1c1, r1c2 = st.columns(2, gap="medium")
        with r1c1:
            chosen_gov = st.selectbox(
                "المحافظة أو النطاق الزراعي",
                options=gov_keys,
                index=gov_keys.index(curr_gov),
                format_func=lambda k: EGYPT_GOVERNORATES[k]["name_ar"],
                key="s1_gov_select",
            )
            if chosen_gov != st.session_state.get("selected_gov_id"):
                st.session_state.selected_gov_id = chosen_gov
                gov_obj = EGYPT_GOVERNORATES[chosen_gov]
                st.session_state.latitude = gov_obj["lat"]
                st.session_state.longitude = gov_obj["lon"]
                st.session_state.soil_type = gov_obj.get("dominant_soil", st.session_state.soil_type)
                st.session_state.telemetry = nasa_client.fetch_point_telemetry(
                    gov_obj["lat"], gov_obj["lon"], days=15, timeout=2, allow_network=False
                )
                st.rerun()

        with r1c2:
            area_val = st.number_input(
                "مساحة الأرض (فدان)",
                min_value=0.5,
                max_value=500.0,
                value=float(st.session_state.get("farm_area", 5.0)),
                step=0.5,
                format="%.1f",
                key="s1_area_input",
            )
            st.session_state.farm_area = area_val

        r2c1, r2c2 = st.columns(2, gap="medium")
        with r2c1:
            chosen_soil = st.selectbox(
                "نوع التربة في الحقل",
                options=soil_keys,
                index=soil_keys.index(curr_soil),
                format_func=lambda s: config.SOIL_TYPES[s]["name_ar"],
                key="s1_soil_select",
            )
            if chosen_soil != st.session_state.get("soil_type"):
                st.session_state.soil_type = chosen_soil

        with r2c2:
            chosen_prev = st.selectbox(
                "المحصول السابق (الذي انتهى موسمه لتوه)",
                options=crop_keys,
                index=crop_keys.index(curr_prev),
                format_func=lambda cid: f"{CROPS_DATABASE[cid]['name_ar']} ({CROPS_DATABASE[cid].get('season_label_ar', '')})",
                key="s1_prev_crop_select",
            )
            if chosen_prev != st.session_state.get("previous_crop"):
                st.session_state.previous_crop = chosen_prev

        # Live Telemetry & Soil Preview Banner
        tel = st.session_state.get("telemetry", {})
        indices = tel.get("indices", {})
        soil_short = config.SOIL_TYPES.get(st.session_state.soil_type, {}).get("name_ar", st.session_state.soil_type)
        moist_pct = float(indices.get("soil_moisture_score", 46.0))
        avg_t = float(indices.get("avg_temp_c", 23.0))
        max_t = float(indices.get("max_temp_c", 31.0))

        st.markdown(
            f"""
            <div class="gf-preview-banner">
                <div>
                    <div class="gf-preview-label">طبيعة التربة المختارة</div>
                    <div class="gf-preview-val">{soil_short}</div>
                </div>
                <div>
                    <div class="gf-preview-label">رطوبة الجذور (<bdi dir="ltr">SMAP</bdi>)</div>
                    <div class="gf-preview-val" style="color:{t['blue']};"><bdi dir="ltr">{moist_pct:.0f}%</bdi></div>
                </div>
                <div>
                    <div class="gf-preview-label">حرارة القمر الصناعي (متوسط / قصوى)</div>
                    <div class="gf-preview-val" style="color:{t['amber']};"><bdi dir="ltr">{avg_t:.1f}° / {max_t:.1f}°C</bdi></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Optional Satellite Pinpoint Expander
        lat_cur = float(st.session_state.get("latitude", 29.3084))
        lon_cur = float(st.session_state.get("longitude", 30.8428))
        with st.expander(f"تحديد موقع الحقل بالضبط على الخريطة أو GPS ({lat_cur:.3f}, {lon_cur:.3f})", expanded=False):
            _render_optional_satellite_picker(t, dark_mode)

        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        _, cta_col = st.columns([2.2, 1.0])
        with cta_col:
            if st.button(
                "التالي: الأهداف والقيود",
                icon=":material/arrow_back:",
                key="stage1_next_btn",
                type="primary",
                width="stretch",
            ):
                _go_stage("stage2")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 3. Stage 2 — Goals, Constraints & 90-Day Climate Simulator
# =============================================================================
def render_stage2_goals(dark_mode: bool = True):
    """Render Stage 2 centered card with 2x2 goal tiles, constraints & climate sim."""
    t = get_tokens(dark_mode)
    st.markdown('<div class="gf-animate">', unsafe_allow_html=True)

    with st.container(key="gf_centered_stage"):
        st.markdown(
            f'<span class="gf-step-tag">المرحلة 2 من 3 • الأهداف والقيود التشغيلية</span>'
            f'<h1 style="font-size:26px;font-weight:800;margin-bottom:6px;color:{t["tx"]};">حدد هدفك الرئيسي وظروف المزرعة</h1>'
            f'<p style="font-size:15px;color:{t["mu"]};margin-bottom:20px;">'
            f'توزن هذه الاختيارات أولوية التوصية بين توفير مياه الري وتقليل اليوريا وأعلى عائد مالي للفدان.'
            f'</p>',
            unsafe_allow_html=True,
        )

        # 2x2 Goal Cards Grid
        goals = [
            ("water", "توفير مياه الري", "أرضي على بئر أو آخر الترعة وأحتاج أقل مقنن مائي (أولوية المياه 5/5)", (5, 3, 2)),
            ("soil", "تجديد خصوبة التربة", "إدخال بقوليات تثبيت نيتروجين وتقليل اليوريا وكسر الآفات (أولوية التربة 5/5)", (3, 5, 2)),
            ("profit", "تعظيم العائد المادي", "أفضل المحاصيل التعاقدية والنقدية ذات أسرع دورة ربحية للفدان (أولوية العائد 5/5)", (2, 3, 5)),
            ("balanced", "خطة متوازنة شاملة", "توازن ذكي متساوٍ بين حفظ رطوبة التربة والربحية وصحة الأرض (4 / 4 / 4)", (4, 4, 4)),
        ]
        curr_goal = st.session_state.get("goal_choice", "water")

        with st.container(key="gf_goal_cards"):
            for i in range(0, 4, 2):
                cols = st.columns(2, gap="medium")
                for col, (gid, title, desc, weights) in zip(cols, goals[i : i + 2]):
                    with col:
                        is_sel = (curr_goal == gid)
                        btype = "primary" if is_sel else "secondary"
                        lbl = f"**{title}**\n\n{desc}"
                        if st.button(lbl, key=f"goal_card_{gid}", type=btype, width="stretch"):
                            st.session_state.goal_choice = gid
                            st.session_state.p_water, st.session_state.p_soil, st.session_state.p_profit = weights
                            st.rerun()

        st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)

        # 3-Column Operational Constraints
        water_opts = {
            "unlimited": "مياه ري منتظمة طوال العام",
            "limited": "مناوبة ري كل 10-14 يوماً",
            "scarce": "شح مائي / اعتماد على بئر",
        }
        labor_opts = {
            "high": "ميكنة كاملة وعمالة متوفرة",
            "medium": "متوسطة",
            "low": "محدودة — يفضل خدمة أقل",
        }
        market_opts = {
            "local": "سوق محلي وتعاقدات جمعية",
            "contract": "توريد مصانع ومحاصيل استراتيجية",
            "export": "جودة تصديرية ومواسم مبكرة",
        }

        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            w_keys = list(water_opts.keys())
            cw = st.session_state.get("constraint_water", "limited")
            st.session_state.constraint_water = st.selectbox(
                "وفرة مياه الري",
                options=w_keys,
                index=w_keys.index(cw) if cw in w_keys else 1,
                format_func=lambda k: water_opts[k],
                key="s2_c_water",
            )
        with c2:
            l_keys = list(labor_opts.keys())
            cl = st.session_state.get("constraint_labor", "medium")
            st.session_state.constraint_labor = st.selectbox(
                "العمالة والميكنة المتاحة",
                options=l_keys,
                index=l_keys.index(cl) if cl in l_keys else 1,
                format_func=lambda k: labor_opts[k],
                key="s2_c_labor",
            )
        with c3:
            m_keys = list(market_opts.keys())
            cm = st.session_state.get("constraint_market", "local")
            st.session_state.constraint_market = st.selectbox(
                "اتجاه التسويق المستهدف",
                options=m_keys,
                index=m_keys.index(cm) if cm in m_keys else 0,
                format_func=lambda k: market_opts[k],
                key="s2_c_market",
            )

        # Blue 90-Day Climate Scenario Simulator Box
        with st.container(key="gf_sim_box"):
            t_cur = float(st.session_state.get("sim_temp_shift", 0.0))
            r_cur = int(st.session_state.get("sim_rain_shift", 0))
            badge_html = (
                '<bdi dir="ltr">0°C</bdi> / أمطار <bdi dir="ltr">0%</bdi>'
                if t_cur == 0.0 and r_cur == 0
                else f'<bdi dir="ltr">{t_cur:+.1f}°C</bdi> &nbsp;|&nbsp; أمطار <bdi dir="ltr">{r_cur:+d}%</bdi>'
            )
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;">'
                f'<span style="font-size:15px;font-weight:800;color:{t["tx"]};">محاكي تغير الطقس خلال <bdi dir="ltr">90</bdi> يوماً القادمة (اختياري)</span>'
                f'<span class="gf-sim-badge">{badge_html}</span>'
                f'</div>'
                f'<p style="font-size:13px;color:{t["mu"]};margin:0 0 8px 0;">'
                f'اختبر صمود الخطط أمام موجات الحر الشديدة أو تغير الأمطار الموسمية قبل بدء الزراعة.'
                f'</p>',
                unsafe_allow_html=True,
            )
            sc1, sc2 = st.columns(2, gap="medium")
            with sc1:
                st.session_state.sim_temp_shift = st.slider(
                    "انحراف الحرارة المتوقع (°C)",
                    min_value=-3.0,
                    max_value=4.5,
                    value=t_cur,
                    step=0.5,
                    key="s2_sim_temp",
                )
            with sc2:
                st.session_state.sim_rain_shift = st.slider(
                    "انحراف الأمطار والرطوبة (%)",
                    min_value=-50,
                    max_value=50,
                    value=r_cur,
                    step=10,
                    key="s2_sim_rain",
                )

        st.markdown('<div style="height: 22px;"></div>', unsafe_allow_html=True)
        nav_back, nav_sp, nav_go = st.columns([1.0, 0.8, 1.4], gap="small")
        with nav_back:
            if st.button(
                "السابق: بيانات الأرض",
                icon=":material/arrow_forward:",
                key="stage2_back_btn",
                type="secondary",
                width="stretch",
            ):
                _go_stage("stage1")
                st.rerun()
        with nav_go:
            if st.button(
                "حساب وعرض الخطط الـ 3",
                icon=":material/auto_awesome:",
                key="stage2_compute_btn",
                type="primary",
                width="stretch",
            ):
                with st.spinner("جاري تحليل قياسات الأقمار الصناعية وحساب التوصيات..."):
                    ensure_strategies_computed(force=True, allow_network=True)
                st.session_state.page = "stage3"
                st.query_params["page"] = "stage3"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
