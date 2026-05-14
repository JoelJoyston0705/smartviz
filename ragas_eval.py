"""
ragas_eval.py - SmartViz RAGAS Supplementary Evaluation
Author: Joel Joyston Cecil Kumar
University of Leicester, 2026
"""

import os
import json
import time
import pickle
from dotenv import load_dotenv
from datasets import Dataset

load_dotenv()

# ── RAGAS IMPORTS ─────────────────────────────────────────────
try:
    from ragas import evaluate
    print("RAGAS imported successfully")
except ImportError as e:
    print("Import error:", e)
    print("Run: pip install ragas datasets langchain-openai")
    exit(1)

# ── AGENT IMPORTS ─────────────────────────────────────────────
from agents.agent2_rag import get_db_connection
from agents.agent1_planner import plan_query

# ── CONTEXT RETRIEVAL ─────────────────────────────────────────
def get_context_for_query(question):
    try:
        from openai import OpenAI
        plan = plan_query(question)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=plan
        )
        plan_embedding = response.data[0].embedding
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT element_type, element_name, description,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM schema_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT 8
        """, (str(plan_embedding), str(plan_embedding)))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        contexts = [
            element_type.upper() + " " + element_name + ": " + description
            for element_type, element_name, description, similarity in results
        ]
        return contexts
    except Exception as e:
        print("  Context retrieval failed:", e)
        return ["Schema context retrieval failed"]


# ── EVALUATION QUERIES ────────────────────────────────────────
EVAL_QUERIES = [
    {"id": "Q01", "question": "Which room has the highest occupancy?"},
    {"id": "Q02", "question": "What is the average CO2 level across all rooms?"},
    {"id": "Q03", "question": "What is the average temperature across all rooms?"},
    {"id": "Q04", "question": "Which room is the least utilised on average?"},
    {"id": "Q05", "question": "What is the average humidity across all rooms?"},
    {"id": "Q06", "question": "Which room had the highest CO2 reading during working hours?"},
    {"id": "Q07", "question": "What are the top 5 most occupied rooms on average?"},
    {"id": "Q08", "question": "Which rooms have an average temperature above 23 degrees?"},
    {"id": "Q09", "question": "Which rooms have the highest preservation index?"},
    {"id": "Q10", "question": "Show me the average occupancy per room during working hours only."},
    {"id": "Q11", "question": "Which sensors have a battery level below 20 percent?"},
    {"id": "Q12", "question": "Show me the daily average CO2 trend across all rooms for the last 7 days of data."},
    {"id": "Q13", "question": "Which rooms had zero occupancy during working hours on more than 10 days?"},
    {"id": "Q14", "question": "Which rooms have the highest metal corrosion risk score?"},
    {"id": "Q15", "question": "What is the average temperature per room for each month in the dataset?"},
]

# ── E1 GROUND TRUTH SQL (GPT-4, EA=100%) ─────────────────────
E1_SQL = {
    "Q01": "SELECT room_name, MAX(value) AS max_occupancy FROM pes_all_readings WHERE is_valid = 'TRUE' AND is_orphan = FALSE AND metric_name = 'Occupancy' AND aggregation = 'max' GROUP BY room_name ORDER BY max_occupancy DESC LIMIT 1;",
    "Q02": "SELECT AVG(value) AS avg_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE'",
    "Q03": "SELECT AVG(value) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' AND aggregation = 'mean';",
    "Q04": "SELECT room_name, AVG(value) AS avg_occupancy FROM pes_all_readings WHERE metric_name = 'Occupancy' AND is_orphan = FALSE AND is_valid = 'TRUE' AND aggregation = 'mean' GROUP BY room_name ORDER BY avg_occupancy LIMIT 1",
    "Q05": "SELECT ROUND(AVG(value)::numeric, 2) AS avg_humidity FROM pes_all_readings WHERE metric_name = 'humidity' AND is_orphan = FALSE AND is_valid = 'TRUE';",
    "Q06": "SELECT room_name, MAX(value) AS max_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name ORDER BY max_co2 DESC LIMIT 1;",
    "Q07": "SELECT p.display_name, ROUND(AVG(r.value)::numeric, 2) AS avg_occupancy FROM pes_all_readings r JOIN pes_rooms p ON p.geometry_id = r.geometry_id WHERE r.is_orphan = FALSE AND r.is_valid = 'TRUE' AND r.metric_name = 'Occupancy' AND r.aggregation = 'mean' GROUP BY p.display_name ORDER BY avg_occupancy DESC LIMIT 5",
    "Q08": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name HAVING AVG(value) > 23;",
    "Q09": "SELECT pes_rooms.display_name, AVG(pes_all_readings.value) AS AvgPreservationIndex FROM pes_rooms JOIN pes_all_readings ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'preservationIndex' GROUP BY pes_rooms.display_name ORDER BY AvgPreservationIndex DESC LIMIT 1;",
    "Q10": "SELECT pr.display_name, ROUND(AVG(par.value)::numeric, 2) AS avg_occupancy FROM pes_all_readings par JOIN pes_rooms pr ON pr.geometry_id = par.geometry_id WHERE par.is_orphan = FALSE AND par.is_valid = 'TRUE' AND par.metric_name = 'Occupancy' GROUP BY pr.display_name",
    "Q11": "SELECT room_name, value as battery_level FROM pes_all_readings WHERE metric_name = 'batteryLevel' AND is_orphan = FALSE AND is_valid = 'TRUE' AND value < 20 GROUP BY room_name, value",
    "Q12": "SELECT room_name, DATE(start_time_utc) AS date, ROUND(AVG(value)::numeric, 2) AS avg_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE' AND start_time_utc >= (SELECT MAX(start_time_utc) FROM pes_all_readings) - INTERVAL '7 days' GROUP BY room_name, DATE(start_time_utc) ORDER BY room_name, DATE(start_time_utc);",
    "Q13": "SELECT room_name, COUNT(DISTINCT DATE(start_time_utc)) AS zero_occupancy_days FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND is_working = 'TRUE' AND metric_name = 'Occupancy' AND value = 0 GROUP BY room_name HAVING COUNT(DISTINCT DATE(start_time_utc)) > 10 ORDER BY zero_occupancy_days DESC;",
    "Q14": "SELECT pes_rooms.display_name, ROUND(AVG(pes_all_readings.value)::numeric, 2) AS avg_corrosion FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.metric_name = 'metalCorrosion' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' GROUP BY pes_rooms.display_name ORDER BY avg_corrosion DESC LIMIT 5;",
    "Q15": "SELECT pes_rooms.display_name, DATE_TRUNC('month', pes_all_readings.start_time_utc) AS month, ROUND(AVG(pes_all_readings.value)::numeric, 2) AS avg_temp FROM pes_all_readings JOIN pes_rooms ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'temp' GROUP BY pes_rooms.display_name, month;",
}

# ── E2 SQLCODER SQL ───────────────────────────────────────────
E2_SQL = {
    "Q01": "SELECT pes_rooms.display_name, MAX(pes_all_readings.value) AS max_occupancy FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'True' AND pes_all_readings.metric_name = 'occupancy' AND pes_all_readings.aggregation = 'max' GROUP BY pes_rooms.display_name ORDER BY max_occupancy DESC LIMIT 1;",
    "Q02": "SELECT AVG(value) AS avg_co2 FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'co2'",
    "Q03": "SELECT room_name, AVG(value) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND aggregation = 'mean' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name;",
    "Q04": "SELECT pes_rooms.display_name, AVG(pes_all_readings.value) AS avg_occupancy FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.metric_name = 'occupancy' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'True' AND pes_all_readings.aggregation = 'mean' GROUP BY pes_rooms.display_name ORDER BY avg_occupancy ASC LIMIT 1;",
    "Q05": "SELECT AVG(value) AS avg_humidity FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'humidity' AND aggregation = 'mean';",
    "Q06": "SELECT pes_rooms.display_name, MAX(pes_all_readings.value) AS max_co2 FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.metric_name = 'co2' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.is_working = 'TRUE' GROUP BY pes_rooms.display_name ORDER BY max_co2 DESC LIMIT 1;",
    "Q07": "SELECT pes_rooms.room_name, AVG(pes_all_readings.value) AS avg_occupancy FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'occupancy' AND aggregation = 'mean' GROUP BY pes_rooms.room_name ORDER BY avg_occupancy DESC LIMIT 5;",
    "Q08": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name HAVING AVG(value) > 23 ORDER BY avg_temp DESC.",
    "Q09": "SELECT pes_all_readings.room_name, AVG(pes_all_readings.value) AS avg_preservation_index FROM pes_all_readings WHERE pes_all_readings.metric_name = 'preservationIndex' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'True' GROUP BY pes_all_readings.room_name ORDER BY avg_preservation_index DESC LIMIT 5;",
    "Q10": "SELECT room_name, AVG(value) AS avg_occupancy FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND is_working = 'TRUE' AND metric_name = 'occupancy' GROUP BY room_name ORDER BY avg_occupancy DESC NULLS LAST;",
    "Q11": "SELECT geometry_id, value FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'True' AND metric_name = 'batteryLevel' HAVING value < 20;",
    "Q12": "SELECT pes_all_readings.room_name, AVG(pes_all_readings.value) AS daily_avg_co2 FROM pes_all_readings WHERE pes_all_readings.metric_name = 'co2' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.start_time_utc >= (SELECT MAX(pes_all_readings.start_time_utc) FROM pes_all_readings WHERE pes_all_readings.metric_name = 'co2' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE') GROUP BY pes_all_readings.room_name, DATE(pes_all_readings.start_time_utc) ORDER BY pes_all_readings.room_name ASC, DATE(pes_all_readings.start_time_utc) DESC;",
    "Q13": "SELECT room_name, start_time_utc, COUNT(*) AS num_days_with_0_occupancy FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'True' AND metric_name = 'occupancy' AND value = 0 AND is_working = 'True' GROUP BY room_name, start_time_utc HAVING COUNT(DISTINCT start_time_utc) > 10 ORDER BY num_days_with_0_occupancy DESC NULLS LAST;",
    "Q14": "SELECT room_name, geometry_id, value FROM pes_all_readings WHERE metric_name = 'metalCorrosion' AND is_orphan = FALSE AND is_valid = 'True' GROUP BY room_name HAVING MAX(value) > 2.5 LIMIT 5;",
    "Q15": "SELECT pes_rooms.display_name, AVG(pes_all_readings.value) AS avg_temp FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'True' AND pes_all_readings.metric_name = 'temp' AND pes_all_readings.aggregation = 'mean' GROUP BY pes_rooms.display_name, EXTRACT(MONTH FROM pes_all_readings.start_time_utc) ORDER BY avg_temp DESC NULLS LAST;",
}

# ── E4 GPT-4 REPEAT SQL ───────────────────────────────────────
E4_SQL = {
    "Q01": "SELECT pes_rooms.display_name, MAX(pes_all_readings.value) AS max_occupancy FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'Occupancy' GROUP BY pes_rooms.display_name ORDER BY max_occupancy DESC LIMIT 1;",
    "Q02": "SELECT AVG(value) AS average_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE'",
    "Q03": "SELECT ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE'",
    "Q04": "SELECT pes_rooms.display_name, AVG(pes_all_readings.value) AS avg_occupancy FROM pes_all_readings JOIN pes_rooms ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.metric_name = 'Occupancy' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' GROUP BY pes_rooms.display_name ORDER BY avg_occupancy ASC LIMIT 1;",
    "Q05": "SELECT AVG(value) AS avg_humidity FROM pes_all_readings WHERE metric_name = 'humidity' AND is_orphan = FALSE AND is_valid = 'TRUE' AND aggregation = 'mean';",
    "Q06": "SELECT pes_all_readings.room_name, pes_rooms.display_name, MAX(value) AS max_co2 FROM pes_all_readings JOIN pes_rooms ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.metric_name = 'co2' AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.aggregation = 'max' GROUP BY pes_all_readings.room_name, pes_rooms.display_name ORDER BY max_co2 DESC LIMIT 1;",
    "Q07": "SELECT room_name, AVG(value) AS avg_occupancy FROM pes_all_readings WHERE metric_name = 'Occupancy' AND is_orphan = FALSE AND is_valid = 'TRUE' AND aggregation = 'mean' GROUP BY room_name ORDER BY avg_occupancy DESC LIMIT 5",
    "Q08": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name HAVING AVG(value) > 23 ORDER BY avg_temp DESC;",
    "Q09": "SELECT pes_all_readings.room_name, ROUND(AVG(pes_all_readings.value)::numeric, 2) AS avg_preservation_index FROM pes_all_readings INNER JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'preservationIndex' GROUP BY pes_all_readings.room_name ORDER BY avg_preservation_index DESC LIMIT 5;",
    "Q10": "SELECT pes_all_readings.room_name, AVG(pes_all_readings.value) AS avg_value FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.metric_name = 'Occupancy' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.aggregation = 'mean' GROUP BY pes_all_readings.room_name LIMIT 10;",
    "Q11": "SELECT room_name FROM pes_all_readings WHERE metric_name = 'batteryLevel' AND is_orphan = FALSE AND is_valid = 'TRUE' AND value < 20 ORDER BY value ASC;",
    "Q12": "SELECT room_name, DATE(start_time_utc) AS date, ROUND(AVG(value)::numeric, 2) AS avg_co2 FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'co2' AND start_time_utc >= (SELECT MAX(start_time_utc) FROM pes_all_readings WHERE metric_name = 'co2') - INTERVAL '7 days' GROUP BY room_name, date ORDER BY date ASC, room_name;",
    "Q13": "SELECT room_name, DATE(start_time_utc) as date FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND is_working = 'TRUE' AND metric_name = 'Occupancy' AND value = 0 GROUP BY room_name, DATE(start_time_utc) HAVING COUNT(*) > 10",
    "Q14": "SELECT pes_rooms.display_name, pes_all_readings.room_name, MAX(pes_all_readings.value) as max_risk_score FROM pes_all_readings JOIN pes_rooms ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.metric_name = 'metalCorrosion' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' GROUP BY pes_rooms.display_name, pes_all_readings.room_name ORDER BY max_risk_score DESC;",
    "Q15": "SELECT room_name, EXTRACT(MONTH FROM start_time_utc) AS month, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name, month ORDER BY room_name, month;",
}

# ── E5 GPT-4 NO RAG SQL ───────────────────────────────────────
E5_SQL = {
    "Q01": "SELECT p1.display_name, p2.room_name, p2.value AS max_occupancy FROM pes_rooms AS p1 INNER JOIN pes_all_readings AS p2 ON p1.geometry_id = p2.geometry_id WHERE p2.is_orphan = FALSE AND p2.is_valid = 'TRUE' AND p2.metric_name = 'Occupancy' AND p2.aggregation = 'max' ORDER BY p2.value DESC LIMIT 1;",
    "Q02": "SELECT AVG(value) AS avg_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE';",
    "Q03": "SELECT AVG(value) AS avg_temp, room_name FROM pes_all_readings INNER JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE metric_name = 'temp' AND aggregation = 'mean' AND is_orphan = FALSE AND is_valid = 'True' GROUP BY room_name;",
    "Q04": "SELECT pes_rooms.display_name, AVG(pes_all_readings.value) AS avg_occupancy FROM pes_rooms INNER JOIN pes_all_readings ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'Occupancy' AND pes_all_readings.aggregation = 'mean' GROUP BY pes_rooms.display_name HAVING AVG(pes_all_readings.value) = (SELECT MIN(avg_occupancy) FROM (SELECT AVG(pes_all_readings.value) AS avg_occupancy FROM pes_all_readings WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'Occupancy' AND pes_all_readings.aggregation = 'mean' GROUP BY pes_all_readings.room_name) sub_query) LIMIT 1;",
    "Q05": "SELECT room_name, AVG(value) AS avg_humidity FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'humidity' GROUP BY room_name;",
    "Q06": "SELECT pr.display_name AS room_name, MAX(par.value) AS max_co2_value FROM pes_rooms pr JOIN pes_all_readings par ON pr.geometry_id = par.geometry_id WHERE par.metric_name = 'co2' AND par.aggregation = 'max' AND par.is_orphan = FALSE AND par.is_valid = 'TRUE' AND par.is_working = 'TRUE' GROUP BY pr.display_name ORDER BY max_co2_value DESC LIMIT 1;",
    "Q07": "SELECT r.display_name, AVG(a.value) AS avg_occupancy FROM pes_rooms r JOIN pes_all_readings a ON r.geometry_id = a.geometry_id WHERE a.is_orphan = FALSE AND a.is_valid = 'TRUE' AND a.metric_name = 'Occupancy' AND a.aggregation = 'mean' GROUP BY r.display_name ORDER BY avg_occupancy DESC LIMIT 5;",
    "Q08": "SELECT pes_rooms.display_name, AVG(pes_all_readings.value) AS avg_temp FROM pes_rooms JOIN pes_all_readings ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.metric_name = 'temp' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' GROUP BY pes_rooms.display_name HAVING AVG(pes_all_readings.value) > 23 ORDER BY avg_temp DESC;",
    "Q09": "SELECT r.display_name AS room, MAX(a.value) AS max_preservation_index FROM pes_rooms r JOIN pes_all_readings a ON r.geometry_id = a.geometry_id WHERE a.is_orphan = FALSE AND a.is_valid = 'TRUE' AND a.metric_name = 'preservationIndex' AND a.aggregation = 'max' GROUP BY r.display_name ORDER BY max_preservation_index DESC LIMIT 5;",
    "Q10": "SELECT pes_all_readings.room_name, ROUND(AVG(pes_all_readings.value), 2) AS avg_occupancy FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'Occupancy' AND pes_all_readings.is_working = 'TRUE' GROUP BY pes_all_readings.room_name;",
    "Q11": "SELECT room_name, AVG(value) AS avg_batteryLevel FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'batteryLevel' GROUP BY room_name HAVING AVG(value) < 20;",
    "Q12": "SELECT DATE(start_time_utc) AS record_date, AVG(value) AS avg_co2 FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'co2' AND start_time_utc >= (CURRENT_DATE - interval '7 days') GROUP BY record_date ORDER BY record_date ASC;",
    "Q13": "SELECT room_name FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.metric_name = 'Occupancy' AND pes_all_readings.value = 0 AND pes_all_readings.is_working = 'True' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' GROUP BY room_name HAVING COUNT(DISTINCT DATE(pes_all_readings.start_time_utc)) > 10 ORDER BY COUNT(DISTINCT DATE(pes_all_readings.start_time_utc)) DESC;",
    "Q14": "SELECT room_name, MAX(value) AS max_metal_corrosion FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'True' AND metric_name = 'metalCorrosion' GROUP BY room_name ORDER BY max_metal_corrosion DESC LIMIT 5",
    "Q15": "SELECT room_name, EXTRACT(MONTH FROM start_time_utc) AS month, AVG(value) AS avg_temp FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'temp' GROUP BY room_name, month;",
}

# ── E6 GPT-4 NO VALIDATOR SQL ─────────────────────────────────
E6_SQL = {
    "Q01": "SELECT pes_rooms.room_name, MAX(pes_all_readings.value) AS max_occupancy FROM pes_all_readings JOIN pes_rooms ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.metric_name = 'Occupancy' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' GROUP BY pes_rooms.room_name ORDER BY max_occupancy DESC LIMIT 1;",
    "Q02": "SELECT ROUND(AVG(value)::numeric, 2) AS avg_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE'",
    "Q03": "SELECT ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE'",
    "Q04": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_occupancy FROM pes_all_readings WHERE metric_name = 'Occupancy' AND is_orphan = FALSE AND is_valid = 'TRUE' AND aggregation = 'mean' GROUP BY room_name ORDER BY avg_occupancy ASC LIMIT 1;",
    "Q05": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_humidity FROM pes_all_readings WHERE metric_name = 'humidity' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name",
    "Q06": "SELECT pes_rooms.room_name AS room_name, MAX(pes_all_readings.value) AS max_co2 FROM pes_all_readings JOIN pes_rooms ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.metric_name = 'co2' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.is_working = 'TRUE' GROUP BY pes_rooms.room_name ORDER BY max_co2 DESC LIMIT 1;",
    "Q07": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_occupancy FROM pes_all_readings WHERE metric_name = 'Occupancy' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name ORDER BY avg_occupancy DESC LIMIT 5;",
    "Q08": "SELECT pes_rooms.room_name, ROUND(AVG(pes_all_readings.value)::numeric, 2) AS avg_temp FROM pes_all_readings JOIN pes_rooms ON pes_rooms.geometry_id = pes_all_readings.geometry_id WHERE pes_all_readings.metric_name = 'temp' AND pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' GROUP BY pes_rooms.room_name HAVING AVG(pes_all_readings.value) > 23;",
    "Q09": "SELECT pes_rooms.display_name, MAX(pes_all_readings.value) AS max_preservation_index FROM pes_all_readings JOIN pes_rooms ON pes_all_readings.geometry_id = pes_rooms.geometry_id WHERE pes_all_readings.is_orphan = FALSE AND pes_all_readings.is_valid = 'TRUE' AND pes_all_readings.metric_name = 'preservationIndex' GROUP BY pes_rooms.display_name ORDER BY max_preservation_index DESC;",
    "Q10": "SELECT pr.display_name as room_display_name, ROUND(AVG(par.value)::numeric, 2) AS avg_occupancy FROM pes_all_readings par JOIN pes_rooms pr ON par.geometry_id = pr.geometry_id WHERE par.metric_name = 'Occupancy' AND par.aggregation = 'mean' AND par.is_orphan = FALSE AND par.is_valid = 'TRUE' AND par.is_working = 'TRUE' GROUP BY pr.display_name ORDER BY avg_occupancy DESC;",
    "Q11": "SELECT geometry_id, room_name FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'batteryLevel' AND value < 20;",
    "Q12": "SELECT DATE(start_time_utc) AS reading_date, room_name, AVG(value) AS avg_daily_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND aggregation = 'mean' AND is_orphan = FALSE AND is_valid = 'TRUE' AND start_time_utc >= (SELECT MAX(start_time_utc) FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE') - INTERVAL '7 days' GROUP BY reading_date, room_name ORDER BY reading_date ASC, room_name ASC",
    "Q13": "SELECT room_name, COUNT(DISTINCT DATE(start_time_utc)) AS days_zero_occupancy FROM pes_all_readings WHERE metric_name = 'Occupancy' AND value = 0 AND is_orphan = FALSE AND is_valid = 'TRUE' AND is_working = 'TRUE' GROUP BY room_name HAVING COUNT(DISTINCT DATE(start_time_utc)) > 10",
    "Q14": "SELECT room_name, AVG(value) AS avg_risk_score FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'metalCorrosion' GROUP BY room_name ORDER BY avg_risk_score DESC LIMIT 5;",
    "Q15": "SELECT room_name, EXTRACT(MONTH FROM start_time_utc) AS month, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name, month ORDER BY room_name, month;",
}
E3_SQL = {
    "Q01": "SELECT r.display_name, MAX(pa.value) AS max_occupancy FROM pes_all_readings pa JOIN pes_rooms r ON pa.geometry_id = r.geometry_id WHERE pa.is_orphan = FALSE AND pa.is_valid = 'TRUE' AND pa.metric_name = 'Occupancy' GROUP BY r.display_name ORDER BY max_occupancy DESC LIMIT 1",
    "Q02": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name",
    "Q03": "SELECT ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE'",
    "Q04": "SELECT room_name, AVG(value) AS avg_occupancy FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'Occupancy' AND aggregation = 'mean' GROUP BY room_name ORDER BY avg_occupancy ASC LIMIT 1",
    "Q05": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_humidity FROM pes_all_readings WHERE metric_name = 'humidity' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name",
    "Q06": "SELECT room_name, MAX(value) AS max_co2 FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'co2' AND aggregation = 'max' GROUP BY room_name ORDER BY max_co2 DESC LIMIT 1",
    "Q07": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_occupancy FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'Occupancy' GROUP BY room_name ORDER BY avg_occupancy DESC LIMIT 5",
    "Q08": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'temp' AND aggregation = 'mean' GROUP BY room_name HAVING AVG(value) > 23 ORDER BY avg_temp DESC;",
    "Q09": "SELECT room_name, value AS preservation_index FROM pes_all_readings WHERE metric_name = 'preservationIndex' AND is_orphan = FALSE AND is_valid = 'TRUE' ORDER BY value DESC LIMIT 1",
    "Q10": "SELECT room_name, AVG(value) AS avg_occupancy FROM pes_all_readings WHERE metric_name = 'Occupancy' AND aggregation = 'mean' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name;",
    "Q11": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name HAVING AVG(value) > 21 ORDER BY avg_temp DESC LIMIT 5",
    "Q12": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_co2 FROM pes_all_readings WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE' GROUP BY room_name ORDER BY start_time_utc",
    "Q13": "SELECT pr.display_name, COUNT(DISTINCT psa.start_time_utc) AS days_with_zero_occupancy FROM pes_rooms AS pr JOIN pes_all_readings AS psa ON pr.display_name = psa.room_name WHERE psa.metric_name = 'Occupancy' AND psa.aggregation = 'min' AND psa.value = 0 AND psa.is_valid = 'TRUE' AND psa.is_orphan = FALSE AND psa.is_working = 'TRUE' GROUP BY pr.display_name HAVING COUNT(DISTINCT psa.start_time_utc) > 10 ORDER BY days_with_zero_occupancy DESC;",
    "Q14": "SELECT r.display_name, ROUND(AVG(p.value)::numeric, 2) AS avg_metal_corrosion FROM pes_all_readings p JOIN pes_rooms r ON p.geometry_id = r.geometry_id WHERE p.metric_name = 'metalCorrosion' AND p.is_orphan = FALSE AND p.is_valid = 'TRUE' GROUP BY r.display_name ORDER BY avg_metal_corrosion DESC LIMIT 10",
    "Q15": "SELECT room_name, ROUND(AVG(value)::numeric, 2) AS avg_temp FROM pes_all_readings WHERE is_orphan = FALSE AND is_valid = 'TRUE' AND metric_name = 'temp' GROUP BY room_name ORDER BY avg_temp DESC;",
}


# ── BUILD DATASET (with caching) ──────────────────────────────
def build_ragas_dataset(experiment_name, sql_dict):
    cache_file = "cache_" + experiment_name.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "").replace("/", "") + ".pkl"

    if os.path.exists(cache_file):
        print("  Loading from cache:", cache_file)
        with open(cache_file, "rb") as cf:
            return pickle.load(cf)

    print("\n" + "="*60)
    print("Building dataset for", experiment_name)
    print("="*60)

    questions, answers, contexts, ground_truths = [], [], [], []

    for q in EVAL_QUERIES:
        qid = q["id"]
        question = q["question"]
        print("\n  Retrieving context for", qid + ":", question[:50] + "...")
        context = get_context_for_query(question)
        print("  Retrieved", len(context), "chunks")
        questions.append(question)
        answers.append(sql_dict.get(qid, ""))
        contexts.append(context)
        ground_truths.append(E1_SQL.get(qid, ""))
        time.sleep(0.5)

    dataset = Dataset.from_dict({
        "user_input": questions,
        "response": answers,
        "retrieved_contexts": contexts,
        "reference": ground_truths,
    })

    with open(cache_file, "wb") as cf:
        pickle.dump(dataset, cf)
    print("\n  Dataset cached to", cache_file)
    return dataset


# ── RUN RAGAS ─────────────────────────────────────────────────
def run_ragas(experiment_name, dataset):
    from ragas import evaluate, EvaluationDataset
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    print("\n" + "="*60)
    print("Running RAGAS for", experiment_name)
    print("="*60)

    llm = LangchainLLMWrapper(ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    ))
    embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(
        model="text-embedding-ada-002",
        api_key=os.getenv("OPENAI_API_KEY")
    ))

    faithfulness.llm = llm
    answer_relevancy.llm = llm
    answer_relevancy.embeddings = embeddings
    context_precision.llm = llm
    context_recall.llm = llm

    eval_dataset = EvaluationDataset.from_hf_dataset(dataset)

    result = evaluate(
        dataset=eval_dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    scores_df = result.to_pandas()
    def get_col(col):
        return round(float(scores_df[col].mean()), 4) if col in scores_df.columns else 0.0
    return {
        "experiment":        experiment_name,
        "faithfulness":      get_col("faithfulness"),
        "answer_relevancy":  get_col("answer_relevancy"),
        "context_precision": get_col("context_precision"),
        "context_recall":    get_col("context_recall"),
    }
if __name__ == "__main__":

    print("\n" + "="*60)
    print("SMARTVIZ RAGAS SUPPLEMENTARY EVALUATION")
    print("E1 (GPT-4) vs E3 (Gemma3)")
    print("="*60)

    all_scores = []

    experiments = [
        ("E1 GPT4 RAG Validator",    "E1 (GPT-4 + RAG + Validator)",         E1_SQL),
        ("E2 SQLCoder RAG Validator", "E2 (SQLCoder + RAG + Validator)",       E2_SQL),
        ("E3 Gemma3 RAG Validator",   "E3 (Gemma3 + RAG + Validator)",         E3_SQL),
        ("E4 GPT4 RAG Validator Rep", "E4 (GPT-4 + RAG + Validator — Repeat)", E4_SQL),
        ("E5 GPT4 NoRAG Validator",   "E5 (GPT-4 + NO RAG + Validator)",       E5_SQL),
        ("E6 GPT4 RAG NoValidator",   "E6 (GPT-4 + RAG + NO Validator)",       E6_SQL),
    ]

    for cache_name, label, sql_dict in experiments:
        print("\n--- " + label)
        ds = build_ragas_dataset(cache_name, sql_dict)
        scores = run_ragas(label, ds)
        all_scores.append(scores)

    print("\n\n" + "="*80)
    print("RAGAS RESULTS — ALL 6 EXPERIMENTS")
    print("="*80)
    print("Experiment                               Faith  Ans.Rel  Ctx.Pre  Ctx.Rec")
    print("-"*80)
    for s in all_scores:
        print(s["experiment"][:40].ljust(40),
              str(s["faithfulness"]).rjust(6),
              str(s["answer_relevancy"]).rjust(8),
              str(s["context_precision"]).rjust(8),
              str(s["context_recall"]).rjust(8))

    print()
    e1 = next(s for s in all_scores if "E1" in s["experiment"])
    e3 = next(s for s in all_scores if "E3" in s["experiment"])
    e5 = next(s for s in all_scores if "E5" in s["experiment"])
    print("Key findings:")
    print("  Faithfulness gap E1 vs E3 (silent hallucination):", round(e1["faithfulness"] - e3["faithfulness"], 4))
    print("  Context recall drop E1 vs E5 (RAG contribution):", round(e1["context_recall"] - e5["context_recall"], 4))
    print("="*80)

    with open("ragas_results.json", "w") as f:
        json.dump({"scores": all_scores}, f, indent=2)
    print("\nResults saved to ragas_results.json")