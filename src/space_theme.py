"""
AgroOrbit - NASA Mission Control Theme Engine (CSS & Styling)
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data

Features:
- Unified Modern Arabic & English Typography: 'Alexandria' + 'Cairo'
- Dual High-End Theme Engine:
    * Deep Space Dark (فضائي مظلم مدعوم بـ Glassmorphism)
    * Solar Daylight (نهاري فاتح وأنيق)
- Automatic High-Performance Custom Wallpaper Optimization (PIL Auto-Compression & In-Memory Caching)
- Futuristic Glassmorphic Tables & HUD Cards (eliminates raw Excel look entirely)
- Synchronized Visual Palette Reference for Charts & Maps
- Chrome Mobile Responsive Optimization
"""

import base64
from pathlib import Path
from src import config

# In-memory cache for background base64 URI
_CACHED_BG_BASE64 = None
_CACHED_SRC_MTIME = 0
_CACHED_LOGO_BASE64 = None
_CACHED_LOGO_MTIME = 0.0


def get_logo_base64() -> str:
    """
    Checks for custom logo image (logo.png, logo.jpg) in root directory.
    Returns web-optimized base64 data URI for intro splash and navbar headers.
    Automatically reloads whenever logo.png is modified on disk.
    """
    global _CACHED_LOGO_BASE64, _CACHED_LOGO_MTIME

    possible_names = ["logo.png", "logo.jpg", "logo.jpeg", "icon.png"]
    root_dir = config.ROOT_DIR
    cache_dir = config.CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    for name in possible_names:
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
                            im_rgba.thumbnail((512, 512), Image.Resampling.LANCZOS)
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


def get_custom_bg_base64() -> str:
    """
    Checks for custom background image files in root directory.
    Automatically creates a high-performance web-optimized version (<400 KB)
    to guarantee instant page rendering and zero websocket latency.
    """
    global _CACHED_BG_BASE64, _CACHED_SRC_MTIME

    possible_names = [
        "background.jpg", "background.png", "background.jpeg",
        "bg.jpg", "bg.png", "bg.jpeg", "wallpaper.jpg", "wallpaper.png"
    ]
    root_dir = config.ROOT_DIR
    cache_dir = config.CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    for name in possible_names:
        img_path = root_dir / name
        if img_path.exists() and img_path.is_file():
            try:
                curr_mtime = img_path.stat().st_mtime
                if _CACHED_BG_BASE64 and _CACHED_SRC_MTIME == curr_mtime:
                    return _CACHED_BG_BASE64

                target_path = img_path
                file_size_kb = img_path.stat().st_size / 1024

                # Auto-optimize large images (> 500 KB) using PIL thumbnail
                if file_size_kb > 500:
                    stem = name.rsplit(".", 1)[0]
                    opt_path = cache_dir / f"opt_{stem}.jpg"
                    if not opt_path.exists() or opt_path.stat().st_mtime < curr_mtime:
                        try:
                            from PIL import Image
                            with Image.open(img_path) as im:
                                im_rgb = im.convert("RGB")
                                im_rgb.thumbnail((2560, 1440), Image.Resampling.LANCZOS)
                                im_rgb.save(opt_path, "JPEG", quality=85, optimize=True)
                        except Exception:
                            opt_path = img_path
                    if opt_path.exists():
                        target_path = opt_path

                with open(target_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    mime = "image/png" if str(target_path).endswith(".png") else "image/jpeg"
                    data_uri = f"data:{mime};base64,{encoded}"
                    _CACHED_BG_BASE64 = data_uri
                    _CACHED_SRC_MTIME = curr_mtime
                    return data_uri
            except Exception:
                pass
    return ""


def get_space_theme_css(dark_mode: bool = True) -> str:
    """Returns CSS string for Streamlit injection based on selected theme mode and custom background."""
    custom_bg = get_custom_bg_base64()

    if dark_mode:
        if custom_bg:
            bg_rule = f"""
                background: 
                    linear-gradient(180deg, rgba(8, 14, 28, 0.76) 0%, rgba(5, 9, 18, 0.86) 45%, rgba(3, 6, 14, 0.94) 100%),
                    radial-gradient(circle at 50% 20%, rgba(0, 229, 255, 0.08) 0%, rgba(0, 0, 0, 0.45) 70%),
                    url('{custom_bg}') center center / cover no-repeat fixed !important;
            """
            starlight_opacity = "0.15"
        else:
            bg_rule = """
                background: radial-gradient(ellipse at top, #0f1c3f 0%, #080c16 55%, #03060a 100%) !important;
                background-attachment: fixed !important;
            """
            starlight_opacity = "0.35"

        return f"""
<style>
    /* =======================================================
       1. Typography & Global Styles (Alexandria + Cairo)
       ======================================================= */
    @import url('https://fonts.googleapis.com/css2?family=Alexandria:wght@300;400;500;600;700;800;900&family=Cairo:wght@400;600;700;800;900&display=swap');

    *, html, body, p, span, div, input, select, textarea, button, label, table, th, td, tr, 
    h1, h2, h3, h4, h5, h6, [class*="st-"], .stMarkdown, .stText, .streamlit-expanderHeader {{
        font-family: 'Alexandria', 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    .stApp {{
        {bg_rule}
        color: #f1f5f9 !important;
    }}

    /* Ambient Starlight Texture */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(1px 1px at 25px 35px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 120px 180px, #00e5ff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 280px 340px, #00ff88, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 480px 90px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.2px 1.2px at 650px 420px, #00e5ff, rgba(0,0,0,0));
        background-repeat: repeat;
        background-size: 1000px 600px;
        opacity: {starlight_opacity};
        pointer-events: none;
        z-index: 0;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: #f8fafc !important;
        font-weight: 800 !important;
        letter-spacing: -0.2px;
    }}

    .orbital-title {{
        font-family: 'Alexandria', sans-serif !important;
        background: linear-gradient(135deg, #00e5ff 0%, #00ff88 50%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px rgba(0, 229, 255, 0.45);
        font-size: 2.35rem !important;
        font-weight: 900;
        margin-bottom: 0.2rem;
        display: inline-block;
    }}

    .orbital-badge {{
        display: inline-block;
        background: rgba(0, 229, 255, 0.12);
        border: 1px solid rgba(0, 229, 255, 0.4);
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #00e5ff;
        font-weight: 700;
        box-shadow: 0 0 16px rgba(0, 229, 255, 0.2);
        margin-bottom: 8px;
    }}

    /* =======================================================
       2. Futuristic Glassmorphism HUD Cards
       ======================================================= */
    .hud-card {{
        background: rgba(13, 22, 44, 0.78) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(0, 229, 255, 0.22) !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
        transition: all 0.3s ease;
    }}

    .hud-card:hover {{
        border-color: rgba(0, 255, 136, 0.4) !important;
        box-shadow: 0 10px 36px 0 rgba(0, 229, 255, 0.22) !important;
    }}

    .telemetry-val {{
        font-size: 1.85rem;
        font-weight: 900;
        color: #00e5ff;
    }}

    .telemetry-label {{
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 600;
        margin-top: 4px;
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, #0284c7 0%, #00e5ff 100%) !important;
        color: #04101e !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 22px !important;
        box-shadow: 0 0 18px rgba(0, 229, 255, 0.3) !important;
        transition: all 0.25s ease !important;
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, #00e5ff 0%, #00ff88 100%) !important;
        box-shadow: 0 0 28px rgba(0, 255, 136, 0.55) !important;
        transform: translateY(-1px);
    }}

    /* Controls (Selectboxes, Inputs, Radio) */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: rgba(13, 21, 39, 0.88) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }}

    div[data-baseweb="select"] *, input {{
        color: #f8fafc !important;
    }}

    ul[role="listbox"] {{
        background-color: #0d1527 !important;
        border: 1px solid #00e5ff !important;
    }}

    li[role="option"] {{
        color: #f1f5f9 !important;
        background-color: #0d1527 !important;
    }}

    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: rgba(0, 229, 255, 0.25) !important;
        color: #00ff88 !important;
    }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        font-weight: 700 !important;
        color: #94a3b8 !important;
        background: transparent !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 18px !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #00e5ff !important;
        border-bottom: 3px solid #00e5ff !important;
        background: rgba(0, 229, 255, 0.1) !important;
    }}

    /* Expanders */
    div[data-testid="stExpander"] {{
        background: rgba(13, 22, 44, 0.78) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(0, 229, 255, 0.22) !important;
        border-radius: 14px !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(6, 12, 24, 0.94) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(0, 229, 255, 0.15) !important;
    }}

    /* =======================================================
       3. Futuristic Orbital Glass Tables (Anti-Excel Theme)
       ======================================================= */
    .orbital-table-card {{
        background: rgba(13, 22, 42, 0.82) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(0, 229, 255, 0.28) !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        overflow-x: auto !important;
        margin: 16px 0 24px 0 !important;
    }}

    .orbital-table {{
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        direction: rtl !important;
        font-family: 'Alexandria', 'Cairo', sans-serif !important;
        text-align: right !important;
    }}

    .orbital-table th {{
        background: linear-gradient(180deg, rgba(0, 229, 255, 0.16) 0%, rgba(0, 229, 255, 0.06) 100%) !important;
        color: #00e5ff !important;
        font-weight: 800 !important;
        font-size: 0.92rem !important;
        padding: 14px 18px !important;
        border-bottom: 2px solid rgba(0, 229, 255, 0.35) !important;
        letter-spacing: -0.2px !important;
        white-space: nowrap !important;
    }}

    .orbital-table td {{
        padding: 12px 18px !important;
        color: #e2e8f0 !important;
        font-size: 0.88rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        vertical-align: middle !important;
    }}

    .orbital-table tbody tr:nth-child(even) {{
        background: rgba(255, 255, 255, 0.02) !important;
    }}

    .orbital-table tbody tr:hover {{
        background: rgba(0, 229, 255, 0.08) !important;
        transition: background 0.2s ease !important;
    }}

    .orbital-table tbody tr:last-child td {{
        border-bottom: none !important;
    }}

    /* Badges & Pills */
    .badge-pill {{
        display: inline-block !important;
        padding: 3px 10px !important;
        border-radius: 12px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
    }}

    .badge-cyan {{
        background: rgba(0, 229, 255, 0.12) !important;
        border: 1px solid rgba(0, 229, 255, 0.4) !important;
        color: #00e5ff !important;
    }}

    .badge-green {{
        background: rgba(0, 255, 136, 0.12) !important;
        border: 1px solid rgba(0, 255, 136, 0.4) !important;
        color: #00ff88 !important;
    }}

    .badge-orange {{
        background: rgba(255, 145, 0, 0.12) !important;
        border: 1px solid rgba(255, 145, 0, 0.4) !important;
        color: #ff9100 !important;
    }}

    .badge-blue {{
        background: rgba(56, 189, 248, 0.12) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        color: #38bdf8 !important;
    }}

    .badge-neutral {{
        background: rgba(148, 163, 184, 0.1) !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        color: #cbd5e1 !important;
    }}

    /* Color Swatch Reference */
    .color-swatch-badge {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        padding: 3px 10px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        background: rgba(14, 24, 46, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        margin: 3px !important;
    }}

    .color-dot {{
        width: 10px !important;
        height: 10px !important;
        border-radius: 50% !important;
        display: inline-block !important;
    }}

    /* Mobile Chrome */
    @media (max-width: 768px) {{
        .orbital-title {{ font-size: 1.65rem !important; }}
        .telemetry-val {{ font-size: 1.45rem !important; }}
        .hud-card {{ padding: 12px 14px !important; margin-bottom: 12px !important; }}
        .orbital-table th, .orbital-table td {{ padding: 10px 12px !important; font-size: 0.82rem !important; }}
    }}
</style>
"""
    else:
        # =======================================================
        # SOLAR DAYLIGHT THEME
        # =======================================================
        if custom_bg:
            bg_rule = f"""
                background: 
                    linear-gradient(180deg, rgba(248, 250, 252, 0.90) 0%, rgba(241, 245, 249, 0.95) 100%),
                    url('{custom_bg}') center center / cover no-repeat fixed !important;
            """
        else:
            bg_rule = """
                background: #f8fafc !important;
            """

        return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Alexandria:wght@300;400;500;600;700;800;900&family=Cairo:wght@400;600;700;800;900&display=swap');

    *, html, body, p, span, div, input, select, textarea, button, label, table, th, td, tr, 
    h1, h2, h3, h4, h5, h6, [class*="st-"], .stMarkdown, .stText, .streamlit-expanderHeader {{
        font-family: 'Alexandria', 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    .stApp {{
        {bg_rule}
        color: #0f172a !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: #0f172a !important;
        font-weight: 800 !important;
    }}

    .orbital-title {{
        font-family: 'Alexandria', sans-serif !important;
        background: linear-gradient(135deg, #0284c7 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.35rem !important;
        font-weight: 900;
        margin-bottom: 0.2rem;
        display: inline-block;
    }}

    .orbital-badge {{
        display: inline-block;
        background: rgba(2, 132, 199, 0.12);
        border: 1px solid rgba(2, 132, 199, 0.4);
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #0284c7;
        font-weight: 700;
        margin-bottom: 8px;
    }}

    .hud-card {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
    }}

    .telemetry-val {{
        font-size: 1.85rem;
        font-weight: 900;
        color: #0284c7;
    }}

    .telemetry-label {{
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 600;
        margin-top: 4px;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 22px !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25) !important;
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, #0369a1 0%, #059669 100%) !important;
    }}

    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        color: #0f172a !important;
    }}

    div[data-baseweb="select"] *, input {{
        color: #0f172a !important;
    }}

    ul[role="listbox"] {{
        background-color: #ffffff !important;
        border: 1px solid #0284c7 !important;
    }}

    li[role="option"] {{
        color: #0f172a !important;
        background-color: #ffffff !important;
    }}

    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: rgba(2, 132, 199, 0.15) !important;
        color: #0284c7 !important;
    }}

    button[data-baseweb="tab"] {{
        font-weight: 700 !important;
        color: #64748b !important;
        background: transparent !important;
        padding: 10px 18px !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #0284c7 !important;
        border-bottom: 3px solid #0284c7 !important;
        background: rgba(2, 132, 199, 0.08) !important;
    }}

    div[data-testid="stExpander"] {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
    }}

    [data-testid="stSidebar"] {{
        background: #f1f5f9 !important;
        border-right: 1px solid #e2e8f0 !important;
    }}

    .orbital-table-card {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
        overflow-x: auto !important;
        margin: 16px 0 24px 0 !important;
    }}

    .orbital-table {{
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        direction: rtl !important;
        font-family: 'Alexandria', 'Cairo', sans-serif !important;
        text-align: right !important;
    }}

    .orbital-table th {{
        background: rgba(2, 132, 199, 0.08) !important;
        color: #0284c7 !important;
        font-weight: 800 !important;
        font-size: 0.92rem !important;
        padding: 14px 18px !important;
        border-bottom: 2px solid #e2e8f0 !important;
        white-space: nowrap !important;
    }}

    .orbital-table td {{
        padding: 12px 18px !important;
        color: #1e293b !important;
        font-size: 0.88rem !important;
        border-bottom: 1px solid #f1f5f9 !important;
        vertical-align: middle !important;
    }}

    .orbital-table tbody tr:nth-child(even) {{
        background: #f8fafc !important;
    }}

    .orbital-table tbody tr:hover {{
        background: rgba(2, 132, 199, 0.04) !important;
    }}

    .badge-pill {{
        display: inline-block !important;
        padding: 3px 10px !important;
        border-radius: 12px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
    }}

    .badge-cyan {{
        background: rgba(2, 132, 199, 0.1) !important;
        border: 1px solid rgba(2, 132, 199, 0.3) !important;
        color: #0284c7 !important;
    }}

    .badge-green {{
        background: rgba(5, 150, 105, 0.1) !important;
        border: 1px solid rgba(5, 150, 105, 0.3) !important;
        color: #059669 !important;
    }}

    .badge-orange {{
        background: rgba(217, 119, 6, 0.1) !important;
        border: 1px solid rgba(217, 119, 6, 0.3) !important;
        color: #d97706 !important;
    }}

    .badge-blue {{
        background: rgba(2, 132, 199, 0.1) !important;
        border: 1px solid rgba(2, 132, 199, 0.3) !important;
        color: #0284c7 !important;
    }}

    .badge-neutral {{
        background: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        color: #475569 !important;
    }}

    .color-swatch-badge {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        padding: 3px 10px !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        background: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        margin: 3px !important;
    }}

    .color-dot {{
        width: 10px !important;
        height: 10px !important;
        border-radius: 50% !important;
        display: inline-block !important;
    }}

    @media (max-width: 768px) {{
        .orbital-title {{ font-size: 1.65rem !important; }}
        .telemetry-val {{ font-size: 1.45rem !important; }}
        .hud-card {{ padding: 12px 14px !important; margin-bottom: 12px !important; }}
        .orbital-table th, .orbital-table td {{ padding: 10px 12px !important; font-size: 0.82rem !important; }}
    }}
</style>
"""
