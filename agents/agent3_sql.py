from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
import ollama
import os

# ── FUNCTION ROUTER (new) ─────────────────────────────────────
from agents.agent_function_router import route_query_plan, get_router_status
# ─────────────────────────────────────────────────────────────

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db_connection():
    """Connect to PostgreSQL smartviz database"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


# ─────────────────────────────────────────────
# GPT-4 BACKEND (original)
# ─────────────────────────────────────────────
def _generate_sql_gpt4(plan: str, schema_context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": schema_context + """
Based on the query plan provided, write a single valid PostgreSQL 
SQL query. Return SQL only — no explanation, no markdown, no backticks.
"""
            },
            {
                "role": "user",
                "content": f"Query plan:\n{plan}"
            }
        ]
    )
    return response.choices[0].message.content.strip()


# ─────────────────────────────────────────────
# SQLCODER BACKEND (local via Ollama)
# ─────────────────────────────────────────────
def _build_sqlcoder_prompt(plan: str, schema_context: str) -> str:
    return f"""<|im_start|>system
Your task is to convert a query plan into a SQL query, given a Postgres database schema.
Adhere to these rules:
- Use Table Aliases to prevent ambiguity
- When creating a ratio, always cast the numerator as float
- Only output the SQL query, nothing else — no explanation, no markdown, no backticks
<|im_end|>
<|im_start|>user
DDL and rules:
{schema_context}

Query plan:
{plan}
<|im_end|>
<|im_start|>assistant
SELECT"""


def _generate_sql_sqlcoder(plan: str, schema_context: str) -> str:
    response = ollama.generate(
        model="sqlcoder",
        prompt=_build_sqlcoder_prompt(plan, schema_context),
        options={
            "temperature": 0,
            "stop": ["<|im_end|>", "###"],
            "num_predict": 300,
        }
    )
    return "SELECT " + response["response"].strip()


# ─────────────────────────────────────────────
# GEMMA3 BACKEND (local via Ollama)
# Google's open-weight general-purpose model
# ─────────────────────────────────────────────
def _build_gemma3_prompt(plan: str, schema_context: str) -> str:
    return f"""<start_of_turn>user
You are a PostgreSQL expert. Convert the query plan below into a single valid SQL query.

Rules:
- Return SQL only — no explanation, no markdown, no backticks
- Use table aliases to prevent ambiguity
- Only use tables and columns described in the schema

Schema and rules:
{schema_context}

Query plan:
{plan}
<end_of_turn>
<start_of_turn>model
SELECT"""


def _generate_sql_gemma3(plan: str, schema_context: str) -> str:
    response = ollama.generate(
        model="gemma3",
        prompt=_build_gemma3_prompt(plan, schema_context),
        options={
            "temperature": 0,
            "stop": ["<end_of_turn>", "<start_of_turn>"],
            "num_predict": 300,
        }
    )
    raw = response["response"].strip()

    # Strip accidental markdown fences Gemma3 sometimes adds
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.lower().startswith("sql"):
            raw = raw[3:]
        raw = raw.strip()

    # Gemma3 sometimes echoes the SELECT prefix from the prompt — strip it
    if raw.upper().startswith("SELECT"):
        return raw
    return "SELECT " + raw


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────
def generate_sql(plan: str, schema_context: str = None, model: str = "gpt4") -> str:
    """
    Agent 3 — SQL Generator
    Takes Agent 1's plan and Agent 2's schema context
    Returns executable PostgreSQL SQL

    Args:
        plan:           Query plan from Agent 1
        schema_context: Schema + rules from Agent 2 (falls back to FALLBACK_SCHEMA)
        model:          "gpt4" | "sqlcoder" | "gemma3"

    Evaluation experiments:
        E1 / E4  →  model="gpt4"      (baseline + consistency check)
        E2       →  model="sqlcoder"  (domain-specific local model)
        E3       →  model="gemma3"    (general-purpose local model, Google open-weight)
        E5       →  model="gpt4"      (no RAG — controlled in agent2)
        E6       →  model="gpt4"      (no Validator — controlled in agent4)

    Function Router:
        Sits between Agent 2 and Agent 3. Deterministically resolves
        high-risk metric mappings before the LLM sees the plan.
        Prevents silent hallucination class found in E3 (Gemma3).
        Zero impact on pipeline if metric is low-risk or unrecognised.
    """

    if schema_context is None:
        schema_context = FALLBACK_SCHEMA

    # ── FUNCTION ROUTER ──────────────────────────────────────
    # Intercepts high-risk metric queries and injects deterministic
    # metric resolution before the LLM generates SQL.
    # No effect on low-risk metrics — plan passes through unchanged.
    enriched_plan = route_query_plan(plan, schema_context)
    router_status = get_router_status(plan)
    # ─────────────────────────────────────────────────────────

    if model == "gpt4":
        sql = _generate_sql_gpt4(enriched_plan, schema_context)
    elif model == "sqlcoder":
        sql = _generate_sql_sqlcoder(enriched_plan, schema_context)
    elif model == "gemma3":
        sql = _generate_sql_gemma3(enriched_plan, schema_context)
    else:
        raise ValueError(
            f"Unknown model: '{model}'. Choose from: 'gpt4', 'sqlcoder', 'gemma3'"
        )

    print(f"\n🔀 ROUTER STATUS: {router_status['message']}")
    print(f"\n🔧 AGENT 3 SQL [{model.upper()}]:\n{sql}\n")
    return sql


# ─────────────────────────────────────────────
# ROUTER STATUS ACCESSOR
# For use by app.py / Streamlit Developer Mode
# ─────────────────────────────────────────────
def get_last_router_status(plan: str) -> dict:
    """
    Returns router status dict for a given plan.
    Call this from app.py to display router status in Developer Mode.

    Usage in app.py:
        from agent3_sql import get_last_router_status
        status = get_last_router_status(plan)
        if status["activated"]:
            st.warning(f"🔀 Function Router: {status['message']}")
        else:
            st.info(f"🔀 Function Router: {status['message']}")
    """
    return get_router_status(plan)


# Fallback schema (used only if Agent 2 is not available)
FALLBACK_SCHEMA = """
You are a SQL expert for a smart building database called SmartViz.

TABLE 1: pes_rooms (32 rooms in PES building)
  - display_name: human readable room name (e.g. 'PES Edmund Safra')
  - geometry_id: unique sensor ID (join key to readings)

TABLE 2: pes_all_readings (1,048,575 hourly sensor readings)
  - geometry_id: links to pes_rooms via JOIN
  - room_name: human readable room name (empty if orphan)
  - metric_name: one of — Occupancy, co2, temp, humidity,
      peopleCount, peopleMotion, peopleMotionTotal,
      inCount, outCount, inCountTotal, outCountTotal,
      daysToMold, equilibriumMoistureContent, preservationIndex,
      mechanicalDamage, metalCorrosion, batteryLevel,
      extTemp, extHumidity, feelslike, cloudcover,
      precip, windspeed, winddir, windgust
  - aggregation: 'max', 'min', or 'mean'
  - value: the sensor reading
  - start_time_utc: timestamp (YYYY-MM-DD HH:MM:SS)
  - end_time_utc: end of hour window
  - is_working: TEXT — 'True' = working hours (9am-5pm weekday)
  - is_orphan: BOOLEAN — filter using is_orphan = FALSE (no quotes)
  - is_valid: TEXT — filter using is_valid = 'TRUE'
  - is_holiday: TEXT — 'TRUE' on bank holidays

STRICT RULES:
  - ALWAYS use pes_all_readings (not pes_occupancy_readings)
  - ALWAYS include WHERE is_orphan = FALSE
  - ALWAYS include WHERE is_valid = 'TRUE'
  - ALWAYS alias aggregations (e.g. AVG(value) AS avg_temp)
  - For 'rooms above/below X' use GROUP BY room_name with HAVING
  - Weather metrics are building-wide — do NOT join to pes_rooms for weather
  - For 'latest' or 'right now' use MAX(start_time_utc), NOT CURRENT_TIMESTAMP
  - Only return valid PostgreSQL SQL
  - Do not include any explanation — SQL only
  - Do not wrap in markdown or backticks
"""


# ─────────────────────────────────────────────
# QUICK TEST — compare all three models
# ─────────────────────────────────────────────
if __name__ == "__main__":

    # Test 1 — LOW RISK query (router passes through)
    test_plan_low = """
    1. Tables needed: pes_all_readings
    2. Columns: room_name, value
    3. Filters: is_orphan = FALSE, is_valid = 'TRUE',
       aggregation = 'max', metric_name = 'co2'
    4. Sort: value DESC
    5. Limit: 1
    """

    # Test 2 — HIGH RISK query (router injects annotation)
    test_plan_high = """
    1. Tables needed: pes_all_readings, pes_rooms
    2. Metric: battery level for all rooms
    3. Aggregation: mean
    4. Filters: is_orphan = FALSE, is_valid = 'TRUE'
    5. Output: room_name, average battery level
    6. Sort: average battery level ASC
    """

    print("=" * 60)
    print("TEST 1 — LOW RISK (CO2) — Router should pass through")
    print("=" * 60)
    sql = generate_sql(test_plan_low, model="gpt4")

    print("=" * 60)
    print("TEST 2 — HIGH RISK (Battery) — Router should activate")
    print("=" * 60)
    sql = generate_sql(test_plan_high, model="gpt4")