"""
AgroOrbit - Botanical Design System
Lush deep-forest dark theme (#0b140f / #13221a / #22c55e) and soft sage-mint
light theme (#f3f7f5 / #ffffff / #15803d), matching refined multi-stage UI patterns
with Cairo & Plus Jakarta Sans typography, 18px glass cards, 999px pills, and Gantt grids.
"""

import base64
from typing import List, Optional, Dict, Any
from src import config

_CACHED_LOGO_BASE64 = None
_CACHED_LOGO_MTIME = 0.0


# =============================================================================
# 1. Exact Botanical Palette Tokens (Dark Default + Light Mint-Sage)
# =============================================================================
DARK_TOKENS = {
    "bg": "#0b140f",
    "surface": "#13221a",
    "surface_alt": "#1b3025",
    "tx": "#f0f7f3",
    "mu": "#9fb7a9",
    "bd": "#284234",
    "ac": "#22c55e",
    "ac_dark": "#16a34a",
    "ac_text": "#052e16",
    "ac_soft": "rgba(34, 197, 94, 0.16)",
    "ac_border": "rgba(34, 197, 94, 0.40)",
    "blue": "#38bdf8",
    "blue_soft": "rgba(56, 189, 248, 0.14)",
    "blue_border": "rgba(56, 189, 248, 0.35)",
    "amber": "#fbbf24",
    "amber_soft": "rgba(251, 191, 36, 0.15)",
    "amber_border": "rgba(251, 191, 36, 0.35)",
    "danger": "#f87171",
    "danger_soft": "rgba(248, 113, 113, 0.15)",
    "shadow": "0 14px 36px -10px rgba(0, 0, 0, 0.55)",
    "shadow_bar": "0 4px 16px rgba(0, 0, 0, 0.22)",
    "hairline": "rgba(240, 247, 243, 0.09)",
    # Aliases used by modules like governorate_analyzer
    "bg_page": "#0b140f",
    "bg_card": "#13221a",
    "bg_raised": "#1b3025",
    "text_primary": "#f0f7f3",
    "text_secondary": "#9fb7a9",
    "text_muted": "#9fb7a9",
    "accent": "#22c55e",
    "wheat_gold": "#fbbf24",
    "sky_teal": "#38bdf8",
    "hairline_strong": "#284234",
}

LIGHT_TOKENS = {
    "bg": "#f3f7f5",
    "surface": "#ffffff",
    "surface_alt": "#e8f2ed",
    "tx": "#12261b",
    "mu": "#4a6355",
    "bd": "#cfe0d6",
    "ac": "#15803d",
    "ac_dark": "#166534",
    "ac_text": "#ffffff",
    "ac_soft": "#dcfce7",
    "ac_border": "rgba(21, 128, 61, 0.38)",
    "blue": "#0284c7",
    "blue_soft": "#e0f2fe",
    "blue_border": "rgba(2, 132, 199, 0.32)",
    "amber": "#d97706",
    "amber_soft": "#fef3c7",
    "amber_border": "rgba(217, 119, 6, 0.35)",
    "danger": "#dc2626",
    "danger_soft": "#fee2e2",
    "shadow": "0 10px 30px -10px rgba(18, 38, 27, 0.09)",
    "shadow_bar": "0 2px 10px rgba(18, 38, 27, 0.05)",
    "hairline": "rgba(18, 38, 27, 0.09)",
    "bg_page": "#f3f7f5",
    "bg_card": "#ffffff",
    "bg_raised": "#e8f2ed",
    "text_primary": "#12261b",
    "text_secondary": "#4a6355",
    "text_muted": "#4a6355",
    "accent": "#15803d",
    "wheat_gold": "#d97706",
    "sky_teal": "#0284c7",
    "hairline_strong": "#cfe0d6",
}


def get_tokens(dark_mode: bool = True) -> Dict[str, str]:
    """Return botanical dark or soft mint-sage light tokens."""
    return DARK_TOKENS if dark_mode else LIGHT_TOKENS


def get_logo_base64() -> str:
    """Return base64-encoded logo image if present on disk."""
    global _CACHED_LOGO_BASE64, _CACHED_LOGO_MTIME

    root_dir = config.ROOT_DIR
    cache_dir = config.CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    for name in ("logo.png", "logo.jpg", "logo.jpeg", "icon.png"):
        img_path = root_dir / name
        if img_path.exists() and img_path.is_file():
            try:
                curr_mtime = img_path.stat().st_mtime
                if _CACHED_LOGO_BASE64 and _CACHED_LOGO_MTIME == curr_mtime:
                    return _CACHED_LOGO_BASE64

                opt_path = cache_dir / f"opt_{name.rsplit('.', 1)[0]}.png"
                if not opt_path.exists() or opt_path.stat().st_mtime < curr_mtime:
                    try:
                        from PIL import Image
                        with Image.open(img_path) as im:
                            im_rgba = im.convert("RGBA")
                            im_rgba.thumbnail((256, 256), Image.Resampling.LANCZOS)
                            im_rgba.save(opt_path, "PNG", optimize=True)
                    except Exception:
                        opt_path = img_path

                target = opt_path if opt_path.exists() else img_path
                with open(target, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    _CACHED_LOGO_BASE64 = f"data:image/png;base64,{encoded}"
                    _CACHED_LOGO_MTIME = curr_mtime
                    return _CACHED_LOGO_BASE64
            except Exception:
                pass
    return ""


# =============================================================================
# 2. Month Allocation Helpers for 12-Month Gantt Calendar
# =============================================================================
MONTH_NAMES_AR = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
]


def _get_crop_months(season_type: str, season_idx: int) -> List[int]:
    """Return 1-indexed active calendar months (1..12) for a rotation crop step."""
    st_low = (season_type or "").lower()
    if "winter" in st_low or season_idx == 0:
        return [11, 12, 1, 2, 3, 4]
    if "summer" in st_low or season_idx == 1:
        return [5, 6, 7, 8]
    return [9, 10]


def build_gantt_timeline_html(timeline: List[Dict[str, Any]], dark_mode: bool = True) -> str:
    """Build crisp 12-month horizontal color-coded calendar grid matching GREEN FUTURE."""
    t = get_tokens(dark_mode)
    cell_empty = t["surface_alt"]

    headers = "".join(
        f'<div style="font-size:11.5px;color:{t["mu"]};text-align:center;font-weight:600;padding:4px 2px;">{m}</div>'
        for m in MONTH_NAMES_AR
    )
    rows_html = []

    occupied = set()
    for idx, step in enumerate(timeline):
        crop = step.get("crop", {})
        c_name = crop.get("name_ar", f"موسم {idx + 1}")
        s_lbl = "شتوي" if "winter" in (crop.get("season_type", "")).lower() or idx == 0 else "صيفي" if "summer" in (crop.get("season_type", "")).lower() or idx == 1 else "نيلي"
        active_m = _get_crop_months(crop.get("season_type", ""), idx)
        for m in active_m:
            occupied.add(m)

        cells = []
        for m_idx in range(1, 13):
            bg = t["ac"] if m_idx in active_m else cell_empty
            cells.append(f'<div style="height:24px;border-radius:6px;background:{bg};"></div>')

        rows_html.append(
            f'<div style="display:grid;grid-template-columns:150px repeat(12,1fr);gap:6px;align-items:center;margin-top:8px;">'
            f'<div style="font-size:13px;font-weight:700;color:{t["tx"]};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{c_name} <span style="font-weight:400;color:{t["mu"]};font-size:11.5px;">({s_lbl})</span></div>'
            + "".join(cells)
            + "</div>"
        )

    # Row for Cover / Pest Break Gap Management (remaining months)
    cover_cells = []
    for m_idx in range(1, 13):
        if m_idx in [9, 10] and m_idx not in occupied:
            bg = t["blue"]
        elif m_idx not in occupied:
            bg = t["amber"]
        else:
            bg = cell_empty
        cover_cells.append(f'<div style="height:24px;border-radius:6px;background:{bg};"></div>')

    rows_html.append(
        f'<div style="display:grid;grid-template-columns:150px repeat(12,1fr);gap:6px;align-items:center;margin-top:8px;">'
        f'<div style="font-size:12.5px;font-weight:600;color:{t["mu"]};">تغطية التربة وكسر الآفات</div>'
        + "".join(cover_cells)
        + "</div>"
    )

    legend = (
        f'<div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:12px;font-size:12.5px;color:{t["mu"]};">'
        f'<span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;border-radius:3px;background:{t["ac"]};display:inline-block;"></span>زراعة وإنتاج</span>'
        f'<span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;border-radius:3px;background:{t["blue"]};display:inline-block;"></span>تغطية وحفظ رطوبة التربة</span>'
        f'<span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;border-radius:3px;background:{t["amber"]};display:inline-block;"></span>تجهيز وكسر آفات</span>'
        f'</div>'
    )

    return (
        f'<div class="gf-card" style="overflow-x:auto;">'
        f'{legend}'
        f'<div style="min-width:680px;">'
        f'<div style="display:grid;grid-template-columns:150px repeat(12,1fr);gap:6px;align-items:center;border-bottom:1px solid {t["bd"]};padding-bottom:6px;">'
        f'<div style="font-size:12px;color:{t["mu"]};font-weight:600;">المحصول / الفترة</div>{headers}'
        f'</div>'
        + "".join(rows_html)
        + "</div></div>"
    )


# =============================================================================
# 3. Complete Stylesheet (Botanical Surface & Pill Controls)
# =============================================================================
def get_design_system_css(dark_mode: bool = True) -> str:
    """Return full stylesheet inspired by GREEN FUTURE visual clarity and palette."""
    t = get_tokens(dark_mode)

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {{
    --bg: {t['bg']};
    --surface: {t['surface']};
    --surface-alt: {t['surface_alt']};
    --tx: {t['tx']};
    --mu: {t['mu']};
    --bd: {t['bd']};
    --ac: {t['ac']};
    --ac-dark: {t['ac_dark']};
    --ac-text: {t['ac_text']};
    --ac-soft: {t['ac_soft']};
    --ac-border: {t['ac_border']};
    --blue: {t['blue']};
    --blue-soft: {t['blue_soft']};
    --blue-border: {t['blue_border']};
    --amber: {t['amber']};
    --amber-soft: {t['amber_soft']};
    --amber-border: {t['amber_border']};
    --danger: {t['danger']};
    --danger-soft: {t['danger_soft']};
    --shadow: {t['shadow']};
    --shadow-bar: {t['shadow_bar']};
    --radius: 18px;
}}

/* Remove default Streamlit UI chrome & sidebar cleanly */
#MainMenu,
header[data-testid="stHeader"],
footer,
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeaderActionElements"],
[data-testid="stHeadingActionElements"],
h1 a[href^="#"], h2 a[href^="#"], h3 a[href^="#"], h4 a[href^="#"] {{
    display: none !important;
    visibility: hidden !important;
}}

html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: var(--bg) !important;
    color: var(--tx) !important;
    font-family: 'Cairo', 'Plus Jakarta Sans', 'Segoe UI', Tahoma, sans-serif !important;
    font-size: 16px;
    direction: rtl !important;
}}

.main .block-container {{
    max-width: 1240px !important;
    padding: 12px 24px 64px 24px !important;
    margin: 0 auto !important;
}}

p, li, label, td, th, input, select, textarea,
.stMarkdown, .stButton button, .stDownloadButton button,
div:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded),
span:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded) {{
    font-family: 'Cairo', 'Plus Jakarta Sans', 'Segoe UI', Tahoma, sans-serif !important;
}}

[data-testid="stIconMaterial"],
.material-symbols-rounded {{
    font-family: 'Material Symbols Rounded' !important;
    letter-spacing: normal !important;
    font-feature-settings: 'liga' !important;
}}

h1, h2, h3, h4 {{
    color: var(--tx) !important;
    font-weight: 800 !important;
    line-height: 1.4 !important;
    margin: 0;
}}

p {{
    color: var(--mu);
    line-height: 1.7;
}}

@keyframes gfSlideUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.gf-animate {{
    animation: gfSlideUp 0.25s ease both;
}}

/* ============================================================================
   1. TOPBAR & NUMBERED STEPPER BAR
   ============================================================================ */
.st-key-gf_topbar {{
    background-color: var(--surface) !important;
    border: 1px solid var(--bd) !important;
    border-radius: 16px !important;
    box-shadow: var(--shadow-bar) !important;
    padding: 10px 20px !important;
    margin: 0 0 10px 0 !important;
    overflow: hidden !important;
}}

.st-key-gf_topbar [data-testid="stButton"] > button,
.st-key-gf_topbar .stButton > button[kind="secondary"] {{
    min-height: 40px !important;
    height: 40px !important;
    padding: 0 16px !important;
    border-radius: 999px !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
    box-shadow: none !important;
}}

.st-key-gf_topbar [class*="st-key-gf_top_lab"] .stButton > button,
.st-key-gf_topbar [class*="st-key-gf_top_lab"] .stButton > button[kind="secondary"] {{
    background-color: var(--ac-soft) !important;
    color: var(--ac) !important;
    border: 1.5px solid var(--ac-border) !important;
}}

.st-key-gf_topbar [class*="st-key-gf_top_lab"] .stButton > button * {{
    color: var(--ac) !important;
}}

.st-key-gf_topbar [class*="st-key-gf_top_pill"] .stButton > button,
.st-key-gf_topbar [class*="st-key-gf_top_pill"] .stButton > button[kind="secondary"] {{
    background-color: var(--surface-alt) !important;
    color: var(--tx) !important;
    border: 1px solid var(--bd) !important;
}}

.st-key-gf_topbar [class*="st-key-gf_top_pill"] .stButton > button:hover {{
    border-color: var(--ac) !important;
}}

/* Stepper Ribbon directly below Topbar */
.st-key-gf_stepper {{
    background-color: var(--surface) !important;
    border: 1px solid var(--bd) !important;
    border-radius: 14px !important;
    padding: 8px 20px !important;
    margin: 0 0 22px 0 !important;
    overflow: hidden !important;
}}

.st-key-gf_stepper [data-testid="stButton"] > button,
.st-key-gf_stepper .stButton > button[kind="secondary"] {{
    min-height: 38px !important;
    height: 38px !important;
    padding: 0 14px !important;
    border-radius: 999px !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    background-color: transparent !important;
    color: var(--mu) !important;
    border: 1px solid transparent !important;
    white-space: nowrap !important;
    box-shadow: none !important;
}}

.st-key-gf_stepper .stButton > button:hover {{
    background-color: var(--surface-alt) !important;
    color: var(--tx) !important;
}}

.st-key-gf_stepper [class*="st-key-gf_step_active"] .stButton > button,
.st-key-gf_stepper [class*="st-key-gf_step_active"] .stButton > button[kind="secondary"] {{
    background-color: var(--ac-soft) !important;
    color: var(--ac) !important;
    border: 1.5px solid var(--ac) !important;
}}

.st-key-gf_stepper [class*="st-key-gf_step_active"] .stButton > button * {{
    color: var(--ac) !important;
}}

.st-key-gf_stepper [class*="st-key-gf_step_done"] .stButton > button,
.st-key-gf_stepper [class*="st-key-gf_step_done"] .stButton > button[kind="secondary"] {{
    color: var(--tx) !important;
    border: 1px solid var(--bd) !important;
    background-color: var(--surface-alt) !important;
}}

.gf-connector {{
    width: 100%;
    min-width: 18px;
    height: 2px;
    margin: 0 auto;
    background-color: var(--bd);
    border-radius: 2px;
}}

.gf-connector-done {{
    background-color: var(--ac);
}}

/* ============================================================================
   2. MAIN STAGE CARDS, STEP TAG, PREVIEW BANNER & BOXES
   ============================================================================ */
.st-key-gf_centered_stage {{
    max-width: 920px !important;
    margin: 0 auto !important;
    background-color: var(--surface) !important;
    border: 1px solid var(--bd) !important;
    border-radius: var(--radius) !important;
    padding: 22px 28px !important;
    box-shadow: var(--shadow) !important;
}}

.gf-card {{
    background-color: var(--surface);
    border: 1px solid var(--bd);
    border-radius: var(--radius);
    padding: 22px 24px;
    box-shadow: var(--shadow);
}}

.gf-step-tag {{
    display: inline-block;
    background-color: var(--ac-soft);
    color: var(--ac);
    border: 1px solid var(--ac-border);
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 700;
    margin-bottom: 12px;
}}

.gf-preview-banner {{
    background-color: var(--surface-alt);
    border: 1px solid var(--bd);
    border-radius: 14px;
    padding: 14px 18px;
    margin: 12px 0 14px 0;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    text-align: center;
}}

.gf-preview-label {{
    font-size: 12.5px;
    color: var(--mu);
    margin-bottom: 4px;
}}

.gf-preview-val {{
    font-size: 15px;
    font-weight: 800;
    color: var(--ac);
}}

/* Blue 90-Day Climate Simulator Box (Stage 2) */
.st-key-gf_sim_box {{
    background-color: var(--blue-soft) !important;
    border: 1px solid var(--blue-border) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    margin-top: 16px !important;
}}

.gf-sim-badge {{
    display: inline-block;
    background-color: var(--blue);
    color: #052236;
    font-size: 12px;
    font-weight: 800;
    padding: 3px 12px;
    border-radius: 999px;
}}

/* 2x2 Selectable Goal Cards */
.st-key-gf_goal_cards .stButton > button,
.st-key-gf_goal_cards .stButton > button[kind="secondary"] {{
    min-height: 112px !important;
    height: auto !important;
    padding: 18px 20px !important;
    border-radius: 14px !important;
    background-color: var(--bg) !important;
    border: 1.5px solid var(--bd) !important;
    color: var(--tx) !important;
    text-align: center !important;
    justify-content: center !important;
    white-space: normal !important;
    line-height: 1.6 !important;
    box-shadow: none !important;
}}

.st-key-gf_goal_cards .stButton > button:hover,
.st-key-gf_goal_cards .stButton > button[kind="secondary"]:hover {{
    border-color: var(--ac) !important;
    background-color: var(--surface-alt) !important;
}}

.st-key-gf_goal_cards .stButton > button[kind="primary"] {{
    background-color: var(--ac-soft) !important;
    border: 2px solid var(--ac) !important;
    color: var(--tx) !important;
}}

.st-key-gf_goal_cards .stButton > button[kind="primary"] * {{
    color: var(--tx) !important;
}}

.st-key-gf_goal_cards .stButton > button[kind="primary"] p:first-child {{
    color: var(--ac) !important;
}}

.st-key-gf_goal_cards .stButton > button > div,
.st-key-gf_goal_cards .stButton > button p {{
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    text-align: center !important;
    width: 100% !important;
    margin: 0 !important;
}}

.st-key-gf_goal_cards .stButton > button p + p {{
    margin-top: 6px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    color: var(--mu) !important;
}}

/* Highlighted KPI Card (Stage 3 Summary Strip) */
.gf-sum-box {{
    background-color: var(--surface);
    border: 1px solid var(--bd);
    border-radius: 16px;
    padding: 18px 20px;
    height: 100%;
    box-shadow: var(--shadow);
}}

.gf-sum-highlight {{
    background: linear-gradient(135deg, var(--surface), var(--ac-soft));
    border: 2px solid var(--ac);
    border-radius: 16px;
    padding: 18px 20px;
    height: 100%;
    box-shadow: var(--shadow);
}}

/* Plan Comparison Cards (Stage 3) */
.gf-plans-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    align-items: stretch;
}}

.gf-plan-card {{
    background-color: var(--surface);
    border: 1.5px solid var(--bd);
    border-radius: 16px;
    padding: 18px 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--shadow);
}}

.gf-plan-best {{
    border: 2.5px solid var(--ac);
}}

.gf-plan-baseline {{
    border: 1.5px dashed var(--bd);
    opacity: 0.92;
}}

.gf-crop-chip {{
    display: inline-block;
    background-color: var(--ac-soft);
    color: var(--ac);
    border: 1px solid var(--ac-border);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
}}

.gf-plan-why {{
    background-color: var(--surface-alt);
    border-inline-start: 4px solid var(--ac);
    border-radius: 10px;
    padding: 12px 14px;
    margin: 14px 0;
    font-size: 13.5px;
    line-height: 1.65;
    color: var(--tx);
}}

.gf-metric-tile {{
    background-color: var(--surface-alt);
    border-radius: 10px;
    padding: 10px 12px;
    border: 1px solid var(--bd);
}}

/* Insight Box inside Science & Charts (Stage 4) */
.gf-insight-box {{
    background-color: var(--surface-alt);
    border-inline-start: 4px solid var(--ac);
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 12px;
    font-size: 13.5px;
    line-height: 1.65;
    color: var(--tx);
}}

/* Advisory Disclaimer Box (Warm Amber) */
.gf-amber-box {{
    background-color: var(--amber-soft);
    border: 1px solid var(--amber-border);
    border-inline-start: 4px solid var(--amber);
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 13.5px;
    line-height: 1.7;
    color: var(--tx);
}}

/* ============================================================================
   3. GENERIC STREAMLIT CONTROLS (BUTTONS, INPUTS, SELECTS, TABLES, TABS)
   ============================================================================ */
.stButton > button,
.stDownloadButton > button {{
    border-radius: 12px !important;
    min-height: 44px !important;
    font-weight: 700 !important;
    font-size: 14.5px !important;
    transition: transform 0.15s ease, background-color 0.15s ease, border-color 0.15s ease !important;
}}

.stButton > button:active {{
    transform: scale(0.98) !important;
}}

.stButton > button[kind="primary"] {{
    background-color: var(--ac) !important;
    color: var(--ac-text) !important;
    border: 1px solid var(--ac) !important;
}}

.stButton > button[kind="primary"] * {{
    color: var(--ac-text) !important;
}}

.stButton > button[kind="primary"]:hover {{
    background-color: var(--ac-dark) !important;
    border-color: var(--ac-dark) !important;
}}

.stButton > button[kind="secondary"],
.stDownloadButton > button {{
    background-color: var(--surface-alt) !important;
    color: var(--tx) !important;
    border: 1px solid var(--bd) !important;
}}

.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button:hover {{
    border-color: var(--ac) !important;
}}

/* Selectbox, Inputs & Popovers synced in both themes */
[data-baseweb="select"] > div,
.stNumberInput input,
.stTextInput input,
[data-testid="stNumberInputContainer"],
[data-testid="stNumberInputField"],
[data-testid="stNumberInput"] button {{
    background-color: var(--bg) !important;
    color: var(--tx) !important;
    border-color: var(--bd) !important;
    border-radius: 10px !important;
}}

[data-testid="stNumberInput"] button svg {{
    fill: var(--tx) !important;
    color: var(--tx) !important;
}}

[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"] {{
    background-color: var(--surface) !important;
    color: var(--tx) !important;
    border: 1px solid var(--bd) !important;
}}

ul[role="listbox"] li:hover,
ul[role="listbox"] li[aria-selected="true"] {{
    background-color: var(--surface-alt) !important;
}}

/* Segmented controls & Pills */
[data-testid="stButtonGroup"] > div {{
    flex-wrap: wrap !important;
    max-width: 100% !important;
    gap: 6px !important;
}}

[data-testid="stButtonGroup"] button {{
    background-color: var(--surface-alt) !important;
    color: var(--mu) !important;
    border: 1px solid var(--bd) !important;
    border-radius: 999px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    max-width: 100% !important;
}}

[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[aria-pressed="true"],
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"],
[data-testid="stButtonGroup"] button[kind="pillsActive"],
[data-testid="stBaseButton-segmented_controlActive"],
[data-testid="stBaseButton-pillsActive"] {{
    background-color: var(--ac-soft) !important;
    color: var(--ac) !important;
    border: 1.5px solid var(--ac) !important;
}}

[data-testid="stButtonGroup"] button[aria-checked="true"] *,
[data-testid="stButtonGroup"] button[aria-pressed="true"] *,
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] *,
[data-testid="stButtonGroup"] button[kind="pillsActive"] * {{
    color: var(--ac) !important;
}}

/* Expander styling */
[data-testid="stExpander"] {{
    background-color: var(--surface) !important;
    border: 1px solid var(--bd) !important;
    border-radius: 14px !important;
}}

/* Data Tables */
.gf-table-wrap {{
    display: block;
    width: 100%;
    max-width: 100%;
    background-color: var(--surface);
    border: 1px solid var(--bd);
    border-radius: 14px;
    overflow-x: auto;
    max-height: 400px;
    overflow-y: auto;
}}

.gf-table {{
    width: 100%;
    border-collapse: collapse;
    text-align: start;
    font-size: 14px;
}}

.gf-table thead th {{
    position: sticky;
    top: 0;
    z-index: 2;
    background-color: var(--surface-alt);
    color: var(--tx);
    font-weight: 700;
    padding: 12px 16px;
    border-bottom: 1px solid var(--bd);
    white-space: nowrap;
}}

.gf-table tbody td {{
    padding: 11px 16px;
    border-bottom: 1px solid var(--hairline);
    color: var(--tx);
}}

.gf-table tbody tr:hover {{
    background-color: var(--surface-alt);
}}

/* Ranked Governorate Rows */
.st-key-gov_list_panel .stButton > button {{
    min-height: 38px !important;
    padding: 6px 12px !important;
    border-radius: 10px !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    text-align: right !important;
    font-size: 13.5px !important;
    background-color: transparent !important;
    color: var(--mu) !important;
    border: 1px solid transparent !important;
}}
.st-key-gov_list_panel .stButton > button > div,
.st-key-gov_list_panel .stButton > button span,
.st-key-gov_list_panel .stButton > button [data-testid="stMarkdownContainer"],
.st-key-gov_list_panel .stButton > button p {{
    width: 100% !important;
    display: block !important;
    text-align: right !important;
    margin: 0 !important;
}}
.st-key-gov_list_panel .stButton > button[kind="primary"] {{
    background-color: var(--ac-soft) !important;
    border: 1.5px solid var(--ac) !important;
    color: var(--ac) !important;
}}
.st-key-gov_list_panel .stButton > button[kind="primary"] * {{
    color: var(--ac) !important;
}}

iframe[title="streamlit_folium.st_folium"] {{
    width: 100% !important;
    border-radius: 16px !important;
    border: 2px solid var(--bd) !important;
}}

hr {{
    border-color: var(--bd) !important;
    margin: 22px 0 !important;
}}

/* Mobile Responsive */
@media (max-width: 900px) {{
    .gf-plans-grid {{
        grid-template-columns: 1fr !important;
    }}
}}

@media (max-width: 768px) {{
    .main .block-container {{
        padding: 8px 14px 56px 14px !important;
    }}
    .st-key-gf_topbar,
    .st-key-gf_stepper {{
        padding: 10px 14px !important;
        margin: 0 0 12px 0 !important;
    }}
    .gf-connector {{
        display: none !important;
    }}
    .st-key-gf_topbar [data-testid="stLayoutWrapper"],
    .st-key-gf_stepper [data-testid="stLayoutWrapper"] {{
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 6px !important;
    }}
    .st-key-gf_centered_stage {{
        padding: 18px 16px !important;
    }}
    .gf-preview-banner {{
        grid-template-columns: 1fr !important;
    }}
}}
</style>
"""
