from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_RETRIES = 3

def get_db_connection():
    """Connect to PostgreSQL smartviz database"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


VALIDATOR_CONTEXT = """
You are a PostgreSQL SQL validator and fixer for a smart building database called SmartViz.

Your job: You receive a SQL query that FAILED with an error. 
Fix the SQL and return ONLY the corrected query.

DATABASE FACTS:
  - Table: pes_all_readings (1,048,575 rows)
    Columns: id, frequency, metric_name, aggregation, value, geometry_id,
             is_holiday, is_valid, is_working, portfolio_id, data_source_id,
             start_time_utc, end_time_utc, is_orphan, room_name
  - Table: pes_rooms (32 rows)
    Columns: id, name, display_name, hierarchy_type, parent, geometry_id,
             portfolio_name, parent_id, portfolio_id
  - Join key: geometry_id in both tables
  - is_orphan is BOOLEAN (use TRUE/FALSE without quotes)
  - is_valid and is_working are TEXT (use 'True'/'False' with quotes)
  - metric_name values: Occupancy, co2, temp, humidity, peopleCount,
    peopleMotion, batteryLevel, etc.
  - Data date range: 2025-03-01 to 2025-06-06 (no CURRENT_TIMESTAMP)
  - For "right now" or "latest" questions, use:
    start_time_utc = (SELECT MAX(start_time_utc) FROM pes_all_readings WHERE metric_name = '<relevant_metric>')

COMMON FIXES:
  - 'TRUE' should be 'True' for is_valid and is_working
  - TRUE (no quotes) for is_orphan
  - CURRENT_TIMESTAMP won't match any data — use MAX(start_time_utc) instead
  - Column doesn't exist — check the column list above
  - room_name = '' for orphans, use room_name != '' to exclude

RULES:
  - Return ONLY the fixed SQL query
  - No explanation, no markdown, no backticks
  - Must be valid PostgreSQL
"""


def validate_and_execute(sql: str, original_question: str = "") -> tuple:
    """
    Agent 4 — Validator
    Tries to execute SQL. If it fails, uses LLM to fix it.
    Retries up to MAX_RETRIES times.
    Returns (col_names, results, final_sql, attempts)
    """
    current_sql = sql
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(current_sql)
            results = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            cursor.close()
            conn.close()

            # Check for empty results
            if len(results) == 0 and attempt < MAX_RETRIES:
                print(f"\n⚠️  VALIDATOR (attempt {attempt}): Query returned 0 rows")
                print(f"    Asking LLM to fix...")

                current_sql = fix_sql(
                    current_sql,
                    "Query executed successfully but returned 0 rows. "
                    "This likely means a filter is too restrictive. "
                    "Common issues: is_valid = 'TRUE' should be 'True', "
                    "CURRENT_TIMESTAMP should be MAX(start_time_utc), "
                    "or is_orphan = 'FALSE' should be is_orphan = FALSE (boolean).",
                    original_question
                )
                continue

            if attempt > 1:
                print(f"\n✅ VALIDATOR: Fixed on attempt {attempt}")
            else:
                print(f"\n✅ VALIDATOR: SQL passed on first attempt")

            return col_names, results, current_sql, attempt

        except Exception as e:
            error_msg = str(e).strip()
            print(f"\n❌ VALIDATOR (attempt {attempt}): SQL failed")
            print(f"    Error: {error_msg}")

            if attempt < MAX_RETRIES:
                print(f"    Asking LLM to fix...")
                current_sql = fix_sql(current_sql, error_msg, original_question)
            else:
                print(f"\n🚨 VALIDATOR: Failed after {MAX_RETRIES} attempts")
                return [], [], current_sql, attempt

    return [], [], current_sql, MAX_RETRIES


def fix_sql(failed_sql: str, error_message: str, original_question: str = "") -> str:
    """
    Uses LLM to fix a failed SQL query based on the error message.
    """
    prompt = f"""The following SQL query failed.

ORIGINAL USER QUESTION: {original_question}

FAILED SQL:
{failed_sql}

ERROR MESSAGE:
{error_message}

Fix the SQL query. Return ONLY the corrected SQL — no explanation."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": VALIDATOR_CONTEXT},
            {"role": "user", "content": prompt}
        ]
    )

    fixed_sql = response.choices[0].message.content.strip()
    
    # Clean up any markdown formatting the LLM might add
    if fixed_sql.startswith("```"):
        fixed_sql = fixed_sql.split("\n", 1)[-1]
    if fixed_sql.endswith("```"):
        fixed_sql = fixed_sql.rsplit("```", 1)[0]
    fixed_sql = fixed_sql.strip()

    print(f"\n🔧 VALIDATOR fixed SQL:\n{fixed_sql}\n")
    return fixed_sql


# Quick test
if __name__ == "__main__":
    # Test 1: SQL that will fail (wrong column name)
    print("=" * 50)
    print("TEST 1: Bad column name")
    print("=" * 50)
    bad_sql = """
    SELECT room_name, occupancy_level 
    FROM pes_all_readings 
    WHERE metric_name = 'Occupancy' 
    ORDER BY occupancy_level DESC LIMIT 1;
    """
    cols, results, final_sql, attempts = validate_and_execute(
        bad_sql, "Which room has the highest occupancy?"
    )
    if results:
        print(f"\n📊 RESULTS (fixed in {attempts} attempts):")
        for row in results:
            for col, val in zip(cols, row):
                print(f"   {col}: {val}")

    # Test 2: SQL that will return 0 rows (CURRENT_TIMESTAMP)
    print("\n" + "=" * 50)
    print("TEST 2: CURRENT_TIMESTAMP (will return 0 rows)")
    print("=" * 50)
    empty_sql = """
    SELECT room_name, value 
    FROM pes_all_readings 
    WHERE metric_name = 'temp' 
    AND aggregation = 'max' 
    AND is_orphan = FALSE 
    AND is_valid = 'TRUE'
    AND start_time_utc = CURRENT_TIMESTAMP
    ORDER BY value DESC LIMIT 1;
    """
    cols, results, final_sql, attempts = validate_and_execute(
        empty_sql, "Hottest room right now?"
    )
    if results:
        print(f"\n📊 RESULTS (fixed in {attempts} attempts):")
        for row in results:
            for col, val in zip(cols, row):
                print(f"   {col}: {val}")