"""
AgroOrbit - Governorates Matrix & Agronomic Library Views
Calm geospatial exploration (1/3 ranked hairline list + 2/3 single-hue choropleth map)
and clean searchable database of strategic Egyptian crops & plant pathologies.
"""

import base64
import io
import streamlit as st
from streamlit_folium import st_folium

from src import config
from src.design_system import get_tokens, svg_icon, season_bar_html
from src.crops_data import CROPS_DATABASE, get_all_diseases
from src.egypt_governorates import EGYPT_GOVERNORATES, EGYPT_REGIONS
from src.nasa_client import nasa_client
from src.governorate_analyzer import (
    CRITERIA_DEFINITIONS,
    rank_governorates,
    build_governorate_radar,
    build_orbital_folium_map,
)


def _crop_seasons_idx(season_type: str):
    """Map crop season key to 3-season bar active slot indices."""
    st_low = (season_type or "").lower()
    if "winter" in st_low:
        return [0]
    if "summer" in st_low:
        return [1]
    if "nili" in st_low:
        return [2]
    return [0, 1]


# =============================================================================
# 1. Governorates Matrix Page (Ranked List + 2/3 Choropleth Map + Detail Panel)
# =============================================================================
def render_governorates_page(dark_mode: bool = True):
    """Display 27 Egyptian governorates ranked with single-hue map synchronization."""
    t = get_tokens(dark_mode)
    st.markdown('<div class="ao-enter">', unsafe_allow_html=True)

    # Top Header + Criterion Filter
    hdr_col, crit_col, ref_col = st.columns([1.8, 1.4, 0.7], vertical_alignment="bottom")
    with hdr_col:
        st.markdown(
            f"""
            <h2 style="font-size:28px;margin-bottom:4px;">ترتيب المحافظات</h2>
            <p style="font-size:14px;color:{t['text_secondary']};margin:0;">
                تقييم المحافظات الـ 27 وفق قياسات التربة والمناخ من ناسا
            </p>
            """,
            unsafe_allow_html=True,
        )
    with crit_col:
        selected_crit = st.selectbox(
            "معيار الترتيب",
            options=list(CRITERIA_DEFINITIONS.keys()),
            format_func=lambda k: CRITERIA_DEFINITIONS[k]["title_ar"],
            key="gov_page_criterion",
        )
    with ref_col:
        if st.button("تحديث البيانات", key="gov_page_refresh", type="secondary", width="stretch"):
            with st.spinner("جاري تحديث قراءات المحافظات..."):
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

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    # 1/3 Slender Hairline Ranked List + 2/3 Focused Choropleth Map
    list_col, map_col = st.columns([1.0, 2.0], gap="large")

    with list_col:
        show_all = st.session_state.get("gov_show_all", False)
        visible_govs = ranked_govs if show_all else ranked_govs[:14]

        with st.container(key="gov_list_panel"):
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;font-size:12px;color:{t["text_muted"]};'
                f'padding:0 12px 8px 12px;border-bottom:1px solid {t["hairline"]};margin-bottom:6px;">'
                f'<span>المحافظة</span><span>المؤشر</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            for g in visible_govs:
                is_sel = (g["id"] == default_gov)
                btn_type = "primary" if is_sel else "secondary"
                row_lbl = f"{g['rank']}. {g['name_ar']}   —   {g['score']:.1f}%"
                if st.button(row_lbl, key=f"gov_row_{g['id']}", type=btn_type, width="stretch"):
                    st.session_state.inspect_gov_id = g["id"]
                    st.rerun()

        toggle_txt = "عرض أعلى 14" if show_all else "عرض الـ 27 محافظة كاملة"
        if st.button(toggle_txt, key="gov_toggle_all", type="secondary", width="stretch"):
            st.session_state.gov_show_all = not show_all
            st.rerun()

    with map_col:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px;padding:8px 14px;background:{t['bg_card']};border:1px solid {t['hairline']};border-radius:10px;">
                <span style="font-size:13px;color:{t['text_secondary']};font-weight:500;">تدرج الألوان على صور الأقمار الصناعية:</span>
                <div style="display:flex;align-items:center;gap:12px;font-size:12px;color:{t['text_secondary']};">
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span class="ao-dot" style="background:#10b981;width:9px;height:9px;"></span>ممتاز</span>
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span class="ao-dot" style="background:#0ea5e9;width:9px;height:9px;"></span>جيد جداً</span>
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span class="ao-dot" style="background:#f59e0b;width:9px;height:9px;"></span>متوسط</span>
                    <span style="display:inline-flex;align-items:center;gap:5px;"><span class="ao-dot" style="background:#ea580c;width:9px;height:9px;"></span>يحتاج تكيّف مائي</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        sel_record = next((g for g in ranked_govs if g["id"] == default_gov), ranked_govs[0])
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
        st_folium(gov_map, height=510, use_container_width=True, key="gov_matrix_map")

    # Selected Governorate Detail Drawer / Card below split
    sel_record = next((g for g in ranked_govs if g["id"] == default_gov), ranked_govs[0])
    ind = sel_record.get("indices", {})
    soil_ar = config.SOIL_TYPES.get(sel_record.get("dominant_soil", ""), {}).get("name_ar", sel_record.get("dominant_soil", ""))
    reg_ar = EGYPT_REGIONS.get(sel_record.get("region", ""), {}).get("name_ar", sel_record.get("region", ""))
    crops_ar = "، ".join(CROPS_DATABASE[c]["name_ar"] for c in sel_record.get("main_crops", []) if c in CROPS_DATABASE)

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="font-size:18px;margin-bottom:12px;">تفاصيل محافظة {sel_record["name_ar"]}</h3>', unsafe_allow_html=True)

    d_info, d_radar = st.columns([1.3, 1.0], gap="large", vertical_alignment="center")
    with d_info:
        st.markdown(
            f"""
            <div class="ao-table-wrap">
                <table class="ao-table">
                    <tbody>
                        <tr><td style="color:{t['text_muted']};width:150px;">الترتيب الوطني</td><td class="ao-mono" style="color:{t['accent']};font-weight:500;">#{sel_record['rank']} / 27 ({sel_record['score']:.1f}%)</td></tr>
                        <tr><td style="color:{t['text_muted']};">الإقليم</td><td>{reg_ar}</td></tr>
                        <tr><td style="color:{t['text_muted']};">التربة السائدة</td><td>{soil_ar}</td></tr>
                        <tr><td style="color:{t['text_muted']};">متوسط الحرارة</td><td class="ao-mono">{ind.get('avg_temp_c', 23.0)} °C</td></tr>
                        <tr><td style="color:{t['text_muted']};">رطوبة التربة</td><td class="ao-mono">{ind.get('soil_moisture_score', 45.0)}%</td></tr>
                        <tr><td style="color:{t['text_muted']};">أبرز المحاصيل</td><td>{crops_ar or '-'}</td></tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
        if st.button(f"ابدأ تحليل لأرض في {sel_record['name_ar']}", key="gov_analyze_cta", type="primary", width="content"):
            st.session_state.selected_gov_id = sel_record["id"]
            st.session_state.latitude = sel_record["lat"]
            st.session_state.longitude = sel_record["lon"]
            st.session_state.soil_type = sel_record.get("dominant_soil", st.session_state.soil_type)
            st.session_state.page = "wizard"
            st.session_state.wizard_step = 2
            st.rerun()

    with d_radar:
        radar_fig = build_governorate_radar(sel_record, dark_mode=dark_mode)
        st.plotly_chart(radar_fig, theme=None, width="stretch")

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 2. Knowledge Library Page (Crops Table & Visual Pathology Atlas)
# =============================================================================
def render_library_page(dark_mode: bool = True):
    """Display clean searchable crops reference and plant pathology catalog."""
    t = get_tokens(dark_mode)
    st.markdown('<div class="ao-enter">', unsafe_allow_html=True)

    h_col, s_col = st.columns([1.8, 1.0], vertical_alignment="bottom")
    with h_col:
        st.markdown(
            f"""
            <h2 style="font-size:28px;margin-bottom:4px;">المكتبة الزراعية</h2>
            <p style="font-size:14px;color:{t['text_secondary']};margin:0;">
                قاعدة بيانات المحاصيل المصرية الـ 11 ودليل تشخيص وكسر دورات الأمراض
            </p>
            """,
            unsafe_allow_html=True,
        )
    with s_col:
        query = st.text_input("بحث", placeholder="ابحث باسم المحصول أو المرض", label_visibility="collapsed", key="lib_search").strip().lower()

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    view_mode = st.segmented_control(
        "أقسام المكتبة",
        options=["crops", "diseases"],
        default="crops",
        selection_mode="single",
        required=True,
        format_func=lambda k: "المحاصيل" if k == "crops" else "الأمراض والآفات",
        label_visibility="collapsed",
        key="lib_view_mode",
    )

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    if view_mode == "crops":
        _render_library_crops(t, dark_mode, query)
    else:
        _render_library_diseases(t, dark_mode, query)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_library_crops(t: dict, dark_mode: bool, query: str):
    """Render clean bordered table of Egypt's strategic crops."""
    rows = []
    for cid, c in CROPS_DATABASE.items():
        searchable = f"{c['name_ar']} {c['name_en']} {c.get('scientific_name', '')}".lower()
        if query and query not in searchable:
            continue

        is_bnf = c.get("biological_nitrogen_fixer", False)
        n_val = c.get("nitrogen_balance_kg_ha", 0)
        n_color = t["positive"] if is_bnf else t["negative"]
        n_bg = t["accent_tint"] if is_bnf else t["negative_tint"]
        s_bars = season_bar_html(_crop_seasons_idx(c.get("season_type", "")), dark_mode=dark_mode)
        profit_map = {"very_high": "مرتفع جداً", "high": "مرتفع", "medium": "متوسط", "low": "منخفض"}
        profit_ar = profit_map.get(c.get("profit_level", ""), c.get("profit_level", ""))

        rows.append(
            f'<tr>'
            f'<td><div style="font-weight:500;color:{t["text_primary"]};">{c["name_ar"]}</div>'
            f'<div style="font-size:12px;color:{t["text_muted"]};"><bdi dir="ltr">{c["name_en"]}</bdi></div></td>'
            f'<td>{s_bars} <span style="font-size:12px;color:{t["text_secondary"]};margin-inline-start:6px;">{c["season_label_ar"]}</span></td>'
            f'<td class="ao-mono" style="color:{t["text_secondary"]};">{c["temp_opt_min"]:.0f}–{c["temp_opt_max"]:.0f}°C</td>'
            f'<td class="ao-mono" style="color:{t["text_secondary"]};">{c["water_demand_mm"]:.0f} مم</td>'
            f'<td><span class="ao-mono" style="background:{n_bg};color:{n_color};padding:2px 8px;border-radius:6px;font-size:12.5px;"><bdi dir="ltr">{n_val:+.0f}</bdi></span></td>'
            f'<td><span class="ao-tag">{profit_ar}</span></td>'
            f'</tr>'
        )

    if not rows:
        st.info("لا توجد نتائج مطابقة لبحثك.")
        return

    st.markdown(
        f'<div class="ao-table-wrap"><table class="ao-table">'
        f'<thead><tr><th>المحصول</th><th>الموسم</th><th>الحرارة المثلى</th><th>الاحتياج المائي</th><th>ميزان N (كجم/هـ)</th><th>الربحية</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _get_disease_thumb_uri(img_path_str: str) -> str:
    """Return compact JPEG base64 thumbnail URI so unified cards align with uniform photo height."""
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


def _render_library_diseases(t: dict, dark_mode: bool, query: str):
    """Render clean plant pathology catalog cards as single unified visual units."""
    diseases = get_all_diseases()

    crop_hosts = ["all"] + sorted({d["crop_id"] for d in diseases})
    host_labels = {"all": "الكل"}
    for d in diseases:
        host_labels[d["crop_id"]] = d["crop_name_ar"]

    selected_host = st.pills(
        "تصفية حسب المحصول",
        options=crop_hosts,
        default="all",
        selection_mode="single",
        required=True,
        format_func=lambda k: host_labels.get(k, k),
        label_visibility="collapsed",
        key="lib_disease_host_pills",
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
        st.info("لا توجد أمراض مطابقة لهذا الاختيار.")
        return

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    for i in range(0, len(filtered), 2):
        cols = st.columns(2, gap="medium")
        for idx, d in enumerate(filtered[i : i + 2]):
            with cols[idx]:
                img_path = config.ROOT_DIR / "assets" / "diseases" / d["image_file"]
                thumb_uri = _get_disease_thumb_uri(str(img_path)) if img_path.exists() else ""
                breaks = "، ".join(d.get("breaking_crops", []))
                crop_obj = CROPS_DATABASE.get(d["crop_id"], {})
                s_bar = season_bar_html(_crop_seasons_idx(crop_obj.get("season_type", "")), dark_mode=dark_mode)

                img_markup = (
                    f'<img src="{thumb_uri}" alt="{d["name_ar"]}" '
                    f'style="width:100%;height:210px;object-fit:cover;border-radius:8px;display:block;margin:12px 0;border:1px solid {t["hairline"]};" />'
                    if thumb_uri else
                    f'<div style="width:100%;height:210px;border-radius:8px;background:{t["bg_raised"]};margin:12px 0;"></div>'
                )

                st.markdown(
                    f"""
                    <div class="ao-card" style="padding:18px 20px;margin-bottom:20px;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
                            <div>
                                <div style="font-size:16px;font-weight:500;color:{t['text_primary']};">{d['name_ar']}</div>
                                <div style="font-size:12px;color:{t['text_muted']};margin-top:2px;"><bdi dir="ltr">{d['scientific_name']}</bdi></div>
                            </div>
                            <span class="ao-tag">{s_bar} <span>{d['crop_name_ar']}</span></span>
                        </div>
                        {img_markup}
                        <p style="font-size:13px;line-height:1.65;margin:0 0 8px 0;"><b style="color:{t['text_primary']};font-weight:500;">الأعراض:</b> {d['symptoms_ar']}</p>
                        <p style="font-size:13px;line-height:1.65;margin:0 0 8px 0;"><b style="color:{t['text_primary']};font-weight:500;">كسر الدورة:</b> {d['pest_break_ar']}</p>
                        <div style="font-size:12px;color:{t['accent']};margin-bottom:8px;">المحاصيل الكاسرة: {breaks}</div>
                        <div style="font-size:12px;color:{t['text_muted']};padding-top:8px;border-top:1px solid {t['hairline']};">
                            شرط الرصد الفضائي: {d['nasa_trigger_condition']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
