"""
AgroOrbit - Configuration & System Constants
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data
"""

import os
from pathlib import Path

# ==========================================
# 1. Project Identity & Metadata
# ==========================================
APP_NAME = "AgroOrbit"
APP_NAME_AR = "أجرواوربت"
APP_TAGLINE = "Precision Agro-Climatic Decision Support System"
APP_TAGLINE_AR = "المنظومة المدارية الذكية لدعم القرار الزراعي وتكييف المزارع"
TEAM_NAME = "Nova Squad NASA"
CHALLENGE_TITLE = "Field Shift: Adapting Farms with NASA Data"
CHALLENGE_YEAR = 2026

# ==========================================
# 2. File System & Directory Paths
# ==========================================
ROOT_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
GOVERNORATES_CACHE_FILE = CACHE_DIR / "governorates_baseline.json"
CACHE_EXPIRY_HOURS = 24

# ==========================================
# 3. NASA POWER API Telemetry Settings
# ==========================================
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_COMMUNITY = "AG"  # Agroclimatology Community

NASA_CORE_PARAMETERS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "PRECTOTCORR",
    "RH2M",
    "GWETROOT",
    "GWETTOP",
    "ALLSKY_SFC_SW_DWN"
]

NASA_PARAMETERS_QUERY_STRING = ",".join(NASA_CORE_PARAMETERS)
ANOMALY_FLAGS = [-999.0, -99.0, -999, -99]
DEFAULT_QUERY_DAYS = 30
MIN_CONFIDENCE_THRESHOLD = 0.70

# ==========================================
# 4. Agricultural & Edaphic Taxonomy
# ==========================================
SOIL_TYPES = {
    "clay": {
        "name_ar": "طينية (Clay)",
        "name_en": "Clay",
        "water_retention": "high",
        "drainage": "low",
        "fertility_base": 0.85,
        "description_ar": "تربة عالية الخصوبة والاحتفاظ بالمياه لكنها بطيئة التصريف وتحتاج ضبط الري لتفادي تعفن الجذور."
    },
    "loam": {
        "name_ar": "طميية (Loam)",
        "name_en": "Loam",
        "water_retention": "medium",
        "drainage": "medium",
        "fertility_base": 0.90,
        "description_ar": "تربة مثالية متوازنة، تجمع بين الاحتفاظ المناسب بالرطوبة والتهوية الجيدة لكافة المحاصيل."
    },
    "sandy": {
        "name_ar": "رملية (Sandy)",
        "name_en": "Sandy",
        "water_retention": "low",
        "drainage": "very_high",
        "fertility_base": 0.50,
        "description_ar": "تربة سريعة التصريف ومنخفضة الاحتفاظ بالعناصر، تتطلب ري بالتنقيط ومحاصيل مقاومة للجفاف."
    },
    "calcareous": {
        "name_ar": "جيرية (Calcareous)",
        "name_en": "Calcareous",
        "water_retention": "medium_low",
        "drainage": "medium",
        "fertility_base": 0.65,
        "description_ar": "تربة شائعة في مناطق الاستصلاح بالساحل الشمالي، تتميز بارتفاع كربونات الكالسيوم وحساسيتها لنقص الفوسفور والحديد."
    }
}

# ==========================================
# 5. Visual Palette (NASA Orbital Mission Control)
# ==========================================
THEME_COLORS = {
    "bg_dark": "#080c14",
    "bg_secondary": "#0e1626",
    "card_bg": "rgba(16, 26, 46, 0.75)",
    "card_border": "rgba(0, 229, 255, 0.20)",
    "neon_cyan": "#00e5ff",
    "neon_green": "#00ff88",
    "solar_amber": "#ff9100",
    "alert_red": "#ff3d71",
    "text_primary": "#f0f4f8",
    "text_muted": "#8899ac"
}
