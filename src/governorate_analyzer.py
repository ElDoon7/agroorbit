"""
AgroOrbit - Egypt Governorates Agro-Climatic Intelligence Engine
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data

Features:
- Multi-criteria Ranking & Benchmark Engine across all 27 Egyptian Governorates
- Synchronized Visual Palette (Exact 1:1 Color Match between Bar Chart & Folium Map)
- Crystal-Clear Plotly Horizontal Bar Chart with Zero Text Clipping & Bold Percentage Badges
- 5-Axis Spider Radar Chart for Agro-Climatic Profiling
- Multi-Layer Folium Map (Default: Esri Vivid Satellite Imagery + Dark Map + City Labels)
"""

from typing import Dict, Any, List, Tuple
import json
from pathlib import Path
import folium
import plotly.graph_objects as go
from src import config

_CACHED_GEOJSON_DATA = None


def get_egypt_geojson_data():
    """Loads and caches Egypt 27 Governorates boundary GeoJSON."""
    global _CACHED_GEOJSON_DATA
    if _CACHED_GEOJSON_DATA is not None:
        return _CACHED_GEOJSON_DATA

    geojson_path = config.ROOT_DIR / "assets" / "egypt_governorates_boundaries.geojson"
    if geojson_path.exists():
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                _CACHED_GEOJSON_DATA = json.load(f)
                return _CACHED_GEOJSON_DATA
        except Exception:
            pass
    return None

# 27 Distinct, High-Vibrancy Space-Themed Colors for 1:1 Chart-to-Map Synchronization
GOVERNORATE_PALETTE_27 = [
    "#00ff88",  # 1: Vivid Emerald Neon
    "#00f5c4",  # 2: Bright Teal Mint
    "#00e5ff",  # 3: Electric Sky Cyan
    "#06b6d4",  # 4: Deep Turquoise
    "#38bdf8",  # 5: Crisp Ice Blue
    "#60a5fa",  # 6: Soft Cobalt Blue
    "#818cf8",  # 7: Bright Periwinkle
    "#a78bfa",  # 8: Radiant Lavender
    "#c084fc",  # 9: Neon Violet
    "#e879f9",  # 10: Bright Fuchsia Orchid
    "#f472b6",  # 11: Vibrant Rose
    "#fb7185",  # 12: Radiant Coral Pink
    "#f87171",  # 13: Bright Crimson Carmine
    "#fb923c",  # 14: Radiant Sunset Orange
    "#f59e0b",  # 15: Warm Amber Gold
    "#fbbf24",  # 16: Cosmic Golden Yellow
    "#facc15",  # 17: Brilliant Topaz
    "#a3e635",  # 18: Lime Spark
    "#4ade80",  # 19: Spring Green
    "#34d399",  # 20: Emerald Jade
    "#2dd4bf",  # 21: Aqua Marine
    "#22d3ee",  # 22: Bright Arctic Cyan
    "#67e8f9",  # 23: Pale Cyan Neon
    "#93c5fd",  # 24: Cornflower Blue
    "#c4b5fd",  # 25: Soft Amethyst
    "#fda4af",  # 26: Peachy Rose
    "#fdba74",  # 27: Light Amber
]

CRITERIA_DEFINITIONS = {
    "soil_moisture_score": {
        "title_ar": "💧 رطوبة وخصوبة التربة (NASA SMAP)",
        "title_en": "Soil Moisture & Water Holding Capacity",
        "index_key": "soil_moisture_score",
        "description_ar": "تقييم الرطوبة الجذرية والسطحية للتربة وملاءمتها للمحاصيل البقولية والاستراتيجية.",
        "unit": "%"
    },
    "water_conservation_potential": {
        "title_ar": "🌱 إمكانات توفير مياه الري (GPM & ET)",
        "title_en": "Water Conservation Potential",
        "index_key": "water_conservation_potential",
        "description_ar": "قدرة المحافظة على توفير المياه عند التحول من المحاصيل الشرهة إلى دورات مرنة.",
        "unit": "%"
    },
    "thermal_stability": {
        "title_ar": "🌡️ الاستقرار والاعتدال الحراري (T2M Stability)",
        "title_en": "Thermal Stability & Stress Avoidance",
        "index_key": "thermal_stability",
        "description_ar": "مدى خلو المحافظة من الإجهاد الحراري الشديد والموجات الحارة القاتلة للأزهار.",
        "unit": "%"
    },
    "composite_score": {
        "title_ar": "🌟 مؤشر الجدارة الزراعية الشامل (Composite Agro-Suitability)",
        "title_en": "Composite Agro-Climatic Suitability Index",
        "index_key": "composite_score",
        "description_ar": "المؤشر الكلي المرجح لتقييم الجدارة الزراعية الشاملة للمحافظة وفق نماذج ناسا.",
        "unit": "%"
    }
}


def rank_governorates(
    gov_telemetry: Dict[str, Dict[str, Any]],
    criterion_key: str = "composite_score"
) -> List[Dict[str, Any]]:
    """
    Rank all 27 governorates based on selected agro-climatic criterion.
    Assigns each governorate a permanent unique color and ranking index.
    """
    index_field = CRITERIA_DEFINITIONS.get(criterion_key, {}).get("index_key", "composite_score")

    ranked = []
    for gid, data in gov_telemetry.items():
        indices = data.get("indices", {})
        score = indices.get(index_field, 50.0)
        ranked.append({
            "id": gid,
            "name_ar": data.get("name_ar", gid),
            "name_en": data.get("name_en", gid),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "region": data.get("region"),
            "dominant_soil": data.get("dominant_soil"),
            "main_crops": data.get("main_crops", []),
            "score": round(score, 1),
            "confidence": data.get("confidence_score", 90.0),
            "indices": indices
        })

    # Sort descending by score
    ranked.sort(key=lambda x: x["score"], reverse=True)

    # Attach exact rank and synchronized color reference
    for idx, g in enumerate(ranked):
        g["rank"] = idx + 1
        g["color"] = GOVERNORATE_PALETTE_27[idx % len(GOVERNORATE_PALETTE_27)]

    return ranked


def build_ranking_barchart(
    ranked_govs: List[Dict[str, Any]],
    criterion_key: str = "composite_score",
    top_n: int = 15,
    dark_mode: bool = True
) -> go.Figure:
    """
    Generate high-impact, crystal-clear Plotly horizontal bar chart.
    Features:
    - 1:1 Color match with the Folium map markers.
    - Zero text clipping: ample left margin for Arabic and English names.
    - Bold, prominent percentage badges outside the bars.
    - High-contrast typography and comprehensive hover cards.
    """
    crit_info = CRITERIA_DEFINITIONS.get(criterion_key, CRITERIA_DEFINITIONS["composite_score"])
    display_govs = ranked_govs[:top_n]

    # Reversed order so rank #1 is at the top of the horizontal bar chart
    rev_govs = list(reversed(display_govs))
    names = [f"#{g['rank']} {g['name_ar']} ({g['name_en']})" for g in rev_govs]
    scores = [g["score"] for g in rev_govs]
    labels = [f"<b>{s:.1f}%</b>" for s in scores]
    colors = [g["color"] for g in rev_govs]

    paper_bg = "rgba(0, 0, 0, 0)"
    plot_bg = "rgba(10, 18, 36, 0.45)" if dark_mode else "rgba(241, 245, 249, 0.6)"
    text_color = "#f8fafc" if dark_mode else "#0f172a"
    grid_color = "rgba(0, 229, 255, 0.12)" if dark_mode else "rgba(0, 0, 0, 0.08)"

    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation="h",
        text=labels,
        textposition="outside",
        textfont=dict(color=text_color, size=13, family="Alexandria, Cairo, sans-serif"),
        marker=dict(
            color=colors,
            line=dict(
                color="rgba(255, 255, 255, 0.4)" if dark_mode else "rgba(0, 0, 0, 0.2)",
                width=1.5
            )
        ),
        customdata=[[g["rank"], g["name_ar"], g["region"], g["dominant_soil"], g["score"]] for g in rev_govs],
        hovertemplate=(
            "<b>المركز: #%{customdata[0]}</b><br>"
            "<b>المحافظة: %{customdata[1]}</b><br>"
            "<b>المؤشر: %{customdata[4]:.1f}%</b><br>"
            "<b>الإقليم الزراعي: %{customdata[2]}</b><br>"
            "<b>نوع التربة: %{customdata[3]}</b>"
            "<extra></extra>"
        )
    ))

    # Calculate optimal chart height based on count of governorates
    chart_height = max(480, top_n * 35)

    fig.update_layout(
        title=dict(
            text=f"📊 ترتيب المحافظات — {crit_info['title_ar']}",
            font=dict(color="#00e5ff" if dark_mode else "#0284c7", size=15, family="Alexandria, Cairo, sans-serif")
        ),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(family="Alexandria, Cairo, sans-serif"),
        xaxis=dict(
            range=[0, 115],  # 115 ensures 100% score labels are never clipped on the right
            title=dict(text="النسبة المئوية للمؤشر (%)", font=dict(color="#00e5ff" if dark_mode else "#0284c7", size=12)),
            tickfont=dict(color="#94a3b8" if dark_mode else "#64748b", size=11),
            gridcolor=grid_color
        ),
        yaxis=dict(
            tickfont=dict(color=text_color, size=12.5, family="Alexandria, Cairo, sans-serif")
        ),
        margin=dict(l=165, r=50, t=55, b=35),  # 165px left margin guarantees zero Arabic name clipping
        height=chart_height,
        bargap=0.22
    )

    return fig


def build_governorate_radar(gov_record: Dict[str, Any], dark_mode: bool = True) -> go.Figure:
    """Generate multi-axis radar chart for selected governorate agro-climatic balance."""
    indices = gov_record.get("indices", {})
    categories = [
        "رطوبة التربة (SMAP)",
        "كفاءة المياه",
        "الملاءمة الحرارية",
        "المؤشر الشامل",
        "الغطاء النباتي التقريبي"
    ]

    values = [
        indices.get("soil_moisture_score", 50.0),
        indices.get("water_conservation_potential", 50.0),
        indices.get("thermal_stability", 50.0),
        indices.get("composite_score", 50.0),
        min(95.0, indices.get("soil_moisture_score", 50.0) * 1.1)
    ]
    values.append(values[0])
    categories.append(categories[0])

    radar_color = gov_record.get("color", "#00e5ff" if dark_mode else "#0284c7")

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(0, 229, 255, 0.25)" if dark_mode else "rgba(2, 132, 199, 0.25)",
        line=dict(color=radar_color, width=2.5),
        marker=dict(color="#00ff88" if dark_mode else "#059669", size=8)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#94a3b8" if dark_mode else "#64748b")),
            angularaxis=dict(tickfont=dict(color="#f8fafc" if dark_mode else "#0f172a", size=11, family="Alexandria, Cairo, sans-serif")),
            bgcolor="rgba(8, 16, 32, 0.7)" if dark_mode else "rgba(248, 250, 252, 0.8)"
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(family="Alexandria, Cairo, sans-serif"),
        title=dict(
            text=f"🎯 البصمة الزراعية لمحافظة {gov_record.get('name_ar')}",
            font=dict(color=radar_color, size=14, family="Alexandria, Cairo, sans-serif")
        ),
        margin=dict(l=30, r=30, t=40, b=30),
        height=320
    )
    return fig


def build_orbital_folium_map(
    center_lat: float,
    center_lon: float,
    ranked_govs: List[Dict[str, Any]],
    criterion_key: str = "composite_score",
    selected_farm_coords: Tuple[float, float] = None
) -> folium.Map:
    """
    Generate high-reliability multi-layer Folium map.
    Each governorate circle marker is colored with the EXACT SAME COLOR as its bar in the ranking chart.
    """
    # 1. Base Map Initialization
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles=None,
        control_scale=True
    )

    # Layer 1: Esri World Imagery (Satellite) - DEFAULT VIVID SATELLITE MAP
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, Maxar, Earthstar Geographics",
        name="🛰️ صور الأقمار الصناعية الواقعية (NASA Satellite - افتراضي)",
        max_zoom=18,
        show=True
    ).add_to(m)

    # Layer 1.1: Administrative Borders & City Labels Overlay
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="🏷️ أسماء المدن والحدود (City Labels)",
        overlay=True,
        show=True
    ).add_to(m)

    # Layer 2: Esri World Dark Gray Base
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, HERE, Garmin, FAO, NOAA",
        name="🌑 خريطة الفضاء الداكنة (Esri Dark)",
        max_zoom=16,
        show=False
    ).add_to(m)

    # Layer 3: OpenStreetMap
    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors",
        name="🗺️ خريطة الشوارع (OpenStreetMap)",
        max_zoom=19,
        show=False
    ).add_to(m)

    # Layer 4: Egypt 27 Governorates Choropleth GeoJSON Polygons (Actual Geographical Boundaries)
    geo_data = get_egypt_geojson_data()
    if geo_data:
        gov_map_data = {g["id"]: g for g in ranked_govs}

        features_copy = []
        for feat in geo_data.get("features", []):
            feat_copy = {
                "type": feat["type"],
                "geometry": feat["geometry"],
                "properties": dict(feat["properties"])
            }
            gid = feat_copy["properties"].get("gov_id")
            if gid in gov_map_data:
                g_info = gov_map_data[gid]
                col = g_info.get("color", "#00e5ff")
                score = g_info.get("score", 0)
                rank = g_info.get("rank", 1)
                feat_copy["properties"]["color"] = col
                feat_copy["properties"]["score_str"] = f"{score:.1f}%"
                feat_copy["properties"]["rank_badge"] = f"#{rank}"
                feat_copy["properties"]["name_ar_display"] = f"محافظة {g_info.get('name_ar', '')}"
                feat_copy["properties"]["region_display"] = g_info.get("region", "مصر")
                feat_copy["properties"]["soil_display"] = g_info.get("dominant_soil", "طميية")
                feat_copy["properties"]["temp_display"] = f"{g_info.get('indices', {}).get('avg_temp_c', 25.0)} °C"
                feat_copy["properties"]["moisture_display"] = f"{g_info.get('indices', {}).get('soil_moisture_score', 50)}%"
                feat_copy["properties"]["tooltip_label"] = f"#{rank} - محافظة {g_info.get('name_ar', '')} ({score:.1f}%)"
            else:
                feat_copy["properties"]["color"] = "#38bdf8"
                feat_copy["properties"]["score_str"] = "غير مصنف"
                feat_copy["properties"]["rank_badge"] = "-"
                feat_copy["properties"]["name_ar_display"] = feat_copy["properties"].get("name_ar", "محافظة مصرية")
                feat_copy["properties"]["region_display"] = "مصر"
                feat_copy["properties"]["soil_display"] = "-"
                feat_copy["properties"]["temp_display"] = "-"
                feat_copy["properties"]["moisture_display"] = "-"
                feat_copy["properties"]["tooltip_label"] = feat_copy["properties"].get("name_ar", "محافظة مصرية")
            features_copy.append(feat_copy)

        enriched_geojson = {
            "type": "FeatureCollection",
            "features": features_copy
        }

        # Style function: Fills the entire physical province area with its exact synchronized color
        def polygon_style(feature):
            col = feature["properties"].get("color", "#00e5ff")
            return {
                "fillColor": col,
                "color": "#ffffff",
                "weight": 1.5,
                "fillOpacity": 0.45,
                "opacity": 0.90
            }

        # Highlight on hover: Vivid glowing border & increased opacity
        def polygon_highlight(feature):
            return {
                "color": "#00ff88",
                "weight": 3.5,
                "fillOpacity": 0.75,
                "opacity": 1.0
            }

        folium.GeoJson(
            enriched_geojson,
            name="🗺️ المساحات والحدود الجغرافية للمحافظات الـ 27 (Governorate Boundaries)",
            style_function=polygon_style,
            highlight_function=polygon_highlight,
            tooltip=folium.GeoJsonTooltip(
                fields=["tooltip_label"],
                aliases=["المحافظة:"],
                style="background-color: rgba(6, 14, 28, 0.92); color: #00e5ff; font-family: Cairo, Alexandria, sans-serif; font-size: 13px; font-weight: 800; border: 1.5px solid #00e5ff; border-radius: 8px; padding: 6px 12px; box-shadow: 0 0 16px rgba(0,229,255,0.4);"
            ),
            popup=folium.GeoJsonPopup(
                fields=[
                    "name_ar_display",
                    "rank_badge",
                    "score_str",
                    "region_display",
                    "soil_display",
                    "temp_display",
                    "moisture_display"
                ],
                aliases=[
                    "📍 المحافظة:",
                    "🏆 الترتيب الوطني:",
                    "📊 التقييم الشامل:",
                    "🌐 الإقليم الجغرافي:",
                    "🌱 نوع التربة:",
                    "🌡️ متوسط الحرارة:",
                    "💧 رطوبة التربة:"
                ],
                style="font-family: Alexandria, Cairo, sans-serif; min-width: 220px; color: #04101e; direction: rtl; font-size: 12px;"
            )
        ).add_to(m)

    # Layer 5: Governorate Name Labels Overlay (Subtle, pointer-transparent labels centered on each governorate)
    labels_group = folium.FeatureGroup(name="🏷️ تسميات أسماء المحافظات (Governorate Labels)", show=True)
    for g in ranked_govs:
        folium.Marker(
            location=[g["lat"], g["lon"]],
            icon=folium.DivIcon(
                html=f"""
                <div style="font-family: 'Alexandria', 'Cairo', sans-serif; font-size: 11px; font-weight: 800; color: #ffffff; text-shadow: 0 0 4px #000000, 0 0 8px #000000, 0 0 12px #04101e; text-align: center; white-space: nowrap; transform: translate(-50%, -50%); pointer-events: none;">
                    {g['name_ar']}
                </div>
                """
            )
        ).add_to(labels_group)
    labels_group.add_to(m)

    # Optional Layer: Center Beacons / Dots (Disabled by default as requested: boundaries replace dots)
    beacons_group = folium.FeatureGroup(name="📍 علامات مراكز المحافظات (Center Beacons)", show=False)
    for g in ranked_govs:
        rank = g.get("rank", 1)
        color = g.get("color", "#00e5ff")
        score = g.get("score", 0)
        folium.CircleMarker(
            location=[g["lat"], g["lon"]],
            radius=6,
            tooltip=f"#{rank} {g['name_ar']} · {score:.1f}%",
            color="#ffffff",
            fill=True,
            fill_color=color,
            fill_opacity=0.90,
            weight=1.5
        ).add_to(beacons_group)
    beacons_group.add_to(m)

    # Highlight Selected Farm Location Pin with pulsing red crosshair
    if selected_farm_coords:
        farm_lat, farm_lon = selected_farm_coords
        folium.Marker(
            location=[farm_lat, farm_lon],
            popup="🛰️ موقع مزرعتك المحدد حالياً",
            tooltip="🎯 موقع مزرعتك المحدد (اضغط للتفاصيل)",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
        ).add_to(m)

    # Live GPS Geolocation Control Plugin
    try:
        from folium.plugins import LocateControl
        LocateControl(
            auto_start=False,
            keepCurrentZoomLevel=False,
            position="topleft",
            strings={"title": "🎯 حدد موقع مزرعتك الفعلي عبر الـ GPS"}
        ).add_to(m)
    except Exception:
        pass

    # Layer Control toggle
    folium.LayerControl(position="topleft").add_to(m)

    return m
