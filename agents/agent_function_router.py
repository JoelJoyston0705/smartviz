"""
agent_function_router.py
─────────────────────────────────────────────────────────────
SmartViz — Function Router (sits between Agent 2 and Agent 3)

PURPOSE:
    Deterministically resolves high-risk metric mappings BEFORE
    the SQL Generator LLM sees the query plan. Prevents the class
    of silent hallucination found in E3 (Gemma3: 100% EA, 46.7% SA)
    where the model substitutes a plausible but incorrect metric.

ARCHITECTURE:
    Agent 1 → Agent 2 → [Function Router] → Agent 3 → Agent 4 → Agent 5
                              ↑
                        This file

ZERO IMPACT ON:
    - Agent 1 (Planner)
    - Agent 2 (RAG)
    - Agent 4 (Validator)
    - Agent 5 (Graph Builder)

USAGE:
    from agent_function_router import route_query_plan
    enriched_plan = route_query_plan(plan, schema_context)
    sql = generate_sql(enriched_plan, schema_context, model=model)

Author: Joel Joyston Cecil Kumar
Project: SmartViz Dissertation — University of Leicester, 2026
"""

import re
from typing import Optional


# ─────────────────────────────────────────────────────────────
# METRIC REGISTRY
# Maps natural language aliases → canonical PostgreSQL column values
# for metric_name in pes_all_readings
# ─────────────────────────────────────────────────────────────

METRIC_REGISTRY = {
    # Battery / Power
    "battery":                  "batteryLevel",
    "battery level":            "batteryLevel",
    "battery levels":           "batteryLevel",
    "battery status":           "batteryLevel",
    "sensor battery":           "batteryLevel",
    "power level":              "batteryLevel",

    # Building Health
    "building health":          "buildingHealth",
    "building health score":    "buildingHealth",
    "health score":             "buildingHealth",
    "structural health":        "buildingHealth",

    # Mold / Preservation
    "mold":                     "daysToMold",
    "mould":                    "daysToMold",
    "days to mold":             "daysToMold",
    "days to mould":            "daysToMold",
    "mold risk":                "daysToMold",
    "mould risk":               "daysToMold",
    "mold growth":              "daysToMold",
    "preservation":             "preservationIndex",
    "preservation index":       "preservationIndex",
    "preservation score":       "preservationIndex",
    "moisture content":         "equilibriumMoistureContent",
    "equilibrium moisture":     "equilibriumMoistureContent",

    # Corrosion / Damage
    "metal corrosion":          "metalCorrosion",
    "corrosion":                "metalCorrosion",
    "mechanical damage":        "mechanicalDamage",
    "mechanical risk":          "mechanicalDamage",

    # Occupancy
    "occupancy":                "Occupancy",
    "occupied":                 "Occupancy",
    "people count":             "peopleCount",
    "people":                   "peopleCount",
    "headcount":                "peopleCount",
    "head count":               "peopleCount",
    "motion":                   "peopleMotion",
    "people motion":            "peopleMotion",
    "movement":                 "peopleMotion",
    "total motion":             "peopleMotionTotal",
    "cumulative motion":        "peopleMotionTotal",
    "people motion total":      "peopleMotionTotal",
    "total people motion":      "peopleMotionTotal",
    "in count":                 "inCount",
    "entries":                  "inCount",
    "total entries":            "inCountTotal",
    "cumulative entries":       "inCountTotal",
    "in count total":           "inCountTotal",
    "total in count":           "inCountTotal",
    "out count":                "outCount",
    "exits":                    "outCount",
    "total exits":              "outCountTotal",
    "cumulative exits":         "outCountTotal",
    "out count total":          "outCountTotal",
    "total out count":          "outCountTotal",

    # Environmental
    "co2":                      "co2",
    "carbon dioxide":           "co2",
    "co 2":                     "co2",
    "temperature":              "temp",
    "temp":                     "temp",
    "heat":                     "temp",
    "humidity":                 "humidity",
    "moisture":                 "humidity",

    # Weather
    "external temperature":     "extTemp",
    "outside temperature":      "extTemp",
    "outdoor temperature":      "extTemp",
    "external humidity":        "extHumidity",
    "outside humidity":         "extHumidity",
    "wind speed":               "windspeed",
    "wind":                     "windspeed",
    "wind direction":           "winddir",
    "wind gust":                "windgust",
    "precipitation":            "precip",
    "rain":                     "precip",
    "cloud cover":              "cloudcover",
    "clouds":                   "cloudcover",
    "feels like":               "feelslike",
    "apparent temperature":     "feelslike",
}

# High-risk metrics — ones where LLMs have demonstrated substitution errors
# (based on E3 Gemma3 evaluation findings)
HIGH_RISK_METRICS = {
    "batteryLevel",
    "buildingHealth",
    "daysToMold",
    "preservationIndex",
    "equilibriumMoistureContent",
    "metalCorrosion",
    "mechanicalDamage",
}


# ─────────────────────────────────────────────────────────────
# AGGREGATION REGISTRY
# Maps natural language → SQL aggregation function
# ─────────────────────────────────────────────────────────────

AGGREGATION_REGISTRY = {
    "average":      "mean",
    "avg":          "mean",
    "mean":         "mean",
    "maximum":      "max",
    "max":          "max",
    "highest":      "max",
    "peak":         "max",
    "minimum":      "min",
    "min":          "min",
    "lowest":       "min",
}


# ─────────────────────────────────────────────────────────────
# CORE RESOLUTION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def resolve_metric(raw_text: str) -> Optional[str]:
    """
    Given free text (from query plan or user query),
    returns canonical metric_name if found in registry.
    Returns None if no match found.

    Matching priority:
    1. Direct exact match
    2. HIGH RISK metric aliases (longest first) — always win
    3. Low-risk metric aliases (longest first)

    This ensures that if a plan mentions both 'battery' and
    'temperature', batteryLevel (HIGH RISK) is returned, not temp.
    """
    normalised = raw_text.lower().strip()

    # 1. Direct exact match
    if normalised in METRIC_REGISTRY:
        return METRIC_REGISTRY[normalised]

    # 2. High-risk aliases first — sorted longest first
    high_risk_aliases = [
        (alias, canon)
        for alias, canon in METRIC_REGISTRY.items()
        if canon in HIGH_RISK_METRICS
    ]
    high_risk_aliases.sort(key=lambda x: len(x[0]), reverse=True)
    for alias, canonical in high_risk_aliases:
        if alias in normalised:
            return canonical

    # 3. Low-risk aliases — sorted longest first
    low_risk_aliases = [
        (alias, canon)
        for alias, canon in METRIC_REGISTRY.items()
        if canon not in HIGH_RISK_METRICS
    ]
    low_risk_aliases.sort(key=lambda x: len(x[0]), reverse=True)
    for alias, canonical in low_risk_aliases:
        if alias in normalised:
            return canonical

    return None


def resolve_aggregation(raw_text: str) -> Optional[str]:
    """
    Given free text, returns canonical aggregation value
    ('max', 'min', 'mean') if found.
    """
    normalised = raw_text.lower().strip()
    for alias, canonical in AGGREGATION_REGISTRY.items():
        if alias in normalised:
            return canonical
    return None


def is_high_risk(metric_name: str) -> bool:
    """Returns True if metric is in the high-risk substitution set."""
    return metric_name in HIGH_RISK_METRICS


# ─────────────────────────────────────────────────────────────
# PLAN ENRICHMENT
# ─────────────────────────────────────────────────────────────

def route_query_plan(plan: str, schema_context: str = None) -> str:
    """
    Main entry point. Takes Agent 1's query plan and returns
    an enriched plan with deterministic metric and aggregation
    annotations injected.

    If no high-risk metrics are detected, plan is returned unchanged.
    If high-risk metrics are detected, a FUNCTION ROUTER ANNOTATION
    block is prepended so Agent 3 uses the correct values.

    Args:
        plan:           Query plan string from Agent 1
        schema_context: Optional — schema context from Agent 2

    Returns:
        Enriched plan string (or original plan if no routing needed)
    """

    resolved_metric = resolve_metric(plan)
    resolved_agg = resolve_aggregation(plan)

    # Check if any high-risk metric is involved
    high_risk_detected = resolved_metric and is_high_risk(resolved_metric)

    # If no resolution or not high-risk — pass through unchanged
    if not resolved_metric:
        print("🔀 FUNCTION ROUTER: No metric match found — passing through unchanged")
        return plan

    if not high_risk_detected:
        print(f"🔀 FUNCTION ROUTER: Metric resolved to '{resolved_metric}' — low risk, passing through")
        return plan

    # High-risk metric detected — inject deterministic annotation
    annotation_lines = [
        "─── FUNCTION ROUTER ANNOTATION (deterministic — do not override) ───",
        f"RESOLVED metric_name = '{resolved_metric}'",
    ]

    if resolved_agg:
        annotation_lines.append(f"RESOLVED aggregation  = '{resolved_agg}'")

    annotation_lines += [
        "USE EXACTLY these values in the WHERE clause.",
        "Do NOT substitute any other metric_name.",
        "IMPORTANT: If you SELECT a non-aggregated column (e.g. display_name), include it in GROUP BY.",
        f"EAV PATTERN: '{resolved_metric}' is a VALUE in the metric_name column, NOT a column itself.",
        f"CORRECT:   WHERE metric_name = '{resolved_metric}'",
        f"INCORRECT: MAX(p.{resolved_metric}) — this column does not exist",
        f"USE THIS PATTERN to get the value:",
        f"  SELECT room_name, MAX(value) AS result",
        f"  FROM pes_all_readings",
        f"  WHERE metric_name = '{resolved_metric}'",
        f"  AND is_orphan = FALSE AND is_valid = 'TRUE'",
        f"  GROUP BY room_name",
        "────────────────────────────────────────────────────────────────────",
    ]

    annotation = "\n".join(annotation_lines)

    enriched_plan = f"{annotation}\n\n{plan}"

    print(f"🔀 FUNCTION ROUTER: HIGH-RISK metric detected")
    print(f"   Resolved: '{resolved_metric}'" + (f" | Aggregation: '{resolved_agg}'" if resolved_agg else ""))
    print(f"   Annotation injected into plan ✓")

    return enriched_plan


# ─────────────────────────────────────────────────────────────
# ROUTER STATUS — for Developer Mode display in Streamlit
# ─────────────────────────────────────────────────────────────

def get_router_status(plan: str) -> dict:
    """
    Returns a status dict for display in Developer Mode.
    Called by app.py after route_query_plan().
    """
    resolved_metric = resolve_metric(plan)
    resolved_agg = resolve_aggregation(plan)
    high_risk = resolved_metric and is_high_risk(resolved_metric)

    return {
        "activated":        bool(high_risk),
        "resolved_metric":  resolved_metric,
        "resolved_agg":     resolved_agg,
        "high_risk":        bool(high_risk),
        "message": (
            f"⚠️ High-risk metric '{resolved_metric}' detected — deterministic routing applied"
            if high_risk else
            f"✅ Metric '{resolved_metric}' resolved — low risk, passed through"
            if resolved_metric else
            "✅ No metric match — passed through unchanged"
        )
    }


# ─────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    test_plans = [
        # HIGH RISK — should inject annotation
        ("""
1. Tables: pes_all_readings, pes_rooms
2. Metric: battery level for all rooms
3. Aggregation: mean
4. Filters: is_orphan=FALSE, is_valid='TRUE'
5. Output: room_name, avg battery level
""", "Battery level query — HIGH RISK"),

        # HIGH RISK — mold
        ("""
1. Tables: pes_all_readings
2. Metric: days to mold
3. Filter latest readings only
4. Sort ascending
""", "Days to mold query — HIGH RISK"),

        # LOW RISK — should pass through
        ("""
1. Tables: pes_all_readings, pes_rooms
2. Metric: co2
3. Aggregation: max
4. Filters: is_orphan=FALSE, is_valid='TRUE'
5. Limit: 5 rooms
""", "CO2 query — LOW RISK (pass through)"),

        # NO MATCH — should pass through unchanged
        ("""
1. Count total rooms in pes_rooms
""", "Room count — NO METRIC MATCH"),
    ]

    for plan, label in test_plans:
        print("\n" + "=" * 65)
        print(f"TEST: {label}")
        print("=" * 65)
        enriched = route_query_plan(plan)
        status = get_router_status(plan)
        print(f"Status: {status['message']}")
        if status["activated"]:
            print(f"\nEnriched plan preview:")
            print(enriched[:300] + "...")