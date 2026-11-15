"""
AgroOrbit - Agricultural Economics & Resource ROI Calculator
Team: Nova Squad NASA
Challenge: NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data

Calculates precise financial, water, and agronomic ROI for Egyptian farms:
- Land units in Feddans (1 feddan = 4,200.83 m²)
- Water volume savings in cubic meters (m³)
- Fertilizer savings in 50kg Urea bags (46.5% N) and Egyptian Pounds (EGP)
- Irrigation pumping energy savings (diesel/electricity)
- Biological pest-break chemical pesticide savings
- Environmental carbon offset (tCO2e)
"""

from typing import Dict, Any


def calculate_farm_economic_roi(
    area_feddan: float,
    strat_baseline: Dict[str, Any],
    strat_soil: Dict[str, Any],
    strat_water: Dict[str, Any],
    urea_bag_price_egp: float = 750.0,
    pumping_cost_m3_egp: float = 1.10,
    pesticide_saving_per_feddan_egp: float = 650.0
) -> Dict[str, Any]:
    """
    Computes comprehensive multi-season economic and resource returns for a given farm acreage.
    """
    area = max(0.5, float(area_feddan))
    
    # Water constants: 1 mm depth on 1 feddan (4200.83 m²) = 4.20083 m³
    M3_PER_MM_FEDDAN = 4.20083

    # Baseline metrics
    w_base_mm = strat_baseline.get("metrics", {}).get("total_water_mm", 1750.0)
    n_base_kg_ha = strat_baseline.get("metrics", {}).get("net_nitrogen_kg_ha", -90.0)

    # Strategy 2 (Soil Health BNF) metrics
    w_soil_mm = strat_soil.get("metrics", {}).get("total_water_mm", 1450.0)
    n_soil_kg_ha = strat_soil.get("metrics", {}).get("net_nitrogen_kg_ha", 60.0)

    # Strategy 3 (Water Resilience) metrics
    w_water_mm = strat_water.get("metrics", {}).get("total_water_mm", 1250.0)
    n_water_kg_ha = strat_water.get("metrics", {}).get("net_nitrogen_kg_ha", 20.0)

    # 1. Water calculations (m³)
    base_total_water_m3 = w_base_mm * M3_PER_MM_FEDDAN * area
    soil_total_water_m3 = w_soil_mm * M3_PER_MM_FEDDAN * area
    water_total_water_m3 = w_water_mm * M3_PER_MM_FEDDAN * area

    water_saved_strat2_m3 = max(0.0, base_total_water_m3 - soil_total_water_m3)
    water_saved_strat3_m3 = max(0.0, base_total_water_m3 - water_total_water_m3)

    # 2. Fertilizer / Urea bags calculations
    # Conversion: 1 hectare = 2.381 feddans -> 1 kg N/ha = (1 / 2.381) = 0.42 kg N/feddan
    # 1 bag of Urea (50 kg, 46.5% N) contains 23.25 kg elemental Nitrogen.
    # Net advantage of BNF: positive biological N fixation replacing synthetic urea
    pure_n_gain_per_feddan_s2 = max(0.0, (n_soil_kg_ha - min(0.0, n_base_kg_ha)) * 0.42)
    pure_n_gain_per_feddan_s3 = max(0.0, (n_water_kg_ha - min(0.0, n_base_kg_ha)) * 0.42)

    urea_bags_saved_per_feddan_s2 = max(1.5, pure_n_gain_per_feddan_s2 / 23.25)
    urea_bags_saved_per_feddan_s3 = max(0.8, pure_n_gain_per_feddan_s3 / 23.25)

    total_urea_bags_saved_s2 = round(urea_bags_saved_per_feddan_s2 * area, 1)
    total_urea_bags_saved_s3 = round(urea_bags_saved_per_feddan_s3 * area, 1)

    fertilizer_cost_saved_s2_egp = total_urea_bags_saved_s2 * urea_bag_price_egp
    fertilizer_cost_saved_s3_egp = total_urea_bags_saved_s3 * urea_bag_price_egp

    # 3. Pumping energy cost savings (EGP)
    pumping_saved_s2_egp = water_saved_strat2_m3 * pumping_cost_m3_egp
    pumping_saved_s3_egp = water_saved_strat3_m3 * pumping_cost_m3_egp

    # 4. Pesticide savings (from pest break cycles)
    pesticide_saved_s2_egp = pesticide_saving_per_feddan_egp * area
    pesticide_saved_s3_egp = (pesticide_saving_per_feddan_egp * 0.75) * area

    # 5. Total Net Economic Benefits (EGP)
    total_benefit_s2_egp = fertilizer_cost_saved_s2_egp + pumping_saved_s2_egp + pesticide_saved_s2_egp
    total_benefit_s3_egp = fertilizer_cost_saved_s3_egp + pumping_saved_s3_egp + pesticide_saved_s3_egp

    benefit_per_feddan_s2 = total_benefit_s2_egp / area
    benefit_per_feddan_s3 = total_benefit_s3_egp / area

    # 6. Environmental Carbon Footprint Offset
    # Producing 1 kg of synthetic urea releases ~2.16 kg CO2 equivalent
    co2_offset_tons_s2 = round((total_urea_bags_saved_s2 * 50 * 2.16) / 1000.0, 2)
    co2_offset_tons_s3 = round((total_urea_bags_saved_s3 * 50 * 2.16) / 1000.0, 2)

    return {
        "area_feddan": area,
        "parameters": {
            "urea_bag_price_egp": urea_bag_price_egp,
            "pumping_cost_m3_egp": pumping_cost_m3_egp,
            "pesticide_saving_per_feddan_egp": pesticide_saving_per_feddan_egp
        },
        "baseline": {
            "total_water_m3": round(base_total_water_m3, 0),
            "water_mm": w_base_mm
        },
        "strategy_2_soil_health": {
            "name_ar": "الاستراتيجية 2: صحة التربة وتثبيت النيتروجين (BNF)",
            "water_saved_m3": round(water_saved_strat2_m3, 0),
            "water_saved_pct": round(((base_total_water_m3 - soil_total_water_m3) / base_total_water_m3) * 100, 1),
            "urea_bags_saved": total_urea_bags_saved_s2,
            "urea_bags_per_feddan": round(urea_bags_saved_per_feddan_s2, 1),
            "fertilizer_savings_egp": round(fertilizer_cost_saved_s2_egp, 0),
            "pumping_savings_egp": round(pumping_saved_s2_egp, 0),
            "pesticide_savings_egp": round(pesticide_saved_s2_egp, 0),
            "total_financial_gain_egp": round(total_benefit_s2_egp, 0),
            "financial_gain_per_feddan_egp": round(benefit_per_feddan_s2, 0),
            "co2_offset_tons": co2_offset_tons_s2
        },
        "strategy_3_water_resilience": {
            "name_ar": "الاستراتيجية 3: التكيف المائي وحماية الجفاف",
            "water_saved_m3": round(water_saved_strat3_m3, 0),
            "water_saved_pct": round(((base_total_water_m3 - water_total_water_m3) / base_total_water_m3) * 100, 1),
            "urea_bags_saved": total_urea_bags_saved_s3,
            "urea_bags_per_feddan": round(urea_bags_saved_per_feddan_s3, 1),
            "fertilizer_savings_egp": round(fertilizer_cost_saved_s3_egp, 0),
            "pumping_savings_egp": round(pumping_saved_s3_egp, 0),
            "pesticide_savings_egp": round(pesticide_saved_s3_egp, 0),
            "total_financial_gain_egp": round(total_benefit_s3_egp, 0),
            "financial_gain_per_feddan_egp": round(benefit_per_feddan_s3, 0),
            "co2_offset_tons": co2_offset_tons_s3
        }
    }
