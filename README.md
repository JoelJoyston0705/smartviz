# SmartViz

A 5-agent LLM pipeline for natural language querying of real IoT
sensor data from a smart building.

**MSc AI for Business Intelligence — University of Leicester (2026)**  
**Industry Partner:** SmartViz Ltd, London  
**Academic Supervisor:** Prof. Paul Ledger  
**Industry Supervisor:** Vishal Sharma

---

## Key Research Finding

Gemma3 4B achieved **100% Execution Accuracy** yet only **46.7%
Semantic Accuracy** through silent metric substitution — returning
temperature data for a battery level query with no error signal.  
Undetectable by the Validator or RAGAS Faithfulness alone.  
Resolved by a deterministic function routing layer.

---

## System Architecture

User Question (Streamlit)
↓
Agent 1 — Query Planner (GPT-4)
↓
Agent 2 — RAG Retrieval (pgvector, text-embedding-ada-002, 24 embeddings)
↓
Function Router — 25 metrics, 74 aliases, 7 high-risk flags (deterministic)
↓
Agent 3 — SQL Generator (GPT-4 / SQLCoder / Gemma3 — interchangeable)
↓
Agent 4 — Validator (deterministic retry loop, max 3 attempts)
↓
Agent 5 — Graph Builder (GPT-4 + matplotlib)
↓
Chart or text answer (Streamlit)

---

## Evaluation Results

| Experiment | Configuration                      | EA (%) | SA (%) |
| ---------- | ---------------------------------- | ------ | ------ |
| E1         | GPT-4 + RAG + Validator (baseline) | 100.0  | 80.0   |
| E2         | SQLCoder + RAG + Validator         | 93.3   | 60.0   |
| E3         | Gemma3 + RAG + Validator           | 100.0  | 46.7   |
| E4         | GPT-4 + RAG + Validator (repeat)   | 100.0  | 73.3   |
| E5         | GPT-4 + No RAG + Validator         | 100.0  | 80.0   |
| E6         | GPT-4 + RAG + No Validator         | 80.0   | 60.0   |

90 total query executions across 6 experiments.  
15 queries per experiment spanning Easy, Medium, and Hard complexity.

---

## Dataset

- **Source:** PES Building, University of Sheffield
- **Rows:** 1,048,575 sensor readings (= 2²⁰ − 1)
- **Rooms:** 32 instrumented rooms
- **Metrics:** 25 sensor types (occupancy, CO2, temperature, battery, building health, weather)
- **Date range:** March–June 2025
- **Schema:** Entity-Attribute-Value (EAV) — all metrics share one metric_name column

---

## Database Setup

The system requires a local PostgreSQL database with the pgvector extension.

**Tables:**

- `pes_rooms` — 32 rooms in the PES Building (display_name, geometry_id)
- `pes_all_readings` — 1,048,575 sensor readings (EAV schema, 25 metrics)
- `schema_embeddings` — 23 vector embeddings for RAG retrieval (created by setup_embeddings.py)

**Setup steps:**

```bash
# 1. Create database
createdb smartviz

# 2. Enable pgvector
psql -d smartviz -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 3. Load your sensor data into pes_rooms and pes_all_readings

# 4. Generate schema embeddings
python setup_embeddings.py
```

**Note:** The PES Building dataset cannot be shared publicly as it contains real occupancy and environmental data from the University of Sheffield. The `.env.example` file shows the required connection variables.

## Installation

```bash
git clone https://github.com/JoelJoyston0705/smartviz.git
cd smartviz
pip install -r requirements.txt
cp .env.example .env  # add your OpenAI API key and DB credentials
streamlit run app_router.py
```

**Requirements:**

- Python 3.10+
- PostgreSQL 18.2 with pgvector extension
- Ollama (for SQLCoder and Gemma3 local inference)
- OpenAI API key (for GPT-4 and text-embedding-ada-002)

---

## Project Structure

smartviz/
├── agents/
│ ├── agent1_planner.py # Query Planner (GPT-4)
│ ├── agent2_rag.py # RAG Retrieval (pgvector)
│ ├── agent3_sql.py # SQL Generator (multi-model)
│ ├── agent4_validator.py # Execution Validator
│ ├── agent5_graph.py # Graph Builder (matplotlib)
│ └── agent_function_router.py # Deterministic metric routing
├── setup_embeddings.py # pgvector schema embedding setup
├── ragas_eval.py # RAGAS supplementary evaluation
├── app_router.py # Streamlit multi-page controller
├── landing.py # Landing page
├── login.py # Login page
├── signup.py # Signup page
└── main_app.py # Main chat interface

---

## Author

**Joel Joyston Cecil Kumar**  
Portfolio: https://joel-joyston-portfolio.vercel.app  
LinkedIn: https://linkedin.com/in/joeljoyston
