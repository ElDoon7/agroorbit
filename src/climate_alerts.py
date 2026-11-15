"""
AgroOrbit - NASA Early Warning & Climate Hazard Alert Engine
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data

Proactively screens live NASA satellite parameters (POWER T2M, RH2M, SMAP GWETROOT/TOP, GPM)
against physiological stress thresholds to issue actionable agricultural hazard warnings:
- Extreme Heatwaves & Thermal Scorch
- Frost Inversion & Cold Stunt
- Spore & Fungal Disease Bloom (Yellow Rust / Blight)
- Root Zone Dehydration & Flash Drought
- Waterlogging & Root Hypoxia
"""

from typing import Dict, Any, List


def evaluate_climate_hazards(
    telemetry: Dict[str, Any],
    previous_crop_id: str = "maize",
    soil_type: str = "clay"
) -> List[Dict[str, Any]]:
    """
    Evaluates micro-climatic and edaphic telemetry to generate prioritized hazard alerts.
    Severity levels: 'critical' (red), 'warning' (amber), 'nominal' (green).
    """
    indices = telemetry.get("indices", {})
    cleaned = telemetry.get("cleaned_parameters", {})

    avg_temp = float(indices.get("avg_temp_c", 22.0))
    max_temp = float(indices.get("max_temp_c", avg_temp + 5.0))
    min_temp = float(indices.get("min_temp_c", avg_temp - 5.0))
    avg_rh = float(indices.get("avg_relative_humidity_pct", 55.0))
    gwetroot = float(indices.get("avg_root_zone_moisture", 0.40))
    gwettop = float(indices.get("avg_surface_moisture", 0.35))
    heat_days = int(indices.get("extreme_heat_days", 0))
    precip = float(indices.get("total_precipitation_mm", 2.0))
    soil_moisture_score = float(indices.get("soil_moisture_score", 45.0))

    alerts = []

    # 1. Extreme Heatwave & Thermal Floral Scorch
    if max_temp >= 38.0 or heat_days >= 3:
        alerts.append({
            "id": "heatwave_critical",
            "severity": "critical",
            "icon": "🔥",
            "title_ar": "إنذار مداري حرج: موجة حرارة شديدة وإجهاد حراري حاد",
            "title_en": "Critical Heatwave & Thermal Stress Alert",
            "trigger_data": f"سجلت أقمار ناسا حرارة عظمى {max_temp:.1f}°C مع {heat_days} أيام إجهاد قيظ متتالية.",
            "impact_ar": "خطر احتراق قمم النموات الحديثة، عقم حبوب اللقاح وسقوط أزهار الذرة والخضروات، وارتفاع معدل النتح بنسبة 60%.",
            "urgent_actions": [
                "الري الليلي أو في الصباح الباكر حصراً لتجنب غليان المياه في الجذور.",
                "رش سليكات البوتاسيوم بمعدل 6 سم/لتر لتدعيم جدران الخلايا ومقاومة النتح.",
                "تقليل التسميد النيتروجيني الحار مؤقتاً لتفادي صدمة الأنسجة الغضة."
            ]
        })
    elif max_temp >= 34.0 or heat_days >= 1:
        alerts.append({
            "id": "heatwave_warning",
            "severity": "warning",
            "icon": "☀️",
            "title_ar": "تنبيه مداري: ارتفاع درجات الحرارة وتزايد التبخر",
            "title_en": "Moderate Heat Stress Warning",
            "trigger_data": f"الحرارة العظمى المرصودة {max_temp:.1f}°C تفوق المعدل الفسيولوجي المريح.",
            "impact_ar": "تزايد الفاقد المائي السطحي وجفاف الطبقة العلوية من التربة بسرعة.",
            "urgent_actions": [
                "تقريب فترات نوبات الري لتعويض البخر المرتفع.",
                "إجراء خربشة سطحية للتربة لكسر الأنابيب الشعرية وتقليل التبخر."
            ]
        })

    # 2. Frost Inversion & Cold Shock
    if min_temp <= 4.0:
        alerts.append({
            "id": "frost_critical",
            "severity": "critical",
            "icon": "❄️",
            "title_ar": "إنذار مداري حرج: موجة صقيع وانجماد ليلي للأنسجة",
            "title_en": "Critical Frost & Sub-Zero Risk",
            "trigger_data": f"أجهزة استشعار ناسا رصدت هبوط الحرارة الصغرى إلى {min_temp:.1f}°C قبل الشروق.",
            "impact_ar": "تمزق أغشية الخلايا النباتية في الطماطم والبطاطس والفراولة وموت القمم النامية للبادرات.",
            "urgent_actions": [
                "إعطاء رية خفيفة على الحامي مساء اليوم لرفع السعة الحرارية للتربة وصد الصقيع.",
                "تشغيل ضباب مائي أو التدخين بقش الأرز المبتل حول أطراف الغيط مع الرياح قبل الفجر.",
                "الرش بمركبات الأحماض الأمينية وعناصر الفوسفور والزنك لتنشيط سريان العصارة."
            ]
        })
    elif min_temp <= 7.5:
        alerts.append({
            "id": "frost_warning",
            "severity": "warning",
            "icon": "🧣",
            "title_ar": "تنبيه مداري: انخفاض حاد في درجات الحرارة الليلية",
            "title_en": "Cold Night Thermal Inversion Warning",
            "trigger_data": f"الحرارة الصغرى المسجلة {min_temp:.1f}°C تدل على برودة قاسية في الساعات المتأخرة.",
            "impact_ar": "توقف مؤقت لامتصاص الفوسفور والنمو الخضري (تقزم شتوي).",
            "urgent_actions": [
                "تجنب التعطيش الليلي والتغطية بالأنفاق البلاستيكية للمحاصيل الحساسة."
            ]
        })

    # 3. Fungal Bloom & Spore Hazard (Yellow Rust / Blight)
    if avg_rh >= 72.0 and 15.0 <= avg_temp <= 26.0:
        alerts.append({
            "id": "fungal_spore_warning",
            "severity": "critical" if avg_rh >= 80.0 else "warning",
            "icon": "🦠",
            "title_ar": "إنذار مداري بيولوجي: نشاط مرتفع لأبواغ الفطريات (الصدأ واللفحة)",
            "title_en": "Fungal Spore Germination Hazard",
            "trigger_data": f"تزامن رطوبة جوية مرتفعة ({avg_rh:.1f}%) مع حرارة معتدلة ({avg_temp:.1f}°C) ورطوبة سطحية {gwettop:.2f}.",
            "impact_ar": "بيئة نموذجية لإنبات أبواغ الصدأ الأصفر في القمح، ولفحة البطاطس المبكرة والمتأخرة، والبياض الزغبي.",
            "urgent_actions": [
                "تنفيذ رشة وقائية عاجلة بأكسي كلورور النحاس أو مانكوزيب قبل حدوث الإصابة المرئية.",
                "الامتناع التام عن الري بالرش العلوي خلال ساعات الصباح والمساء لتفادي ابتلال الأوراق.",
                "تسليك قنوات التهوية بين الخطوط لمنع ركود الهواء الرطب داخل حوض الزراعة."
            ]
        })

    # 4. Flash Drought & Root Zone Dehydration
    if gwetroot <= 0.28 or soil_moisture_score <= 32.0:
        alerts.append({
            "id": "drought_critical",
            "severity": "critical",
            "icon": "🏜️",
            "title_ar": "إنذار إجهاد مائي حرج: نضوب مخزون الرطوبة في منطقة الجذور (SMAP)",
            "title_en": "Root-Zone Severe Moisture Deficit",
            "trigger_data": f"أقمار SMAP رصدت هبوط رطوبة الجذور إلى {gwetroot:.2f} (مؤشر {soil_moisture_score}%).",
            "impact_ar": "انفصال حبيبات التربة عن الجذور، ذبول دائم للأوراق، وتوقف انتقال المغذيات العضوية.",
            "urgent_actions": [
                "تطبيق رية مشبعة بنظام النبضات (Pulse Drip) لترطيب القطاع الجذري دون هدر.",
                "حقن الهيوميك أسيد مع ماء الري لزيادة قدرة مجمعات التربة على الاحتفاظ بالماء.",
                "استخدام قش أو نشارة كغطاء عضوي (Mulch) لمنع البخر السطحي المباشر."
            ]
        })
    elif gwetroot <= 0.36:
        alerts.append({
            "id": "drought_warning",
            "severity": "warning",
            "icon": "💧",
            "title_ar": "تنبيه مائي: انخفاض تدريجي في رطوبة باطن الأرض",
            "title_en": "Moderate Root Moisture Deficit",
            "trigger_data": f"رطوبة منطقة الجذور الحالية ({gwetroot:.2f}) تقترب من نقطة البداية الحرجة للذبول.",
            "impact_ar": "انخفاض كفاءة امتصاص العناصر الكبرى (NPK).",
            "urgent_actions": [
                "جدولة رية تكميلية خلال الـ 48 ساعة القادمة."
            ]
        })

    # 5. Soil Waterlogging & Root Hypoxia
    if gwetroot >= 0.82 or soil_moisture_score >= 82.0:
        alerts.append({
            "id": "waterlogging_warning",
            "severity": "warning",
            "icon": "🌊",
            "title_ar": "تنبيه تشبع التربة: غدق مائي وخطر اختناق الجذور ونقص الأكسجين",
            "title_en": "Soil Waterlogging & Root Hypoxia Alert",
            "trigger_data": f"رطوبة التربة المقاسة من الفضاء ({soil_moisture_score}%) تجاوزت السعة الحقلية القصوى.",
            "impact_ar": "طرد الهواء من مسام التربة مما يسبب تعفن الجذور بسب البيثيوم والفيوزاريوم واصفرار الأوراق.",
            "urgent_actions": [
                "فتح المصارف الحقلية والتأكد من انسياب المياه الزائدة دون ركود.",
                "إيقاف مياه الري مؤقتاً حتى هبوط الرطوبة إلى النطاق الآمن.",
                "عزق سطحي خفيف فور جفاف السطح لإعادة دخول الأكسجين للتربة."
            ]
        })

    # 6. Nominal / Stable Status (If no critical or warning alerts triggered)
    if not alerts:
        alerts.append({
            "id": "nominal_optimal",
            "severity": "nominal",
            "icon": "🛡️",
            "title_ar": "الوضع المداري مستقر: بيئة نمو فسيولوجية مثالية وآمنة",
            "title_en": "Nominal Agro-Climatic Window",
            "trigger_data": f"متوسط الحرارة {avg_temp:.1f}°C، والرطوبة الجوية {avg_rh:.1f}%، ورطوبة التربة {soil_moisture_score}%.",
            "impact_ar": "لا توجد موجات صقيع أو قيظ متطرفة، ومؤشرات البخر في النطاق الطبيعي لكافة المحاصيل المقترحة.",
            "urgent_actions": [
                "الاستمرار في جدول التسميد والري الدوري الموصى به في دورة صحة التربة.",
                "المتابعة الدورية للرصد المداري الفضائي لتحديث أية تغيرات مناخية سريعة."
            ]
        })

    # Sort alerts: critical first, then warning, then nominal
    order = {"critical": 0, "warning": 1, "nominal": 2}
    alerts.sort(key=lambda a: order.get(a["severity"], 3))

    return alerts
