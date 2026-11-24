"""
AgroOrbit - Results View (4 Focused Sub-Tabs)
  1. Plan (Rotation Ring + 3-Season Bar + Alternative Plans + Closed Comparison)
  2. Weather & Risks (4 KPI Stats + Primary 10-Day Chart + Early Warnings + What-If)
  3. Savings ROI (Acreage Sync + 3 KPI Stats + Single Accent Bar Chart + Cost Table)
  4. Report & Voice (Egyptian Colloquial Audio + A4 PDF Download + Scientific Note)
"""

from typing import Dict, Any
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src.design_system import (
    get_tokens,
    svg_icon,
    season_bar_html,
    build_rotation_ring_svg,
    get_crop_ring_color,
)
from src.economics_engine import calculate_farm_economic_roi
from src.climate_alerts import evaluate_climate_hazards
from src.voice_advisor import generate_voice_script, get_agro_voice_audio
from src.pdf_generator import (
    REPORTS_CACHE_DIR,
    generate_advisory_pdf,
    build_advisory_html_report,
)


def _clean_tag_title(raw_tag: str) -> str:
    """Strip legacy strategy numbering prefixes cleanly."""
    if ":" in raw_tag:
        return raw_tag.split(":", 1)[1].strip()
    return raw_tag.strip()


def render_results_page(dark_mode: bool = True):
    """Render top context bar, 4-tab switcher, and active results sub-view."""
    t = get_tokens(dark_mode)
    res = st.session_state.get("strategies_result")

    if not res:
        st.info("لم يتم حساب خطة بعد. ابدأ بتحديد بيانات أرضك أولاً.")
        if st.button("ابدأ التحليل", key="res_fallback_start", type="primary"):
            st.session_state.page = "wizard"
            st.session_state.wizard_step = 1
            st.rerun()
        return

    meta = res.get("metadata", {})
    gov_ar = meta.get("governorate_ar", "موقع مخصص")
    soil_ar = meta.get("soil_name_ar", "").split("(")[0].strip()
    prev_ar = meta.get("previous_crop_name_ar", "")
    area = float(st.session_state.get("farm_area", meta.get("area_feddan", 5.0)))

    st.markdown('<div class="ao-enter">', unsafe_allow_html=True)

    # Compact Context Summary Strip + Edit Action
    ctx_col, edit_col = st.columns([4, 1], vertical_alignment="center")
    with ctx_col:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;font-size:14px;color:{t['text_secondary']};">
                <span style="color:{t['text_primary']};font-weight:500;">{gov_ar}</span>
                <span>·</span>
                <span>تربة {soil_ar}</span>
                <span>·</span>
                <span>بعد {prev_ar}</span>
                <span>·</span>
                <span><bdi class="ao-num">{area:.1f}</bdi> فدان</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with edit_col:
        with st.container(horizontal=True, horizontal_alignment="right"):
            if st.button("تعديل البيانات", key="res_edit_wizard", type="secondary", width="content"):
                st.session_state.page = "wizard"
                st.session_state.wizard_step = 1
                st.rerun()

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    # 4 Clean Segmented Tabs
    tab_labels = {
        "plan": "الخطة",
        "weather": "الطقس والمخاطر",
        "savings": "التوفير",
        "report": "التقرير",
    }
    default_tab = st.session_state.get("results_tab", "plan")
    active_tab = st.segmented_control(
        "أقسام النتائج",
        options=list(tab_labels.keys()),
        default=default_tab if default_tab in tab_labels else "plan",
        selection_mode="single",
        required=True,
        format_func=lambda k: tab_labels[k],
        label_visibility="collapsed",
        key="res_tab_control",
    )
    st.session_state.results_tab = active_tab

    st.markdown(f'<hr style="margin: 16px 0 24px 0 !important; border-color:{t["hairline"]};" />', unsafe_allow_html=True)

    if active_tab == "plan":
        _render_tab_plan(res, t, dark_mode, area)
    elif active_tab == "weather":
        _render_tab_weather(res, t, dark_mode)
    elif active_tab == "savings":
        _render_tab_savings(res, t, dark_mode, area)
    else:
        _render_tab_report(res, t, dark_mode)

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# Tab 1: Plan (Rotation Ring + 3-Season Rows + Alternatives + Closed Matrix)
# =============================================================================
def _render_tab_plan(res: Dict[str, Any], t: Dict[str, str], dark_mode: bool, area: float):
    """Display active strategy with Crop Rotation Ring and season schedule."""
    all_keys = ["strategy_2_soil_health", "strategy_3_water_resilience", "strategy_1_baseline"]
    prio = st.session_state.get("priority_preset", "soil")
    recommended_key = "strategy_3_water_resilience" if prio == "water" else "strategy_2_soil_health"

    active_key = st.session_state.get("active_strategy_key")
    if active_key not in all_keys:
        active_key = recommended_key
        st.session_state.active_strategy_key = active_key

    strat = res.get(active_key, {})
    timeline = strat.get("timeline", [])
    metrics = strat.get("metrics", {})

    # Calculate concrete financial and urea bag numbers for consistency with Savings tab
    roi = calculate_farm_economic_roi(
        area_feddan=area,
        strat_baseline=res.get("strategy_1_baseline", {}),
        strat_soil=res.get("strategy_2_soil_health", {}),
        strat_water=res.get("strategy_3_water_resilience", {}),
    )
    if active_key == "strategy_2_soil_health":
        fin_gain = roi["strategy_2_soil_health"]["total_financial_gain_egp"]
        urea_bags = roi["strategy_2_soil_health"]["urea_bags_saved"]
        water_saved = roi["strategy_2_soil_health"]["water_saved_m3"]
    elif active_key == "strategy_3_water_resilience":
        fin_gain = roi["strategy_3_water_resilience"]["total_financial_gain_egp"]
        urea_bags = roi["strategy_3_water_resilience"]["urea_bags_saved"]
        water_saved = roi["strategy_3_water_resilience"]["water_saved_m3"]
    else:
        fin_gain = 0.0
        urea_bags = 0.0
        water_saved = 0.0

    is_rec = (active_key == recommended_key)
    tag_badge = (
        f'<span class="ao-tag ao-tag-accent">الخطة المقترحة لأولويتك</span>'
        if is_rec else
        f'<span class="ao-tag">خطة بديلة</span>'
    )

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
            <h2 style="font-size:26px;">{_clean_tag_title(strat.get('tag_ar', ''))}</h2>
            {tag_badge}
        </div>
        <p style="font-size:15px;color:{t['text_secondary']};margin-bottom:24px;">
            {strat.get('summary_ar', '')}
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Center ring hero metric adapts cleanly to the viewed strategy
    if active_key == "strategy_1_baseline":
        center_val = f"{metrics.get('total_water_mm', 0):.0f}"
        center_lbl = "ملم إجمالي الري"
    else:
        center_val = f"{water_saved:,.0f}"
        center_lbl = "م³ توفير مياه"

    season_colors = [
        get_crop_ring_color(step.get("crop", {}).get("id", ""), i)
        for i, step in enumerate(timeline)
    ]

    ring_col, table_col = st.columns([1.0, 1.2], vertical_alignment="center", gap="large")

    with ring_col:
        ring_svg = build_rotation_ring_svg(
            timeline=timeline,
            center_value=center_val,
            center_label=center_lbl,
            dark_mode=dark_mode,
            size_px=264,
            show_legend=True,
        )
        st.markdown(
            f'<div class="ao-card" style="padding: 28px 20px;">{ring_svg}</div>',
            unsafe_allow_html=True,
        )

    with table_col:
        season_short = ["شتوي", "صيفي", "نيلي"]
        rows_html = []
        for idx, step in enumerate(timeline):
            crop = step.get("crop", {})
            c_name = crop.get("name_ar", "")
            c_water = crop.get("water_demand_mm", 0)
            c_n = crop.get("nitrogen_balance_kg_ha", 0)
            n_color = t["positive"] if c_n > 0 else t["negative"] if c_n < 0 else t["text_muted"]
            n_str = f"{c_n:+.0f} كجم N"
            bar_html = season_bar_html([idx], dark_mode=dark_mode, season_colors=season_colors)

            rows_html.append(
                f'<tr>'
                f'<td style="color:{t["text_muted"]};font-size:13px;width:64px;">{season_short[idx] if idx < 3 else ""}</td>'
                f'<td style="font-weight:500;color:{t["text_primary"]};">{c_name}</td>'
                f'<td>{bar_html}</td>'
                f'<td style="text-align:end;"><span class="ao-mono" style="color:{t["text_secondary"]};">{c_water:.0f}</span> <span style="font-size:12px;color:{t["text_muted"]};">ملم</span></td>'
                f'<td style="text-align:end;"><span class="ao-mono" style="color:{n_color};">{n_str}</span></td>'
                f'</tr>'
            )

        summary_footer = ""
        if active_key != "strategy_1_baseline":
            summary_footer = (
                f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:16px;border-top:1px solid {t["hairline"]};background:{t["bg_deepest"]};">'
                f'<div><div style="font-size:12px;color:{t["text_muted"]};">توفير يوريا</div><div class="ao-num" style="font-size:16px;font-weight:500;color:{t["text_primary"]};margin-top:4px;">{urea_bags:.1f} شكارة</div></div>'
                f'<div><div style="font-size:12px;color:{t["text_muted"]};">الوفر المالي</div><div class="ao-num" style="font-size:16px;font-weight:500;color:{t["accent"]};margin-top:4px;">{fin_gain:,.0f} ج</div></div>'
                f'<div><div style="font-size:12px;color:{t["text_muted"]};">كسر الآفات</div><div class="ao-num" style="font-size:16px;font-weight:500;color:{t["text_primary"]};margin-top:4px;">{metrics.get("pest_break_efficiency_pct", 0):.0f}%</div></div>'
                f'</div>'
            )
        else:
            summary_footer = (
                f'<div style="padding:14px 16px;border-top:1px solid {t["hairline"]};background:{t["bg_deepest"]};font-size:13px;color:{t["text_secondary"]};">'
                f'يمثل خط الأساس التقليدي للمقارنة. كفاءة كسر الآفات: <bdi class="ao-num">{metrics.get("pest_break_efficiency_pct", 0):.0f}%</bdi>'
                f'</div>'
            )

        st.markdown(
            f'<div class="ao-table-wrap">'
            f'<table class="ao-table">'
            f'<thead><tr><th>الموسم</th><th>المحصول</th><th>التتابع</th><th style="text-align:end;">المياه</th><th style="text-align:end;">النيتروجين</th></tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody>'
            f'</table>'
            f'{summary_footer}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Alternative Strategies Section
    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="font-size:16px;margin-bottom:12px;">خطط بديلة</h3>', unsafe_allow_html=True)

    alt_keys = [k for k in all_keys if k != active_key]
    alt_cols = st.columns(2, gap="medium")
    for col, alt_k in zip(alt_cols, alt_keys):
        alt_s = res.get(alt_k, {})
        alt_tl = alt_s.get("timeline", [])
        alt_colors = [get_crop_ring_color(s.get("crop", {}).get("id", ""), i) for i, s in enumerate(alt_tl)]
        crop_chain = " · ".join(s.get("crop", {}).get("name_ar", "") for s in alt_tl)
        alt_bars = season_bar_html([0, 1, 2], dark_mode=dark_mode, season_colors=alt_colors)
        alt_water_pct = alt_s.get("metrics", {}).get("water_savings_pct", 0.0)

        with col:
            st.markdown(
                f"""
                <div class="ao-card-compact" style="margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px;">
                        <span style="font-size:15px;font-weight:500;color:{t['text_primary']};">{_clean_tag_title(alt_s.get('tag_ar', ''))}</span>
                        {alt_bars}
                    </div>
                    <div style="font-size:13px;color:{t['text_secondary']};margin-bottom:6px;">{crop_chain}</div>
                    <div style="font-size:12px;color:{t['text_muted']};">توفير المياه: <span class="ao-mono">+{alt_water_pct:.1f}%</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"عرض خطة {_clean_tag_title(alt_s.get('tag_ar', ''))}", key=f"alt_btn_{alt_k}", type="secondary", width="stretch"):
                st.session_state.active_strategy_key = alt_k
                st.rerun()

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    # Collapsed Comparison Table & Disclosure Expanders
    with st.expander("مقارنة الخطط الثلاث جنباً إلى جنب", expanded=False):
        matrix = res.get("comparison_matrix", [])
        m_rows = []
        for row in matrix:
            m_rows.append(
                f'<tr>'
                f'<td style="font-weight:500;color:{t["text_primary"]};">{row["criterion_ar"]}</td>'
                f'<td style="color:{t["text_secondary"]};">{row["strategy_1"]}</td>'
                f'<td style="color:{t["accent"]};">{row["strategy_2"]}</td>'
                f'<td style="color:{t["text_primary"]};">{row["strategy_3"]}</td>'
                f'</tr>'
            )
        st.markdown(
            f'<div class="ao-table-wrap">'
            f'<table class="ao-table">'
            f'<thead><tr><th>المعيار</th><th>الوضع الحالي</th><th>صحة التربة</th><th>التكيف المائي</th></tr></thead>'
            f'<tbody>{"".join(m_rows)}</tbody>'
            f'</table></div>',
            unsafe_allow_html=True,
        )

    with st.expander("التحليل العلمي وحدود الرصد لهذه الخطة", expanded=False):
        st.markdown(f"**سبب الاختيار**\n\n{strat.get('why_suggested', '')}")
        st.markdown("---")
        st.markdown(f"**الأدلة من قياسات ناسا**\n\n{strat.get('evidence', '')}")
        st.markdown("---")
        st.markdown(f"**الفوائد المتوقعة**\n\n{strat.get('benefits', '')}")
        st.markdown("---")
        st.markdown(f"**حدود البيانات والمراجعة الحقلية**\n\n{strat.get('information_gaps', '')}\n\n{strat.get('risks_and_agronomist_review', '')}")


# =============================================================================
# Tab 2: Weather & Risks (4 KPI Cards + 1 Primary Chart + Alerts + What-If)
# =============================================================================
def _render_tab_weather(res: Dict[str, Any], t: Dict[str, str], dark_mode: bool):
    """Render clean satellite telemetry cards, 1 primary 10-day chart, and hazard alerts."""
    telemetry = st.session_state.get("telemetry", {})
    indices = telemetry.get("indices", {})
    is_live = telemetry.get("is_live", False)
    confidence = telemetry.get("confidence_score", 90.0)

    status_dot = t["positive"] if is_live else t["warning"]
    status_txt = "اتصال حي مع NASA POWER" if is_live else "بيانات مناخية معايرة"
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
            <span class="ao-tag"><span class="ao-dot" style="background:{status_dot};"></span>{status_txt}</span>
            <span style="font-size:13px;color:{t['text_muted']};">موثوقية الرصد: <span class="ao-mono" style="color:{t['text_primary']};">{confidence:.1f}%</span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Compact Stat Cards (Numbers only, equal height)
    c1, c2, c3, c4 = st.columns(4, gap="small")
    stats = [
        ("متوسط الحرارة", f"{indices.get('avg_temp_c', 22.0)}°C", f"قصوى {indices.get('max_temp_c')} · دنيا {indices.get('min_temp_c')}"),
        ("رطوبة التربة (SMAP)", f"{indices.get('soil_moisture_score', 45.0)}%", f"جذرية {indices.get('avg_root_zone_moisture')} · سطحية {indices.get('avg_surface_moisture')}"),
        ("الأمطار (GPM)", f"{indices.get('total_precip_mm', 0.0)} مم", f"الرطوبة النسبية {indices.get('avg_relative_humidity')}%"),
        ("الإشعاع الشمسي", f"{indices.get('avg_solar_radiation_mj', 18.5)} MJ", f"أيام إجهاد حراري: {indices.get('extreme_heat_days', 0)}"),
    ]
    for col, (lbl, val, sub) in zip((c1, c2, c3, c4), stats):
        with col:
            st.markdown(
                f'<div class="ao-stat-card">'
                f'<div class="ao-stat-label">{lbl}</div>'
                f'<div class="ao-stat-val"><bdi dir="ltr">{val}</bdi></div>'
                f'<div class="ao-stat-meta">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # One Primary Wide Chart (2/3) + Narrow Alert Feed (1/3)
    chart_col, alert_col = st.columns([1.65, 1.0], gap="large")

    with chart_col:
        st.markdown(f'<h3 style="font-size:16px;margin-bottom:12px;">قياسات الطقس اليومية لآخر 10 أيام</h3>', unsafe_allow_html=True)
        params = telemetry.get("cleaned_parameters", {})
        t2m = params.get("T2M", {})
        t2m_max = params.get("T2M_MAX", {})
        t2m_min = params.get("T2M_MIN", {})
        rain = params.get("PRECTOTCORR", {})
        rh = params.get("RH2M", {})
        gwet = params.get("GWETROOT", {})

        dates = sorted(t2m.keys())[-10:]
        if dates:
            x_dates = [f"{d[4:6]}-{d[6:]}" if len(d) == 8 else d for d in dates]
            y_temps = [round(t2m.get(d, 22.0), 1) for d in dates]
            y_rains = [round(rain.get(d, 0.0), 2) for d in dates]

            grid_c = "rgba(237,237,237,0.06)" if dark_mode else "rgba(23,23,23,0.06)"
            bar_muted = "rgba(161,161,166,0.28)" if dark_mode else "rgba(82,82,82,0.22)"

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=x_dates, y=y_rains, name="الأمطار (مم)", yaxis="y2",
                marker=dict(color=bar_muted),
            ))
            fig.add_trace(go.Scatter(
                x=x_dates, y=y_temps, mode="lines+markers", name="الحرارة (°C)",
                line=dict(color=t["accent"], width=2.5),
                marker=dict(color=t["accent"], size=6),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Sans Arabic, sans-serif", color=t["text_secondary"]),
                xaxis=dict(
                    showgrid=False,
                    automargin=True,
                    tickfont=dict(family="IBM Plex Mono, monospace", size=11, color=t["text_muted"]),
                ),
                yaxis=dict(
                    title=dict(text="°C", font=dict(size=11, color=t["text_muted"])),
                    gridcolor=grid_c,
                    automargin=True,
                    tickfont=dict(family="IBM Plex Mono, monospace", size=11, color=t["text_muted"]),
                ),
                yaxis2=dict(
                    overlaying="y", side="right", showgrid=False,
                    automargin=True,
                    tickfont=dict(family="IBM Plex Mono, monospace", size=10, color=t["text_muted"]),
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12)),
                margin=dict(l=48, r=48, t=36, b=28),
                height=310,
            )
            st.plotly_chart(fig, theme=None, width="stretch")

            with st.expander("عرض الجدول اليومي الكامل", expanded=False):
                t_rows = []
                for d in dates:
                    fd = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else d
                    t_rows.append(
                        f'<tr>'
                        f'<td class="ao-mono" style="color:{t["text_primary"]};">{fd}</td>'
                        f'<td class="ao-mono">{t2m.get(d, 0):.1f}°</td>'
                        f'<td class="ao-mono">{t2m_max.get(d, 0):.1f}° / {t2m_min.get(d, 0):.1f}°</td>'
                        f'<td class="ao-mono">{rain.get(d, 0):.1f} مم</td>'
                        f'<td class="ao-mono">{rh.get(d, 0):.0f}%</td>'
                        f'<td class="ao-mono">{round(gwet.get(d, 0.4) * 100, 0):.0f}%</td>'
                        f'</tr>'
                    )
                st.markdown(
                    f'<div class="ao-table-wrap"><table class="ao-table">'
                    f'<thead><tr><th>التاريخ</th><th>المتوسط</th><th>قصوى / دنيا</th><th>الأمطار</th><th>الرطوبة</th><th>رطوبة الجذور</th></tr></thead>'
                    f'<tbody>{"".join(t_rows)}</tbody></table></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("لا توجد قراءات يومية مسجلة لهذه الإحداثيات.")

    with alert_col:
        st.markdown(f'<h3 style="font-size:16px;margin-bottom:12px;">الإنذار المبكر والمخاطر</h3>', unsafe_allow_html=True)
        sim_scenario = st.selectbox(
            "وضع الرصد",
            options=["live", "heatwave_extreme", "frost_shock", "fungal_bloom", "flash_drought"],
            format_func=lambda x: {
                "live": "الرصد الحي الفعلي",
                "heatwave_extreme": "اختبار موجة حر (41°C)",
                "frost_shock": "اختبار صقيع ليلي (2.5°C)",
                "fungal_bloom": "اختبار نشاط فطريات (رطوبة 86%)",
                "flash_drought": "اختبار جفاف جذور (SMAP 0.20)",
            }[x],
            label_visibility="collapsed",
            key="hazard_sim_select",
        )

        active_tel = telemetry
        if sim_scenario != "live":
            active_tel = dict(telemetry)
            idx_copy = dict(indices)
            if sim_scenario == "heatwave_extreme":
                idx_copy.update({"avg_temp_c": 36.5, "max_temp_c": 41.0, "extreme_heat_days": 4})
            elif sim_scenario == "frost_shock":
                idx_copy.update({"min_temp_c": 2.5, "avg_temp_c": 11.0})
            elif sim_scenario == "fungal_bloom":
                idx_copy.update({"avg_relative_humidity_pct": 86.0, "avg_temp_c": 21.0, "avg_surface_moisture": 0.65})
            elif sim_scenario == "flash_drought":
                idx_copy.update({"avg_root_zone_moisture": 0.20, "soil_moisture_score": 22.0})
            active_tel["indices"] = idx_copy

        alerts = evaluate_climate_hazards(
            active_tel,
            previous_crop_id=st.session_state.get("previous_crop", "maize"),
            soil_type=st.session_state.get("soil_type", "clay"),
        )

        for a in alerts:
            sev = a["severity"]
            dot_c = t["negative"] if sev == "critical" else t["warning"] if sev == "warning" else t["positive"]
            sev_txt = "حرج" if sev == "critical" else "تنبيه" if sev == "warning" else "مستقر"
            acts = "".join(f"<li style='margin-bottom:4px;'>{x}</li>" for x in a.get("urgent_actions", []))

            st.markdown(
                f"""
                <div class="ao-card-compact" style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px;">
                        <span style="font-size:14px;font-weight:500;color:{t['text_primary']};">{a['title_ar']}</span>
                        <span class="ao-tag"><span class="ao-dot" style="background:{dot_c};"></span>{sev_txt}</span>
                    </div>
                    <p style="font-size:13px;color:{t['text_secondary']};margin:0 0 8px 0;">{a['trigger_data']}</p>
                    <div style="font-size:13px;color:{t['text_secondary']};">
                        <ol style="margin:0;padding-inline-start:18px;">{acts}</ol>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    with st.expander("محاكاة تغير المناخ (ماذا لو)", expanded=False):
        sc1, sc2 = st.columns(2)
        with sc1:
            t_shift = st.slider("تغير درجة الحرارة (°C)", -4.0, 5.0, 0.0, 0.5, key="whatif_temp")
        with sc2:
            r_shift = st.slider("تغير كمية الأمطار (%)", -50, 50, 0, 10, key="whatif_rain")

        if t_shift != 0.0 or r_shift != 0:
            sim_t = float(indices.get("avg_temp_c", 22.0)) + t_shift
            advice = (
                "يرجح التحول إلى خطة التكيف المائي لتفادي إجهاد الإزهار."
                if t_shift > 1.5
                else "تبقى الدورات المقترحة ضمن النطاق الحراري الآمن."
            )
            st.markdown(
                f'<div class="ao-card-compact" style="margin-top:8px;">'
                f'<span style="color:{t["text_primary"]};font-size:14px;">عند متوسط حرارة <bdi class="ao-num">{sim_t:.1f}°C</bdi>: {advice}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# =============================================================================
# Tab 3: Savings ROI (Acreage Sync + 3 KPI Cards + 1 Chart + Breakdown Table)
# =============================================================================
def _render_tab_savings(res: Dict[str, Any], t: Dict[str, str], dark_mode: bool, area: float):
    """Display water, fertilizer, and cash ROI per feddan cleanly."""
    ctrl1, ctrl2 = st.columns([1.2, 1.4], vertical_alignment="bottom")
    with ctrl1:
        farm_area = st.number_input(
            "مساحة الأرض (فدان)",
            min_value=0.5, max_value=500.0, value=float(area), step=0.5, format="%.1f",
            key="roi_area_sync",
        )
        st.session_state.farm_area = farm_area
    with ctrl2:
        strat_focus = st.segmented_control(
            "اختر الخطة للحساب",
            options=["soil_health", "water_resilience"],
            default="soil_health",
            selection_mode="single",
            required=True,
            format_func=lambda x: "صحة التربة والنيتروجين" if x == "soil_health" else "التكيف المائي",
            key="roi_strat_seg",
        )

    with st.expander("تعديل أسعار اليوريا وتكلفة الري (اختياري)", expanded=False):
        p1, p2, p3 = st.columns(3)
        with p1:
            urea_price = st.number_input("سعر شكارة اليوريا 50 كجم (جنيه)", 250.0, 2000.0, 750.0, 25.0, key="roi_urea_p")
        with p2:
            pump_cost = st.number_input("تكلفة ضخ متر المياه (جنيه/م³)", 0.4, 5.0, 1.1, 0.1, key="roi_pump_p")
        with p3:
            pest_save = st.number_input("وفر المبيدات للفدان (جنيه)", 200.0, 2500.0, 650.0, 50.0, key="roi_pest_p")

    roi = calculate_farm_economic_roi(
        area_feddan=farm_area,
        strat_baseline=res.get("strategy_1_baseline", {}),
        strat_soil=res.get("strategy_2_soil_health", {}),
        strat_water=res.get("strategy_3_water_resilience", {}),
        urea_bag_price_egp=urea_price,
        pumping_cost_m3_egp=pump_cost,
        pesticide_saving_per_feddan_egp=pest_save,
    )
    chosen = roi["strategy_2_soil_health"] if strat_focus == "soil_health" else roi["strategy_3_water_resilience"]

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    # 3 Clean Stat Cards (Numbers only)
    k1, k2, k3 = st.columns(3, gap="medium")
    kpis = [
        ("الوفر المالي التراكمي", f"{chosen['total_financial_gain_egp']:,.0f} ج", f"معدل {chosen['financial_gain_per_feddan_egp']:,.0f} جنيه / فدان"),
        ("مياه الري الموفرة", f"{chosen['water_saved_m3']:,.0f} م³", f"+{chosen['water_saved_pct']}% مقارنة بالوضع الحالي"),
        ("شكاير اليوريا الموفرة", f"{chosen['urea_bags_saved']:,.1f} شكارة", f"تثبيت حيوي · خفض {chosen['co2_offset_tons']:.2f} طن CO₂"),
    ]
    for col, (lbl, val, meta) in zip((k1, k2, k3), kpis):
        with col:
            st.markdown(
                f'<div class="ao-stat-card">'
                f'<div class="ao-stat-label">{lbl}</div>'
                f'<div class="ao-stat-val"><bdi dir="ltr">{val}</bdi></div>'
                f'<div class="ao-stat-meta">{meta}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # One Primary Chart (Water Comparison) + Narrow Breakdown Table
    c_chart, c_table = st.columns([1.55, 1.0], gap="large")
    with c_chart:
        st.markdown(f'<h3 style="font-size:16px;margin-bottom:12px;">استهلاك المياه الكلي لـ {farm_area:.1f} فدان (م³)</h3>', unsafe_allow_html=True)
        w_base = roi["baseline"]["total_water_m3"]
        w_s2 = w_base - roi["strategy_2_soil_health"]["water_saved_m3"]
        w_s3 = w_base - roi["strategy_3_water_resilience"]["water_saved_m3"]

        neutral_bar = "#3a3a3f" if dark_mode else "#d4d4d8"
        bar_colors = [
            neutral_bar,
            t["accent"] if strat_focus == "soil_health" else neutral_bar,
            t["accent"] if strat_focus == "water_resilience" else neutral_bar,
        ]
        grid_c = "rgba(237,237,237,0.06)" if dark_mode else "rgba(23,23,23,0.06)"

        fig_w = go.Figure(go.Bar(
            x=["الوضع الحالي", "صحة التربة", "التكيف المائي"],
            y=[w_base, w_s2, w_s3],
            text=[f"{w_base:,.0f}", f"{w_s2:,.0f}", f"{w_s3:,.0f}"],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=12, color=t["text_primary"]),
            marker=dict(color=bar_colors),
        ))
        fig_w.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="IBM Plex Sans Arabic, sans-serif", color=t["text_secondary"]),
            xaxis=dict(showgrid=False, automargin=True, tickfont=dict(size=13, color=t["text_primary"])),
            yaxis=dict(
                showgrid=True, gridcolor=grid_c,
                automargin=True,
                range=[0, max(w_base, 100) * 1.18],
                tickfont=dict(family="IBM Plex Mono, monospace", size=11, color=t["text_muted"]),
            ),
            margin=dict(l=52, r=24, t=24, b=28),
            height=290,
            showlegend=False,
        )
        st.plotly_chart(fig_w, theme=None, width="stretch")

    with c_table:
        st.markdown(f'<h3 style="font-size:16px;margin-bottom:12px;">تفصيل الوفر المالي</h3>', unsafe_allow_html=True)
        f_save = chosen["fertilizer_savings_egp"]
        p_save = chosen["pumping_savings_egp"]
        pest_s = chosen["pesticide_savings_egp"]
        tot = chosen["total_financial_gain_egp"]

        st.markdown(
            f'<div class="ao-table-wrap"><table class="ao-table">'
            f'<tbody>'
            f'<tr><td>وفر سماد اليوريا</td><td class="ao-mono" style="text-align:end;">{f_save:,.0f} ج</td></tr>'
            f'<tr><td>وفر طاقة وضخ المياه</td><td class="ao-mono" style="text-align:end;">{p_save:,.0f} ج</td></tr>'
            f'<tr><td>وفر مبيدات كسر الآفات</td><td class="ao-mono" style="text-align:end;">{pest_s:,.0f} ج</td></tr>'
            f'<tr style="background:{t["bg_deepest"]};font-weight:500;">'
            f'<td style="color:{t["text_primary"]};">الإجمالي التراكمي</td>'
            f'<td class="ao-mono" style="text-align:end;color:{t["accent"]};">{tot:,.0f} ج</td>'
            f'</tr>'
            f'</tbody></table></div>',
            unsafe_allow_html=True,
        )


# =============================================================================
# Tab 4: Report & Voice (Colloquial Egyptian Audio + Printable A4 PDF)
# =============================================================================
def _render_tab_report(res: Dict[str, Any], t: Dict[str, str], dark_mode: bool):
    """Display Voice Agro-Advisor, PDF/HTML Export, and calm scientific disclaimer."""
    meta = res.get("metadata", {})
    telemetry = st.session_state.get("telemetry", {})

    # 1. Egyptian Dialect Voice Briefing
    st.markdown(
        f"""
        <div class="ao-card" style="margin-bottom: 24px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="color:{t['text_secondary']};display:inline-flex;">{svg_icon("volume", 18)}</span>
                <h3 style="font-size:18px;">الملخص الصوتي بالعامية المصرية</h3>
            </div>
            <p style="font-size:14px;color:{t['text_secondary']};margin:0 0 16px 0;">
                استمع لملخص التوصية بأسلوب واضح ومباشر، أو حمّل الملف الصوتي لتشغيله بدون إنترنت.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    briefing_opts = {
        "comprehensive": "الملخص الشامل",
        "soil_health": "صحة التربة واليوريا",
        "water_resilience": "ترشيد المياه والحر",
        "pest_prevention": "وقاية النبات والآفات",
    }
    selected_b = st.pills(
        "موضوع الرسالة الصوتية",
        options=list(briefing_opts.keys()),
        default="comprehensive",
        selection_mode="single",
        required=True,
        format_func=lambda k: briefing_opts[k],
        label_visibility="collapsed",
        key="report_voice_pills",
    )

    script_text = generate_voice_script(selected_b, meta, res)
    audio_bytes = get_agro_voice_audio(script_text)

    v_col, d_col = st.columns([3, 1], vertical_alignment="center")
    with v_col:
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.info("تعذر توليد الصوت حالياً، يمكنك قراءة النص المكتوب بالأسفل.")
    with d_col:
        if audio_bytes:
            st.download_button(
                label="تحميل الصوت (MP3)",
                data=audio_bytes,
                file_name=f"agroorbit_voice_{selected_b}.mp3",
                mime="audio/mp3",
                width="stretch",
            )

    with st.expander("قراءة نص الرسالة الصوتية", expanded=False):
        st.markdown(
            f'<div class="ao-card-compact" style="line-height:1.85;font-size:15px;color:{t["text_primary"]};">'
            f'{script_text.replace(chr(10), "<br>")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # 2. Official Printable PDF Report
    st.markdown(
        f"""
        <div class="ao-card" style="margin-bottom: 16px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="color:{t['text_secondary']};display:inline-flex;">{svg_icon("file-text", 18)}</span>
                <h3 style="font-size:18px;">التقرير الاستشاري للطباعة (<bdi dir="ltr">A4 PDF</bdi>)</h3>
            </div>
            <p style="font-size:14px;color:{t['text_secondary']};margin:0;">
                وثيقة منظمة تشمل قياسات ناسا للمزرعة، جدول المواسم الثلاثة لكل خطة، وحسابات التوفير لتسليمها للجمعية الزراعية أو المرشد.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    report_filename = f"AgroOrbit_Report_{abs(hash(str(meta))) % 1000000:06d}.pdf"
    cached_pdf = REPORTS_CACHE_DIR / report_filename
    pdf_bytes = None
    if cached_pdf.exists():
        try:
            with open(cached_pdf, "rb") as f:
                pdf_bytes = f.read()
        except Exception:
            pass

    if not pdf_bytes:
        with st.spinner("جاري تجهيز نسخة التقرير..."):
            pdf_bytes = generate_advisory_pdf(meta, res, telemetry, report_filename)

    html_report = build_advisory_html_report(meta, res, telemetry)

    b1, b2 = st.columns(2, gap="medium")
    with b1:
        if pdf_bytes:
            st.download_button(
                label="تحميل التقرير المعتمد (PDF)",
                data=pdf_bytes,
                file_name=report_filename,
                mime="application/pdf",
                width="stretch",
            )
        else:
            st.info("يمكنك تحميل النسخة الرقمية (HTML) وطباعتها كـ PDF مباشرة من المتصفح.")
    with b2:
        st.download_button(
            label="تحميل نسخة ويب للطباعة (HTML)",
            data=html_report.encode("utf-8"),
            file_name=report_filename.replace(".pdf", ".html"),
            mime="text/html",
            width="stretch",
        )

    with st.expander("معاينة صفحة التقرير", expanded=False):
        components.html(html_report, height=620, scrolling=True)

    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # 3. Calm Scientific Disclaimer
    st.markdown(
        f"""
        <div class="ao-card-compact" style="border-color:{t['hairline']};">
            <div style="display:flex;align-items:center;gap:8px;color:{t['text_secondary']};margin-bottom:6px;">
                {svg_icon("shield", 15)}
                <span style="font-size:13px;font-weight:500;color:{t['text_primary']};">حدود الدقة العلمية للبيانات</span>
            </div>
            <p style="font-size:13px;line-height:1.65;color:{t['text_muted']};margin:0;">
                تأتي قياسات <bdi dir="ltr">NASA POWER</bdi> و<bdi dir="ltr">SMAP</bdi> بدقة شبكية إقليمية (~50 كم)، وهي دقيقة لتحديد الاتجاهات الحرارية والبخر نتح، ولكنها لا تغني عن فحص عينة التربة معملياً أو مراجعة المهندس الزراعي المختص بالجمعية.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
