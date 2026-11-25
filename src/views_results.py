"""
AgroOrbit - Stage 3: Custom Rotation Results View
Structured after GREEN FUTURE's clean progressive Stage 3 layout:
  Top Action Bar + 3-Column KPI Summary Strip (with Highlighted Savings Box)
  -> Side-by-Side Comparison Plan Cards (.gf-plan-best / Alt / .gf-plan-baseline)
  -> 12-Month Color-Coded Gantt Timeline Grid
  -> Climate Early Warnings + Live ROI Breakdown Calculator
  -> Scientific Evidence + Printable PDF/HTML Preview + Amber Advisory Box
"""

from typing import Dict, Any
import html
import streamlit as st
import streamlit.components.v1 as components

from src import config
from src.design_system import get_tokens, build_gantt_timeline_html
from src.economics_engine import calculate_farm_economic_roi
from src.climate_alerts import evaluate_climate_hazards
from src.pdf_generator import (
    REPORTS_CACHE_DIR,
    generate_advisory_pdf,
    build_advisory_html_report,
)
from src.views_layout import ensure_strategies_computed, open_voice_dialog


def _clean_tag_title(raw_tag: str) -> str:
    """Strip legacy strategy numbering prefixes cleanly."""
    if ":" in raw_tag:
        return raw_tag.split(":", 1)[1].strip()
    return raw_tag.strip()


def render_stage3_results(dark_mode: bool = True):
    """Render Stage 3 custom crop rotation results matching GREEN FUTURE aesthetic."""
    t = get_tokens(dark_mode)
    res = ensure_strategies_computed(allow_network=False)

    meta = res.get("metadata", {})
    gov_ar = meta.get("governorate_ar", "الفيوم")
    soil_short = meta.get("soil_name_ar", "طينية").split("(")[0].strip()
    prev_ar = meta.get("previous_crop_name_ar", "الذرة الشامية")
    area = float(st.session_state.get("farm_area", meta.get("area_feddan", 5.0)))
    telemetry = st.session_state.get("telemetry", {})
    indices = telemetry.get("indices", {})

    # Apply 90-day scenario deltas from Stage 2 if active
    t_shift = float(st.session_state.get("sim_temp_shift", 0.0))
    r_shift = int(st.session_state.get("sim_rain_shift", 0))
    eval_tel = telemetry
    if t_shift != 0.0 or r_shift != 0:
        eval_tel = dict(telemetry)
        idx_c = dict(indices)
        idx_c["avg_temp_c"] = round(float(idx_c.get("avg_temp_c", 23.0)) + t_shift, 1)
        idx_c["max_temp_c"] = round(float(idx_c.get("max_temp_c", 31.0)) + t_shift, 1)
        if t_shift >= 2.0:
            idx_c["extreme_heat_days"] = int(idx_c.get("extreme_heat_days", 0)) + 2
        if r_shift < 0:
            idx_c["soil_moisture_score"] = max(
                12.0, round(float(idx_c.get("soil_moisture_score", 45.0)) * (1.0 + r_shift / 160.0), 1)
            )
        eval_tel["indices"] = idx_c

    eval_idx = eval_tel.get("indices", {})
    hazards = evaluate_climate_hazards(
        eval_tel,
        previous_crop_id=st.session_state.get("previous_crop", "maize"),
        soil_type=st.session_state.get("soil_type", "clay"),
    )

    urea_price = float(st.session_state.get("roi_urea_price", 750.0))
    pump_cost = float(st.session_state.get("roi_pump_cost", 1.1))
    pest_save = float(st.session_state.get("roi_pest_save", 650.0))

    roi = calculate_farm_economic_roi(
        area_feddan=area,
        strat_baseline=res.get("strategy_1_baseline", {}),
        strat_soil=res.get("strategy_2_soil_health", {}),
        strat_water=res.get("strategy_3_water_resilience", {}),
        urea_bag_price_egp=urea_price,
        pumping_cost_m3_egp=pump_cost,
        pesticide_saving_per_feddan_egp=pest_save,
    )

    # Determine recommended plan ordering based on goal choice
    goal = st.session_state.get("goal_choice", "water")
    if goal == "water":
        best_key = "strategy_3_water_resilience"
        alt_key = "strategy_2_soil_health"
    else:
        best_key = "strategy_2_soil_health"
        alt_key = "strategy_3_water_resilience"
    base_key = "strategy_1_baseline"

    best_roi = roi["strategy_3_water_resilience"] if best_key == "strategy_3_water_resilience" else roi["strategy_2_soil_health"]

    st.markdown('<div class="gf-animate">', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 1. Stage 3 Action Bar Header
    # -------------------------------------------------------------------------
    h_info, b_edit, b_lab, b_voice = st.columns([2.7, 1.0, 1.1, 1.1], vertical_alignment="center", gap="small")
    with h_info:
        sim_note = (
            f' • <span style="color:{t["blue"]};font-weight:700;">سيناريو <bdi dir="ltr">{t_shift:+.1f}°C</bdi> / أمطار <bdi dir="ltr">{r_shift:+d}%</bdi></span>'
            if (t_shift != 0.0 or r_shift != 0) else ""
        )
        st.markdown(
            f'<h1 style="font-size:26px;font-weight:800;color:{t["tx"]};margin-bottom:4px;">خطتك الزراعية المخصصة</h1>'
            f'<div style="font-size:14px;color:{t["mu"]};">'
            f'<b style="color:{t["tx"]};">{gov_ar}</b> • تربة {soil_short} • بعد {prev_ar} • <bdi dir="ltr">{area:.1f}</bdi> فدان{sim_note}'
            f'</div>',
            unsafe_allow_html=True,
        )
    with b_edit:
        if st.button("تعديل الأهداف", icon=":material/tune:", key="s3_edit_goals", type="secondary", width="stretch"):
            st.session_state.page = "stage2"
            st.query_params["page"] = "stage2"
            st.rerun()
    with b_lab:
        if st.button("الخرائط والمختبر", icon=":material/public:", key="s3_go_lab", type="secondary", width="stretch"):
            st.session_state.page = "stage4"
            st.query_params["page"] = "stage4"
            st.rerun()
    with b_voice:
        if st.button("المستشار الصوتي", icon=":material/record_voice_over:", key="s3_open_voice", type="primary", width="stretch"):
            open_voice_dialog()

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. 3-Column Summary Strip (2 Metrics Cards + 1 Highlighted ROI Box)
    # -------------------------------------------------------------------------
    moist_pct = float(eval_idx.get("soil_moisture_score", 46.0))
    avg_t = float(eval_idx.get("avg_temp_c", 23.0))
    max_t = float(eval_idx.get("max_temp_c", 31.0))
    conf_pct = float(telemetry.get("confidence_score", 92.0))
    top_haz = hazards[0] if hazards else {"severity": "safe", "title_ar": "مؤشرات الطقس مستقرة"}
    haz_c = t["danger"] if top_haz["severity"] == "critical" else t["amber"] if top_haz["severity"] == "warning" else t["ac"]
    haz_bg = t["danger_soft"] if top_haz["severity"] == "critical" else t["amber_soft"] if top_haz["severity"] == "warning" else t["ac_soft"]

    s1, s2, s3 = st.columns([1.0, 1.0, 1.35], gap="medium")
    with s1:
        st.markdown(
            f"""
            <div class="gf-sum-box">
                <div style="font-size:12.5px;color:{t['mu']};margin-bottom:6px;">قراءة التربة والرطوبة (<bdi dir="ltr">SMAP</bdi>)</div>
                <div style="font-size:24px;font-weight:800;color:{t['tx']};margin-bottom:6px;">
                    {soil_short} <span style="color:{t['blue']};font-size:20px;"><bdi dir="ltr">{moist_pct:.0f}%</bdi></span>
                </div>
                <div style="font-size:12.5px;color:{t['mu']};">موثوقية بيانات ناسا: <bdi dir="ltr" style="color:{t['ac']};font-weight:700;">{conf_pct:.0f}%</bdi></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div class="gf-sum-box">
                <div style="font-size:12.5px;color:{t['mu']};margin-bottom:6px;">مؤشر الحرارة والإنذار المبكر</div>
                <div style="font-size:24px;font-weight:800;color:{t['tx']};margin-bottom:8px;">
                    <bdi dir="ltr">{avg_t:.1f}°C</bdi> <span style="font-size:13.5px;color:{t['mu']};font-weight:600;">(قصوى <bdi dir="ltr">{max_t:.1f}°C</bdi>)</span>
                </div>
                <span style="display:inline-block;background:{haz_bg};color:{haz_c};padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;">
                    {top_haz['title_ar']}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f"""
            <div class="gf-sum-highlight">
                <div style="font-size:12.5px;color:{t['ac']};font-weight:700;margin-bottom:4px;">أكبر توفير متوقع في دورتك ({area:.1f} فدان)</div>
                <div style="font-size:26px;font-weight:800;color:{t['tx']};margin-bottom:6px;">
                    <bdi dir="ltr">{best_roi['total_financial_gain_egp']:,.0f}</bdi> <span style="font-size:15px;">جنيه صافي وفر</span>
                </div>
                <div style="font-size:13px;color:{t['tx']};">
                    توفير <b style="color:{t['blue']};"><bdi dir="ltr">{best_roi['water_saved_m3']:,.0f}</bdi> م³ مياه</b> (<bdi dir="ltr">+{best_roi['water_saved_pct']:.1f}%</bdi>)
                    &nbsp;•&nbsp; <b style="color:{t['amber']};"><bdi dir="ltr">{best_roi['urea_bags_saved']:,.1f}</bdi> شيكارة يوريا</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 26px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. Side-by-Side 3-Plan Comparison Cards (.gf-plan-best / Alt / Baseline)
    # -------------------------------------------------------------------------
    st.markdown(f'<h2 style="font-size:20px;font-weight:800;margin-bottom:14px;color:{t["tx"]};">مقارنة الخطط الـ 3 لدورة العام الكامل (3 مواسم)</h2>', unsafe_allow_html=True)

    plan_cards_cfg = [
        (best_key, "gf-plan-card gf-plan-best", "✓ الخطة المثلى لهدفك", t["ac"], t["ac_soft"]),
        (alt_key, "gf-plan-card", "خطة بديلة قوية", t["blue"], t["blue_soft"]),
        (base_key, "gf-plan-card gf-plan-baseline", "الوضع التقليدي للمقارنة", t["mu"], t["surface_alt"]),
    ]

    cards_markup = []
    for p_key, cls_name, badge_txt, b_fg, b_bg in plan_cards_cfg:
        strat = res.get(p_key, {})
        title_ar = _clean_tag_title(strat.get("tag_ar", ""))
        metrics = strat.get("metrics", {})
        timeline = strat.get("timeline", [])
        why_short = html.escape(strat.get("why_suggested", strat.get("summary_ar", ""))[:190])
        if len(strat.get("why_suggested", "")) > 190:
            why_short += "..."

        # Build sequence of .gf-crop-chip items with clear seasonal names
        chips_html_parts = []
        for idx, step in enumerate(timeline):
            c_obj = step.get("crop", {})
            c_name = html.escape(c_obj.get("name_ar", ""))
            raw_sl = c_obj.get("season_label_ar", "").strip()
            s_lbl = html.escape(raw_sl.split(" ")[0] if raw_sl else f"موسم {idx + 1}")
            chips_html_parts.append(
                f'<span class="gf-crop-chip" style="padding:3px 10px;font-size:12.5px;">{s_lbl}: {c_name}</span>'
            )
            if idx < len(timeline) - 1:
                chips_html_parts.append(f'<span style="color:{t["mu"]};font-size:12px;">←</span>')
        chips_html = f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:5px;margin:10px 0;">{"".join(chips_html_parts)}</div>'

        w_mm = metrics.get("total_water_mm", 0.0)
        pest_pct = metrics.get("pest_break_efficiency_pct", 0.0)
        if p_key == base_key:
            gain_str = 'مرجع أساسي'
            w_save_str = '<bdi dir="ltr">0%</bdi> (أساس)'
        else:
            p_roi = roi["strategy_3_water_resilience"] if p_key == "strategy_3_water_resilience" else roi["strategy_2_soil_health"]
            gain_str = f'<bdi dir="ltr">{p_roi["total_financial_gain_egp"]:,.0f}</bdi> ج'
            w_save_str = f'<bdi dir="ltr">+{metrics.get("water_savings_pct", 0.0):.1f}%</bdi>'

        cards_markup.append(
            f'<div class="{cls_name}">'
            f'<div>'
            f'<span style="display:inline-block;background:{b_bg};color:{b_fg};padding:3px 12px;border-radius:999px;font-size:12px;font-weight:700;margin-bottom:8px;">{badge_txt}</span>'
            f'<h3 style="font-size:18px;font-weight:800;color:{t["tx"]};margin-bottom:4px;">{title_ar}</h3>'
            f'{chips_html}'
            f'<div class="gf-plan-why">{why_short}</div>'
            f'</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">'
            f'<div class="gf-metric-tile"><div style="font-size:11.5px;color:{t["mu"]};">استهلاك المياه</div><div style="font-size:14px;font-weight:800;color:{t["tx"]};"><bdi dir="ltr">{w_mm:.0f}</bdi> مم</div></div>'
            f'<div class="gf-metric-tile"><div style="font-size:11.5px;color:{t["mu"]};">توفير المياه</div><div style="font-size:14px;font-weight:800;color:{t["blue"]};">{w_save_str}</div></div>'
            f'<div class="gf-metric-tile"><div style="font-size:11.5px;color:{t["mu"]};">كسر دورة الآفات</div><div style="font-size:14px;font-weight:800;color:{t["ac"]};"><bdi dir="ltr">{pest_pct:.0f}%</bdi></div></div>'
            f'<div class="gf-metric-tile"><div style="font-size:11.5px;color:{t["mu"]};">الوفر المالي</div><div style="font-size:14px;font-weight:800;color:{t["amber"]};">{gain_str}</div></div>'
            f'</div>'
            f'</div>'
        )

    st.markdown(f'<div class="gf-plans-grid">{"".join(cards_markup)}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. Interactive 12-Month Color-Coded Gantt Timeline Grid
    # -------------------------------------------------------------------------
    g_hdr, g_ctrl = st.columns([1.8, 1.4], vertical_alignment="center")
    with g_hdr:
        st.markdown(f'<h2 style="font-size:20px;font-weight:800;color:{t["tx"]};">الجدول الزمني السنوي لتغطية التربة (<bdi dir="ltr">12</bdi> شهراً)</h2>', unsafe_allow_html=True)
    with g_ctrl:
        gantt_opts = {
            best_key: "الموصى بها",
            alt_key: "البديلة",
            base_key: "التقليدي",
        }
        chosen_gantt = st.segmented_control(
            "خطة الجدول الزمني",
            options=list(gantt_opts.keys()),
            default=best_key,
            selection_mode="single",
            required=True,
            format_func=lambda k: gantt_opts[k],
            label_visibility="collapsed",
            key="s3_gantt_select",
        )

    active_tl = res.get(chosen_gantt or best_key, {}).get("timeline", [])
    st.markdown(build_gantt_timeline_html(active_tl, dark_mode=dark_mode), unsafe_allow_html=True)

    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. Early Warning Hazards (Left) + Live ROI Calculator Breakdown (Right)
    # -------------------------------------------------------------------------
    haz_col, roi_col = st.columns([1.1, 1.2], gap="large")

    with haz_col:
        st.markdown(f'<h3 style="font-size:18px;font-weight:800;margin-bottom:12px;color:{t["tx"]};">الإنذار المبكر والمخاطر المناخية</h3>', unsafe_allow_html=True)
        for a in hazards:
            sev = a["severity"]
            dot_c = t["danger"] if sev == "critical" else t["amber"] if sev == "warning" else t["ac"]
            badge_bg = t["danger_soft"] if sev == "critical" else t["amber_soft"] if sev == "warning" else t["ac_soft"]
            sev_txt = "حرج" if sev == "critical" else "تنبيه" if sev == "warning" else "مستقر"
            acts = "".join(f"<li style='margin-bottom:4px;'>{x}</li>" for x in a.get("urgent_actions", []))
            st.markdown(
                f"""
                <div class="gf-card" style="padding:16px 18px;margin-bottom:12px;border-inline-start:4px solid {dot_c};">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px;">
                        <span style="font-size:14.5px;font-weight:800;color:{t['tx']};">{a['title_ar']}</span>
                        <span style="background:{badge_bg};color:{dot_c};padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;">{sev_txt}</span>
                    </div>
                    <p style="font-size:13px;color:{t['mu']};margin:0 0 8px 0;">{a['trigger_data']}</p>
                    <ol style="margin:0;padding-inline-start:18px;font-size:13px;color:{t['tx']};">{acts}</ol>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with roi_col:
        st.markdown(f'<h3 style="font-size:18px;font-weight:800;margin-bottom:12px;color:{t["tx"]};">تفاصيل الوفورات الاقتصادية المتوقعة</h3>', unsafe_allow_html=True)
        roi_focus = st.segmented_control(
            "الخطة المحسوب توفيرها",
            options=["soil_health", "water_resilience"],
            default="water_resilience" if goal == "water" else "soil_health",
            selection_mode="single",
            required=True,
            format_func=lambda k: "خطة صحة التربة واليوريا" if k == "soil_health" else "خطة التكيف وترشيد المياه",
            label_visibility="collapsed",
            key="s3_roi_focus",
        )
        focus_roi = roi["strategy_2_soil_health"] if roi_focus == "soil_health" else roi["strategy_3_water_resilience"]

        st.markdown(
            f"""
            <div class="gf-table-wrap">
                <table class="gf-table">
                    <thead><tr><th>بند التوفير السنوي ({area:.1f} فدان)</th><th style="text-align:end;">القيمة</th></tr></thead>
                    <tbody>
                        <tr><td>توفير سماد اليوريا (<bdi dir="ltr">{focus_roi['urea_bags_saved']:,.1f}</bdi> شيكارة)</td><td style="text-align:end;font-weight:700;"><bdi dir="ltr">{focus_roi['fertilizer_savings_egp']:,.0f} ج</bdi></td></tr>
                        <tr><td>توفير طاقة وضخ المياه (<bdi dir="ltr">{focus_roi['water_saved_m3']:,.0f}</bdi> م³)</td><td style="text-align:end;font-weight:700;"><bdi dir="ltr">{focus_roi['pumping_savings_egp']:,.0f} ج</bdi></td></tr>
                        <tr><td>وفر مبيدات كسر دورة الآفات</td><td style="text-align:end;font-weight:700;"><bdi dir="ltr">{focus_roi['pesticide_savings_egp']:,.0f} ج</bdi></td></tr>
                        <tr><td>الأثر البيئي (تجنب انبعاثات <bdi dir="ltr">CO₂</bdi>)</td><td style="text-align:end;color:{t['blue']};font-weight:700;"><bdi dir="ltr">{focus_roi['co2_offset_tons']:.2f} طن</bdi></td></tr>
                        <tr style="background:{t['ac_soft']};font-weight:800;">
                            <td style="color:{t['tx']};">الإجمالي التراكمي للوفر</td>
                            <td style="text-align:end;color:{t['ac']};"><bdi dir="ltr">{focus_roi['total_financial_gain_egp']:,.0f} ج</bdi></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("تخصيص أسعار اليوريا وتكلفة الري والأفدنة", expanded=False):
            c_a, c_u, c_p = st.columns(3, gap="small")
            with c_a:
                new_area = st.number_input("الفدان", 0.5, 500.0, area, 0.5, format="%.1f", key="s3_area_adj")
                if abs(new_area - area) > 0.05:
                    st.session_state.farm_area = new_area
            with c_u:
                st.session_state.roi_urea_price = st.number_input("اليوريا (ج)", 250.0, 2000.0, urea_price, 25.0, key="s3_urea_adj")
            with c_p:
                st.session_state.roi_pump_cost = st.number_input("الضخ (ج/م³)", 0.4, 5.0, pump_cost, 0.1, key="s3_pump_adj")

    st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 6. Scientific Evidence & Printable PDF Report Expanders
    # -------------------------------------------------------------------------
    with st.expander("التفاصيل العلمية ومصفوفة مقارنة الخطط الثلاث", expanded=False):
        matrix = res.get("comparison_matrix", [])
        if matrix:
            m_rows = "".join(
                f'<tr><td style="font-weight:700;">{row["criterion_ar"]}</td>'
                f'<td>{row["strategy_1"]}</td>'
                f'<td style="color:{t["ac"]};font-weight:700;">{row["strategy_2"]}</td>'
                f'<td style="color:{t["blue"]};font-weight:700;">{row["strategy_3"]}</td></tr>'
                for row in matrix
            )
            st.markdown(
                f'<div class="gf-table-wrap"><table class="gf-table">'
                f'<thead><tr><th>المعيار</th><th>الوضع التقليدي</th><th>صحة التربة</th><th>التكيف المائي</th></tr></thead>'
                f'<tbody>{m_rows}</tbody></table></div>',
                unsafe_allow_html=True,
            )
        best_strat = res.get(best_key, {})
        st.markdown(
            f'<div class="gf-insight-box">'
            f'<b>الأدلة الفضائية للخطة الموصى بها:</b> {best_strat.get("evidence", "")}<br><br>'
            f'<b>الفوائد الزراعية:</b> {best_strat.get("benefits", "")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with st.expander("تحميل ومعاينة التقرير الرسمي للجمعية الزراعية (A4 PDF / HTML)", expanded=False):
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
            with st.spinner("جاري تجهيز نسخة التقرير PDF..."):
                pdf_bytes = generate_advisory_pdf(meta, res, telemetry, report_filename)
        html_report = build_advisory_html_report(meta, res, telemetry)

        d1, d2 = st.columns(2, gap="medium")
        with d1:
            if pdf_bytes:
                st.download_button(
                    label="تحميل التقرير المعتمد (PDF)",
                    data=pdf_bytes,
                    file_name=report_filename,
                    mime="application/pdf",
                    width="stretch",
                    key="s3_dl_pdf",
                )
            else:
                st.info("استخدم تحميل HTML وطباعته كـ PDF مباشرة.")
        with d2:
            st.download_button(
                label="تحميل نسخة ويب للطباعة (HTML)",
                data=html_report.encode("utf-8"),
                file_name=report_filename.replace(".pdf", ".html"),
                mime="text/html",
                width="stretch",
                key="s3_dl_html",
            )
        components.html(html_report, height=540, scrolling=True)

    st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 7. Warm Amber Advisory Disclaimer Box
    # -------------------------------------------------------------------------
    st.markdown(
        f"""
        <div class="gf-amber-box">
            <b>ملاحظة الفحص الحقلية والأقمار الصناعية:</b>
            تستند الحسابات المناخية ورطوبة التربة الجذرية (<bdi dir="ltr">NASA POWER / SMAP</bdi>) إلى شبكة رصد بدقة بقطر نحو <bdi dir="ltr">50</bdi> كم.
            هذه التوصية مرجع علمي دقيق للتخطيط، ويُفضّل مطابقتها مع عينة تحليل ملوحة التربة ومناوبة الترعة المحلية بالتنسيق مع المهندس الزراعي.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
