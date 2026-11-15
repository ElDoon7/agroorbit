"""
AgroOrbit (Team: Nova Squad NASA)
NASA Space Apps Challenge 2026 - Challenge: Field Shift: Adapting Farms with NASA Data

Main Application Entry Point (Streamlit Web & Mobile Responsive)
Features:
- Dual Theme Engine: Deep Space Dark (فضائي مظلم) & Solar Daylight (نهاري فاتح)
- Live NASA POWER API Integration, -999 Sensor Anomaly Filtering & 10-Day Historical Table
- 3 NASA-Compliant Spacious Rotation Strategies (Baseline, Soil Health BNF, Water Resilience)
- Fixed Multi-Layer Folium Satellite & Dark Map (Zero Black-Screen Glitches)
- Egypt 27 Governorates Agro-Climatic Intelligence (Plotly Charts & Geospatial Layer)
- What-If Climate Scenario Simulator
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src import config
from src.space_theme import get_space_theme_css, get_logo_base64
from src.crops_data import CROPS_DATABASE, DISEASES_CATALOG, get_all_crop_ids, get_crop
from src.egypt_governorates import EGYPT_GOVERNORATES, get_governorate_choices
from src.nasa_client import nasa_client
from src.decision_engine import decision_engine
from src.governorate_analyzer import (
    CRITERIA_DEFINITIONS,
    rank_governorates,
    build_ranking_barchart,
    build_governorate_radar,
    build_orbital_folium_map
)
from src.ui_components import (
    render_orbital_splash_intro,
    render_header,
    render_telemetry_hud,
    render_nasa_daily_table,
    render_strategy_card,
    render_comparison_matrix_table,
    render_crops_knowledge_table,
    render_diseases_visual_atlas,
    render_scientific_disclaimer,
    render_ai_voice_advisor,
    render_pdf_report_exporter,
    render_economic_roi_calculator,
    render_climate_hazards_hud
)

# =============================================================================
# 1. Page Configuration
# =============================================================================
st.set_page_config(
    page_title="AgroOrbit | أجرواوربت - ناسا 2026",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 2. Session State Management
# =============================================================================
if "latitude" not in st.session_state:
    st.session_state.latitude = 30.0409
if "longitude" not in st.session_state:
    st.session_state.longitude = 31.2357
if "soil_type" not in st.session_state:
    st.session_state.soil_type = "clay"
if "previous_crop" not in st.session_state:
    st.session_state.previous_crop = "maize"
if "telemetry" not in st.session_state:
    st.session_state.telemetry = nasa_client.fetch_point_telemetry(
        st.session_state.latitude,
        st.session_state.longitude,
        days=15,
        timeout=3,
        allow_network=False
    )
if "strategies_result" not in st.session_state or st.session_state.strategies_result is None:
    st.session_state.strategies_result = decision_engine.generate_all_strategies(
        soil_type=st.session_state.soil_type,
        previous_crop_id=st.session_state.previous_crop,
        nasa_telemetry=st.session_state.telemetry,
        priority_water=4,
        priority_soil=5,
        priority_profit=3
    )
if "gov_telemetry" not in st.session_state:
    st.session_state.gov_telemetry = nasa_client.get_all_governorates_telemetry(force_refresh=False)
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"
if "replay_splash" not in st.session_state:
    st.session_state.replay_splash = False

# =============================================================================
# 3. Sidebar: Mission Control Inputs & Farm Configuration
# =============================================================================
with st.sidebar:
    sidebar_logo = get_logo_base64()
    logo_header_html = f'<img src="{sidebar_logo}" style="width: 76px; height: 76px; object-fit: contain; filter: drop-shadow(0 0 14px rgba(0, 229, 255, 0.55)); margin-bottom: 8px;" alt="Logo" />' if sidebar_logo else '<span style="font-size: 2rem;">🛰️</span>'

    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 15px;">
        {logo_header_html}
        <h2 style="margin: 0; font-size: 1.4rem;">لوحة التحكم المدارية</h2>
        <span style="font-size: 0.78rem; color: #00ff88;">Nova Squad NASA Mission Control</span>
    </div>
    """, unsafe_allow_html=True)

    # Theme Switcher (Solves the locked dark mode issue)
    theme_choice = st.radio(
        "🎨 مظهر الواجهة (Theme Mode):",
        options=["🌙 الوضع الفضائي المظلم (Deep Space)", "☀️ وضع ضوء النهار (Solar Daylight)"],
        index=0 if st.session_state.theme_mode == "dark" else 1
    )
    is_dark = "الوضع الفضائي" in theme_choice
    st.session_state.theme_mode = "dark" if is_dark else "light"

    st.divider()

    st.subheader("📋 1. بيانات المزرعة الحقلية")

    soil_options = {
        "clay": "طينية ثقيلة (Clay)",
        "loam": "طميية متوازنة (Loam)",
        "sandy": "رملية خفيفة (Sandy)",
        "calcareous": "جيرية كلسية (Calcareous)"
    }
    selected_soil = st.selectbox(
        "نوع تربة الحقل:",
        options=list(soil_options.keys()),
        format_func=lambda x: soil_options[x],
        index=list(soil_options.keys()).index(st.session_state.soil_type)
    )
    st.session_state.soil_type = selected_soil

    crop_options = {cid: f"{c['name_ar']} ({c['name_en']})" for cid, c in CROPS_DATABASE.items()}
    selected_prev_crop = st.selectbox(
        "المحصول السابق بالحقل:",
        options=list(crop_options.keys()),
        format_func=lambda x: crop_options[x],
        index=list(crop_options.keys()).index(st.session_state.previous_crop)
    )
    st.session_state.previous_crop = selected_prev_crop

    st.divider()

    st.subheader("📍 2. الموقع الجغرافي للمزرعة")

    gov_choices = get_governorate_choices()
    preset_gov = st.selectbox(
        "اختر محافظة مصرية (تحديد سريع):",
        options=["custom"] + list(gov_choices.keys()),
        format_func=lambda x: "موقع يدوي مخصص (Custom Pin)" if x == "custom" else gov_choices[x]
    )
    if preset_gov != "custom":
        gov_obj = EGYPT_GOVERNORATES[preset_gov]
        st.session_state.latitude = gov_obj["lat"]
        st.session_state.longitude = gov_obj["lon"]

    col_lat, col_lon = st.columns(2)
    with col_lat:
        input_lat = st.number_input(
            "خط العرض (Lat)",
            value=float(st.session_state.latitude),
            format="%.4f",
            step=0.01
        )
    with col_lon:
        input_lon = st.number_input(
            "خط الطول (Lon)",
            value=float(st.session_state.longitude),
            format="%.4f",
            step=0.01
        )
    st.session_state.latitude = input_lat
    st.session_state.longitude = input_lon

    if st.button("🛰️ تحديث بيانات الطقس حياً من ناسا", use_container_width=True):
        with st.spinner("جاري الاتصال بالأقمار الصناعية وسيرفرات NASA POWER..."):
            telemetry_data = nasa_client.fetch_point_telemetry(
                st.session_state.latitude,
                st.session_state.longitude,
                days=30,
                allow_network=True
            )
            st.session_state.telemetry = telemetry_data
            st.success("✅ تم تحديث بيانات التليمترية من ناسا وتطهير القيم الشاذة بنجاح!")

    st.divider()

    st.subheader("🎯 3. أولويات المزارع (Weights)")
    p_water = st.slider("💧 توفير مياه الري", min_value=1, max_value=5, value=4)
    p_soil = st.slider("🌿 تحسين صحة وخصوبة التربة", min_value=1, max_value=5, value=5)
    p_profit = st.slider("💰 العائد الاقتصادي والربحية", min_value=1, max_value=5, value=3)

    st.divider()

    if st.button("🚀 اقترح الاستراتيجيات الثلاث لدعم القرار", use_container_width=True):
        with st.spinner("يقوم محرك AgroOrbit بتحليل التليمترية وتوليد الاستراتيجيات..."):
            strategies = decision_engine.generate_all_strategies(
                soil_type=st.session_state.soil_type,
                previous_crop_id=st.session_state.previous_crop,
                nasa_telemetry=st.session_state.telemetry,
                priority_water=p_water,
                priority_soil=p_soil,
                priority_profit=p_profit
            )
            st.session_state.strategies_result = strategies
            st.success("✅ تم توليد ومطابقة الاستراتيجيات الثلاث بنجاح!")

    st.divider()
    if st.button("🎬 إعادة تشغيل المقدمة المدارية (Replay Intro)", use_container_width=True):
        st.session_state.replay_splash = True
        st.rerun()

# Apply Theme CSS
st.markdown(get_space_theme_css(dark_mode=is_dark), unsafe_allow_html=True)

# Cinematic Fullscreen Orbital Intro Splash Screen
render_orbital_splash_intro(dark_mode=is_dark, force=st.session_state.replay_splash)
st.session_state.replay_splash = False

# =============================================================================
# 4. Main View Layout & Navigation Tabs
# =============================================================================
render_header(dark_mode=is_dark)

tab1, tab2, tab3 = st.tabs([
    "🌾 تخطيط الدورات الزراعية (Farm Shift Engine)",
    "🗺️ مصفوفة مقارنة المحافظات الـ 27 (Egypt Agro-Matrix)",
    "📚 قاعدة بيانات المحاصيل والآفات (Knowledge Base)"
])

# =============================================================================
# TAB 1: Farm Decision Support & 3-Strategy Rotation Engine
# =============================================================================
with tab1:
    st.markdown("### 🛰️ بيانات التليمترية المدارية الحية للمزرعة")
    render_telemetry_hud(st.session_state.telemetry, dark_mode=is_dark)

    # Feature #4: NASA Climate Hazards & Early Warning System
    render_climate_hazards_hud(
        st.session_state.telemetry,
        previous_crop_id=st.session_state.previous_crop,
        soil_type=st.session_state.soil_type,
        dark_mode=is_dark
    )

    # NASA 10-Day Historical Table & Trends (User requested feature)
    with st.expander("📅 جدول ورسم بياني لطقس ناسا (آخر 10 أيام في موقعك)", expanded=False):
        render_nasa_daily_table(st.session_state.telemetry, days=10, dark_mode=is_dark)

    st.markdown("#### 📍 موقع المزرعة على الخريطة المدارية التفاعلية:")
    st.markdown(f"""
    <div style="background: {'rgba(0, 229, 255, 0.08)' if is_dark else '#e0f2fe'}; border-right: 4px solid {'#00e5ff' if is_dark else '#0284c7'}; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; font-size: 0.9rem;">
        🎯 <b>تحديد الموقع التلقائي (Live GPS):</b> يمكنك الضغط على زر مستشعر الـ GPS <b>(🎯)</b> بأعلى يسار الخريطة لتحديد مكانك الفعلي عبر الهاتف أو اللابتوب، أو الضغط كليك في أي مكان على الخريطة لتحديث موقع مزرعتك وسحب بيانات ناسا المدارية فوراً.
    </div>
    """, unsafe_allow_html=True)

    ranked_govs_default = rank_governorates(st.session_state.gov_telemetry, "composite_score")
    farm_map = build_orbital_folium_map(
        center_lat=st.session_state.latitude,
        center_lon=st.session_state.longitude,
        ranked_govs=ranked_govs_default,
        criterion_key="composite_score",
        selected_farm_coords=(st.session_state.latitude, st.session_state.longitude)
    )

    map_interaction = st_folium(
        farm_map,
        height=450,
        use_container_width=True,
        returned_objects=["last_clicked"],
        key="farm_map_selector"
    )

    if map_interaction and map_interaction.get("last_clicked"):
        new_lat = round(map_interaction["last_clicked"]["lat"], 4)
        new_lon = round(map_interaction["last_clicked"]["lng"], 4)
        if abs(new_lat - st.session_state.latitude) > 0.001 or abs(new_lon - st.session_state.longitude) > 0.001:
            st.session_state.latitude = new_lat
            st.session_state.longitude = new_lon
            st.info(f"🎯 تم تحديد موقع جديد: Lat {new_lat}, Lon {new_lon}")
            st.session_state.telemetry = nasa_client.fetch_point_telemetry(
                new_lat, new_lon, days=15, timeout=3, allow_network=False
            )
            st.rerun()

    st.divider()

    # Decision Engine Output (Spacious Tabbed/Segmented Presentation)
    if st.session_state.strategies_result:
        res = st.session_state.strategies_result
        meta = res["metadata"]

        st.markdown(f"""
        <div style="background: {'rgba(0, 229, 255, 0.08)' if is_dark else '#e0f2fe'}; border-right: 4px solid {'#00e5ff' if is_dark else '#0284c7'}; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px;">
            <h4 style="margin: 0; color: {'#00e5ff' if is_dark else '#0284c7'};">💡 نتائج محرك دعم القرار الزراعي المتكيف مع بيانات ناسا</h4>
            <span style="font-size: 0.92rem;">
                التربة: <b>{meta['soil_name_ar']}</b> | المحصول السابق: <b>{meta['previous_crop_name_ar']}</b> | 
                متوسط الحرارة الفضائي: <b>{meta['nasa_avg_temp']}°C</b> | رطوبة التربة الجذرية: <b>{meta['soil_moisture_score']}%</b>
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Feature #3: NASA AI Voice Agro-Advisor (Colloquial Egyptian Audio Advisory)
        render_ai_voice_advisor(meta, res, dark_mode=is_dark)

        st.markdown("#### 🌟 اختر الاستراتيجية لاستعراض تفاصيلها كاملة بأريحية:")

        # Spacious Sub-tabs solving the crammed 3-column issue
        strat_subtab1, strat_subtab2, strat_subtab3 = st.tabs([
            "🟢 الاستراتيجية 1: الوضع الراهن (Baseline)",
            "🔵 الاستراتيجية 2: صحة التربة والنيتروجين (BNF)",
            "🟠 الاستراتيجية 3: التكيف المائي وحماية الجفاف"
        ])

        with strat_subtab1:
            render_strategy_card(res["strategy_1_baseline"], dark_mode=is_dark)

        with strat_subtab2:
            render_strategy_card(res["strategy_2_soil_health"], dark_mode=is_dark)

        with strat_subtab3:
            render_strategy_card(res["strategy_3_water_resilience"], dark_mode=is_dark)

        st.divider()

        # Side-by-Side Comparison Table
        render_comparison_matrix_table(res["comparison_matrix"], dark_mode=is_dark)

        st.divider()

        # Feature #1: Agricultural Economics & Water Savings Calculator (ROI)
        render_economic_roi_calculator(res, dark_mode=is_dark)

        st.divider()

        # What-If Scenario Slider Simulation
        st.markdown("### 🧪 محاكاة سيناريو التغير المناخي المستقبلي (What-If Climate Scenario)")
        st.caption("اختبر استجابة المزرعة لتغير درجات الحرارة أو الأمطار:")

        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            temp_shift = st.slider("محاكاة ارتفاع/انخفاض الحرارة (°C):", -4.0, 5.0, 0.0, 0.5)
        with sim_col2:
            rain_shift_pct = st.slider("محاكاة تغير كميات الأمطار (%):", -50, 50, 0, 10)

        if temp_shift != 0.0 or rain_shift_pct != 0:
            simulated_temp = meta['nasa_avg_temp'] + temp_shift
            st.warning(f"""
            🌡️ **نتائج المحاكاة المناخية:** عند متوسط حرارة **{simulated_temp:.1f}°C**، 
            {"ستتزايد الحاجة لاعتماد الاستراتيجية 3 (التكيف المائي) لتفادي احتراق أزهار المحاصيل الحساسة." if temp_shift > 1.5 else "تبقى الدورات المقترحة في نطاق التكيف الآمن فسيولوجياً."}
            """)

        st.divider()

        # Feature #2: Official NASA Field Advisory Report (Print-Ready A4 PDF Exporter)
        render_pdf_report_exporter(meta, res, st.session_state.telemetry, dark_mode=is_dark)
    else:
        st.info("💡 **لبدء التوصيات:** حدد بيانات مزرعتك في القائمة الجانبية واضغط على زر **'🚀 اقترح الاستراتيجيات الثلاث لدعم القرار'**.")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    render_scientific_disclaimer()

# =============================================================================
# TAB 2: Egypt 27 Governorates Agro-Climatic Intelligence
# =============================================================================
with tab2:
    st.markdown("### 🗺️ مصفوفة الذكاء الزراعي والمناخي لمحافظات مصر الـ 27")
    st.write("مقارنة شاملة بين محافظات الجمهورية استناداً إلى تليمترية وكالة ناسا المدارية (SMAP, POWER, GPM).")

    crit_col1, crit_col2 = st.columns([2, 1])
    with crit_col1:
        selected_criterion = st.selectbox(
            "اختر معيار المقارنة والترتيب بين المحافظات:",
            options=list(CRITERIA_DEFINITIONS.keys()),
            format_func=lambda x: CRITERIA_DEFINITIONS[x]["title_ar"],
            index=3
        )
    with crit_col2:
        if st.button("🔄 تحديث كاش المحافظات من ناسا", use_container_width=True):
            with st.spinner("جاري تحديث كاش بيانات المحافظات الـ 27..."):
                st.session_state.gov_telemetry = nasa_client.get_all_governorates_telemetry(force_refresh=True)
                st.success("✅ تم تحديث كاش المحافظات بنجاح!")

    crit_data = CRITERIA_DEFINITIONS[selected_criterion]
    st.caption(f"ℹ️ {crit_data['description_ar']}")

    ranked_govs = rank_governorates(st.session_state.gov_telemetry, selected_criterion)

    # Filter & Synchronized Color Indicator
    ctrl_col1, ctrl_col2 = st.columns([1, 1])
    with ctrl_col1:
        top_n_choice = st.radio(
            "نطاق عرض المحافظات في الرسم البياني:",
            options=[10, 15, 27],
            index=1,
            horizontal=True,
            format_func=lambda x: f"أعلى {x} محافظات" if x < 27 else "جميع المحافظات الـ 27 كاملة"
        )
    with ctrl_col2:
        st.markdown(f"""
        <div style="background: {'rgba(0, 229, 255, 0.08)' if is_dark else '#e0f2fe'}; border-right: 4px solid {'#00e5ff' if is_dark else '#0284c7'}; padding: 8px 12px; border-radius: 8px; margin-top: 6px; font-size: 0.85rem;">
            🎨 <b>تزامن لوني دقيق (1:1):</b> لون كل شريط في الرسم البياني يطابق تماماً لون المساحة والحدود الفعلية للمحافظة (Choropleth Polygon) على الخريطة المدارية.
        </div>
        """, unsafe_allow_html=True)

    chart_col, map_col = st.columns([1, 1])

    with chart_col:
        bar_fig = build_ranking_barchart(ranked_govs, selected_criterion, top_n=top_n_choice, dark_mode=is_dark)
        st.plotly_chart(bar_fig, theme=None, use_container_width=True)

    with map_col:
        st.markdown("##### 🛰️ التوزيع الجغرافي والحدود الفعلية للمحافظات (Choropleth):")
        gov_map = build_orbital_folium_map(
            center_lat=27.5,
            center_lon=31.0,
            ranked_govs=ranked_govs,
            criterion_key=selected_criterion,
            selected_farm_coords=(st.session_state.latitude, st.session_state.longitude)
        )
        st_folium(gov_map, height=520, use_container_width=True, key="gov_map_overview")

    st.divider()

    st.markdown("### 🔍 الفحص التفصيلي لبصمة محافظة مختارة")
    gov_list_choices = {g["id"]: f"#{g['rank']} - {g['name_ar']} ({g['name_en']})" for g in ranked_govs}
    inspect_gov_id = st.selectbox(
        "اختر محافظة لعرض بصمتها الرادارية متكاملة:",
        options=list(gov_list_choices.keys()),
        format_func=lambda x: gov_list_choices[x]
    )

    selected_ranked = next((g for g in ranked_govs if g["id"] == inspect_gov_id), None)
    if selected_ranked:
        r_col1, r_col2 = st.columns([1, 1])
        with r_col1:
            radar_fig = build_governorate_radar(selected_ranked, dark_mode=is_dark)
            st.plotly_chart(radar_fig, theme=None, use_container_width=True)

        with r_col2:
            ind = selected_ranked.get("indices", {})
            gov_color = selected_ranked.get("color", "#00e5ff")
            st.markdown(f"""
            <div class="hud-card" style="margin-top: 15px; border-right: 6px solid {gov_color} !important;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="color: {gov_color}; margin: 0; font-size: 1.25rem;">📍 محافظة {selected_ranked.get('name_ar')}</h4>
                    <span class="badge-pill" style="background: {gov_color}; color: #04101e; font-weight: 900;">الترتيب: #{selected_ranked.get('rank')}</span>
                </div>
                <p><b>الإقليم الزراعي:</b> {selected_ranked.get('region')}</p>
                <p><b>نوع التربة السائد:</b> {selected_ranked.get('dominant_soil')}</p>
                <p><b>مؤشر الخصوبة والرطوبة (SMAP):</b> <span style="color: #00ff88; font-weight: 800;">{ind.get('soil_moisture_score')}%</span></p>
                <p><b>مؤشر توفير المياه:</b> <span style="color: #00e5ff; font-weight: 800;">{ind.get('water_conservation_potential')}%</span></p>
                <p><b>مؤشر الجدارة الإنتاجية الشامل:</b> <span style="color: {gov_color}; font-weight: 900;">{selected_ranked.get('score')}%</span></p>
                <p><b>أهم المحاصيل الحالية:</b> {', '.join(selected_ranked.get('main_crops', []))}</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: Crops Knowledge Base & Pest Interruption Matrix
# =============================================================================
with tab3:
    st.markdown("### 📚 قاعدة بيانات المحاصيل الاستراتيجية الـ 11 والآفات الزراعية")
    st.write("بيانات علمية دقيقة للاحتياجات المائية والحدود الفسيولوجية وتثبيت النيتروجين الحيوي (BNF):")

    render_crops_knowledge_table(CROPS_DATABASE, dark_mode=is_dark)

    st.divider()

    render_diseases_visual_atlas(DISEASES_CATALOG, dark_mode=is_dark)

# =============================================================================
# Footer
# =============================================================================
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 40px; padding: 10px; border-top: 1px solid rgba(0, 229, 255, 0.1);">
    🛰️ Developed by <b>Team Nova Squad NASA</b> for NASA Space Apps Challenge 2026<br/>
    Powered by NASA POWER API, SMAP, GPM & MODIS Telemetry Models.
</div>
""", unsafe_allow_html=True)
