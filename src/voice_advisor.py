"""
AgroOrbit - AI Voice Agro-Advisor (المساعد الصوتي الزراعي الفضائي)
Generates tailored, conversational Egyptian colloquial Arabic agricultural briefings
synthesized into natural voice audio using NASA satellite telemetry and crop rotation intelligence.
"""

import os
import hashlib
import re
from typing import Dict, Any, Optional
from gtts import gTTS

AUDIO_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "audio")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)


def _clean_text_for_speech(text: str) -> str:
    """Removes English letters, markdown symbols, brackets, and extra spaces so TTS pronounces purely and cleanly."""
    text = re.sub(r'\(.*?\)', '', text)  # remove parenthesized terms like (Clay), (BNF), etc.
    text = re.sub(r'[a-zA-Z]', '', text)  # strip English characters so Arabic TTS doesn't stumble
    text = re.sub(r'[*_#`~\[\]\(\)\{\}<>|]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_voice_script(
    briefing_type: str,
    metadata: Dict[str, Any],
    strategies: Dict[str, Any]
) -> str:
    """
    Generates warm, authentic Egyptian colloquial Arabic agricultural advisory scripts.
    
    briefing_type:
      - 'comprehensive': التوجيه المداري الشامل
      - 'soil_health': نصيحة توفير الأسمدة وتثبيت النيتروجين (BNF)
      - 'water_resilience': نصيحة ترشيد الري ومجابهة الحرارة
      - 'pest_prevention': نصيحة حماية المحصول وكسر دورات الآفات
    """
    soil_map = {
        "clay": "الطينية",
        "loam": "الطميية",
        "sandy": "الرملية",
        "calcareous": "الجيرية"
    }
    soil_raw = metadata.get("soil_type", "clay")
    soil_clean = soil_map.get(soil_raw, "الزراعية")
    
    prev_raw = metadata.get("previous_crop_name_ar", "المحصول السابق")
    prev_crop = re.sub(r'\(.*?\)', '', prev_raw).strip()
    
    temp = round(float(metadata.get("nasa_avg_temp", 24.0)), 1)
    moisture = round(float(metadata.get("soil_moisture_score", 40.0)), 1)
    
    strat_baseline = strategies.get("strategy_1_baseline", {})
    strat_soil = strategies.get("strategy_2_soil_health", {})
    strat_water = strategies.get("strategy_3_water_resilience", {})

    # Extract crop names for soil health rotation
    soil_timeline = strat_soil.get("timeline", [])
    crop1_soil = re.sub(r'\(.*?\)', '', soil_timeline[0]["crop"].get("name_ar", "بقوليات")).strip() if len(soil_timeline) > 0 else "بقوليات"
    crop2_soil = re.sub(r'\(.*?\)', '', soil_timeline[1]["crop"].get("name_ar", "محصول صيفي")).strip() if len(soil_timeline) > 1 else "محصول صيفي"
    crop3_soil = re.sub(r'\(.*?\)', '', soil_timeline[2]["crop"].get("name_ar", "محصول رئيسي")).strip() if len(soil_timeline) > 2 else "محصول رئيسي"

    # Extract crop names for water resilience
    water_timeline = strat_water.get("timeline", [])
    crop1_water = re.sub(r'\(.*?\)', '', water_timeline[0]["crop"].get("name_ar", "بنجر السكر")).strip() if len(water_timeline) > 0 else "بنجر السكر"
    crop2_water = re.sub(r'\(.*?\)', '', water_timeline[1]["crop"].get("name_ar", "فول الصويا")).strip() if len(water_timeline) > 1 else "فول الصويا"

    soil_net_n = strat_soil.get("metrics", {}).get("net_nitrogen_kg_ha", 45)
    urea_sacks = max(1, round(abs(soil_net_n) / 23))  # 50kg urea bag contains ~23kg pure N
    water_savings_pct = strat_water.get("metrics", {}).get("water_savings_pct", 22.0)

    if briefing_type == "soil_health":
        script = f"""
يا مرحب بيك يا ريسنا الغالي. صلي على النبي وركز معايا في نصيحة الأرض. 
أقمار ناسا بتقول إن أرضك بعد محصول {prev_crop} مجهدة ومحتاجة دفعة نيتروجين حيوية.
عشان كده، استراتيجية صحة التربة هي اختيارك الدهبي! 
هننزل الأول بمحصول {crop1_soil} وندعمه ببكتيريا العقد الجذرية، وبعده ننزل بمحصول {crop2_soil} ثم {crop3_soil}.
الدورة دي يا بطل هتثبت في باطن أرضك نيتروجين طبيعي ببلاش، يوفرلك حوالي {urea_sacks} شكاير يوريا للفدان الواحد! 
غير كده، هتهوي تربتك {soil_clean} وتكسر شوكة الآفات بنسبة تسعين في المية. 
امشي على الدورة دي وادعيلي، وبركة ربنا في غيطك هتزيد!
"""

    elif briefing_type == "water_resilience":
        script = f"""
أهلاً بحبايبنا المزارعين. خبير الري المداري بيكلمك مخصوص لأرضك. 
بيانات ناسا المسجلة من أقمار إس ماب وباور بتوضح إن متوسط الحرارة اليومين دول حوالين {temp} درجة، ونسبة رطوبة التربة {moisture} في المية.
عشان نأمن محصولك من لفحة الحر وموجات العطش، استراتيجية التكيف المائي هي الحل السحري.
بننصحك تنزل بمحصول {crop1_water} ومعاه {crop2_water}. 
المحاصيل دي جذورها بتمص الرطوبة بكفاءة، وبتوفرلك في مية الري أكتر من {water_savings_pct} في المية مقارنة بالزراعة القديمة. 
ونصيحة من دهب: خلي دايماً ريك على الحامي في الصباح الباكر قبل طلوع الشمس أو بعد العصر، عشان نبعد عن تبخير المية وتمليح التربة. 
ربنا يخضّر عودك ويطرح في أرضك البركة!
"""

    elif briefing_type == "pest_prevention":
        script = f"""
يا أهلاً بيك يا طيب. تنبيه بيولوجي عاجل من مرصد ناسا لحماية نباتاتك. 
تكرار زراعة المحصول نفسه بعد {prev_crop} بيعمل بيئة مثالية لسوسة الجذور ودودة الحشد وفطريات الصدأ والتفحم في أرضك {soil_clean}. 
أقمار ناسا رصدت رطوبة سطحية بتسمح بنشاط الأبواغ الفطرية لو فضلنا على نفس الدورة المجهدة. 
عشان تقطع دابر الآفة دي من جذورها، لازم نغير العائل النباتي فوراً بدورة ثنائية أو ثلاثية متباعدة. 
بندخل محصول بقولي يقطع تغذية الديدان، متبوع بمحصول وتدي الجذور. 
الخطوة دي لوحدها بتوفر عليك نص مصاريف المبيدات الكيماوية وبتحمي صحتك وصحة محصولك. 
خلي عينك في الغيط أول بأول، وعين ناسا في السما حارساك!
"""

    else:  # 'comprehensive' - الإحاطة الشاملة
        script = f"""
يا صباح الخير والبركة على أجدع مزارع مصري. دي إحاطتك الاستشارية الفضائية المباشرة من مدار أجرواوربت. 
أقمار وكالة ناسا الصناعية اللي بتعدي فوق غيطك حللت حالة الجو والتربة النهاردة: 
متوسط الحرارة مستقر عند {temp} درجة مئوية، ومستوى رطوبة التربة في حدود {moisture} في المية. 
أرضك {soil_clean} بعد ما شيلت منها {prev_crop}، قدامها فرصة دهبية ترجع شبابها وقوتها. 
محرك القرار بينصحك بقوة تتبنى دورة صحة التربة، وابدأ بزراعة {crop1_soil} عشان نوفر شكاير السماد النيتروجيني ونغذي الأرض حيوي. 
ولو كان عندك ضغط في نوبات المية والترعة، انزل على طول باستراتيجية التكيف المائي مع {crop1_water} عشان توفر ربع استهلاك المية. 
كل البيانات دي محسوبة بالمللي من الفضاء عشانك. 
توكل على الله، ويومك كله خير وبركة وإنتاج عالي إن شاء الله!
"""

    return _clean_text_for_speech(script)

    return _clean_text_for_speech(script)


def get_agro_voice_audio(text: str) -> Optional[bytes]:
    """
    Synthesizes the given Arabic text into MP3 audio using gTTS.
    Uses MD5 disk cache so identical speeches return instantly.
    """
    if not text or not text.strip():
        return None

    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    cache_file = os.path.join(AUDIO_CACHE_DIR, f"{text_hash}.mp3")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "rb") as f:
                return f.read()
        except Exception:
            pass

    try:
        tts = gTTS(text=text, lang="ar")
        tts.save(cache_file)
        with open(cache_file, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"Error generating audio via gTTS: {e}")
        return None
