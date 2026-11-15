"""
AgroOrbit - Crop Agronomic & Biological Database
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data

Contains comprehensive agronomic, physiological, and ecological parameters
for major strategic Egyptian crops, covering biological nitrogen fixation (BNF),
water footprint, thermal thresholds, and pest-cycle interruption dynamics.
"""

from typing import Dict, Any, List

CROPS_DATABASE: Dict[str, Dict[str, Any]] = {
    "wheat": {
        "id": "wheat",
        "name_ar": "القمح",
        "name_en": "Wheat",
        "scientific_name": "Triticum aestivum",
        "season_type": "winter",
        "season_label_ar": "شتوي (نوفمبر - مايو)",
        "season_label_en": "Winter (Nov - May)",
        "temp_min": 10.0,
        "temp_opt_min": 15.0,
        "temp_opt_max": 23.0,
        "temp_max": 28.0,
        "heat_stress_threshold": 32.0,
        "water_need_level": "medium",
        "water_demand_mm": 450.0,
        "water_savings_potential": 0.65,
        "nitrogen_effect": "neutral",
        "nitrogen_balance_kg_ha": -20.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["clay", "loam", "calcareous"],
        "profit_level": "medium",
        "profit_score": 0.65,
        "erosion_control": "high",
        "organic_matter_score": 0.60,
        "common_diseases_ar": [
            "الصدأ الأصفر (Yellow Rust)",
            "صدأ الساق والبرتقالي (Stem Rust)",
            "التفحم السائب (Loose Smut)",
            "البياض الدقيقي (Powdery Mildew)"
        ],
        "pest_families": ["rusts", "smut", "aphids", "mildew"],
        "breaks_pest_cycle_of": ["maize", "rice", "cotton"],
        "bare_field_months": [6, 7],
        "description_ar": "المحصول الاستراتيجي الأول للأمن الغذائي بمصر، مناسب لغالبية أنواع الأراضي الزراعية."
    },
    "clover": {
        "id": "clover",
        "name_ar": "البرسيم المصري",
        "name_en": "Egyptian Clover (Berseem)",
        "scientific_name": "Trifolium alexandrinum",
        "season_type": "winter",
        "season_label_ar": "شتوي (أكتوبر - مايو)",
        "season_label_en": "Winter (Oct - May)",
        "temp_min": 12.0,
        "temp_opt_min": 16.0,
        "temp_opt_max": 25.0,
        "temp_max": 30.0,
        "heat_stress_threshold": 34.0,
        "water_need_level": "high",
        "water_demand_mm": 580.0,
        "water_savings_potential": 0.40,
        "nitrogen_effect": "improves",
        "nitrogen_balance_kg_ha": 160.0,
        "biological_nitrogen_fixer": True,
        "soil_suitability": ["clay", "loam", "calcareous"],
        "profit_level": "medium",
        "profit_score": 0.55,
        "erosion_control": "very_high",
        "organic_matter_score": 0.95,
        "common_diseases_ar": [
            "عفن الجذور والتاج (Root Rot)",
            "البياض الدقيقي (Powdery Mildew)",
            "دودة ورق القطن في الحشات الأولى"
        ],
        "pest_families": ["root_rot", "mildew", "armyworm"],
        "breaks_pest_cycle_of": ["maize", "rice", "wheat", "cotton"],
        "bare_field_months": [6],
        "description_ar": "ملك المحاصيل البقولية الشتوية في مصر، يثبت أكثر من 150 كجم نيتروجين/هكتار ويجدد خصوبة التربة المنهكة."
    },
    "maize": {
        "id": "maize",
        "name_ar": "الذرة الشامية",
        "name_en": "Maize",
        "scientific_name": "Zea mays",
        "season_type": "summer",
        "season_label_ar": "صيفي (مايو - سبتمبر)",
        "season_label_en": "Summer (May - Sep)",
        "temp_min": 18.0,
        "temp_opt_min": 24.0,
        "temp_opt_max": 32.0,
        "temp_max": 38.0,
        "heat_stress_threshold": 38.0,
        "water_need_level": "high",
        "water_demand_mm": 650.0,
        "water_savings_potential": 0.45,
        "nitrogen_effect": "depletes",
        "nitrogen_balance_kg_ha": -160.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["clay", "loam", "sandy"],
        "profit_level": "high",
        "profit_score": 0.78,
        "erosion_control": "medium",
        "organic_matter_score": 0.50,
        "common_diseases_ar": [
            "دودة الحشد الخريفية (Fall Armyworm)",
            "لفحة الأوراق (Leaf Blight)",
            "التفحم العادي (Common Smut)",
            "ثاقبات الذرة (Corn Borers)"
        ],
        "pest_families": ["armyworm", "leaf_blight", "borers"],
        "breaks_pest_cycle_of": ["clover", "faba_bean"],
        "bare_field_months": [10, 11],
        "description_ar": "محصول صيفي رئيسي للأعلاف والصناعات الغذائية، مجهد للنيتروجين ويحتاج دورة تعويضية بعده."
    },
    "faba_bean": {
        "id": "faba_bean",
        "name_ar": "الفول البلدي",
        "name_en": "Faba Bean",
        "scientific_name": "Vicia faba",
        "season_type": "winter",
        "season_label_ar": "شتوي (نوفمبر - أبريل)",
        "season_label_en": "Winter (Nov - Apr)",
        "temp_min": 12.0,
        "temp_opt_min": 16.0,
        "temp_opt_max": 24.0,
        "temp_max": 28.0,
        "heat_stress_threshold": 30.0,
        "water_need_level": "medium",
        "water_demand_mm": 380.0,
        "water_savings_potential": 0.75,
        "nitrogen_effect": "improves",
        "nitrogen_balance_kg_ha": 110.0,
        "biological_nitrogen_fixer": True,
        "soil_suitability": ["clay", "loam", "calcareous"],
        "profit_level": "high",
        "profit_score": 0.80,
        "erosion_control": "high",
        "organic_matter_score": 0.85,
        "common_diseases_ar": [
            "التبقع البني (Chocolate Spot)",
            "الصدأ (Bean Rust)",
            "الهالوك (Orobanche)",
            "أعفان الجذور والذبول"
        ],
        "pest_families": ["parasitic_weeds", "leaf_spot", "rusts"],
        "breaks_pest_cycle_of": ["maize", "rice", "wheat"],
        "bare_field_months": [5, 6],
        "description_ar": "غذاء شعبي أساسي ومثبت ممتاز للنيتروجين، ذو كفاءة مائية عالية مقارنة بالبرسيم."
    },
    "rice": {
        "id": "rice",
        "name_ar": "الأرز",
        "name_en": "Rice",
        "scientific_name": "Oryza sativa",
        "season_type": "summer",
        "season_label_ar": "صيفي (مايو - أكتوبر)",
        "season_label_en": "Summer (May - Oct)",
        "temp_min": 20.0,
        "temp_opt_min": 25.0,
        "temp_opt_max": 33.0,
        "temp_max": 38.0,
        "heat_stress_threshold": 37.0,
        "water_need_level": "very_high",
        "water_demand_mm": 1150.0,
        "water_savings_potential": 0.15,
        "nitrogen_effect": "depletes",
        "nitrogen_balance_kg_ha": -130.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["clay"],
        "profit_level": "high",
        "profit_score": 0.82,
        "erosion_control": "medium",
        "organic_matter_score": 0.40,
        "common_diseases_ar": [
            "اللفحة (Rice Blast)",
            "التبقع البني (Brown Spot)",
            "ديدان القصب والحشرات الثاقبة"
        ],
        "pest_families": ["blast", "brown_spot", "borers"],
        "breaks_pest_cycle_of": ["clover", "faba_bean"],
        "bare_field_months": [11, 12],
        "description_ar": "محصول استراتيجي صيفي يتركز في شمال الدلتا لغسيل أملاح التربة، لكنه يستهلك مقننات مائية ضخمة."
    },
    "tomato": {
        "id": "tomato",
        "name_ar": "الطماطم",
        "name_en": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "season_type": "summer",
        "season_label_ar": "صيفي/شتوي (عروات متعددة)",
        "season_label_en": "Multi-season crops",
        "temp_min": 15.0,
        "temp_opt_min": 20.0,
        "temp_opt_max": 28.0,
        "temp_max": 34.0,
        "heat_stress_threshold": 35.0,
        "water_need_level": "high",
        "water_demand_mm": 520.0,
        "water_savings_potential": 0.50,
        "nitrogen_effect": "depletes",
        "nitrogen_balance_kg_ha": -140.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["loam", "sandy", "clay"],
        "profit_level": "very_high",
        "profit_score": 0.92,
        "erosion_control": "medium",
        "organic_matter_score": 0.45,
        "common_diseases_ar": [
            "اللفحة المبكرة والمتأخرة (Early & Late Blight)",
            "الذبول البكتيري والفيوزاريوم",
            "فيروس تجعد واصفرار الأوراق (TYLCV)",
            "توتا أبسلوتا (Tuta absoluta)"
        ],
        "pest_families": ["solanaceous_blight", "wilt", "leafminer"],
        "breaks_pest_cycle_of": ["wheat", "clover"],
        "bare_field_months": [7, 8],
        "description_ar": "محصول نقدي عالي الربحية، شديد الحساسية للآفات ودرجات الحرارة القصوى، يجهد خصوبة التربة."
    },
    "onion": {
        "id": "onion",
        "name_ar": "البصل",
        "name_en": "Onion",
        "scientific_name": "Allium cepa",
        "season_type": "winter",
        "season_label_ar": "شتوي/ربيعي (نوفمبر - مايو)",
        "season_label_en": "Winter/Spring (Nov - May)",
        "temp_min": 12.0,
        "temp_opt_min": 16.0,
        "temp_opt_max": 24.0,
        "temp_max": 30.0,
        "heat_stress_threshold": 32.0,
        "water_need_level": "medium",
        "water_demand_mm": 410.0,
        "water_savings_potential": 0.70,
        "nitrogen_effect": "neutral",
        "nitrogen_balance_kg_ha": -50.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["loam", "clay", "sandy"],
        "profit_level": "high",
        "profit_score": 0.85,
        "erosion_control": "medium",
        "organic_matter_score": 0.50,
        "common_diseases_ar": [
            "العفن الأبيض (White Rot)",
            "البياض الزغبي (Downy Mildew)",
            "اللطعة الأرجوانية (Purple Blotch)",
            "تربس البصل (Thrips)"
        ],
        "pest_families": ["white_rot", "downy_mildew", "thrips"],
        "breaks_pest_cycle_of": ["maize", "cotton"],
        "bare_field_months": [6, 7],
        "description_ar": "محصول تصديري واعد بمصر يتميز بمتوسط استهلاك مائي معتدل وقدرة على تنويع دخل المزرعة."
    },
    "sugar_beet": {
        "id": "sugar_beet",
        "name_ar": "بنجر السكر",
        "name_en": "Sugar Beet",
        "scientific_name": "Beta vulgaris",
        "season_type": "winter",
        "season_label_ar": "شتوي (أغسطس/أكتوبر - مارس/مايو)",
        "season_label_en": "Winter (Aug/Oct - Mar/May)",
        "temp_min": 12.0,
        "temp_opt_min": 18.0,
        "temp_opt_max": 26.0,
        "temp_max": 32.0,
        "heat_stress_threshold": 33.0,
        "water_need_level": "medium",
        "water_demand_mm": 430.0,
        "water_savings_potential": 0.72,
        "nitrogen_effect": "neutral",
        "nitrogen_balance_kg_ha": -40.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["clay", "calcareous", "loam", "sandy"],
        "profit_level": "high",
        "profit_score": 0.82,
        "erosion_control": "high",
        "organic_matter_score": 0.70,
        "common_diseases_ar": [
            "تبقع الأوراق السركسبوري (Cercospora Leaf Spot)",
            "البياض الدقيقي (Powdery Mildew)",
            "خنفساء البنجر السلحفائية وذبابة البنجر",
            "أعفان الجذور والرايزوكتونيا"
        ],
        "pest_families": ["cercospora", "mildew", "beet_beetle"],
        "breaks_pest_cycle_of": ["wheat", "maize", "rice"],
        "bare_field_months": [5, 6],
        "description_ar": "أحد أهم محاصيل السكر بالدلتا ومشاريع الاستصلاح، يتحمل الملوحة المعتدلة ويوفر المياه مقارنة بالقصب."
    },
    "cotton": {
        "id": "cotton",
        "name_ar": "القطن المصري",
        "name_en": "Egyptian Cotton",
        "scientific_name": "Gossypium barbadense",
        "season_type": "summer",
        "season_label_ar": "صيفي (مارس/أبريل - أكتوبر)",
        "season_label_en": "Summer (Mar/Apr - Oct)",
        "temp_min": 18.0,
        "temp_opt_min": 25.0,
        "temp_opt_max": 34.0,
        "temp_max": 40.0,
        "heat_stress_threshold": 40.0,
        "water_need_level": "high",
        "water_demand_mm": 720.0,
        "water_savings_potential": 0.40,
        "nitrogen_effect": "depletes",
        "nitrogen_balance_kg_ha": -120.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["clay", "loam"],
        "profit_level": "high",
        "profit_score": 0.88,
        "erosion_control": "medium",
        "organic_matter_score": 0.55,
        "common_diseases_ar": [
            "دودة ورق القطن (Cotton Leafworm)",
            "ديدان اللوز الشوكية والقرنفلية",
            "الذبول الفيوزاريومي (Fusarium Wilt)",
            "المن والتربس في البادرات الأولى"
        ],
        "pest_families": ["bollworm", "leafworm", "wilt"],
        "breaks_pest_cycle_of": ["wheat", "clover"],
        "bare_field_months": [11, 12],
        "description_ar": "الذهب الأبيض الشهير عالمياً بجودته وفائق طول تيلته، يمثل عموداً للصناعة والتصدير بالدلتا."
    },
    "potato": {
        "id": "potato",
        "name_ar": "البطاطس",
        "name_en": "Potato",
        "scientific_name": "Solanum tuberosum",
        "season_type": "winter",
        "season_label_ar": "شتوي/خريفي (عروات سبتمبر ونوفمبر)",
        "season_label_en": "Winter/Autumn (Sep - Feb)",
        "temp_min": 10.0,
        "temp_opt_min": 16.0,
        "temp_opt_max": 23.0,
        "temp_max": 28.0,
        "heat_stress_threshold": 30.0,
        "water_need_level": "medium",
        "water_demand_mm": 470.0,
        "water_savings_potential": 0.65,
        "nitrogen_effect": "depletes",
        "nitrogen_balance_kg_ha": -110.0,
        "biological_nitrogen_fixer": False,
        "soil_suitability": ["loam", "sandy"],
        "profit_level": "very_high",
        "profit_score": 0.94,
        "erosion_control": "medium",
        "organic_matter_score": 0.55,
        "common_diseases_ar": [
            "الندوة المتأخرة والمبكرة (Late & Early Blight)",
            "الجرب العادي والعفن البني البكتيري",
            "فراشة درنات البطاطس",
            "النيماتودا الحوصلية"
        ],
        "pest_families": ["solanaceous_blight", "potato_tuber_moth", "nematodes"],
        "breaks_pest_cycle_of": ["wheat", "maize"],
        "bare_field_months": [3, 4],
        "description_ar": "محصول تصديري واقتصادي ضخم بمصر يزرع بكثافة في الأراضي الرملية والطميية الحديثة والوادي."
    },
    "soybean": {
        "id": "soybean",
        "name_ar": "فول الصويا",
        "name_en": "Soybean",
        "scientific_name": "Glycine max",
        "season_type": "summer",
        "season_label_ar": "صيفي (مايو - سبتمبر)",
        "season_label_en": "Summer (May - Sep)",
        "temp_min": 18.0,
        "temp_opt_min": 22.0,
        "temp_opt_max": 30.0,
        "temp_max": 36.0,
        "heat_stress_threshold": 36.0,
        "water_need_level": "medium",
        "water_demand_mm": 490.0,
        "water_savings_potential": 0.70,
        "nitrogen_effect": "improves",
        "nitrogen_balance_kg_ha": 90.0,
        "biological_nitrogen_fixer": True,
        "soil_suitability": ["loam", "clay", "sandy"],
        "profit_level": "high",
        "profit_score": 0.82,
        "erosion_control": "high",
        "organic_matter_score": 0.80,
        "common_diseases_ar": [
            "عفن الجذور الفيوزاريومي (Fusarium Root Rot)",
            "دودة ورق القطن والحفار",
            "فيروس الموزاييك (Soybean Mosaic Virus)"
        ],
        "pest_families": ["root_rot", "armyworm", "mosaic_virus"],
        "breaks_pest_cycle_of": ["wheat", "maize", "rice", "cotton"],
        "bare_field_months": [10, 11],
        "description_ar": "محصول زيت وبقوليات صيفي استراتيجي يثبت النيتروجين ويعوض إجهاد المحاصيل الصيفية كبديل واعد للذرة والأرز."
    }
}


def get_crop(crop_id: str) -> Dict[str, Any]:
    """Retrieve crop specifications by identifier."""
    return CROPS_DATABASE.get(crop_id, {})


def get_all_crop_ids() -> List[str]:
    """Retrieve all available crop identifiers."""
    return list(CROPS_DATABASE.keys())


def get_crops_by_season(season: str) -> List[Dict[str, Any]]:
    """Filter crops by growing season (winter / summer)."""
    return [crop for crop in CROPS_DATABASE.values() if crop["season_type"] == season]


def check_pest_interruption(prev_crop_id: str, next_crop_id: str) -> bool:
    """
    Check if the next crop effectively interrupts the pest/disease cycle of the previous crop.
    """
    next_crop = get_crop(next_crop_id)
    if not next_crop:
        return False
    return prev_crop_id in next_crop.get("breaks_pest_cycle_of", [])


# =============================================================================
# Visual Plant Pathology & Crop Disease Atlas
# =============================================================================
DISEASES_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "wheat_yellow_rust",
        "name_ar": "الصدأ الأصفر (صدأ المخطط)",
        "name_en": "Yellow Rust (Stripe Rust)",
        "scientific_name": "Puccinia striiformis f. sp. tritici",
        "crop_id": "wheat",
        "crop_name_ar": "القمح",
        "pathogen_type": "فطري إجباري التطفل (Fungal)",
        "image_file": "wheat_yellow_rust.jpg",
        "symptoms_ar": "بثور يوريدية صفراء ليمونية متوازية على نصل الأوراق موازية للعروق الطولية، تمتد بسرعة مسببة جفاف نصل الورقة وفقدان قدرة البناء الضوئي.",
        "pest_break_ar": "زراعة محاصيل غير نجيلية (مثل الفول البلدي، البرسيم، بنجر السكر) كفاصل زمني يجوع جراثيم الفطر ويمنع توطن السلالات الوبائية المتطورة.",
        "breaking_crops": ["البرسيم المصري", "الفول البلدي", "بنجر السكر"],
        "nasa_trigger_condition": "رطوبة نسبية عالية (RH2M > 70%) مع درجات حرارة معتدلة مائلة للبرودة (10 - 18°C) وندى ليلي متكرر."
    },
    {
        "id": "wheat_stem_rust",
        "name_ar": "صدأ الساق الأسود",
        "name_en": "Stem Rust (Black Rust)",
        "scientific_name": "Puccinia graminis",
        "crop_id": "wheat",
        "crop_name_ar": "القمح",
        "pathogen_type": "فطري خبيث (Fungal)",
        "image_file": "wheat_stem_rust.jpg",
        "symptoms_ar": "بثور بنية داكنة إلى سوداء ممزقة للبشرة على سيقان القمح وأغماد الأوراق، تؤدي إلى رقاد المحصول وضمور الحبوب قبل الحصاد.",
        "pest_break_ar": "إدخال محاصيل البقوليات الشتوية في الدورة لمنع بقاء الفطر وتكسير بيئة الرطوبة الميكرو-مناخية بالساق.",
        "breaking_crops": ["الفول البلدي", "البرسيم المصري"],
        "nasa_trigger_condition": "ارتفاع تدريجي في حرارة الربيع المتأخر (T2M بين 18 - 28°C) مع رطوبة ندى صباحي كافية لإنبات الجراثيم."
    },
    {
        "id": "faba_bean_chocolate_spot",
        "name_ar": "مرض التبقع البني",
        "name_en": "Chocolate Spot Disease",
        "scientific_name": "Botrytis fabae",
        "crop_id": "faba_bean",
        "crop_name_ar": "الفول البلدي",
        "pathogen_type": "فطري شديد الشراسة (Fungal)",
        "image_file": "faba_bean_chocolate_spot.jpg",
        "symptoms_ar": "بقع صغيرة بنية محمرة شوكولاتية اللون بحواف محددة تتسع وتلتحم في الجو الرطب لتتحول إلى لفحة سريعة تسقط الأزهار والأوراق.",
        "pest_break_ar": "التدوير مع محاصيل الحبوب (القمح والذرة) لمنع تراكم الأجسام الحجرية (Sclerotia) في التربة وتقليل رطوبة قاع الحقل.",
        "breaking_crops": ["القمح", "الذرة الشامية"],
        "nasa_trigger_condition": "موجات هطول أمطار شتوية متتالية (GPM > 10 ملم) مصحوبة برطوبة جوية خانقة (RH2M > 80%)."
    },
    {
        "id": "faba_bean_orobanche",
        "name_ar": "حشيشة الهالوك الطفيلية",
        "name_en": "Crenate Broomrape (Parasitic)",
        "scientific_name": "Orobanche crenata",
        "crop_id": "faba_bean",
        "crop_name_ar": "الفول البلدي",
        "pathogen_type": "نبات زهري طفيلي متطفل الجذور",
        "image_file": "faba_bean_orobanche.jpg",
        "symptoms_ar": "شماريخ زهرية حرشفية تخرج من الأرض ملتصقة ومخترقة لجذور نبات الفول بممصات خبيثة، تمتص العصارة وتسبب تقزماً واصفراراً وموت الحقل.",
        "pest_break_ar": "الدورة الزراعية هي خط الدفاع الأول ضد الهالوك! إدخال الكتان أو البرسيم كمحاصيل صائدة (Trap Crops) تحفز إنبات بذور الهالوك دون تغذيتها، والتبادل مع القمح لتجويع البذور لسنوات.",
        "breaking_crops": ["البرسيم المصري", "القمح", "بنجر السكر"],
        "nasa_trigger_condition": "رطوبة تربة جذرية دافئة (SMAP) تحفز إفرازات جذور العوائل الحساسة في درجات حرارة 15-20°C."
    },
    {
        "id": "tomato_late_blight",
        "name_ar": "اللفحة المتأخرة (الندوة المتأخرة)",
        "name_en": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "crop_id": "tomato",
        "crop_name_ar": "الطماطم والبطاطس",
        "pathogen_type": "شبه فطري مائي (Oomycete)",
        "image_file": "tomato_late_blight.jpg",
        "symptoms_ar": "بقع مائية زيتية خضراء داكنة تمتد لحواف الأوراق وتتحول للون البني مع نمو زغبي أبيض دقيق على السطح السفلي، وعفن بني جلدي بالثمار.",
        "pest_break_ar": "كسر عائلة الباذنجانيات بالكامل! استبدال الحقل بالنجيليات (القمح أو الذرة) يوقف تماماً دورة حياة الفطر المحب للرطوبة.",
        "breaking_crops": ["القمح", "الذرة الشامية", "البرسيم المصري"],
        "nasa_trigger_condition": "تنبيه ناسا الحرج: تزامن درجات حرارة معتدلة (15 - 22°C) مع رطوبة نسبية قياسية تتجاوز 85% لعدة أيام."
    },
    {
        "id": "tomato_early_blight",
        "name_ar": "اللفحة المبكرة (الترناريا)",
        "name_en": "Early Blight (Target Spot)",
        "scientific_name": "Alternaria solani",
        "crop_id": "tomato",
        "crop_name_ar": "الطماطم والبطاطس",
        "pathogen_type": "فطري يصيب الأنسجة المجهدة",
        "image_file": "tomato_early_blight.jpg",
        "symptoms_ar": "بقع بنية داكنة ذات حلقات متداخلة دائرية متميزة تشبه لوحة التهديف (Target Spot) تبدأ على الأوراق السفلية القديمة وتجففها.",
        "pest_break_ar": "التدوير الزراعي مع البقوليات يرفع محتوى نيتروجين التربة ويقلل الإجهاد الفسيولوجي المسبب لسهولة الاختراق الفطري.",
        "breaking_crops": ["الفول البلدي", "البرسيم المصري"],
        "nasa_trigger_condition": "تناوب فترات الجفاف الحار مع فترات الندى الرطب وإجهاد التربة الفقيرة بالمادة العضوية."
    },
    {
        "id": "maize_fall_armyworm",
        "name_ar": "دودة الحشد الخريفية",
        "name_en": "Fall Armyworm",
        "scientific_name": "Spodoptera frugiperda",
        "crop_id": "maize",
        "crop_name_ar": "الذرة الشامية",
        "pathogen_type": "آفة حشرية خطيرة (Lepidoptera)",
        "image_file": "maize_fall_armyworm.jpg",
        "symptoms_ar": "ثقوب غائرة بنوافذ شفافة في أوراق القمة النامية مع تغذية شرهة داخل بلعوم الذرة وتراكم براز يشبه نشارة الخشب الرطبة.",
        "pest_break_ar": "تدوير حقول الذرة بعد الحصاد الصيفي بزراعة البرسيم أو الفول يقطع استمرارية العوائل ويقضي على عذارى الحشرة البياتية بالتربة.",
        "breaking_crops": ["البرسيم المصري", "الفول البلدي", "بنجر السكر"],
        "nasa_trigger_condition": "موجات حرارية صيفية دافئة (T2M > 28°C) تسرع أجيال التكاثر الحشري وتزيد ضغط الهجوم."
    },
    {
        "id": "maize_leaf_blight",
        "name_ar": "لفحة أوراق الذرة الشمالية",
        "name_en": "Northern Corn Leaf Blight",
        "scientific_name": "Exserohilum turcicum",
        "crop_id": "maize",
        "crop_name_ar": "الذرة الشامية",
        "pathogen_type": "فطري ورقي",
        "image_file": "maize_leaf_blight.jpg",
        "symptoms_ar": "بقع مغزلية الشكل رمادية مخضرة طويلة تشبه السيجار تصل لأكثر من 15 سم مسببة احتراق جفاف الأوراق ونقص امتلاء الكيزان.",
        "pest_break_ar": "التناوب مع المحاصيل غير العائلة (القطن وفول الصويا) يمنع نمو الجراثيم المتبقية على بقايا قش الذرة.",
        "breaking_crops": ["القطن المصري", "فول الصويا"],
        "nasa_trigger_condition": "رطوبة جوية معتدلة وحرارة بين 20 - 27°C مع انخفاض حركة الهواء بين النباتات الكثيفة."
    },
    {
        "id": "onion_white_rot",
        "name_ar": "مرض العفن الأبيض في البصل",
        "name_en": "White Rot Disease",
        "scientific_name": "Stromatinia cepivora",
        "crop_id": "onion",
        "crop_name_ar": "البصل والثوم",
        "pathogen_type": "فطري ترابي مزمن ومستوطن",
        "image_file": "onion_white_rot.jpg",
        "symptoms_ar": "اصفرار الأوراق وموتها من القمة للقاعدة، مع تكون نسيج ميسيليوم أبيض قطني كثيف وأجسام حجرية سوداء دقيقة على قاعدة البصلة والجذور.",
        "pest_break_ar": "أخطر أمراض الثوميات! يحتاج دورة زراعية مشددة لا تقل عن 4-5 سنوات تزرع فيها الحبوب (القمح، الذرة) والقطن لتجنب تنشيط الأجسام الحجرية.",
        "breaking_crops": ["القمح", "القطن المصري", "البرسيم المصري"],
        "nasa_trigger_condition": "درجات حرارة تربة باردة إلى معتدلة (10 - 20°C) مع رطوبة تربة مشبعة ومستمرة."
    },
    {
        "id": "cotton_bollworm",
        "name_ar": "دودة لوز القطن (القرنفلية والشوكية)",
        "name_en": "Cotton Bollworm",
        "scientific_name": "Helicoverpa armigera",
        "crop_id": "cotton",
        "crop_name_ar": "القطن المصري",
        "pathogen_type": "آفة حشرية اقتصادية",
        "image_file": "cotton_bollworm.jpg",
        "symptoms_ar": "ثقوب دخول دائرية في لوز القطن وبراعمه الزهرية (الوسواس) وتلف تام للألياف التيلية وبذور الزيت وتساقط اللوز الأخضر.",
        "pest_break_ar": "كسر دورة الحشرة بالتبادل الشتوي مع القمح وبنجر السكر والحرث العميق للتخلص من الشرانق الساكنة بالتربة.",
        "breaking_crops": ["القمح", "بنجر السكر"],
        "nasa_trigger_condition": "إشعاع شمسي صيفي مرتفع (POWER) وساعات حرارية تراكمية (GDD) تدفع خروج الأطوار اليرقية."
    },
    {
        "id": "sugar_beet_cercospora",
        "name_ar": "تبقع الأوراق السركسبوري",
        "name_en": "Cercospora Leaf Spot",
        "scientific_name": "Cercospora beticola",
        "crop_id": "sugar_beet",
        "crop_name_ar": "بنجر السكر",
        "pathogen_type": "فطري يقلل نسبة السكر",
        "image_file": "sugar_beet_cercospora.jpg",
        "symptoms_ar": "بقع دائرية صغيرة رمادية محاطة بحافة بنية محمرة تنتشر على أوراق البنجر وتتلاحم مسببة موت المجموع الخضري ونقص إنتاجية السكروز.",
        "pest_break_ar": "تدوير البنجر كل 3 سنوات مع محاصيل غير درنية مثل القمح والأرز والذرة لتثبيط الجراثيم الهاجعة.",
        "breaking_crops": ["القمح", "الأرز", "الذرة الشامية"],
        "nasa_trigger_condition": "رطوبة نسبية تزيد عن 60% مع حرارة دافئة ليلاً (T2M_MIN > 16°C) ونهاراً فوق 25°C."
    },
    {
        "id": "clover_root_rot",
        "name_ar": "عفن الجذور والتاج في البرسيم",
        "name_en": "Root and Crown Rot",
        "scientific_name": "Rhizoctonia solani / Fusarium",
        "crop_id": "clover",
        "crop_name_ar": "البرسيم المصري",
        "pathogen_type": "مركب فطري ترابي",
        "image_file": "clover_root_rot.jpg",
        "symptoms_ar": "ذبول البادرات وموت الجذور الثانوية واسوداد منطقة التاج بعد الحشة الأولى وتخلخل النباتات عند الجذب.",
        "pest_break_ar": "التبادل مع المحاصيل النجيلية جيدة الصرف (القمح والشعير والذرة) وتفادي غمر الأرض بمياه الري الزائدة.",
        "breaking_crops": ["القمح", "الذرة الشامية"],
        "nasa_trigger_condition": "تشبع مائي جذري عالي (SMAP > 80%) مع تربة طينية سيئة الصرف وحرارة دافئة."
    }
]


def get_all_diseases() -> List[Dict[str, Any]]:
    """Retrieve full catalog of visual crop diseases and pests."""
    return DISEASES_CATALOG

