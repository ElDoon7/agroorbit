"""
AgroOrbit - Design System (Tokens, RTL Typography, Icons, SVG Moments)
Clean, calm, earthy agricultural intelligence interface.
"""

import base64
import math
from typing import List, Optional, Dict, Any
from src import config

_CACHED_LOGO_BASE64 = None
_CACHED_LOGO_MTIME = 0.0


# =============================================================================
# 1. Color & Spacing Tokens
# =============================================================================
DARK_TOKENS = {
    "bg_deepest": "#0f0f10",
    "bg_page": "#141415",
    "bg_card": "#19191b",
    "bg_raised": "#232325",
    "hairline": "rgba(237, 237, 237, 0.08)",
    "hairline_strong": "rgba(237, 237, 237, 0.14)",
    "text_primary": "#ededed",
    "text_secondary": "#a1a1a6",
    "text_muted": "#85858b",
    "accent": "#7cb77f",
    "accent_text": "#0f1710",
    "accent_tint": "rgba(124, 183, 127, 0.12)",
    "accent_border": "rgba(124, 183, 127, 0.35)",
    "positive": "#4cc38a",
    "negative": "#e5484d",
    "warning": "#d4a24c",
    "wheat_gold": "#d4a24c",
    "nile_teal": "#5a9ea6",
}

LIGHT_TOKENS = {
    "bg_deepest": "#f4f4f5",
    "bg_page": "#fafafa",
    "bg_card": "#ffffff",
    "bg_raised": "#f4f4f5",
    "hairline": "rgba(23, 23, 23, 0.08)",
    "hairline_strong": "rgba(23, 23, 23, 0.14)",
    "text_primary": "#171717",
    "text_secondary": "#525252",
    "text_muted": "#737373",
    "accent": "#2f7d4f",
    "accent_text": "#ffffff",
    "accent_tint": "rgba(47, 125, 79, 0.09)",
    "accent_border": "rgba(47, 125, 79, 0.30)",
    "positive": "#16a34a",
    "negative": "#dc2626",
    "warning": "#b7791f",
    "wheat_gold": "#b7791f",
    "nile_teal": "#2c7a82",
}


def get_tokens(dark_mode: bool = True) -> Dict[str, str]:
    """Return theme palette tokens."""
    return DARK_TOKENS if dark_mode else LIGHT_TOKENS


# =============================================================================
# 2. Brand Logo Loader (Clean Flat Mark, Zero Glow)
# =============================================================================
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
# 3. Unified Lucide Line Icons (16px, 1.5 stroke, inherit text color)
# =============================================================================
_LUCIDE_PATHS = {
    "home": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "map": '<path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/>',
    "book": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    "map-pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "thermometer": '<path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/>',
    "droplets": '<path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/><path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "cloud-rain": '<path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "volume": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>',
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "sprout": '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    "sliders": '<line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="2" x2="6" y1="14" y2="14"/><line x1="10" x2="14" y1="8" y2="8"/><line x1="18" x2="22" y1="16" y2="16"/>',
    "edit": '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "bar-chart": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
}


def svg_icon(name: str, size: int = 16, cls: str = "") -> str:
    """Return an inline Lucide-style SVG icon with consistent 1.5 stroke."""
    path_markup = _LUCIDE_PATHS.get(name, _LUCIDE_PATHS["compass"])
    extra_cls = f' class="{cls}"' if cls else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra_cls}>'
        f'{path_markup}</svg>'
    )


# =============================================================================
# 4. Product Moment & Signature: Crop Rotation Ring & 3-Season Bar
# =============================================================================
CROP_ARC_COLORS = {
    "clover": "#7cb77f",      # Field clover green
    "faba_bean": "#5f9d76",   # Deep sage
    "soybean": "#6aa88e",     # Leaf teal-green
    "wheat": "#d4a24c",       # Ripened wheat gold
    "maize": "#c89643",       # Amber grain
    "sugar_beet": "#5a9ea6",  # Coastal mineral blue-teal
    "onion": "#a8825a",       # Earth clay amber
    "rice": "#5c92b5",        # Water basin blue
    "cotton": "#a3a3a8",      # Crisp lint silver
    "tomato": "#c96f5b",      # Warm terracotta
    "potato": "#9b876a",      # Loam tuber brown
}


def get_crop_ring_color(crop_id: str, index: int = 0) -> str:
    """Return calm agricultural tint for a crop arc inside the Rotation Ring."""
    if crop_id in CROP_ARC_COLORS:
        return CROP_ARC_COLORS[crop_id]
    fallback = ["#7cb77f", "#d4a24c", "#5a9ea6"]
    return fallback[index % len(fallback)]


def season_bar_html(active_seasons: List[int], dark_mode: bool = True, season_colors: Optional[List[str]] = None) -> str:
    """
    Signature product detail: 3-segment season bar indicating Winter / Summer / Nili slots.
    active_seasons: 0-indexed list e.g. [0], [1], or [0, 1, 2].
    """
    t = get_tokens(dark_mode)
    inactive_bg = t["hairline_strong"]
    bars = []
    for idx in range(3):
        is_active = idx in active_seasons
        if is_active:
            color = (season_colors[idx] if season_colors and idx < len(season_colors) else t["accent"])
        else:
            color = inactive_bg
        bars.append(
            f'<span style="display:inline-block;width:16px;height:4px;border-radius:4px;background:{color};"></span>'
        )
    return (
        f'<span class="ao-season-bar" title="المواسم: شتوي / صيفي / نيلي" '
        f'style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;">'
        + "".join(bars)
        + "</span>"
    )


def _describe_arc(cx: float, cy: float, r: float, start_deg: float, end_deg: float) -> str:
    """Compute SVG path `d` for a circular arc from start_deg to end_deg (0 deg at 12 o'clock clockwise)."""
    start_rad = math.radians(start_deg - 90)
    end_rad = math.radians(end_deg - 90)
    x1 = cx + r * math.cos(start_rad)
    y1 = cy + r * math.sin(start_rad)
    x2 = cx + r * math.cos(end_rad)
    y2 = cy + r * math.sin(end_rad)
    large_arc = 1 if (end_deg - start_deg) > 180 else 0
    return f"M {x1:.2f} {y1:.2f} A {r:.2f} {r:.2f} 0 {large_arc} 1 {x2:.2f} {y2:.2f}"


def build_rotation_ring_svg(
    timeline: List[Dict[str, Any]],
    center_value: str,
    center_label: str,
    dark_mode: bool = True,
    size_px: int = 260,
    show_legend: bool = True,
) -> str:
    """
    Hero & Results signature visual:
    Circular 3-season rotation ring divided into 3 spaced arcs colored by crop,
    with a central tabular figure. Mirrors the restraint of the reference ring motif.
    """
    t = get_tokens(dark_mode)
    vb = 260
    cx = cy = vb / 2.0
    r = 92.0
    stroke_w = 22.0
    track_color = "rgba(237, 237, 237, 0.06)" if dark_mode else "rgba(23, 23, 23, 0.06)"

    # 3 equal 120-degree sectors with 12-degree gaps between segments
    arcs = [(6, 114), (126, 234), (246, 354)]
    season_short = ["شتوي", "صيفي", "نيلي"]

    svg_parts = [
        f'<svg viewBox="0 0 {vb} {vb}" width="{size_px}" height="{size_px}" '
        f'role="img" aria-label="حلقة الدورة الزراعية" style="display:block;max-width:100%;height:auto;">',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track_color}" stroke-width="{stroke_w}" />',
    ]

    legend_items = []
    for idx in range(3):
        s_deg, e_deg = arcs[idx]
        if idx < len(timeline):
            crop = timeline[idx].get("crop", {})
            crop_id = crop.get("id", "")
            crop_name = crop.get("name_ar", f"موسم {idx + 1}")
        else:
            crop_id = ""
            crop_name = f"موسم {idx + 1}"

        arc_col = get_crop_ring_color(crop_id, idx)
        path_d = _describe_arc(cx, cy, r, s_deg, e_deg)
        svg_parts.append(
            f'<path d="{path_d}" fill="none" stroke="{arc_col}" stroke-width="{stroke_w}" '
            f'stroke-linecap="round"><title>{season_short[idx]}: {crop_name}</title></path>'
        )

        # Outer radial season markers
        mid_deg = (s_deg + e_deg) / 2.0
        mid_rad = math.radians(mid_deg - 90)
        lx = cx + (r + 27) * math.cos(mid_rad)
        ly = cy + (r + 27) * math.sin(mid_rad)
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{t["text_muted"]}" font-size="11" font-family="IBM Plex Sans Arabic, sans-serif">'
            f'{season_short[idx]}</text>'
        )

        legend_items.append(
            f'<div style="display:inline-flex;align-items:center;gap:6px;">'
            f'<span style="width:8px;height:8px;border-radius:2px;background:{arc_col};display:inline-block;"></span>'
            f'<span style="color:{t["text_secondary"]};font-size:13px;">{season_short[idx]}: '
            f'<b style="color:{t["text_primary"]};font-weight:500;">{crop_name}</b></span>'
            f'</div>'
        )

    svg_parts.append(
        f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" dominant-baseline="middle" '
        f'fill="{t["text_primary"]}" font-size="30" font-weight="500" '
        f'font-family="IBM Plex Mono, monospace" dir="ltr">{center_value}</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" dominant-baseline="middle" '
        f'fill="{t["text_secondary"]}" font-size="12" '
        f'font-family="IBM Plex Sans Arabic, sans-serif">{center_label}</text>'
    )
    svg_parts.append("</svg>")

    legend_html = ""
    if show_legend:
        legend_html = (
            f'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:16px;margin-top:16px;">'
            + "".join(legend_items)
            + "</div>"
        )

    return (
        f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;">'
        + "".join(svg_parts)
        + legend_html
        + "</div>"
    )


# =============================================================================
# 5. Global Design System CSS (Unslop Rules + Full RTL Discipline)
# =============================================================================
def get_design_system_css(dark_mode: bool = True) -> str:
    """Return complete calm neutral stylesheet for dark or light mode."""
    t = get_tokens(dark_mode)
    depth_card = "none" if dark_mode else "0 1px 2px rgba(0, 0, 0, 0.05)"
    top_highlight = "inset 0 1px 0 rgba(255, 255, 255, 0.06)" if dark_mode else "none"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Arabic:wght@400;500;600&display=swap');

:root {{
    --ao-bg-deepest: {t['bg_deepest']};
    --ao-bg-page: {t['bg_page']};
    --ao-bg-card: {t['bg_card']};
    --ao-bg-raised: {t['bg_raised']};
    --ao-hairline: {t['hairline']};
    --ao-hairline-strong: {t['hairline_strong']};
    --ao-text-primary: {t['text_primary']};
    --ao-text-secondary: {t['text_secondary']};
    --ao-text-muted: {t['text_muted']};
    --ao-accent: {t['accent']};
    --ao-accent-text: {t['accent_text']};
    --ao-accent-tint: {t['accent_tint']};
    --ao-accent-border: {t['accent_border']};
    --ao-positive: {t['positive']};
    --ao-negative: {t['negative']};
    --ao-warning: {t['warning']};
    --ao-ease: cubic-bezier(0.22, 1, 0.36, 1);
}}

/* Hide Streamlit default chrome & sidebar completely */
#MainMenu,
header[data-testid="stHeader"],
footer,
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{
    display: none !important;
    visibility: hidden !important;
}}

/* Root Surface & RTL Typography */
html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: var(--ao-bg-page) !important;
    color: var(--ao-text-primary) !important;
    font-family: 'IBM Plex Sans Arabic', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 400;
    letter-spacing: 0 !important;
    direction: rtl !important;
}}

.main .block-container {{
    max-width: 1360px !important;
    padding: 16px 24px 64px 24px !important;
    margin: 0 auto !important;
}}

p, li, label, td, th, input, select, textarea,
.stMarkdown, .stButton button, .stDownloadButton button,
div:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded),
span:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded) {{
    font-family: 'IBM Plex Sans Arabic', -apple-system, BlinkMacSystemFont, sans-serif !important;
    letter-spacing: 0 !important;
}}

/* Preserve Streamlit native Material Symbols ligature icons cleanly */
[data-testid="stIconMaterial"],
.material-symbols-rounded {{
    font-family: 'Material Symbols Rounded' !important;
    letter-spacing: normal !important;
    font-feature-settings: 'liga' !important;
}}

/* Hide Streamlit automatic heading anchor icon that shifts RTL headings */
[data-testid="stHeaderActionElements"],
[data-testid="stHeadingActionElements"],
h1 a[href^="#"], h2 a[href^="#"], h3 a[href^="#"], h4 a[href^="#"] {{
    display: none !important;
}}

/* Tooltip contrast across both modes */
[data-testid="stTooltipContent"] {{
    background-color: var(--ao-bg-raised) !important;
    color: var(--ao-text-primary) !important;
    border: 1px solid var(--ao-hairline-strong) !important;
}}

p, li {{
    line-height: 1.65;
    color: var(--ao-text-secondary);
}}

h1, h2, h3, h4 {{
    color: var(--ao-text-primary) !important;
    font-weight: 500 !important;
    line-height: 1.35 !important;
    letter-spacing: 0 !important;
    margin: 0;
}}

.ao-mono {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-variant-numeric: tabular-nums !important;
    direction: ltr !important;
    unicode-bidi: isolate !important;
}}

.ao-num {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-variant-numeric: tabular-nums !important;
}}

/* Single gentle entrance motion */
@keyframes aoFadeRise {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.ao-enter {{
    animation: aoFadeRise 360ms var(--ao-ease) both;
}}

/* Quiet Surfaces & Cards */
.ao-card {{
    background-color: var(--ao-bg-card);
    border: 1px solid var(--ao-hairline);
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: {depth_card};
}}

.ao-card-compact {{
    background-color: var(--ao-bg-card);
    border: 1px solid var(--ao-hairline);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: {depth_card};
}}

.ao-stat-card {{
    background-color: var(--ao-bg-card);
    border: 1px solid var(--ao-hairline);
    border-radius: 12px;
    padding: 16px 20px;
    height: 100%;
    box-shadow: {depth_card};
}}

.ao-stat-label {{
    font-size: 13px;
    color: var(--ao-text-muted);
    margin-bottom: 8px;
}}

.ao-stat-val {{
    font-family: 'IBM Plex Mono', 'IBM Plex Sans Arabic', monospace !important;
    font-variant-numeric: tabular-nums !important;
    font-size: 28px;
    font-weight: 500;
    line-height: 1.1;
    color: var(--ao-text-primary);
}}

.ao-stat-meta {{
    font-size: 13px;
    color: var(--ao-text-secondary);
    margin-top: 8px;
}}

/* Clean Bordered Data Tables */
.ao-table-wrap {{
    display: block;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    background-color: var(--ao-bg-card);
    border: 1px solid var(--ao-hairline);
    border-radius: 14px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}}

.ao-table {{
    width: 100%;
    border-collapse: collapse;
    text-align: start;
    font-size: 14px;
}}

.ao-table thead th {{
    background-color: var(--ao-bg-deepest);
    color: var(--ao-text-secondary);
    font-weight: 500;
    font-size: 13px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--ao-hairline);
    white-space: nowrap;
    text-align: start;
}}

.ao-table tbody td {{
    padding: 12px 16px;
    border-bottom: 1px solid var(--ao-hairline);
    color: var(--ao-text-primary);
    vertical-align: middle;
}}

.ao-table tbody tr:last-child td {{
    border-bottom: none;
}}

.ao-table tbody tr {{
    transition: background-color 140ms var(--ao-ease);
}}

.ao-table tbody tr:hover {{
    background-color: var(--ao-bg-raised);
}}

/* Status Dots & Quiet Badges (No Glowing Pills) */
.ao-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    background-color: var(--ao-bg-raised);
    border: 1px solid var(--ao-hairline);
    color: var(--ao-text-secondary);
    white-space: nowrap;
}}

.ao-tag-accent {{
    background-color: var(--ao-accent-tint);
    border-color: var(--ao-accent-border);
    color: var(--ao-accent);
}}

.ao-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}}

/* Navigation Bar Strip Styling */
.st-key-ao_navbar {{
    background-color: var(--ao-bg-card);
    border: 1px solid var(--ao-hairline);
    border-radius: 14px;
    padding: 8px 16px;
    margin-bottom: 24px;
}}

.st-key-ao_navbar button {{
    min-height: 36px !important;
    height: 36px !important;
    padding: 0 12px !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    white-space: nowrap !important;
}}

.st-key-ao_navbar button[kind="secondary"],
.st-key-ao_navbar button[kind="tertiary"] {{
    background-color: transparent !important;
    border: 1px solid transparent !important;
    color: var(--ao-text-secondary) !important;
    box-shadow: none !important;
}}

.st-key-ao_navbar button[kind="secondary"]:hover {{
    background-color: var(--ao-bg-raised) !important;
    color: var(--ao-text-primary) !important;
}}

/* Active nav pill button */
.st-key-ao_nav_active button {{
    background-color: var(--ao-bg-raised) !important;
    border: 1px solid var(--ao-hairline-strong) !important;
    color: var(--ao-text-primary) !important;
    box-shadow: {top_highlight} !important;
}}

/* Standard Streamlit Buttons */
.stButton > button,
.stDownloadButton > button {{
    border-radius: 8px !important;
    min-height: 40px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: background-color 150ms var(--ao-ease), border-color 150ms var(--ao-ease), transform 120ms var(--ao-ease) !important;
    box-shadow: none !important;
}}

.stButton > button:active {{
    transform: scale(0.98) !important;
}}

.stButton > button[kind="primary"] {{
    background-color: var(--ao-accent) !important;
    color: var(--ao-accent-text) !important;
    border: 1px solid var(--ao-accent) !important;
}}

.stButton > button[kind="primary"] * {{
    color: var(--ao-accent-text) !important;
}}

.stButton > button[kind="primary"]:hover {{
    opacity: 0.92;
}}

.stButton > button[kind="secondary"],
.stDownloadButton > button {{
    background-color: var(--ao-bg-raised) !important;
    color: var(--ao-text-primary) !important;
    border: 1px solid var(--ao-hairline-strong) !important;
}}

.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button:hover {{
    border-color: var(--ao-accent-border) !important;
}}

/* Selectable Card Grids in Wizard (Soil & Priority Cards) */
.st-key-soil_cards_grid button,
.st-key-prio_cards_grid button {{
    height: auto !important;
    min-height: 96px !important;
    padding: 16px !important;
    text-align: start !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    border-radius: 12px !important;
    white-space: normal !important;
    line-height: 1.55 !important;
}}

.st-key-soil_cards_grid button > div,
.st-key-soil_cards_grid button p,
.st-key-prio_cards_grid button > div,
.st-key-prio_cards_grid button p {{
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    text-align: start !important;
    width: 100% !important;
    margin: 0 !important;
}}

.st-key-soil_cards_grid button p + p,
.st-key-prio_cards_grid button p + p {{
    margin-top: 6px !important;
    font-size: 13px !important;
    color: var(--ao-text-secondary) !important;
}}

.st-key-soil_cards_grid button[kind="primary"],
.st-key-prio_cards_grid button[kind="primary"] {{
    background-color: var(--ao-accent-tint) !important;
    border: 1px solid var(--ao-accent) !important;
    color: var(--ao-text-primary) !important;
}}

.st-key-soil_cards_grid button[kind="primary"] *,
.st-key-prio_cards_grid button[kind="primary"] * {{
    color: var(--ao-text-primary) !important;
}}

/* Ranked Governorate Rows */
.st-key-gov_list_panel button {{
    min-height: 36px !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
    justify-content: flex-start !important;
    text-align: start !important;
    font-size: 13.5px !important;
    border: 1px solid transparent !important;
    background-color: transparent !important;
    color: var(--ao-text-secondary) !important;
}}
.st-key-gov_list_panel button > div,
.st-key-gov_list_panel button p {{
    width: 100% !important;
    text-align: start !important;
}}

.st-key-gov_list_panel button:hover {{
    background-color: var(--ao-bg-raised) !important;
    color: var(--ao-text-primary) !important;
}}

.st-key-gov_list_panel button[kind="primary"] {{
    background-color: var(--ao-accent-tint) !important;
    border: 1px solid var(--ao-accent) !important;
    color: var(--ao-text-primary) !important;
}}

.st-key-gov_list_panel button[kind="primary"] * {{
    color: var(--ao-text-primary) !important;
}}

/* Streamlit Pills & Segmented Controls */
[data-testid="stPills"] button,
[data-testid="stSegmentedControl"] button {{
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
}}

/* Inputs, Selectboxes, Sliders */
[data-baseweb="select"] > div,
.stNumberInput input,
.stTextInput input {{
    background-color: var(--ao-bg-raised) !important;
    border: 1px solid var(--ao-hairline-strong) !important;
    border-radius: 8px !important;
    color: var(--ao-text-primary) !important;
}}

/* Expander styling */
[data-testid="stExpander"] {{
    background-color: var(--ao-bg-card) !important;
    border: 1px solid var(--ao-hairline) !important;
    border-radius: 12px !important;
}}

[data-testid="stExpander"] summary {{
    color: var(--ao-text-primary) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}}

/* Horizontal Divider */
hr {{
    border-color: var(--ao-hairline) !important;
    margin: 24px 0 !important;
}}

/* Folium iframe rounding inside calm frame */
iframe[title="streamlit_folium.st_folium"] {{
    border-radius: 12px !important;
    border: 1px solid var(--ao-hairline) !important;
}}

/* Stepper Bar */
.ao-stepper {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}}

.ao-step-item {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.ao-step-track {{
    height: 3px;
    border-radius: 3px;
    background-color: var(--ao-hairline-strong);
    width: 100%;
}}

.ao-step-track-active {{
    background-color: var(--ao-accent);
}}

.ao-step-label {{
    font-size: 13px;
    color: var(--ao-text-muted);
}}

.ao-step-label-active {{
    color: var(--ao-text-primary);
    font-weight: 500;
}}

/* Responsive Adjustments */
@media (max-width: 768px) {{
    .main .block-container {{
        padding: 12px 16px 48px 16px !important;
    }}
    .ao-hero-title {{
        font-size: 32px !important;
    }}
    .ao-stat-val {{
        font-size: 22px !important;
    }}
    .st-key-ao_navbar [data-testid="stLayoutWrapper"],
    .st-key-ao_navbar [data-testid="stVerticalBlock"] {{
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 6px !important;
    }}
    .st-key-ao_navbar button {{
        padding: 0 10px !important;
        font-size: 13px !important;
        min-width: max-content !important;
    }}
    .ao-table th,
    .ao-table td {{
        padding: 10px 10px !important;
        font-size: 13px !important;
    }}
}}
</style>
"""
