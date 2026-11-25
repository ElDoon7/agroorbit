"""
AgroOrbit - Stage 4: Satellite Maps, NASA Charts & Scientific Lab View
Combines Egypt's 27-governorate Esri Satellite Choropleth Map, 10-day NASA POWER chart,
5-axis Governorate Radar with .gf-insight-box callouts, 2x2 Scientific Methodology grid,
11-Crop Table, and 12-Disease Visual Pathology Atlas.
"""

import base64
import io
import html
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from src import config
from src.design_system import get_tokens
from src.crops_data import CROPS_DATABASE, get_all_diseases
from src.egypt_governorates import EGYPT_REGIONS
from src.nasa_client import nasa_client
from src.governorate_analyzer import (
    CRITERIA_DEFINITIONS,
    rank_governorates,
    build_governorate_radar,
    build_orbital_folium_map,
)
from src.views_layout import ensure_strategies_computed


def _season_badge_html(season_type: str, season_label_ar: str, t: dict) -> str:
    """Return crisp Botanical pill badge indicating crop season."""
    st_low = (season_type or "").lower()
    if "winter" in st_low:
        fg, bg = t["blue"], t["blue_soft"]
    elif "summer" in st_low:
        fg, bg = t["amber"], t["amber_soft"]
    else:
        fg, bg = t["ac"], t["ac_soft"]
    return (
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;">'
        f'{html.escape(season_label_ar)}'
        f'</span>'
    )


@st.cache_data(show_spinner=False)
def _get_disease_thumb_uri(img_path_str: str) -> str:
    """Return compact JPEG base64 thumbnail URI so pathology cards share uniform 210px height."""
    try:
        from PIL import Image
        with Image.open(img_path_str) as im:
            rgb = im.convert("RGB")
            rgb.thumbnail((640, 420), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            rgb.save(buf, format="JPEG", quality=82, optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return ""


def _build_10day_nasa_chart(telemetry: dict, t: dict, dark_mode: bool):
    """Build 10-day NASA POWER historical temperature line + rainfall bars."""
    params = telemetry.get("cleaned_parameters", {})
    t2m = params.get("T2M", {})
    rain = params.get("PRECTOTCORR", {})
    dates = sorted(t2m.keys())[-10:]
    if not dates:
        return None

    x_dates = [f"{d[4:6]}-{d[6:]}" if len(d) == 8 else d for d in dates]
    y_temps = [round(float(t2m.get(d, 22.0)), 1) for d in dates]
    y_rains = [round(float(rain.get(d, 0.0)), 2) for d in dates]

    grid_c = "rgba(240,247,243,0.08)" if dark_mode else "rgba(18,38,27,0.07)"
    bar_c = "rgba(56,189,248,0.42)" if dark_mode else "rgba(2,132,199,0.32)"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_dates,
        y=y_rains,
        name="الأمطار (مم)",
        yaxis="y2",
        marker=dict(color=bar_c, line=dict(width=0)),
    ))
    fig.add_trace(go.Scatter(
        x=x_dates,
        y=y_temps,
        mode="lines+markers",
        name="الحرارة (°C)",
        line=dict(color=t["ac"], width=2.5),
        marker=dict(color=t["ac"], size=7),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Cairo, sans-serif", color=t["tx"]),
        xaxis=dict(
            showgrid=False,
            automargin=True,
            tickfont=dict(size=11, color=t["mu"]),
        ),
        yaxis=dict(
            title=dict(text="°C", font=dict(size=11, color=t["mu"])),
            gridcolor=grid_c,
            automargin=True,
            tickfont=dict(size=11, color=t["mu"]),
        ),
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            automargin=True,
            tickfont=dict(size=10, color=t["mu"]),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color=t["tx"]),
        ),
        margin=dict(l=48, r=48, t=34, b=28),
        height=300,
    )
    return fig


def render_stage4_lab(dark_mode: bool = True):
    """Render Stage 4 Satellite Choropleth Map, Telemetry Charts & Scientific Library."""
    t = get_tokens(dark_mode)
    st.markdown('<div class="gf-animate">', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 1. Stage 4 Header + Return to Custom Plan Button
    # -------------------------------------------------------------------------
    hdr_col, back_col = st.columns([3.2, 1.1], vertical_alignment="center", gap="small")
    with hdr_col:
        st.markdown(
            f'<h1 style="font-size:26px;font-weight:800;color:{t["tx"]};margin-bottom:4px;">خرائط الرصد والمختبر العلمي</h1>'
            f'<p style="font-size:14.5px;color:{t["mu"]};margin:0;">'
            f'خريطة <bdi dir="ltr">Egypt 27</bdi> التفاعلية بالأقمار الصناعية، رسوم طقس <bdi dir="ltr">NASA POWER</bdi>، وقاعدة المحاصيل والأمراض'
            f'</p>',
            unsafe_allow_html=True,
        )
    with back_col:
        if st.button("العودة إلى خطتك المخصصة", icon=":material/arrow_forward:", key="s4_back_plan", type="primary", width="stretch"):
            ensure_strategies_computed(allow_network=False)
            st.session_state.page = "stage3"
            st.query_params["page"] = "stage3"
            st.rerun()

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Governorate Choropleth Satellite Map & Criterion Pills
    # -------------------------------------------------------------------------
    ctrl1, ctrl2 = st.columns([3.3, 0.9], vertical_alignment="center", gap="small")
    with ctrl1:
        crit_keys = list(CRITERIA_DEFINITIONS.keys())
        curr_crit = st.session_state.get("s4_crit_key", crit_keys[0])
        selected_crit = st.pills(
            "معيار الخريطة",
            options=crit_keys,
            default=curr_crit if curr_crit in crit_keys else crit_keys[0],
            selection_mode="single",
            required=True,
            format_func=lambda k: CRITERIA_DEFINITIONS[k]["title_ar"],
            label_visibility="collapsed",
            key="s4_crit_pills",
        )
        st.session_state.s4_crit_key = selected_crit
    with ctrl2:
        if st.button("تحديث الأقمار", icon=":material/refresh:", key="s4_refresh_govs", type="secondary", width="stretch"):
            with st.spinner("جاري سحب أحدث قراءات المحافظات..."):
                st.session_state.gov_telemetry = nasa_client.get_all_governorates_telemetry(force_refresh=True)
            st.rerun()

    ranked_govs = rank_governorates(st.session_state.gov_telemetry, selected_crit, dark_mode=dark_mode)
    if not ranked_govs:
        st.info("لا توجد بيانات محافظات متاحة حالياً.")
        return

    default_gov = st.session_state.get("inspect_gov_id") or ranked_govs[0]["id"]
    if not any(g["id"] == default_gov for g in ranked_govs):
        default_gov = ranked_govs[0]["id"]
    st.session_state.inspect_gov_id = default_gov
    sel_record = next((g for g in ranked_govs if g["id"] == default_gov), ranked_govs[0])

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    list_col, map_col = st.columns([1.0, 2.1], gap="large")

    with list_col:
        show_all = st.session_state.get("gov_show_all", False)
        visible_govs = ranked_govs if show_all else ranked_govs[:14]

        with st.container(key="gov_list_panel"):
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;font-size:12px;color:{t["mu"]};'
                f'padding:0 12px 8px 12px;border-bottom:1px solid {t["bd"]};margin-bottom:6px;font-weight:700;">'
                f'<span>ترتيب المحافظات</span><span>المؤشر</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            for g in visible_govs:
                is_sel = (g["id"] == default_gov)
                btn_type = "primary" if is_sel else "secondary"
                row_lbl = f"{g['rank']}. {g['name_ar']}   —   {g['score']:.1f}%"
                if st.button(row_lbl, key=f"s4_gov_row_{g['id']}", type=btn_type, width="stretch"):
                    st.session_state.inspect_gov_id = g["id"]
                    st.rerun()

        toggle_txt = "عرض أعلى 14 محافظة" if show_all else "عرض الـ 27 محافظة كاملة"
        if st.button(toggle_txt, key="s4_gov_toggle", type="secondary", width="stretch"):
            st.session_state.gov_show_all = not show_all
            st.rerun()

        if st.button(f"خطط لأرضي في {sel_record['name_ar']}", icon=":material/agriculture:", key="s4_apply_gov", type="primary", width="stretch"):
            st.session_state.selected_gov_id = sel_record["id"]
            st.session_state.latitude = sel_record["lat"]
            st.session_state.longitude = sel_record["lon"]
            st.session_state.soil_type = sel_record.get("dominant_soil", st.session_state.soil_type)
            st.session_state.telemetry = nasa_client.fetch_point_telemetry(
                sel_record["lat"], sel_record["lon"], days=15, timeout=2, allow_network=False
            )
            st.session_state.page = "stage1"
            st.query_params["page"] = "stage1"
            st.rerun()

    with map_col:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px;padding:10px 16px;background:{t['surface']};border:1px solid {t['bd']};border-radius:12px;">
                <span style="font-size:13px;color:{t['tx']};font-weight:700;">مفتاح طبقة الأقمار الصناعية ({CRITERIA_DEFINITIONS[selected_crit]['title_ar']}):</span>
                <div style="display:flex;align-items:center;gap:14px;font-size:12px;color:{t['mu']};font-weight:600;">
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#10b981;display:inline-block;"></span>ممتاز</span>
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#0ea5e9;display:inline-block;"></span>جيد جداً</span>
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#f59e0b;display:inline-block;"></span>متوسط</span>
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span style="width:10px;height:10px;border-radius:50%;background:#ea580c;display:inline-block;"></span>يحتاج تكيّف مائي</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        gov_map = build_orbital_folium_map(
            center_lat=27.2,
            center_lon=30.8,
            ranked_govs=ranked_govs,
            criterion_key=selected_crit,
            selected_farm_coords=(st.session_state.latitude, st.session_state.longitude),
            selected_gov_id=default_gov,
            dark_mode=dark_mode,
            zoom_start=6,
        )
        st_folium(gov_map, height=490, use_container_width=True, key="s4_matrix_map")

        ind = sel_record.get("indices", {})
        soil_ar = config.SOIL_TYPES.get(sel_record.get("dominant_soil", ""), {}).get("name_ar", "")
        reg_ar = EGYPT_REGIONS.get(sel_record.get("region", ""), {}).get("name_ar", "")
        crops_ar = "، ".join(CROPS_DATABASE[c]["name_ar"] for c in sel_record.get("main_crops", []) if c in CROPS_DATABASE)

        st.markdown(
            f"""
            <div class="gf-insight-box">
                <b style="color:{t['ac']};">{sel_record['name_ar']} (#{sel_record['rank']} من 27 — {sel_record['score']:.1f}%):</b>
                الإقليم: {reg_ar} • التربة السائدة: {soil_ar} • متوسط الحرارة: <bdi dir="ltr">{ind.get('avg_temp_c', 23.0)}°C</bdi> •
                رطوبة التربة: <bdi dir="ltr">{ind.get('soil_moisture_score', 45.0)}%</bdi> • المحاصيل الرئيسية: {crops_ar or '-'}.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. Side-by-Side Analytics Pair (10-Day NASA Line/Bar + 5-Axis Radar)
    # -------------------------------------------------------------------------
    c_chart, c_radar = st.columns(2, gap="large")
    with c_chart:
        st.markdown(f'<h3 style="font-size:18px;font-weight:800;margin-bottom:10px;color:{t["tx"]};">رصد الطقس اليومي لآخر 10 أيام (<bdi dir="ltr">NASA POWER</bdi>)</h3>', unsafe_allow_html=True)
        tel = st.session_state.get("telemetry", {})
        tel_idx = tel.get("indices", {})
        fig_10d = _build_10day_nasa_chart(tel, t, dark_mode)
        if fig_10d:
            st.plotly_chart(fig_10d, theme=None, width="stretch")
        else:
            st.info("اختر موقعاً في المرحلة 1 لعرض السلسلة الزمنية اليومية.")

        st.markdown(
            f'<div class="gf-insight-box">'
            f'<b>ملخص القياسات الحقلية للإحداثيات المختارة:</b> متوسط الحرارة <bdi dir="ltr">{tel_idx.get("avg_temp_c", 23.0)}°C</bdi>، '
            f'إجمالي الأمطار <bdi dir="ltr">{tel_idx.get("total_precip_mm", 0.0)}</bdi> مم، '
            f'أيام الإجهاد الحراري <bdi dir="ltr">{tel_idx.get("extreme_heat_days", 0)}</bdi> يوم.'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c_radar:
        st.markdown(f'<h3 style="font-size:18px;font-weight:800;margin-bottom:10px;color:{t["tx"]};">البصمة المناخية خماسية المحاور: {sel_record["name_ar"]}</h3>', unsafe_allow_html=True)
        radar_fig = build_governorate_radar(sel_record, dark_mode=dark_mode)
        st.plotly_chart(radar_fig, theme=None, width="stretch")

        st.markdown(
            f'<div class="gf-insight-box">'
            f'<b>توازن المحاور المناخية:</b> يقيس الرادار كفاءة الموارد المائية والاعتدال الحراري وجودة التربة لتحديد الميزة التنافسية لكل محافظة.'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. 2x2 Scientific Methodology Grid
    # -------------------------------------------------------------------------
    st.markdown(f'<h2 style="font-size:20px;font-weight:800;margin-bottom:14px;color:{t["tx"]};">المنهجية العلمية ونموذج القرار الفضائي</h2>', unsafe_allow_html=True)
    meth_cards = [
        ("دمج بيانات الأقمار الصناعية", "تُجمع درجات الحرارة القصوى والدنيا والإشعاع الشمسي من شبكة <bdi dir='ltr'>NASA POWER</bdi> مع مؤشرات رطوبة الجذور من <bdi dir='ltr'>SMAP</bdi> لكل نقطة في مصر."),
        ("موازنة النيتروجين الحيوي", "يُدمج البرسيم المصري أو الفول السوداني أو فول الصويا داخل الدورة لتعويض استنزاف النجيلات وتقليل الحاجة لشيكارات اليوريا الكيماوية."),
        ("حدود الدقة والمراجعة الحقلية", "دقة الشبكة الفضائية تبلغ بقطر نحو <bdi dir='ltr'>50</bdi> كم، لذا يُنصح دائماً بمراجعة فحص ملوحة التربة المحلية والالتزام بنوبات الري الرسمية."),
        ("كسر سلاسل الآفات التخصصية", "تمنع الدورة المتنوعة تكرار نفس العائل النباتي في المواسم المتعاقبة، مما يخفض إصابات الحشرات والأمراض التراكمية دون زيادة المبيدات."),
    ]
    for i in range(0, 4, 2):
        mc1, mc2 = st.columns(2, gap="medium")
        for col, (m_title, m_desc) in zip((mc1, mc2), meth_cards[i : i + 2]):
            with col:
                st.markdown(
                    f"""
                    <div class="gf-card" style="margin-bottom:14px;padding:18px 20px;">
                        <div style="font-size:15.5px;font-weight:800;color:{t['ac']};margin-bottom:6px;">{m_title}</div>
                        <p style="font-size:13.5px;line-height:1.7;color:{t['tx']};margin:0;">{m_desc}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. Searchable Agronomic Knowledge Library (11 Crops + 12 Diseases Atlas)
    # -------------------------------------------------------------------------
    lib_hdr, lib_search = st.columns([1.8, 1.0], vertical_alignment="bottom")
    with lib_hdr:
        st.markdown(
            f'<h2 style="font-size:20px;font-weight:800;color:{t["tx"]};margin-bottom:4px;">الموسوعة الزراعية وأطلس الأمراض</h2>'
            f'<p style="font-size:13.5px;color:{t["mu"]};margin:0;">قاعدة المحاصيل الاستراتيجية <bdi dir="ltr">(11)</bdi> ودليل كسر دورات الآفات <bdi dir="ltr">(12)</bdi></p>',
            unsafe_allow_html=True,
        )
    with lib_search:
        query = st.text_input("ابحث باسم المحصول أو المرض", placeholder="مثال: القمح، المن، الصدأ...", label_visibility="collapsed", key="s4_lib_search").strip().lower()

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
    lib_mode = st.segmented_control(
        "أقسام الموسوعة",
        options=["crops", "diseases"],
        default="crops",
        selection_mode="single",
        required=True,
        format_func=lambda k: "جدول المحاصيل المصرية (11)" if k == "crops" else "أطلس أمراض النبات بالصور (12)",
        label_visibility="collapsed",
        key="s4_lib_mode",
    )

    st.markdown('<div style="height: 14px;"></div>', unsafe_allow_html=True)
    if lib_mode == "crops":
        _render_crops_table(t, query)
    else:
        _render_diseases_atlas(t, query)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_crops_table(t: dict, query: str):
    """Render Botanical-styled searchable 11-crop database table."""
    rows = []
    profit_map = {"very_high": "مرتفع جداً", "high": "مرتفع", "medium": "متوسط", "low": "منخفض"}
    for _, c in CROPS_DATABASE.items():
        searchable = f"{c['name_ar']} {c['name_en']} {c.get('scientific_name', '')}".lower()
        if query and query not in searchable:
            continue

        is_bnf = c.get("biological_nitrogen_fixer", False)
        n_val = c.get("nitrogen_balance_kg_ha", 0)
        n_fg = t["ac"] if is_bnf else t["danger"]
        n_bg = t["ac_soft"] if is_bnf else t["danger_soft"]
        s_badge = _season_badge_html(c.get("season_type", ""), c.get("season_label_ar", ""), t)
        profit_ar = profit_map.get(c.get("profit_level", ""), c.get("profit_level", ""))

        rows.append(
            f'<tr>'
            f'<td><div style="font-weight:700;color:{t["tx"]};">{c["name_ar"]}</div>'
            f'<div style="font-size:12px;color:{t["mu"]};"><bdi dir="ltr">{c["name_en"]}</bdi></div></td>'
            f'<td>{s_badge}</td>'
            f'<td style="color:{t["mu"]};font-weight:600;"><bdi dir="ltr">{c["temp_opt_min"]:.0f}–{c["temp_opt_max"]:.0f}°C</bdi></td>'
            f'<td style="color:{t["tx"]};font-weight:600;"><bdi dir="ltr">{c["water_demand_mm"]:.0f} مم</bdi></td>'
            f'<td><span style="background:{n_bg};color:{n_fg};padding:2px 10px;border-radius:999px;font-size:12.5px;font-weight:700;"><bdi dir="ltr">{n_val:+.0f}</bdi></span></td>'
            f'<td><span style="background:{t["surface_alt"]};border:1px solid {t["bd"]};padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;">{profit_ar}</span></td>'
            f'</tr>'
        )

    if not rows:
        st.info("لا توجد محاصيل مطابقة لبحثك.")
        return

    st.markdown(
        f'<div class="gf-table-wrap"><table class="gf-table">'
        f'<thead><tr><th>المحصول</th><th>الموسم</th><th>الحرارة المثلى</th><th>الاحتياج المائي</th><th>ميزان N (كجم/هـ)</th><th>الربحية</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def _render_diseases_atlas(t: dict, query: str):
    """Render unified Botanical disease pathology photo cards."""
    diseases = get_all_diseases()
    crop_hosts = ["all"] + sorted({d["crop_id"] for d in diseases})
    host_labels = {"all": "جميع المحاصيل"}
    for d in diseases:
        host_labels[d["crop_id"]] = d["crop_name_ar"]

    selected_host = st.pills(
        "تصفية الأمراض حسب المحصول",
        options=crop_hosts,
        default="all",
        selection_mode="single",
        required=True,
        format_func=lambda k: host_labels.get(k, k),
        label_visibility="collapsed",
        key="s4_disease_host_pills",
    )

    filtered = []
    for d in diseases:
        if selected_host != "all" and d["crop_id"] != selected_host:
            continue
        searchable = f"{d['name_ar']} {d['name_en']} {d['crop_name_ar']} {d.get('scientific_name', '')}".lower()
        if query and query not in searchable:
            continue
        filtered.append(d)

    if not filtered:
        st.info("لا توجد أمراض مطابقة لهذا البحث.")
        return

    st.markdown('<div style="height: 14px;"></div>', unsafe_allow_html=True)

    for i in range(0, len(filtered), 2):
        cols = st.columns(2, gap="medium")
        for idx, d in enumerate(filtered[i : i + 2]):
            with cols[idx]:
                img_path = config.ROOT_DIR / "assets" / "diseases" / d["image_file"]
                thumb_uri = _get_disease_thumb_uri(str(img_path)) if img_path.exists() else ""
                breaks = "، ".join(d.get("breaking_crops", []))
                crop_obj = CROPS_DATABASE.get(d["crop_id"], {})
                s_badge = _season_badge_html(crop_obj.get("season_type", ""), d["crop_name_ar"], t)

                img_markup = (
                    f'<img src="{thumb_uri}" alt="{d["name_ar"]}" '
                    f'style="width:100%;height:210px;object-fit:cover;border-radius:12px;display:block;margin:12px 0;border:1px solid {t["bd"]};" />'
                    if thumb_uri else
                    f'<div style="width:100%;height:210px;border-radius:12px;background:{t["surface_alt"]};margin:12px 0;"></div>'
                )

                st.markdown(
                    f"""
                    <div class="gf-card" style="padding:18px 20px;margin-bottom:18px;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
                            <div>
                                <div style="font-size:16px;font-weight:800;color:{t['tx']};">{d['name_ar']}</div>
                                <div style="font-size:12px;color:{t['mu']};margin-top:2px;"><bdi dir="ltr">{d['scientific_name']}</bdi></div>
                            </div>
                            {s_badge}
                        </div>
                        {img_markup}
                        <p style="font-size:13px;line-height:1.65;margin:0 0 8px 0;color:{t['tx']};"><b style="color:{t['ac']};">الأعراض:</b> {d['symptoms_ar']}</p>
                        <p style="font-size:13px;line-height:1.65;margin:0 0 8px 0;color:{t['tx']};"><b style="color:{t['blue']};">كسر الدورة:</b> {d['pest_break_ar']}</p>
                        <div style="font-size:12.5px;color:{t['ac']};font-weight:700;margin-bottom:8px;">المحاصيل الكاسرة: {breaks}</div>
                        <div style="font-size:12px;color:{t['mu']};padding-top:8px;border-top:1px solid {t['bd']};">
                            شرط الرصد الفضائي: {d['nasa_trigger_condition']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
