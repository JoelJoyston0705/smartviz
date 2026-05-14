"""
test_sqlcoder.py
Quick test to verify SQLCoder (defog/sqlcoder-7b-2) is working correctly
via Ollama with a structured prompt.

Usage:
    python test_sqlcoder.py

Requirements:
    pip install ollama
    ollama pull sqlcoder
"""

import ollama

# ─────────────────────────────────────────────
# STEP 1: Define your schema
# TODO: Replace with your actual SmartViz table name and columns
# ─────────────────────────────────────────────
SCHEMA = """
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    room_id VARCHAR(50),
    building_id VARCHAR(50),
    temperature FLOAT,          -- degrees Celsius
    humidity FLOAT,             -- percentage
    co2 FLOAT,                  -- ppm
    occupancy INTEGER,          -- number of people
    battery_level FLOAT,        -- sensor battery %
    days_to_mold FLOAT,         -- predicted days until mold risk
    building_health FLOAT       -- overall building health score
);
"""

# ─────────────────────────────────────────────
# STEP 2: The exact prompt format SQLCoder expects
# defog/sqlcoder-7b-2 uses a specific chat template:
# <|im_start|>system ... <|im_end|><|im_start|>user ... <|im_end|><|im_start|>assistant
# ─────────────────────────────────────────────
def build_prompt(question: str) -> str:
    return f"""<|im_start|>system
Your task is to convert a question into a SQL query, given a Postgres database schema.
Adhere to these rules:
- Deliberately go through the question and database schema word by word to appropriately answer the question
- Use Table Aliases to prevent ambiguity
- When creating a ratio, always cast the numerator as float
- Only output the SQL query, nothing else
<|im_end|>
<|im_start|>user
Generate a SQL query that answers the question: {question}

DDL statements:
{SCHEMA}
<|im_end|>
<|im_start|>assistant
SELECT"""

# ─────────────────────────────────────────────
# STEP 3: Call SQLCoder via Ollama
# ─────────────────────────────────────────────
def ask_sqlcoder(question: str) -> str:
    print(f"\n🔍 Question: {question}")
    print("⏳ Asking SQLCoder...\n")

    response = ollama.generate(
        model="sqlcoder",
        prompt=build_prompt(question),
        options={
            "temperature": 0,       # deterministic output
            "stop": ["###", ";"],   # stop after first SQL statement
            "num_predict": 200,     # max tokens to generate
        }
    )

    sql = "SELECT " + response["response"].strip()
    print(f"✅ Generated SQL:\n{sql}\n")
    return sql


# ─────────────────────────────────────────────
# STEP 4: Test questions
# ─────────────────────────────────────────────
if __name__ == "__main__":
    test_questions = [
        "What is the average temperature across all rooms?",
        "Which room has the highest CO2 level right now?",
        "Show me the occupancy for each building over the last 7 days.",
        "Which rooms have a building health score below 50?",
    ]

    results = []
    for q in test_questions:
        sql = ask_sqlcoder(q)
        results.append({"question": q, "sql": sql})

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in results:
        print(f"\nQ: {r['question']}")
        print(f"SQL: {r['sql']}")