"""
AgroOrbit - Egypt Governorates Geospatial & Agronomic Registry
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data

Full geospatial centroids, agricultural zoning, dominant soils,
and regional classifications for all 27 Egyptian Governorates.
"""

from typing import Dict, Any, List

EGYPT_REGIONS = {
    "delta": {
        "name_ar": "وجه بحري والدلتا",
        "name_en": "Nile Delta & North",
        "color": "#00ff88"
    },
    "upper_egypt": {
        "name_ar": "مصر الوسطى والصعيد",
        "name_en": "Middle & Upper Egypt",
        "color": "#ff9100"
    },
    "frontier": {
        "name_ar": "المحافظات الحدودية والاستصلاح",
        "name_en": "Frontier & Reclamation",
        "color": "#00e5ff"
    },
    "canal_coastal": {
        "name_ar": "القناة والمدن الساحلية",
        "name_en": "Canal & Coastal Cities",
        "color": "#b388ff"
    }
}

EGYPT_GOVERNORATES: Dict[str, Dict[str, Any]] = {
    "dakahlia": {
        "id": "dakahlia",
        "name_ar": "الدقهلية",
        "name_en": "Dakahlia",
        "lat": 31.0409,
        "lon": 31.3785,
        "region": "delta",
        "dominant_soil": "clay",
        "main_crops": ["wheat", "rice", "clover", "cotton", "sugar_beet"],
        "agricultural_area_feddan": 650000,
        "water_source": "Nile surface irrigation",
        "salinity_risk": "low_to_medium"
    },
    "beheira": {
        "id": "beheira",
        "name_ar": "البحيرة",
        "name_en": "Beheira",
        "lat": 30.8481,
        "lon": 30.3436,
        "region": "delta",
        "dominant_soil": "loam",
        "main_crops": ["potato", "tomato", "wheat", "sugar_beet", "onion"],
        "agricultural_area_feddan": 920000,
        "water_source": "Nile branches + groundwater reclamation",
        "salinity_risk": "medium"
    },
    "sharqia": {
        "id": "sharqia",
        "name_ar": "الشرقية",
        "name_en": "Sharqia",
        "lat": 30.5765,
        "lon": 31.5041,
        "region": "delta",
        "dominant_soil": "clay",
        "main_crops": ["wheat", "rice", "clover", "maize", "sugar_beet"],
        "agricultural_area_feddan": 880000,
        "water_source": "Nile canals + drain reuse",
        "salinity_risk": "medium"
    },
    "kafr_el_sheikh": {
        "id": "kafr_el_sheikh",
        "name_ar": "كفر الشيخ",
        "name_en": "Kafr El Sheikh",
        "lat": 31.1107,
        "lon": 30.9388,
        "region": "delta",
        "dominant_soil": "clay",
        "main_crops": ["rice", "cotton", "sugar_beet", "wheat", "clover"],
        "agricultural_area_feddan": 560000,
        "water_source": "Lower Nile delta canals",
        "salinity_risk": "high"
    },
    "gharbia": {
        "id": "gharbia",
        "name_ar": "الغربية",
        "name_en": "Gharbia",
        "lat": 30.7865,
        "lon": 31.0004,
        "region": "delta",
        "dominant_soil": "clay",
        "main_crops": ["wheat", "clover", "maize", "onion", "cotton"],
        "agricultural_area_feddan": 390000,
        "water_source": "Nile heartland canals",
        "salinity_risk": "low"
    },
    "menoufia": {
        "id": "menoufia",
        "name_ar": "المنوفية",
        "name_en": "Menoufia",
        "lat": 30.4720,
        "lon": 30.9904,
        "region": "delta",
        "dominant_soil": "loam",
        "main_crops": ["maize", "wheat", "clover", "potato", "soybean"],
        "agricultural_area_feddan": 330000,
        "water_source": "Rosetta and Damietta Nile forks",
        "salinity_risk": "low"
    },
    "qalyubia": {
        "id": "qalyubia",
        "name_ar": "القليوبية",
        "name_en": "Qalyubia",
        "lat": 30.3292,
        "lon": 31.2168,
        "region": "delta",
        "dominant_soil": "loam",
        "main_crops": ["maize", "wheat", "clover", "tomato", "citrus"],
        "agricultural_area_feddan": 175000,
        "water_source": "Nile canals",
        "salinity_risk": "low"
    },
    "damietta": {
        "id": "damietta",
        "name_ar": "دمياط",
        "name_en": "Damietta",
        "lat": 31.4175,
        "lon": 31.8144,
        "region": "delta",
        "dominant_soil": "clay",
        "main_crops": ["rice", "wheat", "tomato", "clover"],
        "agricultural_area_feddan": 115000,
        "water_source": "Nile Damietta branch terminus",
        "salinity_risk": "high"
    },
    "faiyum": {
        "id": "faiyum",
        "name_ar": "الفيوم",
        "name_en": "Faiyum",
        "lat": 29.3084,
        "lon": 30.8428,
        "region": "upper_egypt",
        "dominant_soil": "clay",
        "main_crops": ["wheat", "clover", "sugar_beet", "tomato", "onion"],
        "agricultural_area_feddan": 420000,
        "water_source": "Bahr Yussef canal basin",
        "salinity_risk": "medium_to_high"
    },
    "beni_suef": {
        "id": "beni_suef",
        "name_ar": "بني سويف",
        "name_en": "Beni Suef",
        "lat": 29.0661,
        "lon": 31.0994,
        "region": "upper_egypt",
        "dominant_soil": "clay",
        "main_crops": ["wheat", "maize", "garlic", "onion", "soybean"],
        "agricultural_area_feddan": 310000,
        "water_source": "Ibrahimia canal & Nile",
        "salinity_risk": "low"
    },
    "minya": {
        "id": "minya",
        "name_ar": "المنيا",
        "name_en": "Minya",
        "lat": 28.0871,
        "lon": 30.7618,
        "region": "upper_egypt",
        "dominant_soil": "loam",
        "main_crops": ["sugar_beet", "soybean", "wheat", "maize", "potato"],
        "agricultural_area_feddan": 540000,
        "water_source": "Ibrahimia canal + west desert groundwater",
        "salinity_risk": "low_to_medium"
    },
    "asyut": {
        "id": "asyut",
        "name_ar": "أسيوط",
        "name_en": "Asyut",
        "lat": 27.1783,
        "lon": 31.1859,
        "region": "upper_egypt",
        "dominant_soil": "clay",
        "main_crops": ["wheat", "maize", "cotton", "faba_bean", "clover"],
        "agricultural_area_feddan": 360000,
        "water_source": "Nile river valley canals",
        "salinity_risk": "low"
    },
    "sohag": {
        "id": "sohag",
        "name_ar": "سوهاج",
        "name_en": "Sohag",
        "lat": 26.5590,
        "lon": 31.6957,
        "region": "upper_egypt",
        "dominant_soil": "clay",
        "main_crops": ["wheat", "sugar_cane", "clover", "onion", "maize"],
        "agricultural_area_feddan": 320000,
        "water_source": "Nile river valley canals",
        "salinity_risk": "low"
    },
    "qena": {
        "id": "qena",
        "name_ar": "قنا",
        "name_en": "Qena",
        "lat": 26.1551,
        "lon": 32.7160,
        "region": "upper_egypt",
        "dominant_soil": "clay",
        "main_crops": ["sugar_cane", "wheat", "tomato", "clover", "faba_bean"],
        "agricultural_area_feddan": 280000,
        "water_source": "Upper Nile main stream",
        "salinity_risk": "low"
    },
    "luxor": {
        "id": "luxor",
        "name_ar": "الأقصر",
        "name_en": "Luxor",
        "lat": 25.6872,
        "lon": 32.6396,
        "region": "upper_egypt",
        "dominant_soil": "clay",
        "main_crops": ["sugar_cane", "tomato", "wheat", "onion"],
        "agricultural_area_feddan": 150000,
        "water_source": "Nile main stream",
        "salinity_risk": "low"
    },
    "aswan": {
        "id": "aswan",
        "name_ar": "أسوان",
        "name_en": "Aswan",
        "lat": 24.0889,
        "lon": 32.8998,
        "region": "upper_egypt",
        "dominant_soil": "sandy",
        "main_crops": ["sugar_cane", "wheat", "dates", "hibiscus"],
        "agricultural_area_feddan": 210000,
        "water_source": "Lake Nasser & Nile south",
        "salinity_risk": "low"
    },
    "giza": {
        "id": "giza",
        "name_ar": "الجيزة",
        "name_en": "Giza",
        "lat": 30.0131,
        "lon": 31.2089,
        "region": "upper_egypt",
        "dominant_soil": "loam",
        "main_crops": ["wheat", "clover", "maize", "tomato", "potato"],
        "agricultural_area_feddan": 190000,
        "water_source": "Nile + desert reclamation wells",
        "salinity_risk": "medium"
    },
    "new_valley": {
        "id": "new_valley",
        "name_ar": "الوادي الجديد",
        "name_en": "New Valley (El Wadi El Gedid)",
        "lat": 25.4514,
        "lon": 30.5472,
        "region": "frontier",
        "dominant_soil": "sandy",
        "main_crops": ["wheat", "dates", "clover", "onion", "potato"],
        "agricultural_area_feddan": 480000,
        "water_source": "Nubian Sandstone Deep Aquifer",
        "salinity_risk": "medium"
    },
    "matrouh": {
        "id": "matrouh",
        "name_ar": "مطروح",
        "name_en": "Matrouh",
        "lat": 31.3543,
        "lon": 27.2373,
        "region": "frontier",
        "dominant_soil": "calcareous",
        "main_crops": ["olive", "fig", "barley", "wheat", "tomato"],
        "agricultural_area_feddan": 260000,
        "water_source": "Winter precipitation + coastal wells",
        "salinity_risk": "high"
    },
    "north_sinai": {
        "id": "north_sinai",
        "name_ar": "شمال سيناء",
        "name_en": "North Sinai",
        "lat": 31.1316,
        "lon": 33.7984,
        "region": "frontier",
        "dominant_soil": "sandy",
        "main_crops": ["olive", "peach", "wheat", "barley", "tomato"],
        "agricultural_area_feddan": 210000,
        "water_source": "El Salam canal + groundwater",
        "salinity_risk": "medium_to_high"
    },
    "south_sinai": {
        "id": "south_sinai",
        "name_ar": "جنوب سيناء",
        "name_en": "South Sinai",
        "lat": 28.9599,
        "lon": 34.0531,
        "region": "frontier",
        "dominant_soil": "calcareous",
        "main_crops": ["olive", "dates", "herbs", "vegetables"],
        "agricultural_area_feddan": 35000,
        "water_source": "Wadi flash floods + deep wells",
        "salinity_risk": "high"
    },
    "red_sea": {
        "id": "red_sea",
        "name_ar": "البحر الأحمر",
        "name_en": "Red Sea",
        "lat": 26.7292,
        "lon": 33.9365,
        "region": "frontier",
        "dominant_soil": "sandy",
        "main_crops": ["vegetables", "dates", "herbs"],
        "agricultural_area_feddan": 15000,
        "water_source": "Wadi wells & desalination brackish",
        "salinity_risk": "high"
    },
    "alexandria": {
        "id": "alexandria",
        "name_ar": "الإسكندرية",
        "name_en": "Alexandria",
        "lat": 31.2001,
        "lon": 29.9187,
        "region": "canal_coastal",
        "dominant_soil": "calcareous",
        "main_crops": ["wheat", "sugar_beet", "tomato", "clover"],
        "agricultural_area_feddan": 160000,
        "water_source": "Mahmoudia & Nubaria canals",
        "salinity_risk": "medium"
    },
    "ismailia": {
        "id": "ismailia",
        "name_ar": "الإسماعيلية",
        "name_en": "Ismailia",
        "lat": 30.5965,
        "lon": 32.2715,
        "region": "canal_coastal",
        "dominant_soil": "sandy",
        "main_crops": ["mango", "peanut", "strawberry", "wheat", "maize"],
        "agricultural_area_feddan": 380000,
        "water_source": "Ismailia sweetwater canal",
        "salinity_risk": "low_to_medium"
    },
    "port_said": {
        "id": "port_said",
        "name_ar": "بورسعيد",
        "name_en": "Port Said",
        "lat": 31.2653,
        "lon": 32.3019,
        "region": "canal_coastal",
        "dominant_soil": "clay",
        "main_crops": ["sugar_beet", "wheat", "cotton", "rice"],
        "agricultural_area_feddan": 135000,
        "water_source": "El Serw canal & drain reclamation",
        "salinity_risk": "high"
    },
    "suez": {
        "id": "suez",
        "name_ar": "السويس",
        "name_en": "Suez",
        "lat": 29.9668,
        "lon": 32.5498,
        "region": "canal_coastal",
        "dominant_soil": "sandy",
        "main_crops": ["wheat", "clover", "vegetables", "maize"],
        "agricultural_area_feddan": 45000,
        "water_source": "Suez sweetwater canal",
        "salinity_risk": "medium"
    },
    "cairo": {
        "id": "cairo",
        "name_ar": "القاهرة",
        "name_en": "Cairo",
        "lat": 30.0444,
        "lon": 31.2357,
        "region": "canal_coastal",
        "dominant_soil": "loam",
        "main_crops": ["vegetables", "fodder", "herbs"],
        "agricultural_area_feddan": 12000,
        "water_source": "Nile metro periphery",
        "salinity_risk": "low"
    }
}


def get_governorate(gov_id: str) -> Dict[str, Any]:
    """Retrieve governorate data by identifier."""
    return EGYPT_GOVERNORATES.get(gov_id, {})


def get_all_governorates() -> List[Dict[str, Any]]:
    """Retrieve list of all 27 governorates."""
    return list(EGYPT_GOVERNORATES.values())


def get_governorates_by_region(region_key: str) -> List[Dict[str, Any]]:
    """Filter governorates by agricultural zone/region."""
    return [g for g in EGYPT_GOVERNORATES.values() if g["region"] == region_key]


def get_governorate_choices() -> Dict[str, str]:
    """Return dictionary of {id: 'Arabic Name (English Name)'} for UI dropdowns."""
    return {
        gid: f"{g['name_ar']} ({g['name_en']})"
        for gid, g in EGYPT_GOVERNORATES.items()
    }
