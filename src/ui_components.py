"""
AgroOrbit - UI Components & Visual Presentation Layer
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data

Modular rendering components for:
- Cinematic Fullscreen Space Splash Screen with Rotating Earth, Orbiting Satellite & User Logo
- Telemetry HUD & NASA 10-Day Historical Table & Trends (Custom Glassmorphism Anti-Excel Theme)
- High-Clarity NASA Strategy Cards (Zero Markdown Indentation Bugs)
- Side-by-Side Comparison Matrix (Direct HTML with Custom Glowing Glass Theme)
- Crops Knowledge Base Table (Futuristic Glass Table replacing st.dataframe)
- Visual Plant Pathology & Crop Disease Atlas (Diagnostic Cards with Real Images)
- Scientific Uncertainty Disclaimers
"""

import time
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from src import config
from src.space_theme import get_logo_base64
from src.voice_advisor import generate_voice_script, get_agro_voice_audio
from src.pdf_generator import build_advisory_html_report, generate_advisory_pdf, REPORTS_CACHE_DIR
from src.economics_engine import calculate_farm_economic_roi
from src.climate_alerts import evaluate_climate_hazards


def render_html_clean(html_content: str):
    """
    Renders HTML safely in Streamlit without triggering Markdown 4-space code block bugs.
    Trims all leading whitespaces on each line to guarantee no <pre><code> wrappers appear.
    """
    lines = [line.strip() for line in html_content.strip().splitlines() if line.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


def render_orbital_splash_intro(dark_mode: bool = True, force: bool = False):
    """
    Renders a cinematic fullscreen orbital intro on first visit.
    Features:
    - User's Logo with pulsing celestial HUD glow.
    - Rotating 3D Earth sphere with atmospheric cyan halo.
    - 3D Orbiting Satellite sweeping in perspective with a luminous solar trail.
    - Dynamic Mission Control Telemetry Ticker & Progress Bar.
    - Smooth 1-second fade-out/zoom transition into the main application.
    """
    logo_base64 = get_logo_base64()
    splash_id = f"agroorbit-splash-{int(time.time()*1000)}" if force else "agroorbit-splash"

    splash_html = f"""
    <div id="{splash_id}" class="splash-fullscreen-overlay">
        <!-- Cosmic Starfield Texture -->
        <div class="splash-starfield"></div>

        <div class="splash-arena">
            <!-- Concentric Orbital Gyroscopes -->
            <div class="gyro-ring gyro-outer"></div>
            <div class="gyro-ring gyro-inner"></div>

            <!-- 3D Orbit Path & Sweeping Satellite -->
            <div class="satellite-orbit-track">
                <div class="orbiting-satellite-unit">
                    <span class="satellite-body">🛰️</span>
                    <div class="satellite-light-glare"></div>
                </div>
            </div>

            <!-- Central Rotating 3D Earth Globe -->
            <div class="earth-globe-sphere">
                <div class="earth-continents-layer">
                    <svg viewBox="0 0 1000 500" class="continents-svg">
                        <!-- Seamless World Map Continents for Infinite Horizontal Rotation -->
                        <path fill="#22c55e" opacity="0.85" d="M150,120 Q180,90 220,110 T280,140 T320,110 T300,180 T260,220 T210,250 T170,220 T140,160 Z M190,260 Q220,290 240,360 T220,440 T190,410 T170,320 Z M460,90 Q510,70 560,90 T610,130 T570,180 T510,150 Z M480,190 Q540,180 580,220 T590,320 T550,420 T490,390 T460,280 Z M650,110 Q730,90 820,120 T890,190 T840,260 T760,240 T680,180 Z M760,320 Q820,310 850,360 T820,410 T750,380 Z" />
                        <path fill="#22c55e" opacity="0.85" d="M650,120 Q680,90 720,110 T780,140 T820,110 T800,180 T760,220 T710,250 T670,220 T640,160 Z M690,260 Q720,290 740,360 T720,440 T690,410 T670,320 Z M960,90 Q1010,70 1060,90 T1110,130 T1070,180 T1010,150 Z" />
                    </svg>
                </div>
                <div class="earth-atmosphere-glow"></div>
            </div>

            <!-- Floating User Logo in HUD Crest -->
            <div class="splash-logo-crest">
                {f'<img src="{logo_base64}" class="splash-logo-img" alt="AgroOrbit Logo" />' if logo_base64 else '<span style="font-size: 3.5rem;">🛰️</span>'}
                <div class="logo-sonar-aura"></div>
            </div>
        </div>

        <!-- Mission Control Branding & Telemetry Status -->
        <div class="splash-content-panel">
            <div class="splash-badge-pill">🛰️ NASA Space Apps Challenge 2026 · Challenge: Field Shift</div>
            <h1 class="splash-brand-title">AgroOrbit | أجرواوربت</h1>
            <p class="splash-brand-sub">المنظومة المدارية الذكية لدعم القرار الزراعي وتكييف المزارع ببيانات وكالة ناسا</p>
            <div class="splash-team-tag">🚀 Team: Nova Squad NASA</div>

            <!-- Dynamic Telemetry Loading Bar -->
            <div class="splash-progress-wrapper">
                <div class="splash-progress-track">
                    <div class="splash-progress-fill"></div>
                </div>
                <div class="splash-telemetry-text">
                    <span id="splash-status-lbl">📡 جاري تهيئة الاتصال المداري المباشر مع أسطول أقمار ناسا (SMAP, POWER, GPM)...</span>
                </div>
            </div>

            <!-- Enter / Skip Mission Control Button -->
            <button id="splash-enter-btn" class="splash-enter-btn" onclick="dismissAgroOrbitSplash()">
                🚀 بدء المهمة فوراً (Start Mission)
            </button>
        </div>
    </div>

    <style>
    /* =======================================================
       Fullscreen Cinematic Space Splash Styling
       ======================================================= */
    .splash-fullscreen-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(ellipse at center, #0a152d 0%, #050b18 55%, #010307 100%);
        z-index: 99999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Alexandria', 'Cairo', sans-serif !important;
        color: #f8fafc;
        overflow: hidden;
        animation: splashFadeAuto 4.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }}

    @keyframes splashFadeAuto {{
        0%, 75% {{ opacity: 1; visibility: visible; pointer-events: all; transform: scale(1); filter: blur(0px); }}
        92% {{ opacity: 0; filter: blur(8px); transform: scale(1.1); }}
        100% {{ opacity: 0; visibility: hidden; pointer-events: none; }}
    }}

    .splash-fullscreen-overlay.splash-exit {{
        opacity: 0 !important;
        transform: scale(1.14) !important;
        filter: blur(10px) !important;
        visibility: hidden !important;
        pointer-events: none !important;
        transition: all 0.75s ease !important;
    }}

    .splash-starfield {{
        position: absolute;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(1px 1px at 30px 40px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 140px 190px, #00e5ff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 320px 380px, #00ff88, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 520px 100px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.2px 1.2px at 700px 460px, #00e5ff, rgba(0,0,0,0));
        background-repeat: repeat;
        background-size: 800px 500px;
        opacity: 0.45;
        animation: starsDrift 30s linear infinite;
    }}

    @keyframes starsDrift {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 800px 500px; }}
    }}

    /* Arena Container */
    .splash-arena {{
        position: relative;
        width: 380px;
        height: 280px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }}

    /* Concentric Gyroscopes */
    .gyro-ring {{
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }}

    .gyro-outer {{
        width: 320px;
        height: 320px;
        border: 1.5px solid rgba(0, 229, 255, 0.25);
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.15);
        transform: rotateX(72deg) rotateY(-20deg);
        animation: spinGyroOuter 16s linear infinite;
    }}

    .gyro-inner {{
        width: 250px;
        height: 250px;
        border: 1.5px dashed rgba(0, 255, 136, 0.35);
        transform: rotateX(72deg) rotateY(25deg);
        animation: spinGyroInner 12s linear infinite reverse;
    }}

    @keyframes spinGyroOuter {{
        from {{ transform: rotateX(72deg) rotateY(-20deg) rotateZ(0deg); }}
        to {{ transform: rotateX(72deg) rotateY(-20deg) rotateZ(360deg); }}
    }}

    @keyframes spinGyroInner {{
        from {{ transform: rotateX(72deg) rotateY(25deg) rotateZ(0deg); }}
        to {{ transform: rotateX(72deg) rotateY(25deg) rotateZ(360deg); }}
    }}

    /* Central 3D Rotating Earth */
    .earth-globe-sphere {{
        position: relative;
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #1d4ed8 0%, #0f2c59 55%, #050e1d 85%, #02050b 100%);
        box-shadow: 
            0 0 50px rgba(0, 229, 255, 0.55),
            inset -22px -22px 35px rgba(0, 0, 0, 0.85),
            inset 12px 12px 25px rgba(0, 229, 255, 0.45);
        overflow: hidden;
        z-index: 2;
    }}

    .earth-continents-layer {{
        position: absolute;
        width: 200%;
        height: 100%;
        top: 0;
        left: 0;
        animation: rotateEarth 10s linear infinite;
        opacity: 0.75;
    }}

    .continents-svg {{
        width: 100%;
        height: 100%;
    }}

    @keyframes rotateEarth {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}

    .earth-atmosphere-glow {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        border-radius: 50%;
        box-shadow: inset 0 0 20px rgba(0, 229, 255, 0.6);
        pointer-events: none;
    }}

    /* Floating Logo Crest */
    .splash-logo-crest {{
        position: absolute;
        z-index: 5;
        width: 88px;
        height: 88px;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: floatLogo 3s ease-in-out infinite alternate;
    }}

    .splash-logo-img {{
        width: 82px;
        height: 82px;
        object-fit: contain;
        filter: drop-shadow(0 0 22px rgba(0, 229, 255, 0.85));
    }}

    @keyframes floatLogo {{
        from {{ transform: translateY(-4px) scale(1); }}
        to {{ transform: translateY(4px) scale(1.04); }}
    }}

    .logo-sonar-aura {{
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 1px solid #00e5ff;
        animation: sonarPulse 2s ease-out infinite;
        pointer-events: none;
    }}

    @keyframes sonarPulse {{
        0% {{ transform: scale(1); opacity: 0.8; }}
        100% {{ transform: scale(1.8); opacity: 0; }}
    }}

    /* 3D Orbit & Satellite */
    .satellite-orbit-track {{
        position: absolute;
        width: 360px;
        height: 140px;
        border-radius: 50%;
        border: 1.5px dashed rgba(0, 229, 255, 0.4);
        transform: rotateX(68deg) rotateY(-22deg);
        z-index: 6;
        pointer-events: none;
    }}

    .orbiting-satellite-unit {{
        position: absolute;
        top: 0;
        left: 50%;
        width: 36px;
        height: 36px;
        margin-left: -18px;
        margin-top: -18px;
        animation: orbit3DSweep 4.5s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .satellite-body {{
        font-size: 1.8rem;
        filter: drop-shadow(0 0 14px #00e5ff) drop-shadow(0 0 25px #00ff88);
        display: inline-block;
    }}

    @keyframes orbit3DSweep {{
        0% {{
            transform: rotate(0deg) translateX(180px) rotate(0deg) scale(0.8);
            z-index: 1;
            opacity: 0.7;
        }}
        25% {{
            transform: rotate(90deg) translateX(70px) rotate(-90deg) scale(1.1);
            z-index: 8;
            opacity: 0.95;
        }}
        50% {{
            transform: rotate(180deg) translateX(180px) rotate(-180deg) scale(1.35);
            z-index: 8;
            opacity: 1;
        }}
        75% {{
            transform: rotate(270deg) translateX(70px) rotate(-270deg) scale(1.0);
            z-index: 1;
            opacity: 0.8;
        }}
        100% {{
            transform: rotate(360deg) translateX(180px) rotate(-360deg) scale(0.8);
            z-index: 1;
            opacity: 0.7;
        }}
    }}

    /* Text & Telemetry Content */
    .splash-content-panel {{
        text-align: center;
        z-index: 10;
        max-width: 620px;
        padding: 0 20px;
    }}

    .splash-badge-pill {{
        display: inline-block;
        background: rgba(0, 229, 255, 0.12);
        border: 1px solid rgba(0, 229, 255, 0.4);
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.82rem;
        color: #00e5ff;
        font-weight: 700;
        margin-bottom: 8px;
        box-shadow: 0 0 16px rgba(0, 229, 255, 0.2);
    }}

    .splash-brand-title {{
        font-size: 2.4rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00e5ff 0%, #00ff88 50%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px rgba(0, 229, 255, 0.5);
        margin: 0 0 4px 0 !important;
    }}

    .splash-brand-sub {{
        color: #cbd5e1;
        font-size: 0.98rem;
        margin: 0 0 6px 0;
        font-weight: 500;
    }}

    .splash-team-tag {{
        color: #00ff88;
        font-size: 0.88rem;
        font-weight: 800;
        margin-bottom: 16px;
    }}

    /* Progress & Telemetry */
    .splash-progress-wrapper {{
        width: 100%;
        max-width: 440px;
        margin: 0 auto 16px auto;
    }}

    .splash-progress-track {{
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(0, 229, 255, 0.3);
    }}

    .splash-progress-fill {{
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #0284c7 0%, #00e5ff 50%, #00ff88 100%);
        box-shadow: 0 0 12px #00e5ff;
        animation: progressLoad 3.4s ease-out forwards;
    }}

    @keyframes progressLoad {{
        0% {{ width: 0%; }}
        30% {{ width: 35%; }}
        70% {{ width: 78%; }}
        100% {{ width: 100%; }}
    }}

    .splash-telemetry-text {{
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 8px;
        min-height: 20px;
    }}

    /* Enter Button */
    .splash-enter-btn {{
        background: linear-gradient(135deg, #0284c7 0%, #00e5ff 100%);
        color: #04101e !important;
        font-family: 'Alexandria', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 26px !important;
        box-shadow: 0 0 22px rgba(0, 229, 255, 0.4) !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
    }}

    .splash-enter-btn:hover {{
        background: linear-gradient(135deg, #00e5ff 0%, #00ff88 100%) !important;
        box-shadow: 0 0 32px rgba(0, 255, 136, 0.6) !important;
        transform: translateY(-2px);
    }}

    @media (max-width: 768px) {{
        .splash-arena {{ width: 300px; height: 220px; }}
        .gyro-outer {{ width: 260px; height: 260px; }}
        .satellite-orbit-track {{ width: 290px; height: 110px; }}
        .earth-globe-sphere {{ width: 120px; height: 120px; }}
        .splash-logo-crest {{ width: 68px; height: 68px; }}
        .splash-logo-img {{ width: 60px; height: 60px; }}
        .splash-brand-title {{ font-size: 1.8rem !important; }}
    }}
    </style>

    <script>
    (function() {{
        const isForced = {"true" if force else "false"};
        const splash = document.getElementById('agroorbit-splash');
        if (!splash) return;

        // Ticker status transitions
        const lbl = document.getElementById('splash-status-lbl');
        if (lbl) {{
            setTimeout(() => {{ if (lbl) lbl.innerText = "🛰️ تم قفل المدار وتدقيق بيانات التربة من SMAP و MERRA-2..."; }}, 1100);
            setTimeout(() => {{ if (lbl) lbl.innerText = "🌾 محرك التدوير الزراعي AgroOrbit متصل وجاهز للتشغيل..."; }}, 2200);
            setTimeout(() => {{ if (lbl) lbl.innerText = "🌍 اكتملت التهيئة المدارية بنجاح · الدخول لغرفة العمليات..."; }}, 3200);
        }}

        window.dismissAgroOrbitSplash = function() {{
            const s = document.getElementById('agroorbit-splash');
            if (s) {{
                s.classList.add('splash-exit');
                setTimeout(() => {{
                    s.style.display = 'none';
                }}, 850);
            }}
            try {{ sessionStorage.setItem('agroorbit_splash_done', '1'); }} catch(e){{}}
        }};

        // Check if already played in this tab unless explicitly forced
        if (!isForced) {{
            try {{
                if (sessionStorage.getItem('agroorbit_splash_done') === '1') {{
                    splash.style.display = 'none';
                    return;
                }}
            }} catch(e){{}}
        }}

        // Auto dismiss after 3.8s
        setTimeout(() => {{
            window.dismissAgroOrbitSplash();
        }}, 3800);
    }})();
    </script>
    """
    render_html_clean(splash_html)

    # Bind button click and session state to parent DOM
    components.html(f"""
    <script>
    (function() {{
        const isForced = {"true" if force else "false"};
        const pDoc = window.parent.document;
        const splashId = "{splash_id}";

        if (isForced) {{
            try {{ sessionStorage.removeItem('agroorbit_splash_done'); }} catch(e){{}}
        }}

        function dismissIntro() {{
            const splash = pDoc.getElementById(splashId) || pDoc.getElementById('agroorbit-splash');
            if (splash && !splash.classList.contains('splash-exit')) {{
                splash.classList.add('splash-exit');
                setTimeout(() => {{ splash.style.display = 'none'; }}, 800);
            }}
            try {{ sessionStorage.setItem('agroorbit_splash_done', '1'); }} catch(e){{}}
        }}

        if (!isForced) {{
            try {{
                if (sessionStorage.getItem('agroorbit_splash_done') === '1') {{
                    const s = pDoc.getElementById(splashId) || pDoc.getElementById('agroorbit-splash');
                    if (s) s.style.display = 'none';
                    return;
                }}
            }} catch(e){{}}
        }}

        let attempts = 0;
        const interval = setInterval(() => {{
            attempts++;
            const btn = pDoc.getElementById('splash-enter-btn');
            if (btn) {{
                btn.onclick = dismissIntro;
                btn.addEventListener('click', dismissIntro);
                clearInterval(interval);
            }}
            if (attempts > 30) clearInterval(interval);
        }}, 80);
    }})();
    </script>
    """, height=0)


def render_header(dark_mode: bool = True):
    """Render the NASA Mission Control Orbital header with Logo."""
    badge_bg = "rgba(0, 229, 255, 0.12)" if dark_mode else "rgba(2, 132, 199, 0.12)"
    badge_color = "#00e5ff" if dark_mode else "#0284c7"
    subtitle_color = "#94a3b8" if dark_mode else "#475569"
    logo_base64 = get_logo_base64()

    logo_markup = f"""
    <div style="margin-bottom: 12px;">
        <img src="{logo_base64}" style="width: 88px; height: 88px; object-fit: contain; filter: drop-shadow(0 0 22px rgba(0, 229, 255, 0.7));" alt="AgroOrbit Logo" />
    </div>
    """ if logo_base64 else ""

    header_html = f"""
    <div style="text-align: center; margin-bottom: 22px;">
        {logo_markup}
        <div class="orbital-badge" style="background: {badge_bg}; color: {badge_color};">🛰️ NASA Space Apps Challenge 2026 · Challenge: Field Shift</div>
        <div class="orbital-title">AgroOrbit | أجرواوربت</div>
        <p style="color: {subtitle_color}; font-size: 1.05rem; margin-top: 4px; font-weight: 600;">
            المنظومة المدارية الذكية لدعم القرار الزراعي وتكييف المزارع ببيانات وكالة ناسا
        </p>
        <div style="font-size: 0.85rem; color: #00ff88; font-weight: 700;">
            🚀 Team: Nova Squad NASA
        </div>
    </div>
    """
    render_html_clean(header_html)


def render_telemetry_hud(telemetry: Dict[str, Any], dark_mode: bool = True):
    """Render high-tech orbital telemetry metrics bar."""
    indices = telemetry.get("indices", {})
    confidence = telemetry.get("confidence_score", 90.0)
    is_live = telemetry.get("is_live", False)

    status_label = "🟢 اتصال حي مع ناسا (Live NASA Telemetry)" if is_live else "🟡 وضع الكاش المناخي (Calibrated Baseline)"
    status_color = "#00ff88" if is_live else "#ff9100"

    status_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 4px 8px;">
        <span style="color: {status_color}; font-size: 0.88rem; font-weight: 700;">{status_label}</span>
        <span style="color: {'#94a3b8' if dark_mode else '#64748b'}; font-size: 0.88rem;">درجة موثوقية الرصد: <b style="color: #00e5ff;">{confidence:.1f}%</b></span>
    </div>
    """
    render_html_clean(status_html)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_html_clean(f"""
        <div class="hud-card" style="text-align: center;">
            <div style="font-size: 1.6rem;">🌡️</div>
            <div class="telemetry-val">{indices.get('avg_temp_c', 22.0)}°C</div>
            <div class="telemetry-label">متوسط الحرارة (T2M)</div>
            <div style="font-size: 0.72rem; color: #64748b;">قصوى: {indices.get('max_temp_c')}°C | دنيا: {indices.get('min_temp_c')}°C</div>
        </div>
        """)

    with col2:
        render_html_clean(f"""
        <div class="hud-card" style="text-align: center;">
            <div style="font-size: 1.6rem;">🌧️</div>
            <div class="telemetry-val">{indices.get('total_precip_mm', 0.0)} <span style="font-size: 1rem;">ملم</span></div>
            <div class="telemetry-label">الهطول المطري (GPM)</div>
            <div style="font-size: 0.72rem; color: #64748b;">الرطوبة النسبية: {indices.get('avg_relative_humidity')}%</div>
        </div>
        """)

    with col3:
        render_html_clean(f"""
        <div class="hud-card" style="text-align: center;">
            <div style="font-size: 1.6rem;">💧</div>
            <div class="telemetry-val">{indices.get('soil_moisture_score', 50.0)}%</div>
            <div class="telemetry-label">رطوبة التربة (SMAP)</div>
            <div style="font-size: 0.72rem; color: #64748b;">جذرية: {indices.get('avg_root_zone_moisture')} | سطحية: {indices.get('avg_surface_moisture')}</div>
        </div>
        """)

    with col4:
        render_html_clean(f"""
        <div class="hud-card" style="text-align: center;">
            <div style="font-size: 1.6rem;">☀️</div>
            <div class="telemetry-val">{indices.get('avg_solar_radiation_mj', 18.5)}</div>
            <div class="telemetry-label">الإشعاع الشمسي (POWER)</div>
            <div style="font-size: 0.72rem; color: #64748b;">GDD: {indices.get('growing_degree_days')} | أيام حرجة: {indices.get('extreme_heat_days')}</div>
        </div>
        """)


def render_nasa_daily_table(telemetry: Dict[str, Any], days: int = 10, dark_mode: bool = True):
    """
    Renders daily temperature and precipitation records for the past 10 days from NASA POWER.
    Replaces raw Excel-like st.dataframe with a sleek, futuristic glassmorphic table.
    """
    params = telemetry.get("cleaned_parameters", {})
    t2m_dict = params.get("T2M", {})
    t2m_max_dict = params.get("T2M_MAX", {})
    t2m_min_dict = params.get("T2M_MIN", {})
    rain_dict = params.get("PRECTOTCORR", {})
    rh_dict = params.get("RH2M", {})
    gwet_dict = params.get("GWETROOT", {})

    all_dates = sorted(t2m_dict.keys())
    selected_dates = all_dates[-days:] if len(all_dates) >= days else all_dates

    if not selected_dates:
        st.info("لا توجد بيانات يومية مسجلة لهذه الإحداثيات حالياً.")
        return

    # Build Futuristic Orbital Glass Table HTML
    table_html = """
    <div class="orbital-table-card">
        <table class="orbital-table">
            <thead>
                <tr>
                    <th>📅 التاريخ (Date)</th>
                    <th>🌡️ متوسط الحرارة</th>
                    <th>🔺 القصوى</th>
                    <th>🔻 الدنيا</th>
                    <th>🌧️ الأمطار (GPM)</th>
                    <th>💨 الرطوبة</th>
                    <th>🌱 رطوبة الجذور (SMAP)</th>
                </tr>
            </thead>
            <tbody>
    """

    chart_dates = []
    chart_temps = []
    chart_rains = []

    for d in selected_dates:
        formatted_date = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else d
        t_avg = t2m_dict.get(d, 22.0)
        t_max = t2m_max_dict.get(d, t_avg + 4.0)
        t_min = t2m_min_dict.get(d, t_avg - 4.0)
        rain = rain_dict.get(d, 0.0)
        rh = rh_dict.get(d, 50.0)
        gwet = gwet_dict.get(d, 0.4)

        chart_dates.append(formatted_date)
        chart_temps.append(round(t_avg, 1))
        chart_rains.append(round(rain, 2))

        # Temperature Badge Logic
        if t_avg >= 28:
            temp_badge = f'<span class="badge-pill badge-orange">{t_avg:.1f} °C</span>'
        elif t_avg <= 16:
            temp_badge = f'<span class="badge-pill badge-blue">{t_avg:.1f} °C</span>'
        else:
            temp_badge = f'<span class="badge-pill badge-cyan">{t_avg:.1f} °C</span>'

        # Rain Badge Logic
        if rain > 0.05:
            rain_badge = f'<span class="badge-pill badge-blue">💧 {rain:.2f} ملم</span>'
        else:
            rain_badge = '<span style="color: #64748b; font-size: 0.8rem;">0.0 ملم (جاف)</span>'

        gwet_pct = round(gwet * 100, 1)

        table_html += f"""
        <tr>
            <td style="font-weight: 700; color: {'#38bdf8' if dark_mode else '#0284c7'};">{formatted_date}</td>
            <td>{temp_badge}</td>
            <td style="color: #f87171; font-weight: 600;">{t_max:.1f} °C</td>
            <td style="color: #38bdf8; font-weight: 600;">{t_min:.1f} °C</td>
            <td>{rain_badge}</td>
            <td>{rh:.0f}%</td>
            <td><span class="badge-pill badge-green">{gwet_pct}%</span></td>
        </tr>
        """

    table_html += """
            </tbody>
        </table>
    </div>
    """
    render_html_clean(table_html)

    # Plotly Trend Chart with Alexandria / Cairo Typography
    fig = go.Figure()

    # Temperature Line
    fig.add_trace(go.Scatter(
        x=chart_dates,
        y=chart_temps,
        mode="lines+markers",
        name="متوسط الحرارة (°C)",
        line=dict(color="#00e5ff" if dark_mode else "#0284c7", width=3),
        marker=dict(size=7, color="#00e5ff" if dark_mode else "#0284c7")
    ))

    # Rainfall Bar
    fig.add_trace(go.Bar(
        x=chart_dates,
        y=chart_rains,
        name="الأمطار (ملم)",
        yaxis="y2",
        marker=dict(color="rgba(0, 255, 136, 0.65)" if dark_mode else "rgba(5, 150, 105, 0.65)")
    ))

    fig.update_layout(
        title=dict(
            text=f"📈 منحنى التغير اليومي للحرارة وهطول الأمطار لآخر {len(selected_dates)} أيام (NASA POWER)",
            font=dict(color="#00e5ff" if dark_mode else "#0284c7", size=14, family="Alexandria, Cairo, sans-serif")
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(10, 18, 36, 0.4)" if dark_mode else "rgba(241, 245, 249, 0.5)",
        font=dict(family="Alexandria, Cairo, sans-serif"),
        yaxis=dict(
            title=dict(text="درجة الحرارة (°C)", font=dict(color="#00e5ff" if dark_mode else "#0284c7")),
            tickfont=dict(color="#94a3b8" if dark_mode else "#64748b"),
            gridcolor="rgba(0, 229, 255, 0.1)" if dark_mode else "rgba(0, 0, 0, 0.08)"
        ),
        yaxis2=dict(
            title=dict(text="الأمطار (ملم)", font=dict(color="#00ff88" if dark_mode else "#059669")),
            tickfont=dict(color="#00ff88" if dark_mode else "#059669"),
            overlaying="y",
            side="right"
        ),
        xaxis=dict(
            tickfont=dict(color="#94a3b8" if dark_mode else "#64748b"),
            gridcolor="rgba(0, 229, 255, 0.05)" if dark_mode else "rgba(0, 0, 0, 0.05)"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=30),
        height=320
    )

    st.plotly_chart(fig, theme=None, use_container_width=True)


def render_strategy_card(strat: Dict[str, Any], dark_mode: bool = True):
    """
    Renders an individual NASA Strategy Card.
    Avoids 4-space markdown indentations to ensure no unwanted code blocks appear.
    """
    badge_color = strat.get("badge_color", "#00e5ff")
    metrics = strat.get("metrics", {})
    timeline = strat.get("timeline", [])

    render_html_clean(f"""
    <div class="hud-card" style="border-right: 6px solid {badge_color} !important; margin-bottom: 20px;">
        <h3 style="margin: 0 0 6px 0; color: {badge_color} !important; font-size: 1.35rem;">
            {strat.get('tag_ar')}
        </h3>
        <p style="color: {'#cbd5e1' if dark_mode else '#334155'}; font-size: 1rem; margin-bottom: 8px;">
            {strat.get('summary_ar')}
        </p>
    </div>
    """)

    # 3 Seasons Sequence Cards
    st.markdown("##### 🗓️ تسلسل الدورة المقترحة لـ 3 مواسم متعاقبة:")
    cols = st.columns(3)
    for i, step in enumerate(timeline):
        crop = step["crop"]
        with cols[i]:
            card_bg = "rgba(15, 23, 42, 0.85)" if dark_mode else "#f8fafc"
            card_border = "rgba(0, 229, 255, 0.3)" if dark_mode else "rgba(2, 132, 199, 0.3)"
            crop_color = "#00ff88" if dark_mode else "#059669"
            sub_color = "#cbd5e1" if dark_mode else "#475569"

            render_html_clean(f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <div style="font-size: 0.82rem; color: #94a3b8; font-weight: 700;">{step['season_ar']}</div>
                <div style="font-size: 1.35rem; font-weight: 900; color: {crop_color}; margin: 4px 0;">{crop.get('name_ar')}</div>
                <div style="font-size: 0.8rem; color: {sub_color};">{crop.get('season_label_ar')}</div>
                <div style="font-size: 0.78rem; color: #00e5ff; font-weight: 700; margin-top: 6px;">
                    💧 {crop.get('water_demand_mm')} ملم | 🌿 {crop.get('profit_level')}
                </div>
            </div>
            """)

    # Key Performance Indicators
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("💧 إجمالي استهلاك المياه", f"{metrics.get('total_water_mm', 0):.0f} ملم")
    with m_col2:
        st.metric("🌱 نسبة وفر المياه", f"+{metrics.get('water_savings_pct', 0):.1f}%")
    with m_col3:
        n_val = metrics.get('net_nitrogen_kg_ha', 0)
        st.metric("🌾 ميزان النيتروجين الحيوي", f"{n_val:+.0f} كجم/هكتار")
    with m_col4:
        st.metric("🛡️ كفاءة كسر الآفات", f"{metrics.get('pest_break_efficiency_pct', 0):.0f}%")

    # NASA Concise Analytical Sections
    with st.expander("📑 التقرير التحليلي الرسمي المعتمد لناسا (NASA Analytical Disclosure)"):
        st.markdown(f"**1. لماذا اقترحناها؟ (Why Suggested):**\n{strat.get('why_suggested')}")
        st.markdown("---")
        st.markdown(f"**2. الأدلة الفضائية الداعمة (NASA Satellite Telemetry Evidence):**\n{strat.get('evidence')}")
        st.markdown("---")
        st.markdown(f"**3. الفوائد الكمية المتوقعة (Quantitative Benefits):**\n{strat.get('benefits')}")
        st.markdown("---")
        st.markdown(f"**4. فجوات البيانات الفضائية ومناطق عدم اليقين (Information Gaps):**\n{strat.get('information_gaps')}")
        st.markdown("---")
        st.markdown(f"**5. تقييم المخاطر ومراجعة الخبير المحلي (Risks & Agronomist Review):**\n{strat.get('risks_and_agronomist_review')}")


def render_comparison_matrix_table(matrix_data: List[Dict[str, Any]], dark_mode: bool = True):
    """
    Render side-by-side strategy comparison table in futuristic glassmorphism theme.
    Guaranteed zero code block formatting bugs.
    """
    st.markdown("### ⚖️ جدول المقارنة المباشر بين الاستراتيجيات الثلاث (Side-by-Side Comparison)")

    table_html = """
    <div class="orbital-table-card">
        <table class="orbital-table">
            <thead>
                <tr>
                    <th style="width: 28%;">📌 المعيار / مؤشر التقييم</th>
                    <th style="color: #ff9100; width: 24%;">🟠 الاستراتيجية 1 (الوضع الراهن)</th>
                    <th style="color: #00ff88; width: 24%;">🟢 الاستراتيجية 2 (صحة التربة BNF)</th>
                    <th style="color: #00e5ff; width: 24%;">🔵 الاستراتيجية 3 (التكيف المائي)</th>
                </tr>
            </thead>
            <tbody>
    """

    for row in matrix_data:
        crit = row["criterion_ar"]
        s1 = row["strategy_1"]
        s2 = row["strategy_2"]
        s3 = row["strategy_3"]

        table_html += f"""
        <tr>
            <td style="font-weight: 800; color: {'#00e5ff' if dark_mode else '#0284c7'};">{crit}</td>
            <td style="color: {'#cbd5e1' if dark_mode else '#475569'};">{s1}</td>
            <td style="color: {'#a7f3d0' if dark_mode else '#059669'}; font-weight: 700;">{s2}</td>
            <td style="color: {'#bae6fd' if dark_mode else '#0284c7'}; font-weight: 700;">{s3}</td>
        </tr>
        """

    table_html += """
            </tbody>
        </table>
    </div>
    """
    render_html_clean(table_html)


def render_crops_knowledge_table(crops_database: Dict[str, Any], dark_mode: bool = True):
    """
    Renders the 11 Strategic Crops Knowledge Base in a sleek glassmorphic table.
    Replaces raw Excel-like st.dataframe completely.
    """
    table_html = """
    <div class="orbital-table-card">
        <table class="orbital-table">
            <thead>
                <tr>
                    <th>🌾 المحصول (العربي / English)</th>
                    <th>🗓️ الموسم</th>
                    <th>🌡️ الحرارة المثلى</th>
                    <th>💧 الاحتياج المائي</th>
                    <th>🌿 تثبيت النيتروجين (BNF)</th>
                    <th>⚖️ ميزان N (كجم/هكتار)</th>
                    <th>💰 مستوى الربحية</th>
                </tr>
            </thead>
            <tbody>
    """

    for cid, c in crops_database.items():
        is_legume = c.get("biological_nitrogen_fixer", False)
        if is_legume:
            bnf_badge = '<span class="badge-pill badge-green">🌾 نعم (+ مثبت)</span>'
            n_val = f'<span style="color: #00ff88; font-weight: 700;">{c["nitrogen_balance_kg_ha"]:+.0f}</span>'
        else:
            bnf_badge = '<span class="badge-pill badge-orange">مستهلك (-)</span>'
            n_val = f'<span style="color: #f87171; font-weight: 600;">{c["nitrogen_balance_kg_ha"]:+.0f}</span>'

        water_badge = f'<span class="badge-pill badge-cyan">{c["water_demand_mm"]} ملم</span>'
        profit_badge = f'<span class="badge-pill badge-neutral">{c["profit_level"]}</span>'

        table_html += f"""
        <tr>
            <td style="font-weight: 800; color: {'#f8fafc' if dark_mode else '#0f172a'};">
                {c['name_ar']} <span style="font-size: 0.8rem; color: #94a3b8;">({c['name_en']})</span>
            </td>
            <td>{c['season_label_ar']}</td>
            <td>{c['temp_opt_min']} - {c['temp_opt_max']} °C</td>
            <td>{water_badge}</td>
            <td>{bnf_badge}</td>
            <td>{n_val}</td>
            <td>{profit_badge}</td>
        </tr>
        """

    table_html += """
            </tbody>
        </table>
    </div>
    """
    render_html_clean(table_html)


def render_diseases_visual_atlas(diseases_catalog: List[Dict[str, Any]], dark_mode: bool = True):
    """
    Renders an interactive, visually stunning plant pathology atlas.
    Displays real scientific imagery, field diagnostic symptoms, biological pest-break mechanisms,
    and NASA satellite telemetry early-warning correlations.
    """
    st.markdown("### 🔬 الأطلس الميداني البصري لتشخيص وكسر دورات الأمراض النباتية")
    st.write("أدلة مصورة لتشخيص أخطر الأمراض والآفات في الحقول المصرية وكيف تكسر دورات AgroOrbit الزراعية دورات حياتها بيولوجياً:")

    # Filter by host crop
    crop_filter_options = {
        "all": "🌟 جميع المحاصيل (12 مرض وآفة)",
        "wheat": "🌾 القمح (Wheat)",
        "faba_bean": "🌱 الفول البلدي (Faba Bean)",
        "tomato": "🍅 الطماطم والبطاطس (Solanaceae)",
        "maize": "🌽 الذرة الشامية (Maize)",
        "onion": "🧅 البصل والثوم (Onion & Alliums)",
        "sugar_beet": "🌿 بنجر السكر (Sugar Beet)",
        "cotton": "☁️ القطن المصري (Cotton)",
        "clover": "🍀 البرسيم المصري (Clover)"
    }

    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        selected_filter = st.selectbox(
            "تصفية الأمراض والآفات حسب المحصول العائل:",
            options=list(crop_filter_options.keys()),
            format_func=lambda x: crop_filter_options[x],
            index=0
        )

    if selected_filter == "all":
        filtered_diseases = diseases_catalog
    else:
        filtered_diseases = [d for d in diseases_catalog if d["crop_id"] == selected_filter]

    with f_col2:
        st.markdown(f"""
        <div style="background: rgba(0, 229, 255, 0.08); border-right: 4px solid #00e5ff; padding: 8px 12px; border-radius: 8px; margin-top: 25px; font-size: 0.85rem;">
            📌 معروض: <b>{len(filtered_diseases)}</b> إصابة حقلية مصورة
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # 2-Column Responsive Card Grid
    for i in range(0, len(filtered_diseases), 2):
        row_cols = st.columns(2)
        for col_idx, d in enumerate(filtered_diseases[i:i+2]):
            with row_cols[col_idx]:
                card_bg = "rgba(13, 22, 44, 0.85)" if dark_mode else "#ffffff"
                card_border = "rgba(0, 229, 255, 0.3)" if dark_mode else "#cbd5e1"
                accent_c = "#00e5ff" if dark_mode else "#0284c7"
                img_path = config.ROOT_DIR / "assets" / "diseases" / d["image_file"]

                # Card Outer Container
                render_html_clean(f"""
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 16px; padding: 18px; margin-bottom: 22px; box-shadow: 0 6px 24px rgba(0,0,0,0.25);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                        <div>
                            <h4 style="margin: 0; color: {accent_c}; font-size: 1.2rem;">🦠 {d['name_ar']}</h4>
                            <span style="font-size: 0.82rem; color: #94a3b8; font-style: italic;">{d['scientific_name']}</span>
                        </div>
                        <span class="badge-pill badge-cyan">{d['crop_name_ar']}</span>
                    </div>
                </div>
                """)

                # Display Image
                if img_path.exists():
                    st.image(
                        str(img_path),
                        caption=f"أعراض {d['name_ar']} — {d['scientific_name']}",
                        use_container_width=True
                    )
                else:
                    st.info("الصورة قيد المعالجة...")

                # Disease Details & NASA Integration
                breaking_chips = " ".join([f"<span class='badge-pill badge-green'>🌾 {b}</span>" for b in d.get("breaking_crops", [])])

                render_html_clean(f"""
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-top: none; border-radius: 0 0 16px 16px; padding: 14px 18px; margin-top: -24px; margin-bottom: 22px;">
                    <div style="font-size: 0.88rem; line-height: 1.65; color: {'#e2e8f0' if dark_mode else '#1e293b'};">
                        <p style="margin: 6px 0;"><b>🔍 الأعراض الحقلية المرئية:</b> {d['symptoms_ar']}</p>
                        <p style="margin: 6px 0;"><b>🛡️ آلية الكسر بالتدوير:</b> {d['pest_break_ar']}</p>
                        <div style="margin: 8px 0;"><b>🌱 المحاصيل المقترحة لكسر الدورة:</b> {breaking_chips}</div>
                        <div style="background: rgba(255, 145, 0, 0.12); border-right: 4px solid #ff9100; padding: 8px 12px; border-radius: 8px; margin-top: 10px;">
                            <span style="color: #ff9100; font-weight: 800; font-size: 0.84rem;">🛰️ تنبيه استشعار ناسا المبكر:</span>
                            <div style="font-size: 0.82rem; color: {'#cbd5e1' if dark_mode else '#334155'}; margin-top: 2px;">{d['nasa_trigger_condition']}</div>
                        </div>
                    </div>
                </div>
                """)


def render_scientific_disclaimer():
    """Render official NASA challenge honesty and uncertainty disclaimer."""
    render_html_clean("""
    <div class="hud-card" style="border: 1px solid rgba(255, 145, 0, 0.3) !important; background: rgba(25, 20, 10, 0.5) !important;">
        <h4 style="color: #ff9100 !important; margin: 0 0 6px 0; font-size: 1rem;">
            ⚠️ إخلاء المسؤولية العلمية والحدود الفنية (NASA Scientific Disclaimer)
        </h4>
        <p style="font-size: 0.85rem; line-height: 1.6; margin: 0;">
            تأتي بيانات علوم الأرض من وكالة ناسا (مثل NASA POWER و MERRA-2 و SMAP) بدقة مكانية إقليمية (~0.5° × 0.625° أي قرابة 50 كم). 
            تُعد هذه البيانات ممتازة لرصد الاتجاهات المناخية الإقليمية، والإشعاع الشمسي، ومتطلبات البخر نتح، ولكنها لا تكتشف الفروق الطبوغرافية الدقيقة 
            داخل الحقل الواحد أو تباينات شبكات الري بالتنقيط الفردية. 
            <b>منظومة AgroOrbit صُممت كأداة استرشادية لدعم القرار الزراعي وليس بديلاً عن الفحص المعملي الميداني للتربة والمياه أو استشارة الخبير الزراعي.</b>
        </p>
    </div>
    """)


def render_ai_voice_advisor(metadata: Dict[str, Any], strategies: Dict[str, Any], dark_mode: bool = True):
    """
    Renders the NASA AgroOrbit AI Voice Agro-Advisor (المساعد الصوتي الزراعي الفضائي).
    Features:
    - Warm, practical Egyptian colloquial Arabic tailored to the farmer's soil and telemetry.
    - 4 selectable briefing angles (Comprehensive, Soil BNF, Water Resilience, Pest Break).
    - Instant voice synthesis with disk-cached MP3 generation via gTTS.
    - Glassmorphism HUD player with animated voice equalizer waves.
    - Collapsible written transcript with highlighted numbers.
    - WhatsApp / Offline MP3 download button.
    """
    card_bg = "rgba(13, 22, 44, 0.85)" if dark_mode else "#ffffff"
    card_border = "rgba(0, 229, 255, 0.35)" if dark_mode else "#93c5fd"
    text_color = "#f8fafc" if dark_mode else "#0f172a"
    accent_cyan = "#00e5ff" if dark_mode else "#0284c7"
    accent_green = "#00ff88" if dark_mode else "#16a34a"

    render_html_clean(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0, 229, 255, 0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 50px; height: 50px; border-radius: 14px; background: linear-gradient(135deg, rgba(0,229,255,0.2), rgba(0,255,136,0.2)); border: 1px solid {accent_cyan}; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 0 16px rgba(0,229,255,0.3);">
                    🎙️
                </div>
                <div>
                    <h3 style="margin: 0; color: {accent_cyan}; font-size: 1.3rem; font-weight: 800;">
                        المستشار الزراعي الصوتي الذكي (AI Voice Agro-Advisor)
                    </h3>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 3px;">
                        إحاطة إرشادية بلهجة مصرية مبسطة للمزارع مدعومة بأقمار وكالة ناسا (POWER, SMAP)
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <div class="voice-eq-container" style="display: flex; align-items: center; gap: 3px; height: 26px; padding: 0 8px; background: rgba(0, 229, 255, 0.08); border-radius: 20px;">
                    <span style="width: 3px; height: 10px; background: {accent_cyan}; border-radius: 2px;"></span>
                    <span style="width: 3px; height: 20px; background: {accent_green}; border-radius: 2px;"></span>
                    <span style="width: 3px; height: 14px; background: {accent_cyan}; border-radius: 2px;"></span>
                    <span style="width: 3px; height: 22px; background: #a855f7; border-radius: 2px;"></span>
                    <span style="width: 3px; height: 8px; background: {accent_green}; border-radius: 2px;"></span>
                </div>
                <span class="badge-pill badge-cyan">🇪🇬 لهجة مصرية أصيلة</span>
                <span class="badge-pill badge-green">🛰️ تليمترية حية</span>
            </div>
        </div>
    </div>
    """)

    b_options = {
        "comprehensive": "🎙️ الإحاطة المدارية الشاملة (ملخص عام وتوجيه ذهبي للمزرعة)",
        "soil_health": "🌿 استشارة صحة التربة وتوفير شكاير اليوريا (تثبيت النيتروجين BNF)",
        "water_resilience": "💧 استشارة التكيف المائي وترشيد الري ومجابهة موجات الحر",
        "pest_prevention": "⚠️ استشارة وقاية النبات وكسر دورات الآفات الفطرية والحشرية"
    }

    selected_briefing = st.radio(
        "🎧 اختر زاوية الاستشارة الصوتية المطلوبة للمزرعة:",
        options=list(b_options.keys()),
        format_func=lambda x: b_options[x],
        horizontal=True,
        key="selected_voice_briefing_type"
    )

    script_text = generate_voice_script(selected_briefing, metadata, strategies)

    with st.spinner("جاري استحضار الصوت والاتصال بمنظومة التوليف الصوتي المداري..."):
        audio_bytes = get_agro_voice_audio(script_text)

    # Audio player and download bar
    v_col1, v_col2 = st.columns([3, 1])
    with v_col1:
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.warning("تعذر توليف الصوت مؤقتاً، يمكنك قراءة نص الاستشارة بالأسفل.")
    with v_col2:
        if audio_bytes:
            st.download_button(
                label="📲 تحميل الرسالة (MP3)",
                data=audio_bytes,
                file_name=f"agroorbit_voice_{selected_briefing}.mp3",
                mime="audio/mp3",
                use_container_width=True,
                help="حفظ الرسالة الصوتية للاستماع إليها بدون إنترنت في الغيط أو مشاركتها عبر واتساب"
            )

    # Collapsible written transcript
    with st.expander("📜 قراءة نص الاستشارة المكتوبة بالتزامن مع الصوت", expanded=True):
        formatted_script = script_text.replace("\n", "<br>")
        render_html_clean(f"""
        <div style="background: {'rgba(15, 23, 42, 0.75)' if dark_mode else '#f1f5f9'}; border-right: 4px solid {accent_cyan}; padding: 16px 20px; border-radius: 10px; font-size: 1.02rem; line-height: 1.9; color: {text_color}; font-weight: 500; direction: rtl; text-align: right; box-shadow: inset 0 2px 8px rgba(0,0,0,0.2);">
            {formatted_script}
        </div>
        """)


def render_pdf_report_exporter(
    metadata: Dict[str, Any],
    strategies: Dict[str, Any],
    telemetry: Dict[str, Any],
    dark_mode: bool = True
):
    """
    Renders the NASA Field Advisory Report Exporter module (Feature #2).
    Provides one-click export of an official, print-ready A4 PDF document,
    interactive HTML export, and real-time document preview.
    """
    card_bg = "rgba(13, 22, 44, 0.85)" if dark_mode else "#ffffff"
    card_border = "rgba(0, 229, 255, 0.35)" if dark_mode else "#93c5fd"
    accent_cyan = "#00e5ff" if dark_mode else "#0284c7"
    accent_green = "#00ff88" if dark_mode else "#16a34a"
    text_color = "#f8fafc" if dark_mode else "#0f172a"

    render_html_clean(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 16px; padding: 22px; margin-top: 24px; margin-bottom: 22px; box-shadow: 0 8px 32px rgba(0, 229, 255, 0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 50px; height: 50px; border-radius: 14px; background: linear-gradient(135deg, rgba(2,132,199,0.25), rgba(0,229,255,0.25)); border: 1px solid {accent_cyan}; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 0 16px rgba(0,229,255,0.3);">
                    📑
                </div>
                <div>
                    <h3 style="margin: 0; color: {accent_cyan}; font-size: 1.3rem; font-weight: 800;">
                        التقرير الاستشاري الميداني الرسمي (Official NASA Field Advisory PDF)
                    </h3>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 3px;">
                        وثيقة استشارية معتمدة ومصممة للطباعة القياسية A4 للمرشدين الزراعيين، مديري المزارع، والجهات التمويلية
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge-pill badge-green">📄 جاهز للطباعة A4</span>
                <span class="badge-pill badge-cyan">🛰️ معتمد برقم تتبع مداري</span>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 14px; margin-bottom: 18px;">
            <div style="background: {'rgba(15, 23, 42, 0.6)' if dark_mode else '#f8fafc'}; border: 1px solid {'rgba(255,255,255,0.08)' if dark_mode else '#e2e8f0'}; border-radius: 10px; padding: 12px;">
                <div style="font-size: 0.8rem; color: #94a3b8;">محتوى التقرير الاستشاري</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: {text_color}; margin-top: 3px;">3 استراتيجيات محصولية متكاملة</div>
            </div>
            <div style="background: {'rgba(15, 23, 42, 0.6)' if dark_mode else '#f8fafc'}; border: 1px solid {'rgba(255,255,255,0.08)' if dark_mode else '#e2e8f0'}; border-radius: 10px; padding: 12px;">
                <div style="font-size: 0.8rem; color: #94a3b8;">تليمترية ناسا الموثقة</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: {text_color}; margin-top: 3px;">حرارة، رطوبة، أمطار، وإشعاع POWER</div>
            </div>
            <div style="background: {'rgba(15, 23, 42, 0.6)' if dark_mode else '#f8fafc'}; border: 1px solid {'rgba(255,255,255,0.08)' if dark_mode else '#e2e8f0'}; border-radius: 10px; padding: 12px;">
                <div style="font-size: 0.8rem; color: #94a3b8;">المؤشرات الاقتصادية</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: {accent_green}; margin-top: 3px;">حسابات وفر اليوريا ومياه الري للفدان</div>
            </div>
        </div>
    </div>
    """)

    report_filename = f"AgroOrbit_NASA_Advisory_Report_{abs(hash(str(metadata))) % 1000000:06d}.pdf"
    cached_pdf_path = REPORTS_CACHE_DIR / report_filename

    pdf_bytes = None
    if cached_pdf_path.exists():
        try:
            with open(cached_pdf_path, "rb") as f:
                pdf_bytes = f.read()
        except Exception:
            pass

    if not pdf_bytes:
        with st.spinner("جاري صياغة التقرير الاستشاري الرسمي واعتماده بصيغة PDF..."):
            pdf_bytes = generate_advisory_pdf(metadata, strategies, telemetry, report_filename)

    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:
        if pdf_bytes:
            st.download_button(
                label="📥 تحميل التقرير الاستشاري المعتمد (PDF)",
                data=pdf_bytes,
                file_name=report_filename,
                mime="application/pdf",
                use_container_width=True,
                help="تحميل وثيقة PDF رسمية جاهزة للطباعة الورقية A4 والأرشفة"
            )
        else:
            st.warning("تعذر تصدير PDF التلقائي، يمكنك استخدام النسخة التفاعلية بالجانب.")

    with btn_col2:
        html_report = build_advisory_html_report(metadata, strategies, telemetry)
        st.download_button(
            label="🌐 تحميل نسخة التقرير الرقمية (HTML)",
            data=html_report.encode("utf-8"),
            file_name=report_filename.replace(".pdf", ".html"),
            mime="text/html",
            use_container_width=True,
            help="تحميل صفحة الويب الكاملة لفتحها وطباعتها مباشرة من أي متصفح"
        )

    with st.expander("👁️ استعراض مباشر لمعاينة وثيقة التقرير الاستشاري (A4 Print Preview)", expanded=False):
        components.html(html_report, height=650, scrolling=True)


def render_economic_roi_calculator(
    strategies: Dict[str, Any],
    dark_mode: bool = True
):
    """
    Renders the NASA AgroOrbit Farm Economic & Resource ROI Calculator (Feature #1).
    Allows interactive acreage inputs (Feddans) and calculates financial returns in EGP,
    water volume savings in m³, fertilizer urea bag offsets, and carbon footprint reduction.
    """
    s1 = strategies.get("strategy_1_baseline", {})
    s2 = strategies.get("strategy_2_soil_health", {})
    s3 = strategies.get("strategy_3_water_resilience", {})

    card_bg = "rgba(13, 22, 44, 0.85)" if dark_mode else "#ffffff"
    card_border = "rgba(0, 229, 255, 0.35)" if dark_mode else "#93c5fd"
    accent_cyan = "#00e5ff" if dark_mode else "#0284c7"
    accent_green = "#00ff88" if dark_mode else "#16a34a"
    accent_amber = "#ff9100" if dark_mode else "#d97706"
    text_color = "#f8fafc" if dark_mode else "#0f172a"
    muted_color = "#94a3b8" if dark_mode else "#64748b"

    render_html_clean(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 16px; padding: 22px; margin-top: 24px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0, 229, 255, 0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 50px; height: 50px; border-radius: 14px; background: linear-gradient(135deg, rgba(0,255,136,0.25), rgba(0,229,255,0.25)); border: 1px solid {accent_green}; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 0 16px rgba(0,255,136,0.3);">
                    💰
                </div>
                <div>
                    <h3 style="margin: 0; color: {accent_green}; font-size: 1.3rem; font-weight: 800;">
                        حاسبة الوفر الاقتصادي والمائي المباشر (Farm ROI & Resource Calculator)
                    </h3>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 3px;">
                        حساب دقيق للمردود المالي بالجنيه المصري، وتوفير مياه الري بالمتر المكعب، وشكاير سماد اليوريا وفق مساحة أرضك بالأفدنة
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge-pill badge-green">🌾 حسابات بالأفدنة</span>
                <span class="badge-pill badge-cyan">🇪🇬 بالجنيه المصري (EGP)</span>
                <span class="badge-pill badge-amber">💧 بالمتر المكعب (m³)</span>
            </div>
        </div>
    </div>
    """)

    # Interactive Inputs
    in_col1, in_col2 = st.columns([2, 1])

    with in_col1:
        farm_area = st.slider(
            "🌾 حدد مساحة المزرعة بالأفدنة (Farm Acreage):",
            min_value=1.0,
            max_value=100.0,
            value=10.0,
            step=1.0,
            format="%.0f فدان"
        )

    with in_col2:
        strat_focus = st.radio(
            "اختر الاستراتيجية للتركيز على حساباتها:",
            options=["soil_health", "water_resilience"],
            format_func=lambda x: "🌿 دورة صحة التربة والنيتروجين (BNF)" if x == "soil_health" else "💧 دورة التكيف المائي وحماية الجفاف",
            key="roi_strat_focus"
        )

    with st.expander("⚙️ تخصيص أسعار وتكاليف السوق المصري (اختياري للتدقيق المالي)", expanded=False):
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            urea_price = st.number_input("سعر شيكارة اليوريا 50 كجم (جنيه):", min_value=250.0, max_value=1500.0, value=750.0, step=25.0)
        with p_col2:
            pumping_cost = st.number_input("تكلفة ضخ متر المياه بالسولار/الكهرباء (جنيه/م³):", min_value=0.40, max_value=3.50, value=1.10, step=0.10)
        with p_col3:
            pesticide_saving = st.number_input("وفر المبيدات لكسر الآفات (جنيه/فدان):", min_value=200.0, max_value=2000.0, value=650.0, step=50.0)

    # Perform ROI Calculations
    roi_data = calculate_farm_economic_roi(
        area_feddan=farm_area,
        strat_baseline=s1,
        strat_soil=s2,
        strat_water=s3,
        urea_bag_price_egp=urea_price,
        pumping_cost_m3_egp=pumping_cost,
        pesticide_saving_per_feddan_egp=pesticide_saving
    )

    chosen_strat = roi_data["strategy_2_soil_health"] if strat_focus == "soil_health" else roi_data["strategy_3_water_resilience"]
    strat_title = chosen_strat["name_ar"]

    # 4 Large Glowing KPI Metric Cards
    render_html_clean(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-top: 14px; margin-bottom: 22px;">
        
        <!-- Metric 1: Financial Gain EGP -->
        <div style="background: {'rgba(16, 185, 129, 0.12)' if dark_mode else '#ecfdf5'}; border: 1px solid {accent_green}; border-radius: 14px; padding: 18px; box-shadow: 0 4px 20px rgba(0,255,136,0.15);">
            <div style="font-size: 0.82rem; color: {accent_green}; font-weight: 700;">💰 إجمالي الوفر المالي التراكمي</div>
            <div style="font-size: 1.85rem; font-weight: 900; color: {text_color}; margin: 6px 0;">{chosen_strat['total_financial_gain_egp']:,.0f} <span style="font-size: 1rem; color: {accent_green};">جنيه</span></div>
            <div style="font-size: 0.8rem; color: {muted_color};">معدل الوفر: <b>{chosen_strat['financial_gain_per_feddan_egp']:,.0f} ج/فدان</b></div>
        </div>

        <!-- Metric 2: Water Volume Saved m3 -->
        <div style="background: {'rgba(0, 229, 255, 0.12)' if dark_mode else '#eff6ff'}; border: 1px solid {accent_cyan}; border-radius: 14px; padding: 18px; box-shadow: 0 4px 20px rgba(0,229,255,0.15);">
            <div style="font-size: 0.82rem; color: {accent_cyan}; font-weight: 700;">💧 حجم مياه الري الموفرة سنوياً</div>
            <div style="font-size: 1.85rem; font-weight: 900; color: {text_color}; margin: 6px 0;">{chosen_strat['water_saved_m3']:,.0f} <span style="font-size: 1rem; color: {accent_cyan};">م³</span></div>
            <div style="font-size: 0.8rem; color: {muted_color};">نسبة التوفير المائي: <b>+{chosen_strat['water_saved_pct']}%</b></div>
        </div>

        <!-- Metric 3: Urea Bags Saved -->
        <div style="background: {'rgba(255, 145, 0, 0.12)' if dark_mode else '#fffbeb'}; border: 1px solid {accent_amber}; border-radius: 14px; padding: 18px; box-shadow: 0 4px 20px rgba(255,145,0,0.15);">
            <div style="font-size: 0.82rem; color: {accent_amber}; font-weight: 700;">🌾 شكاير سماد اليوريا الموفرة (BNF)</div>
            <div style="font-size: 1.85rem; font-weight: 900; color: {text_color}; margin: 6px 0;">{chosen_strat['urea_bags_saved']:,.0f} <span style="font-size: 1rem; color: {accent_amber};">شيكارة</span></div>
            <div style="font-size: 0.8rem; color: {muted_color};">توفير سماد: <b>{chosen_strat['fertilizer_savings_egp']:,.0f} جنيه</b></div>
        </div>

        <!-- Metric 4: CO2 Offset -->
        <div style="background: {'rgba(168, 85, 247, 0.12)' if dark_mode else '#faf5ff'}; border: 1px solid #c084fc; border-radius: 14px; padding: 18px; box-shadow: 0 4px 20px rgba(168,85,247,0.15);">
            <div style="font-size: 0.82rem; color: #c084fc; font-weight: 700;">🌍 خفض الانبعاثات الكربونية</div>
            <div style="font-size: 1.85rem; font-weight: 900; color: {text_color}; margin: 6px 0;">{chosen_strat['co2_offset_tons']:.2f} <span style="font-size: 1rem; color: #c084fc;">طن CO₂e</span></div>
            <div style="font-size: 0.8rem; color: {muted_color};">مكافئ تجنب تصنيع الأسمدة الصناعية</div>
        </div>

    </div>
    """)

    # Visual Comparison Charts (Plotly)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Water Consumption Bar Chart for the farm area
        base_water = roi_data["baseline"]["total_water_m3"]
        s2_water = base_water - roi_data["strategy_2_soil_health"]["water_saved_m3"]
        s3_water = base_water - roi_data["strategy_3_water_resilience"]["water_saved_m3"]

        fig_water = go.Figure()
        fig_water.add_trace(go.Bar(
            x=["الوضع التقليدي (Baseline)", "دورة صحة التربة (BNF)", "دورة التكيف المائي ⭐"],
            y=[base_water, s2_water, s3_water],
            text=[f"{base_water:,.0f} م³", f"{s2_water:,.0f} م³", f"{s3_water:,.0f} م³"],
            textposition="outside",
            marker=dict(
                color=["#ff9100", "#00ff88", "#00e5ff"],
                line=dict(color=["rgba(255,255,255,0.3)", "rgba(255,255,255,0.3)", "rgba(255,255,255,0.3)"], width=1.5)
            )
        ))
        fig_water.update_layout(
            title=dict(text=f"💧 مقارنة إجمالي استهلاك مياه الري لمساحة {farm_area:.0f} فدان (م³)", font=dict(color=text_color, size=13)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
            xaxis=dict(showgrid=False, tickfont=dict(color=text_color, size=11)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color=muted_color, size=10)),
            showlegend=False
        )
        st.plotly_chart(fig_water, use_container_width=True)

    with chart_col2:
        # Donut Chart for Financial Savings Breakdown
        fert_save = chosen_strat["fertilizer_savings_egp"]
        pump_save = chosen_strat["pumping_savings_egp"]
        pest_save = chosen_strat["pesticide_savings_egp"]

        fig_breakdown = go.Figure(data=[go.Pie(
            labels=["وفر الأسمدة (اليوريا)", "وفر طاقة الضخ (مياه)", "وفر المبيدات والآفات"],
            values=[fert_save, pump_save, pest_save],
            hole=0.55,
            marker=dict(colors=["#ff9100", "#00e5ff", "#00ff88"]),
            textinfo="percent+label",
            textfont=dict(color="#ffffff", size=10)
        )])
        fig_breakdown.update_layout(
            title=dict(text=f"💰 توزيع الوفر المالي لمزرعتك ({strat_title.split(':')[0]})", font=dict(color=text_color, size=13)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
            showlegend=False
        )
        st.plotly_chart(fig_breakdown, use_container_width=True)

    # Practical Takeaway Box for the Farmer
    render_html_clean(f"""
    <div style="background: {'rgba(15, 23, 42, 0.75)' if dark_mode else '#f1f5f9'}; border-right: 4px solid {accent_green}; padding: 14px 18px; border-radius: 10px; margin-top: 10px;">
        <h4 style="margin: 0 0 6px 0; color: {accent_green}; font-size: 1.05rem;">
            💡 ماذا تعني هذه الأرقام لمزرعتك ميدانياً ({farm_area:.0f} فدان)؟
        </h4>
        <div style="font-size: 0.92rem; line-height: 1.7; color: {text_color};">
            • <b>سيولة نقدية مباشرة:</b> اعتمادك لـ <b>{strat_title}</b> يوفر لمزرعتك سيولة صافية تقدر بـ <b>{chosen_strat['total_financial_gain_egp']:,.0f} جنيه مصري</b> تذهب مباشرة لزيادة صافي أرباحك.<br>
            • <b>أمان مائي مستدام:</b> توفير <b>{chosen_strat['water_saved_m3']:,.0f} متر مكعب مياه</b> يكفي لتشغيل طلمبة الري بالطاقة الشمسية أو السولار لمدة <b>{max(1, round(chosen_strat['water_saved_m3'] / 350))} يوم ري إضافي</b> دون استنزاف البير أو التخلف عن نوبات الترعة.<br>
            • <b>تسميد بيولوجي مجاني:</b> تثبيت النيتروجين الطبيعي يمنحك ما يعادل <b>{chosen_strat['urea_bags_saved']:,.0f} شيكارة يوريا</b> مغذاة بالتدريج في الجذور دون فاقد الغسيل بالرشح.
        </div>
    </div>
    """)


def render_climate_hazards_hud(
    telemetry: Dict[str, Any],
    previous_crop_id: str = "maize",
    soil_type: str = "clay",
    dark_mode: bool = True
):
    """
    Renders the NASA Early Warning & Climate Hazard Alert System (Feature #4).
    Monitors live NASA POWER & SMAP telemetry for extreme heatwaves, frost,
    fungal disease spore blooms, and root zone moisture deficits with actionable protocols.
    """
    card_bg = "rgba(13, 22, 44, 0.85)" if dark_mode else "#ffffff"
    card_border = "rgba(0, 229, 255, 0.35)" if dark_mode else "#93c5fd"
    text_color = "#f8fafc" if dark_mode else "#0f172a"
    accent_cyan = "#00e5ff" if dark_mode else "#0284c7"
    accent_green = "#00ff88" if dark_mode else "#16a34a"
    accent_amber = "#ff9100" if dark_mode else "#d97706"
    accent_red = "#ef4444" if dark_mode else "#dc2626"

    # Evaluate Hazards based on telemetry
    alerts = evaluate_climate_hazards(telemetry, previous_crop_id=previous_crop_id, soil_type=soil_type)

    has_critical = any(a["severity"] == "critical" for a in alerts)
    has_warning = any(a["severity"] == "warning" for a in alerts)

    if has_critical:
        status_banner_color = accent_red
        status_bg = "rgba(239, 68, 68, 0.15)" if dark_mode else "#fef2f2"
        status_text = "🚨 إنذار مداري حرج نشط: تم رصد مؤشرات مناخية متطرفة تستوجب التدخل الحقلي الفوري!"
    elif has_warning:
        status_banner_color = accent_amber
        status_bg = "rgba(245, 158, 11, 0.15)" if dark_mode else "#fffbeb"
        status_text = "⚠️ تنبيهات مدارية وقائية: رصد إجهادات بيئية تستلزم تدابير زراعية استباقية"
    else:
        status_banner_color = accent_green
        status_bg = "rgba(16, 185, 129, 0.15)" if dark_mode else "#f0fdf4"
        status_text = "🛡️ كافة المؤشرات المناخية والمدارية مستقرة وآمنة فسيولوجياً"

    render_html_clean(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 16px; padding: 22px; margin-top: 15px; margin-bottom: 22px; box-shadow: 0 8px 32px rgba(0, 229, 255, 0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 50px; height: 50px; border-radius: 14px; background: linear-gradient(135deg, rgba(239,68,68,0.25), rgba(245,158,11,0.25)); border: 1px solid {status_banner_color}; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 0 16px rgba(239,68,68,0.25);">
                    🛰️
                </div>
                <div>
                    <h3 style="margin: 0; color: {accent_cyan}; font-size: 1.3rem; font-weight: 800;">
                        مرصد الإنذار المبكر والتنبيهات المدارية (NASA Climate Hazard Early Warning)
                    </h3>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 3px;">
                        مراقبة فضائية استباقية لموجات الصقيع، القيظ الشديد، جفاف الجذور، وتفشي الأبواغ الفطرية (NASA POWER & SMAP)
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge-pill badge-{'red' if has_critical else 'amber' if has_warning else 'green'}">
                    {'🔴 إنذار حرج' if has_critical else '🟠 تحذير وقائي' if has_warning else '🟢 الوضع مستقر'}
                </span>
                <span class="badge-pill badge-cyan">⚡ تحديث تليمترى لحظي</span>
            </div>
        </div>

        <!-- Global Status Bar -->
        <div style="background: {status_bg}; border: 1px solid {status_banner_color}; border-right: 5px solid {status_banner_color}; border-radius: 10px; padding: 12px 16px; font-weight: 700; color: {status_banner_color}; font-size: 0.95rem; margin-bottom: 16px;">
            {status_text}
        </div>
    </div>
    """)

    # Interactive Stress Scenario Simulator Expander
    with st.expander("🧪 اختبار واستعراض سيناريوهات الطوارئ المناخية (Hazard Scenario Simulator)", expanded=False):
        st.caption("اختبر استجابة نظام الإنذار المبكر لحالات الطقس المتطرفة:")
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            sim_scenario = st.selectbox(
                "اختر سيناريو مناخي لاختباره:",
                options=["live", "heatwave_extreme", "frost_shock", "fungal_bloom", "flash_drought"],
                format_func=lambda x: {
                    "live": "📡 البيانات الحية اللحظية من أقمار ناسا (Default Live)",
                    "heatwave_extreme": "🔥 محاكاة موجة قيظ شديدة (حرارة 40°C وإجهاد شمسي)",
                    "frost_shock": "❄️ محاكاة موجة صقيع وانجماد ليلي (حرارة صغرى 3°C)",
                    "fungal_bloom": "🦠 محاكاة بيئة تفشي أبواغ الصدأ واللفحة (رطوبة 85% وحرارة 21°C)",
                    "flash_drought": "🏜️ محاكاة جفاف حاد وانخفاض رطوبة باطن الأرض (SMAP 0.20)"
                }[x]
            )

    # If a simulation scenario is active, override telemetry temporarily for display
    active_telemetry = telemetry
    if sim_scenario != "live":
        active_telemetry = dict(telemetry)
        active_indices = dict(telemetry.get("indices", {}))
        if sim_scenario == "heatwave_extreme":
            active_indices["avg_temp_c"] = 36.5
            active_indices["max_temp_c"] = 41.0
            active_indices["extreme_heat_days"] = 4
        elif sim_scenario == "frost_shock":
            active_indices["min_temp_c"] = 2.5
            active_indices["avg_temp_c"] = 11.0
        elif sim_scenario == "fungal_bloom":
            active_indices["avg_relative_humidity_pct"] = 86.0
            active_indices["avg_temp_c"] = 21.0
            active_indices["avg_surface_moisture"] = 0.65
        elif sim_scenario == "flash_drought":
            active_indices["avg_root_zone_moisture"] = 0.20
            active_indices["soil_moisture_score"] = 22.0
        active_telemetry["indices"] = active_indices
        alerts = evaluate_climate_hazards(active_telemetry, previous_crop_id=previous_crop_id, soil_type=soil_type)

    # Render Individual Hazard Alert Cards
    for a in alerts:
        sev = a["severity"]
        card_border_color = accent_red if sev == "critical" else accent_amber if sev == "warning" else accent_green
        card_bg_glow = "rgba(239, 68, 68, 0.08)" if sev == "critical" else "rgba(245, 158, 11, 0.08)" if sev == "warning" else "rgba(16, 185, 129, 0.08)"
        badge_label = "🔴 خطر حرج (درجة 3)" if sev == "critical" else "🟠 تحذير وقائي (درجة 2)" if sev == "warning" else "🟢 حالة طبيعية (درجة 1)"
        badge_cls = "badge-red" if sev == "critical" else "badge-amber" if sev == "warning" else "badge-green"

        actions_html = "".join([f"<li style='margin-bottom: 4px;'>{act}</li>" for act in a["urgent_actions"]])

        render_html_clean(f"""
        <div style="background: {card_bg_glow}; border: 1px solid {card_border_color}; border-right: 5px solid {card_border_color}; border-radius: 14px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.6rem;">{a['icon']}</span>
                    <h4 style="margin: 0; color: {card_border_color}; font-size: 1.15rem; font-weight: 800;">
                        {a['title_ar']}
                    </h4>
                </div>
                <span class="badge-pill {badge_cls}">{badge_label}</span>
            </div>

            <div style="font-size: 0.92rem; line-height: 1.7; color: {text_color}; margin-top: 8px;">
                <div style="margin-bottom: 6px;">
                    <b>🛰️ رصد الأقمار الصناعية (NASA Trigger):</b> <span style="color: {card_border_color}; font-weight: 600;">{a['trigger_data']}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <b>⚠️ الأثر الفسيولوجي المباشر على الحقل:</b> {a['impact_ar']}
                </div>
                <div style="background: {'rgba(15, 23, 42, 0.6)' if dark_mode else '#ffffff'}; border: 1px solid {'rgba(255,255,255,0.08)' if dark_mode else '#e2e8f0'}; border-radius: 8px; padding: 10px 14px; margin-top: 10px;">
                    <b style="color: {accent_green}; font-size: 0.95rem;">🛡️ بروتوكول التدخل السريع للمزارع:</b>
                    <ol style="margin: 6px 0 0 18px; padding: 0; font-size: 0.9rem; line-height: 1.65;">
                        {actions_html}
                    </ol>
                </div>
            </div>
        </div>
        """)




