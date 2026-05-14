"""
router_validation.py
─────────────────────────────────────────────────────────────
SmartViz — Function Router Before/After Validation

Reproduces the exact Gemma3 failure from E3 evaluation and
demonstrates the router fix. Uses the same queries that failed
in E3 (SA=0) due to metric substitution.

Run from: ~/Desktop/Dissertation/smartviz_agents_copy/agents/
Command:  python router_validation.py

Author: Joel Joyston Cecil Kumar
Project: SmartViz Dissertation — University of Leicester, 2026
"""

import psycopg2
import ollama
import os
from dotenv import load_dotenv
from agent_function_router import route_query_plan, get_router_status

load_dotenv()

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def run_sql(sql):
    """Execute SQL and return (rows, error)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        return rows, cols, None
    except Exception as e:
        return None, None, str(e)


# ─────────────────────────────────────────────
# GEMMA3 SQL GENERATION
# ─────────────────────────────────────────────
SCHEMA_CONTEXT = """
TABLE 1: pes_rooms (32 rooms in PES building)
  - display_name: human readable room name
  - geometry_id: unique sensor ID (join key to readings)

TABLE 2: pes_all_readings (1,048,575 hourly sensor readings)
  - geometry_id: links to pes_rooms via JOIN
  - room_name: human readable room name
  - metric_name: one of — Occupancy, co2, temp, humidity,
      peopleCount, peopleMotion, peopleMotionTotal,
      inCount, outCount, inCountTotal, outCountTotal,
      daysToMold, equilibriumMoistureContent, preservationIndex,
      mechanicalDamage, metalCorrosion, batteryLevel,
      extTemp, extHumidity, feelslike, cloudcover,
      precip, windspeed, winddir, windgust
  - aggregation: 'max', 'min', or 'mean'
  - value: the sensor reading
  - start_time_utc: timestamp
  - is_working: TEXT — 'True' = working hours
  - is_orphan: BOOLEAN — filter using is_orphan = FALSE
  - is_valid: TEXT — filter using is_valid = 'TRUE'

STRICT RULES:
  - ALWAYS include WHERE is_orphan = FALSE
  - ALWAYS include WHERE is_valid = 'TRUE'
  - For latest readings use MAX(start_time_utc), NOT CURRENT_TIMESTAMP
  - Return SQL only — no explanation, no markdown, no backticks
"""

def generate_sql_gemma3(plan: str) -> str:
    prompt = f"""<start_of_turn>user
You are a PostgreSQL expert. Convert the query plan below into a single valid SQL query.

Rules:
- Return SQL only — no explanation, no markdown, no backticks
- Use table aliases to prevent ambiguity
- Only use tables and columns described in the schema

Schema and rules:
{SCHEMA_CONTEXT}

Query plan:
{plan}
<end_of_turn>
<start_of_turn>model
SELECT"""

    response = ollama.generate(
        model="gemma3",
        prompt=prompt,
        options={"temperature": 0, "stop": ["<end_of_turn>", "<start_of_turn>"], "num_predict": 300}
    )
    raw = response["response"].strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.lower().startswith("sql"):
            raw = raw[3:]
        raw = raw.strip()
    if raw.upper().startswith("SELECT"):
        return raw
    return "SELECT " + raw


# ─────────────────────────────────────────────
# VALIDATION TEST CASES
# Taken directly from E3 evaluation failures (SA=0)
# ─────────────────────────────────────────────
TEST_CASES = [
    {
        "query_id": "Q11",
        "difficulty": "Medium",
        "question": "Which sensors have a battery level below 20 percent?",
        "agent1_plan": """
1. Tables needed: pes_all_readings
2. Target metric: battery level
3. Filter: value below 20
4. Filters: is_orphan = FALSE, is_valid = 'TRUE'
5. Output: room_name, battery value
6. Sort: value ASC
""",
        "e3_sql": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name HAVING AVG(value) > 21 ORDER BY avg_temp DESC LIMIT 5",
        "expected_metric": "batteryLevel",
        "wrong_metric": "temp",
    },
    {
        "query_id": "Q14",
        "difficulty": "Hard",
        "question": "Which rooms have the highest metal corrosion risk score?",
        "agent1_plan": """
1. Tables needed: pes_all_readings, pes_rooms
2. Target metric: metal corrosion risk
3. Aggregation: average per room
4. Filters: is_orphan = FALSE, is_valid = 'TRUE'
5. Output: room_name, avg corrosion score
6. Sort: DESC, Limit 5
""",
        "e3_sql": "SELECT r.display_name, ROUND(AVG(p.value)::numeric, 2) AS avg_metal_corrosion FROM pes_all_readings p JOIN pes_rooms r ON p.geometry_id = r.geometry_id WHERE p.metric_name = 'metalCorrosion' AND p.is_orphan = FALSE AND p.is_valid = 'TRUE' GROUP BY r.display_name ORDER BY avg_metal_corrosion DESC LIMIT 10",
        "expected_metric": "metalCorrosion",
        "wrong_metric": None,  # E3 Q14 got this right — EA=1 SA=0 for different reason
    },
    {
        "query_id": "Q09",
        "difficulty": "Medium",
        "question": "Which rooms have the highest preservation index?",
        "agent1_plan": """
1. Tables needed: pes_all_readings
2. Target metric: preservation index
3. Aggregation: max per room
4. Filters: is_orphan = FALSE, is_valid = 'TRUE'
5. Output: room_name, preservation index value
6. Sort: DESC, Limit 5
""",
        "e3_sql": "SELECT room_name, value AS preservation_index FROM pes_all_readings WHERE metric_name = 'preservationIndex' AND is_orphan = FALSE AND is_valid = 'TRUE' ORDER BY value DESC LIMIT 1",
        "expected_metric": "preservationIndex",
        "wrong_metric": None,
    },
]


# ─────────────────────────────────────────────
# MAIN VALIDATION RUNNER
# ─────────────────────────────────────────────
def run_validation():
    print("\n" + "=" * 70)
    print("SMARTVIZ FUNCTION ROUTER — BEFORE/AFTER VALIDATION")
    print("Comparing E3 Gemma3 failures with router-enabled re-run")
    print("=" * 70)

    results = []

    for tc in TEST_CASES:
        print(f"\n{'─' * 70}")
        print(f"QUERY {tc['query_id']} [{tc['difficulty']}]: {tc['question']}")
        print(f"{'─' * 70}")

        # ── BEFORE: Run original E3 SQL (no router) ──────────────
        print(f"\n📋 BEFORE (E3 — no router):")
        print(f"   SQL used metric: '{tc['wrong_metric'] or tc['expected_metric']}'")
        rows_before, cols_before, err_before = run_sql(tc["e3_sql"])

        if err_before:
            print(f"   ❌ Execution error: {err_before}")
            before_result = "ERROR"
        else:
            print(f"   ✅ Executed — {len(rows_before)} rows returned")
            if rows_before:
                print(f"   Columns: {cols_before}")
                for r in rows_before[:3]:
                    print(f"   {r}")
                if len(rows_before) > 3:
                    print(f"   ... and {len(rows_before)-3} more rows")
            if tc["wrong_metric"] and tc["wrong_metric"] != tc["expected_metric"]:
                print(f"   ⚠️  WRONG METRIC — returned {tc['wrong_metric']} data, not {tc['expected_metric']}")
                before_result = f"WRONG ({tc['wrong_metric']} instead of {tc['expected_metric']})"
            else:
                before_result = "CORRECT METRIC"

        # ── AFTER: Generate with router enabled ──────────────────
        print(f"\n🔀 ROUTER CHECK:")
        status = get_router_status(tc["agent1_plan"])
        print(f"   {status['message']}")

        enriched_plan = route_query_plan(tc["agent1_plan"])

        print(f"\n🤖 AFTER (Gemma3 + router):")
        print(f"   Generating SQL with Gemma3...")
        sql_after = generate_sql_gemma3(enriched_plan)
        print(f"   Generated SQL:\n   {sql_after}")

        # Check metric in generated SQL
        if tc["expected_metric"].lower() in sql_after.lower():
            print(f"   ✅ Correct metric '{tc['expected_metric']}' found in SQL")
            metric_correct = True
        else:
            print(f"   ❌ Expected metric '{tc['expected_metric']}' NOT found in SQL")
            metric_correct = False

        # Execute generated SQL
        rows_after, cols_after, err_after = run_sql(sql_after)
        if err_after:
            print(f"   ❌ Execution error: {err_after}")
            after_result = "ERROR"
        else:
            print(f"   ✅ Executed — {len(rows_after)} rows returned")
            if rows_after:
                print(f"   Columns: {cols_after}")
                for r in rows_after[:3]:
                    print(f"   {r}")
                if len(rows_after) > 3:
                    print(f"   ... and {len(rows_after)-3} more rows")
            after_result = "CORRECT" if metric_correct else "WRONG METRIC"

        results.append({
            "query_id": tc["query_id"],
            "question": tc["question"],
            "router_activated": status["activated"],
            "before": before_result,
            "after": after_result,
            "metric_fixed": tc["wrong_metric"] is not None and metric_correct,
        })

    # ── SUMMARY ──────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"{'Query':<8} {'Router':<12} {'Before':<35} {'After':<15}")
    print(f"{'─'*70}")
    for r in results:
        router = "🔴 ACTIVE" if r["router_activated"] else "🟢 pass-through"
        print(f"{r['query_id']:<8} {router:<12} {r['before']:<35} {r['after']:<15}")

    print(f"\n{'─'*70}")
    fixed = sum(1 for r in results if r["metric_fixed"])
    print(f"Metric substitution errors fixed by router: {fixed}/{sum(1 for r in results if r['router_activated'])}")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    run_validation()