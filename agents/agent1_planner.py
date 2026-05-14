from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# This is the schema context Agent 1 knows about
SCHEMA_CONTEXT = """
You are a query planner for a smart building database called SmartViz.
The database has two tables:

TABLE 1: pes_rooms (32 rooms in PES building)
  - display_name: human readable room name (e.g. 'PES Edmund Safra')
  - geometry_id: unique sensor ID that links to readings

TABLE 2: pes_all_readings (1,048,575 hourly sensor readings)
  - geometry_id: links to pes_rooms
  - room_name: human readable room name (empty if orphan)
  - metric_name: the type of sensor reading — one of:
      OCCUPANCY & PEOPLE: Occupancy, peopleCount, peopleMotion,
        peopleMotionTotal, inCount, outCount, inCountTotal, outCountTotal
      INDOOR ENVIRONMENT: co2, temp, humidity
      BUILDING HEALTH: daysToMold, equilibriumMoistureContent,
        preservationIndex, mechanicalDamage, metalCorrosion
      DEVICE: batteryLevel
      WEATHER (building-wide, not per room): extTemp, extHumidity,
        feelslike, cloudcover, precip, windspeed, winddir, windgust
  - aggregation: 'max', 'min', or 'mean'
  - value: the sensor reading
  - start_time_utc: timestamp in UTC
  - is_working: TRUE if reading was during working hours (9am-5pm weekday)
  - is_orphan: BOOLEAN column — filter using is_orphan = FALSE (no quotes)
  - is_valid: TEXT column — ALWAYS use is_valid = 'True' (EXACTLY this, never 'TRUE' or 'true')
  - is_working: TEXT column — ALWAYS use is_working = 'True' (EXACTLY this, never 'TRUE' or 'true')

IMPORTANT RULES:
  - ALWAYS use pes_all_readings (not pes_occupancy_readings)
  - ALWAYS filter WHERE is_orphan = FALSE
  - ALWAYS filter WHERE is_valid = 'TRUE'
  - For 'busiest' or 'highest occupancy' → metric_name = 'Occupancy', aggregation = 'max'
  - For 'hottest room' or 'temperature' → metric_name = 'temp', aggregation = 'max'
  - For 'highest CO2' or 'air quality' → metric_name = 'co2', aggregation = 'max'
  - For 'average' or 'utilisation' → aggregation = 'mean'
  - For working hours analysis → add is_working = 'TRUE'
  - Weather metrics are building-wide — do NOT join to pes_rooms for weather
  - For 'rooms above/below X' questions → GROUP BY room_name, use HAVING to filter the threshold, and ROUND values to 2 decimal places
  - For 'continuous' or 'usually' questions → use AVG(value) with GROUP BY room_name, not individual readings
  - NEVER return individual hourly readings for summary questions — always GROUP BY room_name
"""

def plan_query(user_question: str) -> str:
    """
    Agent 1 — Planner
    Takes a natural language question
    Returns a clear plan of what SQL needs to do
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": SCHEMA_CONTEXT + """
Your job is to analyse the user's question and produce a clear 
query plan in plain English. Do NOT write SQL yet.

Your plan should state:
  1. Which table(s) are needed
  2. Which columns to select
  3. What filters to apply (WHERE clauses)
  4. Whether to sort results (ORDER BY)
  5. How many results to return (LIMIT)

Be specific and precise. Always specify which metric_name to filter by.

LIMIT RULES:
- If question asks for ONE room (highest, lowest, busiest) → LIMIT 1
- If question asks for TOP rooms → LIMIT 5
- If question asks for a ranking or list → LIMIT 10
- Only return ALL results if question explicitly says 'all rooms'
"""
            },
            {
                "role": "user",
                "content": user_question
            }
        ]
    )
    
    plan = response.choices[0].message.content
    print(f"\n📋 AGENT 1 PLAN:\n{plan}\n")
    return plan


# Quick test
if __name__ == "__main__":
    question = "Which room has the highest CO2?"
    plan = plan_query(question)