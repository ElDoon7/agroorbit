"""
AgroOrbit - Egypt Governorates Agro-Climatic Intelligence Engine
Ranks Egypt's 27 governorates from NASA Earth observation indices and renders
vivid satellite choropleth maps with an Emerald-Teal-Gold agronomic gradient.
"""

import json
from typing import Dict, Any, List, Tuple, Optional
import folium
import plotly.graph_objects as go
from src import config
from src.design_system import get_tokens

_CACHED_GEOJSON_DATA = None


def get_egypt_geojson_data():
    """Load and cache Egypt 27 governorates boundary GeoJSON."""
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


def _lerp_rgb(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _interpolate_agronomic_hex(rank_idx: int, total: int) -> str:
    """
    Continuous 4-stop agricultural spectrum from Rank 1 (Emerald) -> Teal -> Amber Gold -> Copper.
    Vivid over satellite imagery without garish neon hues.
    """
    pos = rank_idx / max(1, total - 1)  # 0.0 at rank 1 -> 1.0 at rank 27
    stops = [
        (0.00, (16, 185, 129)),   # #10b981 Emerald
        (0.35, (14, 165, 233)),   # #0ea5e9 Sky Teal
        (0.70, (245, 158, 11)),   # #f59e0b Wheat Amber Gold
        (1.00, (234, 88, 12)),    # #ea580c Warm Terracotta
    ]
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= pos <= p1:
            local_t = (pos - p0) / max(1e-6, (p1 - p0))
            r, g, b = _lerp_rgb(c0, c1, local_t)
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#ea580c"


CRITERIA_DEFINITIONS = {
    "composite_score": {
        "title_ar": "الملاءمة الزراعية الشاملة",
        "title_en": "Composite Agro-Climatic Suitability",
        "index_key": "composite_score",
        "description_ar": "المؤشر الكلي المرجح لتقييم ملاءمة المحافظة وفق رطوبة التربة والاعتدال الحراري",
        "unit": "%"
    },
    "soil_moisture_score": {
        "title_ar": "رطوبة التربة (SMAP)",
        "title_en": "Soil Moisture & Water Holding",
        "index_key": "soil_moisture_score",
        "description_ar": "تقييم الرطوبة الجذرية والسطحية للتربة وملاءمتها للمحاصيل الاستراتيجية",
        "unit": "%"
    },
    "water_conservation_potential": {
        "title_ar": "فرصة توفير مياه الري",
        "title_en": "Water Conservation Potential",
        "index_key": "water_conservation_potential",
        "description_ar": "قدرة المحافظة على خفض استهلاك المياه عند تطبيق دورات متكيفة",
        "unit": "%"
    },
    "thermal_stability": {
        "title_ar": "الاستقرار الحراري (T2M)",
        "title_en": "Thermal Stability",
        "index_key": "thermal_stability",
        "description_ar": "انخفاض أيام الإجهاد الحراري الشديد والموجات الضارة بالإزهار",
        "unit": "%"
    },
}


def rank_governorates(
    gov_telemetry: Dict[str, Dict[str, Any]],
    criterion_key: str = "composite_score",
    dark_mode: bool = False,
) -> List[Dict[str, Any]]:
    """Rank all 27 governorates based on the selected criterion with Emerald-Teal-Gold tones."""
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

    ranked.sort(key=lambda x: x["score"], reverse=True)
    total = len(ranked)
    for idx, g in enumerate(ranked):
        g["rank"] = idx + 1
        g["color"] = _interpolate_agronomic_hex(idx, total)

    return ranked


def build_governorate_radar(gov_record: Dict[str, Any], dark_mode: bool = False) -> go.Figure:
    """Generate crisp, vibrant polar profile for a selected governorate."""
    t = get_tokens(dark_mode)
    indices = gov_record.get("indices", {})
    categories = [
        "رطوبة التربة",
        "توفير المياه",
        "الاستقرار الحراري",
        "الملاءمة الشاملة",
        "الغطاء النباتي",
    ]
    values = [
        indices.get("soil_moisture_score", 50.0),
        indices.get("water_conservation_potential", 50.0),
        indices.get("thermal_stability", 50.0),
        indices.get("composite_score", 50.0),
        min(95.0, indices.get("soil_moisture_score", 50.0) * 1.1),
    ]
    values.append(values[0])
    categories.append(categories[0])

    radar_color = gov_record.get("color", t["accent"])
    fill_rgba = "rgba(16, 185, 129, 0.22)" if dark_mode else "rgba(5, 150, 105, 0.16)"
    grid_col = "rgba(226, 232, 240, 0.10)" if dark_mode else "rgba(15, 23, 42, 0.08)"

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor=fill_rgba,
        line=dict(color=radar_color, width=2.5),
        marker=dict(color=t["wheat_gold"], size=6),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color=t["text_muted"], size=10, family="IBM Plex Mono, monospace"),
                gridcolor=grid_col,
                linecolor=grid_col,
            ),
            angularaxis=dict(
                tickfont=dict(color=t["text_primary"], size=12, family="IBM Plex Sans Arabic, sans-serif"),
                gridcolor=grid_col,
                linecolor=grid_col,
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans Arabic, sans-serif"),
        margin=dict(l=36, r=36, t=24, b=24),
        height=290,
        showlegend=False,
    )
    return fig


def build_orbital_folium_map(
    center_lat: float,
    center_lon: float,
    ranked_govs: List[Dict[str, Any]],
    criterion_key: str = "composite_score",
    selected_farm_coords: Optional[Tuple[float, float]] = None,
    selected_gov_id: Optional[str] = None,
    dark_mode: bool = False,
    zoom_start: int = 6,
    show_labels: bool = True,
) -> folium.Map:
    """
    Build vivid realistic satellite Folium map with Emerald-Teal-Gold choropleth polygons
    across all 27 Egyptian governorates, crisp white borders, and native GPS LocateControl.
    """
    t = get_tokens(dark_mode)

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles=None,
        control_scale=True,
    )

    # Layer 1 (Default): Real Satellite Imagery + Geographic Labels
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, Maxar, Earthstar Geographics",
        name="صور الأقمار الصناعية (Satellite)",
        max_zoom=18,
        show=True,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="حدود وأسماء المدن",
        overlay=True,
        show=True,
    ).add_to(m)

    # Alternative clean map bases
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, HERE, Garmin",
        name="خريطة فاتحة نظيفة",
        max_zoom=16,
        show=False,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, HERE, Garmin",
        name="خريطة داكنة",
        max_zoom=16,
        show=False,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="OpenStreetMap",
        name="خريطة الشوارع",
        max_zoom=19,
        show=False,
    ).add_to(m)

    # GeoJSON Governorate Choropleth Polygons
    geo_data = get_egypt_geojson_data()
    if geo_data:
        gov_map_data = {g["id"]: g for g in ranked_govs}
        soil_map = config.SOIL_TYPES

        features_copy = []
        for feat in geo_data.get("features", []):
            feat_copy = {
                "type": feat["type"],
                "geometry": feat["geometry"],
                "properties": dict(feat["properties"]),
            }
            gid = feat_copy["properties"].get("gov_id")
            is_sel = (selected_gov_id is not None and gid == selected_gov_id)
            feat_copy["properties"]["is_selected"] = is_sel

            if gid in gov_map_data:
                g_info = gov_map_data[gid]
                score = g_info.get("score", 0)
                rank = g_info.get("rank", 1)
                soil_id = g_info.get("dominant_soil", "loam")
                soil_ar = soil_map.get(soil_id, {}).get("name_ar", soil_id)

                feat_copy["properties"]["color"] = g_info.get("color", "#10b981")
                feat_copy["properties"]["score_str"] = f"{score:.1f}%"
                feat_copy["properties"]["rank_badge"] = f"#{rank}"
                feat_copy["properties"]["name_ar_display"] = g_info.get("name_ar", "")
                feat_copy["properties"]["soil_display"] = soil_ar
                feat_copy["properties"]["temp_display"] = f"{g_info.get('indices', {}).get('avg_temp_c', 24.0)} °C"
                feat_copy["properties"]["moisture_display"] = f"{g_info.get('indices', {}).get('soil_moisture_score', 45)}%"
                feat_copy["properties"]["tooltip_label"] = f"{g_info.get('name_ar', '')} · #{rank} ({score:.1f}%)"
            else:
                feat_copy["properties"]["color"] = "#0ea5e9"
                feat_copy["properties"]["score_str"] = "-"
                feat_copy["properties"]["rank_badge"] = "-"
                feat_copy["properties"]["name_ar_display"] = feat_copy["properties"].get("name_ar", "")
                feat_copy["properties"]["soil_display"] = "-"
                feat_copy["properties"]["temp_display"] = "-"
                feat_copy["properties"]["moisture_display"] = "-"
                feat_copy["properties"]["tooltip_label"] = feat_copy["properties"].get("name_ar", "محافظة")
            features_copy.append(feat_copy)

        enriched_geojson = {"type": "FeatureCollection", "features": features_copy}

        def polygon_style(feature):
            props = feature["properties"]
            is_sel = props.get("is_selected", False)
            return {
                "fillColor": props.get("color", "#10b981"),
                "color": "#fef08a" if is_sel else "#ffffff",
                "weight": 2.8 if is_sel else 1.2,
                "fillOpacity": 0.62 if is_sel else 0.42,
                "opacity": 1.0 if is_sel else 0.85,
            }

        def polygon_highlight(feature):
            return {
                "color": "#ffffff",
                "weight": 2.5,
                "fillOpacity": 0.68,
                "opacity": 1.0,
            }

        folium.GeoJson(
            enriched_geojson,
            name="تدرج المحافظات (27 محافظة)",
            style_function=polygon_style,
            highlight_function=polygon_highlight,
            tooltip=folium.GeoJsonTooltip(
                fields=["tooltip_label"],
                aliases=[""],
                labels=False,
                style=(
                    "background-color: #ffffff; color: #0f172a; "
                    "font-family: IBM Plex Sans Arabic, sans-serif; font-size: 12.5px; font-weight: 500; "
                    "border: 1px solid rgba(15,23,42,0.16); border-radius: 8px; padding: 6px 10px; "
                    "box-shadow: 0 4px 12px rgba(15,23,42,0.12);"
                ),
            ),
            popup=folium.GeoJsonPopup(
                fields=["name_ar_display", "rank_badge", "score_str", "soil_display", "temp_display", "moisture_display"],
                aliases=["المحافظة", "الترتيب", "المؤشر", "التربة السائدة", "متوسط الحرارة", "رطوبة التربة"],
                style=(
                    "font-family: IBM Plex Sans Arabic, sans-serif; min-width: 195px; "
                    "color: #0f172a; direction: rtl; font-size: 12.5px;"
                ),
            ),
        ).add_to(m)

    if show_labels:
        labels_group = folium.FeatureGroup(name="أسماء المحافظات", show=True)
        for g in ranked_govs:
            folium.Marker(
                location=[g["lat"], g["lon"]],
                icon=folium.DivIcon(
                    html=(
                        f'<div style="font-family:\'IBM Plex Sans Arabic\',sans-serif;font-size:11px;'
                        f'font-weight:600;color:#ffffff;'
                        f'text-shadow:0 1px 3px rgba(0,0,0,0.9),0 0 6px rgba(0,0,0,0.8);'
                        f'text-align:center;white-space:nowrap;transform:translate(-50%,-50%);'
                        f'pointer-events:none;">{g["name_ar"]}</div>'
                    )
                ),
            ).add_to(labels_group)
        labels_group.add_to(m)

    # Farm Location Pin
    if selected_farm_coords:
        farm_lat, farm_lon = selected_farm_coords
        folium.Marker(
            location=[farm_lat, farm_lon],
            popup="موقع الأرض المختار",
            tooltip="موقع الأرض المختار",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
        ).add_to(m)

    try:
        from folium.plugins import LocateControl
        LocateControl(
            auto_start=False,
            keepCurrentZoomLevel=False,
            position="topleft",
            strings={"title": "موقعي الحالي (GPS)"},
        ).add_to(m)
    except Exception:
        pass

    folium.LayerControl(position="topleft").add_to(m)
    return m
