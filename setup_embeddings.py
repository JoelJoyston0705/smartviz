"""
=============================================================================
Populate pgvector schema_embeddings table
=============================================================================
Run once to embed your database schema descriptions into pgvector.
These embeddings are what Agent 2 (RAG) searches at query time.

Usage:
    cd smartviz_agents
    python setup_embeddings.py
=============================================================================
"""

from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# ── Schema descriptions to embed ──
# Each entry describes one element of your database
# Agent 2 will search these to find relevant schema for each query

SCHEMA_ELEMENTS = [
    # Tables
    {
        "type": "table",
        "name": "pes_all_readings",
        "description": "Main sensor readings table containing 1,048,575 hourly IoT sensor readings from the PES building. Contains all 25 metric types including occupancy, CO2, temperature, humidity, building health, and weather data. Each row is one hourly reading for one room and one metric. Date range: March to June 2025."
    },
    {
        "type": "table",
        "name": "pes_rooms",
        "description": "Room directory table containing 32 named rooms in the PES building at the University of Sheffield. Each row is one room with a human-readable display name like 'PES Seminar Room 9' or 'PES Edmund Safra'. Use this table to get room names when they are not available in pes_all_readings."
    },

    # Join key
    {
        "type": "column",
        "name": "geometry_id",
        "description": "Foreign key that links sensor readings to room names. Present in both pes_all_readings and pes_rooms tables. JOIN pes_all_readings ON pes_rooms.geometry_id = pes_all_readings.geometry_id to get room display names for sensor readings."
    },

    # Key columns in pes_all_readings
    {
        "type": "column",
        "name": "metric_name",
        "description": "The type of sensor measurement. Filter this column to select which metric you want. Values include: Occupancy (people count), co2 (carbon dioxide ppm), temp (temperature celsius), humidity (relative humidity percentage), peopleCount, peopleMotion, inCount, outCount, inCountTotal, outCountTotal, peopleMotionTotal, daysToMold, equilibriumMoistureContent, preservationIndex, mechanicalDamage, metalCorrosion, batteryLevel, extTemp, extHumidity, feelslike, cloudcover, precip, windspeed, winddir, windgust."
    },
    {
        "type": "column",
        "name": "value",
        "description": "The actual numeric sensor reading value. For occupancy this is people count, for co2 this is parts per million, for temp this is degrees celsius, for humidity this is percentage. Use AVG(value), MAX(value), MIN(value) for aggregations. Always alias aggregations like AVG(value) AS avg_temp."
    },
    {
        "type": "column",
        "name": "aggregation",
        "description": "How the hourly value was calculated from raw sensor data. Values are 'max' (maximum in that hour), 'min' (minimum in that hour), or 'mean' (average in that hour). For 'busiest' or 'highest' queries use aggregation = 'max'. For 'average' or 'typical' queries use aggregation = 'mean'. For 'lowest' queries use aggregation = 'min'."
    },
    {
        "type": "column",
        "name": "room_name",
        "description": "Human-readable room name in the sensor readings table, e.g. 'PES Seminar Room 9', 'PES Edmund Safra', 'PES Lecture Theatre 4'. Empty string for orphan sensors that have no matching room. Use room_name != '' to exclude unnamed sensors. This column already contains the room name so you often don't need to JOIN to pes_rooms."
    },
    {
        "type": "column",
        "name": "start_time_utc",
        "description": "Timestamp for when the hourly reading started, in UTC format YYYY-MM-DD HH:MM:SS. Data ranges from 2025-03-01 to 2025-06-06. Use this for time-based filtering. For 'latest' or 'right now' queries use start_time_utc = (SELECT MAX(start_time_utc) FROM pes_all_readings WHERE metric_name = 'relevant_metric'). Never use CURRENT_TIMESTAMP as the data is historical."
    },
    {
        "type": "column",
        "name": "is_working",
        "description": "Text flag indicating whether the reading was during standard working hours (9am-5pm, Monday-Friday). Values are 'TRUE' or 'FALSE'. Filter WHERE is_working = 'TRUE' for working hours analysis, utilisation queries, or questions about 'during office hours'."
    },
    {
        "type": "column",
        "name": "is_orphan",
        "description": "Boolean flag indicating whether the sensor has no matching room in the hierarchy. TRUE means the geometry_id has no room name. ALWAYS filter WHERE is_orphan = FALSE to exclude unidentified sensors. This is a boolean column so use FALSE without quotes."
    },
    {
        "type": "column",
        "name": "is_valid",
        "description": "Text flag indicating whether the sensor reading is trustworthy. Values are 'TRUE' or 'FALSE'. ALWAYS filter WHERE is_valid = 'TRUE' to exclude invalid readings."
    },
    {
        "type": "column",
        "name": "display_name",
        "description": "Human-readable room name in the pes_rooms table, e.g. 'PES Seminar Room 9', 'PES Edmund Safra'. This is the canonical room name. Use when joining pes_rooms to pes_all_readings if room_name column is not sufficient."
    },

    # Metric-specific knowledge
    {
        "type": "metric",
        "name": "Occupancy",
        "description": "People count sensor measuring how many people are in a room. metric_name = 'Occupancy'. Use for questions about busiest rooms, highest occupancy, room utilisation, how many people. Peak value in dataset is 452 (PES Edmund Safra). For busiest room use aggregation = 'max'. For average utilisation use aggregation = 'mean'."
    },
    {
        "type": "metric",
        "name": "co2",
        "description": "Carbon dioxide concentration in parts per million (ppm). metric_name = 'co2'. Use for questions about air quality, CO2 levels, ventilation, stuffiness. Below 800 ppm = good, 800-1000 = acceptable, 1000-1500 = poor with drowsiness risk, above 1500 = hazardous. Peak in dataset is 4452 ppm (PES Seminar Room 3). For worst air quality use aggregation = 'max'. For average CO2 use aggregation = 'mean'."
    },
    {
        "type": "metric",
        "name": "temp",
        "description": "Room temperature in degrees Celsius. metric_name = 'temp'. Use for questions about hottest room, temperature, thermal comfort, overheating. Healthy range is 18-23 degrees. For hottest room use aggregation = 'max'. For average temperature use aggregation = 'mean'. For rooms usually above a threshold use GROUP BY room_name HAVING AVG(value) > threshold."
    },
    {
        "type": "metric",
        "name": "humidity",
        "description": "Relative humidity as a percentage. metric_name = 'humidity'. Use for questions about moisture, humidity levels, dampness. Comfortable range is 40-60%. For humidity analysis use aggregation = 'mean'."
    },
    {
        "type": "metric",
        "name": "weather",
        "description": "External weather metrics are building-wide, NOT per room. Includes extTemp (outside temperature), extHumidity (outside humidity), feelslike (feels-like temperature), cloudcover (percentage), precip (rainfall mm), windspeed (km/h), winddir (degrees), windgust (km/h). Only 1,446 rows total. Do NOT join weather metrics to pes_rooms — they are not room-specific."
    },
    {
        "type": "metric",
        "name": "batteryLevel",
        "description": "Battery level of wireless IoT sensors as a percentage. metric_name = 'batteryLevel'. Use for questions about sensor health, device maintenance, low battery alerts, or sensor reliability. 91,617 rows in the dataset. Helps facility managers identify sensors that need battery replacement before they go offline."
    },
    {
        "type": "metric",
        "name": "daysToMold",
        "description": "Estimated number of days until mold could start growing given current humidity and temperature conditions. metric_name = 'daysToMold'. Use for questions about mold risk, preventative maintenance, building health, or moisture-related issues. Lower values indicate higher mold risk and more urgent maintenance needed. 43,215 rows in the dataset."
    },
    {
        "type": "metric",
        "name": "buildingHealth",
        "description": "Building health metrics include equilibriumMoistureContent (moisture level in building materials — metric_name = 'equilibriumMoistureContent'), preservationIndex (composite score for how well the building preserves its contents — metric_name = 'preservationIndex'), mechanicalDamage (risk score for damage to mechanical systems — metric_name = 'mechanicalDamage'), and metalCorrosion (risk score for metal component corrosion — metric_name = 'metalCorrosion'). Use for questions about structural integrity, building condition, maintenance scheduling, or infrastructure longevity. Each has approximately 43,215 rows."
    },

    # Query patterns
    {
        "type": "pattern",
        "name": "rooms_above_threshold",
        "description": "For questions like 'rooms usually above X degrees' or 'rooms with average CO2 above Y': Use GROUP BY room_name, then HAVING AVG(value) > threshold, ORDER BY AVG(value) DESC. Always use ROUND() for readable output. Example: SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name HAVING AVG(value) > 21 ORDER BY avg_temp DESC."
    },
    {
        "type": "pattern",
        "name": "top_worst_rooms",
        "description": "For questions like 'top 5 worst rooms' or 'worst offending spaces': Use GROUP BY room_name with AVG(value) or MAX(value), ORDER BY DESC, LIMIT N. Always alias aggregations. Example: SELECT room_name, AVG(value) AS avg_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name ORDER BY avg_co2 DESC LIMIT 5."
    },
    {
        "type": "pattern",
        "name": "working_hours_filter",
        "description": "For questions about 'during working hours' or 'office hours' or 'utilisation': Add WHERE is_working = 'TRUE' to filter for 9am-5pm weekday readings only. Combine with other filters like metric_name and is_orphan = FALSE."
    },
]


def get_embedding(text: str) -> list:
    """Get OpenAI embedding for a text string"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


def main():
    print("=" * 60)
    print("Setting up pgvector schema embeddings")
    print("=" * 60)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing embeddings
    cursor.execute("DELETE FROM schema_embeddings")
    conn.commit()
    print(f"\n✅ Cleared existing embeddings")

    # Generate and insert embeddings
    total = len(SCHEMA_ELEMENTS)
    for i, element in enumerate(SCHEMA_ELEMENTS, 1):
        # Combine name and description for richer embedding
        embed_text = f"{element['type']}: {element['name']} — {element['description']}"
        
        print(f"   Embedding {i}/{total}: {element['type']}:{element['name']}...")
        embedding = get_embedding(embed_text)

        cursor.execute(
            """INSERT INTO schema_embeddings (element_type, element_name, description, embedding)
               VALUES (%s, %s, %s, %s)""",
            (element['type'], element['name'], element['description'], str(embedding))
        )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Inserted {total} schema embeddings into pgvector")
    print(f"   Tables: 2")
    print(f"   Columns: {sum(1 for e in SCHEMA_ELEMENTS if e['type'] == 'column')}")
    print(f"   Metrics: {sum(1 for e in SCHEMA_ELEMENTS if e['type'] == 'metric')}")
    print(f"   Patterns: {sum(1 for e in SCHEMA_ELEMENTS if e['type'] == 'pattern')}")

    # Verify
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM schema_embeddings")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f"\n✅ Verified: {count} rows in schema_embeddings")
    print(f"\nDone! Agent 2 can now search these embeddings.")


if __name__ == "__main__":
    main()