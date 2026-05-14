from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
import os

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


def get_embedding(text: str) -> list:
    """Get OpenAI embedding for a text string"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


def retrieve_schema(plan: str, top_k: int = 8) -> str:
    """
    Agent 2 — RAG Retrieval
    Takes Agent 1's query plan, converts it to a vector,
    searches pgvector for the most relevant schema elements,
    and returns a focused schema context for Agent 3.
    """

    # Convert the plan to a vector embedding
    plan_embedding = get_embedding(plan)

    # Search pgvector for the closest matching schema descriptions
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT element_type, element_name, description,
               1 - (embedding <=> %s::vector) AS similarity
        FROM schema_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (str(plan_embedding), str(plan_embedding), top_k))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Build the focused schema context from retrieved elements
    print(f"\n🔍 AGENT 2 RAG — Retrieved {len(results)} relevant schema elements:")

    schema_parts = []
    for element_type, element_name, description, similarity in results:
        sim_pct = similarity * 100
        print(f"   [{sim_pct:.1f}%] {element_type}:{element_name}")
        schema_parts.append(f"  - {element_type.upper()} {element_name}: {description}")

    # Assemble the dynamic schema context
    schema_context = """You are a SQL expert for a smart building database called SmartViz.

Based on the retrieved schema information below, write a valid PostgreSQL query.

RETRIEVED SCHEMA (most relevant to this query):
""" + "\n".join(schema_parts) + """

STRICT RULES:
  - ALWAYS use pes_all_readings as the main table
  - ALWAYS include WHERE is_orphan = FALSE (boolean, no quotes)
  - ALWAYS include WHERE is_valid = 'TRUE'
  - ALWAYS alias aggregations (e.g. AVG(value) AS avg_temp)
  - For 'rooms above/below X' use GROUP BY room_name with HAVING
  - Weather metrics are building-wide — do NOT join to pes_rooms for weather
  - For 'latest' or 'right now' use MAX(start_time_utc) subquery, NOT CURRENT_TIMESTAMP
  - Only return valid PostgreSQL SQL
  - Do not include any explanation — SQL only
  - Do not wrap in markdown or backticks
"""

    print(f"   Schema context: {len(schema_context)} chars (vs ~2000 chars if hardcoded)")

    return schema_context


# Quick test
if __name__ == "__main__":
    test_plan = """
    1. Tables needed: pes_all_readings
    2. Columns: room_name, AVG(value) as avg_co2
    3. Filters: is_orphan = FALSE, is_valid = 'TRUE', metric_name = 'co2'
    4. Group by: room_name
    5. Sort: avg_co2 DESC
    6. Limit: 5
    """

    schema = retrieve_schema(test_plan)
    print(f"\n📝 Generated schema context:")
    print(schema)