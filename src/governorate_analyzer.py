"""
AgroOrbit - Egypt Governorates Agro-Climatic Intelligence Engine
Ranks Egypt's 27 governorates from NASA Earth observation indices and renders
calm single-hue choropleth maps and clean radar profiles.
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


def _interpolate_single_hue_hex(rank_idx: int, total: int, dark_mode: bool = True) -> str:
    """
    Generate a clean single-hue luminance ramp from rank 1 (strongest) to rank 27 (lowest).
    Eliminates rainbow noise so ranking is readable without scanning legends.
    """
    ratio = 1.0 - (rank_idx / max(1, total - 1))  # 1.0 at rank 1, 0.0 at rank 27
    if dark_mode:
        # Interpolate from muted slate (#2a332b) to calm sage emerald (#6ba670)
        r0, g0, b0 = 42, 46, 44
        r1, g1, b1 = 107, 166, 112
    else:
        # Interpolate from soft mist (#e2e6e3) to earthy field green (#2f7d4f)
        r0, g0, b0 = 220, 226, 222
        r1, g1, b1 = 47, 125, 79

    r = int(r0 + (r1 - r0) * ratio)
    g = int(g0 + (g1 - g0) * ratio)
    b = int(b0 + (b1 - b0) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


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
    dark_mode: bool = True,
) -> List[Dict[str, Any]]:
    """Rank all 27 governorates based on the selected criterion with single-hue tones."""
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
        g["color"] = _interpolate_single_hue_hex(idx, total, dark_mode=dark_mode)

    return ranked


def build_governorate_radar(gov_record: Dict[str, Any], dark_mode: bool = True) -> go.Figure:
    """Generate clean, quiet polar profile for a selected governorate."""
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

    accent = t["accent"]
    fill_rgba = "rgba(124, 183, 127, 0.20)" if dark_mode else "rgba(47, 125, 79, 0.16)"
    grid_col = "rgba(237, 237, 237, 0.08)" if dark_mode else "rgba(23, 23, 23, 0.08)"

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor=fill_rgba,
        line=dict(color=accent, width=2),
        marker=dict(color=accent, size=5),
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
                tickfont=dict(color=t["text_secondary"], size=12, family="IBM Plex Sans Arabic, sans-serif"),
                gridcolor=grid_col,
                linecolor=grid_col,
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans Arabic, sans-serif"),
        margin=dict(l=36, r=36, t=24, b=24),
        height=280,
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
    dark_mode: bool = True,
    zoom_start: int = 6,
    show_labels: bool = True,
) -> folium.Map:
    """
    Build clean choropleth Folium map without rainbow noise or glowing tooltips.
    Polygons use a calm single-hue luminance scale, highlighting only the selected governorate.
    """
    t = get_tokens(dark_mode)

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles=None,
        control_scale=True,
    )

    # Default calm watermark-free basemap matched to app theme; Satellite & OSM sit 1 click away
    if dark_mode:
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
            attr="Esri, HERE, Garmin",
            name="الخريطة الداكنة",
            max_zoom=16,
            show=True,
        ).add_to(m)
    else:
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
            attr="Esri, HERE, Garmin",
            name="الخريطة الفاتحة",
            max_zoom=16,
            show=True,
        ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, Maxar",
        name="صور الأقمار الصناعية",
        max_zoom=18,
        show=False,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="OpenStreetMap",
        name="خريطة الطرق",
        max_zoom=19,
        show=False,
    ).add_to(m)

    # GeoJSON Governorate Choropleth Boundaries
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

                feat_copy["properties"]["color"] = t["accent"] if is_sel else g_info.get("color", t["bg_raised"])
                feat_copy["properties"]["score_str"] = f"{score:.1f}%"
                feat_copy["properties"]["rank_badge"] = f"#{rank}"
                feat_copy["properties"]["name_ar_display"] = g_info.get("name_ar", "")
                feat_copy["properties"]["soil_display"] = soil_ar
                feat_copy["properties"]["temp_display"] = f"{g_info.get('indices', {}).get('avg_temp_c', 24.0)} °C"
                feat_copy["properties"]["moisture_display"] = f"{g_info.get('indices', {}).get('soil_moisture_score', 45)}%"
                feat_copy["properties"]["tooltip_label"] = f"{g_info.get('name_ar', '')} · #{rank} ({score:.1f}%)"
            else:
                feat_copy["properties"]["color"] = t["bg_raised"]
                feat_copy["properties"]["score_str"] = "-"
                feat_copy["properties"]["rank_badge"] = "-"
                feat_copy["properties"]["name_ar_display"] = feat_copy["properties"].get("name_ar", "")
                feat_copy["properties"]["soil_display"] = "-"
                feat_copy["properties"]["temp_display"] = "-"
                feat_copy["properties"]["moisture_display"] = "-"
                feat_copy["properties"]["tooltip_label"] = feat_copy["properties"].get("name_ar", "محافظة")
            features_copy.append(feat_copy)

        enriched_geojson = {"type": "FeatureCollection", "features": features_copy}
        border_muted = "rgba(237, 237, 237, 0.25)" if dark_mode else "rgba(23, 23, 23, 0.22)"

        def polygon_style(feature):
            props = feature["properties"]
            is_sel = props.get("is_selected", False)
            return {
                "fillColor": props.get("color", t["bg_raised"]),
                "color": t["accent"] if is_sel else border_muted,
                "weight": 2.5 if is_sel else 1.0,
                "fillOpacity": 0.65 if is_sel else 0.48,
                "opacity": 1.0 if is_sel else 0.75,
            }

        def polygon_highlight(feature):
            return {
                "color": t["accent"],
                "weight": 2.0,
                "fillOpacity": 0.70,
                "opacity": 1.0,
            }

        folium.GeoJson(
            enriched_geojson,
            name="حدود المحافظات",
            style_function=polygon_style,
            highlight_function=polygon_highlight,
            tooltip=folium.GeoJsonTooltip(
                fields=["tooltip_label"],
                aliases=[""],
                labels=False,
                style=(
                    f"background-color: {t['bg_card']}; color: {t['text_primary']}; "
                    f"font-family: IBM Plex Sans Arabic, sans-serif; font-size: 12px; font-weight: 500; "
                    f"border: 1px solid {t['hairline_strong']}; border-radius: 6px; padding: 6px 10px;"
                ),
            ),
            popup=folium.GeoJsonPopup(
                fields=["name_ar_display", "rank_badge", "score_str", "soil_display", "temp_display", "moisture_display"],
                aliases=["المحافظة", "الترتيب", "المؤشر", "التربة السائدة", "متوسط الحرارة", "رطوبة التربة"],
                style=(
                    f"font-family: IBM Plex Sans Arabic, sans-serif; min-width: 190px; "
                    f"color: #171717; direction: rtl; font-size: 12px;"
                ),
            ),
        ).add_to(m)

    if show_labels:
        label_color = "#ededed" if dark_mode else "#171717"
        label_halo = "rgba(20,20,21,0.85)" if dark_mode else "rgba(255,255,255,0.85)"
        labels_group = folium.FeatureGroup(name="أسماء المحافظات", show=True)
        for g in ranked_govs:
            folium.Marker(
                location=[g["lat"], g["lon"]],
                icon=folium.DivIcon(
                    html=(
                        f'<div style="font-family:\'IBM Plex Sans Arabic\',sans-serif;font-size:11px;'
                        f'font-weight:500;color:{label_color};'
                        f'text-shadow:0 1px 2px {label_halo},0 0 4px {label_halo};'
                        f'text-align:center;white-space:nowrap;transform:translate(-50%,-50%);'
                        f'pointer-events:none;">{g["name_ar"]}</div>'
                    )
                ),
            ).add_to(labels_group)
        labels_group.add_to(m)

    # Clean pinpoint marker for the farmer's selected plot
    if selected_farm_coords:
        farm_lat, farm_lon = selected_farm_coords
        folium.CircleMarker(
            location=[farm_lat, farm_lon],
            radius=8,
            color="#ffffff" if dark_mode else "#171717",
            weight=2,
            fill=True,
            fill_color=t["accent"],
            fill_opacity=1.0,
            tooltip="موقع الأرض المختار",
        ).add_to(m)

    try:
        from folium.plugins import LocateControl
        LocateControl(
            auto_start=False,
            keepCurrentZoomLevel=False,
            position="topleft",
            strings={"title": "موقعي الحالي"},
        ).add_to(m)
    except Exception:
        pass

    folium.LayerControl(position="topleft").add_to(m)
    return m
