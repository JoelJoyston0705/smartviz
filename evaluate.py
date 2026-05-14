"""
SmartViz Evaluation Harness
============================
Runs 15 test queries × 6 experiments = 90 executions
Saves results to evaluation_results.csv for Chapter 5

Experiments:
  E1  GPT-4    + RAG + Validator        (baseline)
  E2  SQLCoder + RAG + Validator        (local domain-specific)
  E3  Gemma3   + RAG + Validator        (local general-purpose)
  E4  GPT-4    + RAG + Validator        (consistency repeat)
  E5  GPT-4    + NO RAG + Validator     (ablation — RQ2)
  E6  GPT-4    + RAG + NO Validator     (ablation — RQ3)

Metrics per query:
  EA   Execution Accuracy   — did SQL execute + return rows? (1/0)
  SA   Semantic Accuracy    — did result answer the question? (1/0, manual)
  ARC  Avg Retry Count      — how many validator attempts?
  AL   Avg Latency (s)      — wall-clock end-to-end
  ERR  Empty Result Rate    — zero rows returned? (1/0)
  CPQ  Cost Per Query (USD) — OpenAI token cost (0 for local models)

Usage:
  python evaluate.py                    # run all 6 experiments
  python evaluate.py --exp E1           # run single experiment
  python evaluate.py --exp E2 --dry-run # print queries without running
"""

import os
import sys
import csv
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent1_planner import plan_query
from agents.agent2_rag import retrieve_schema
from agents.agent3_sql import generate_sql, FALLBACK_SCHEMA
from agents.agent4_validator import validate_and_execute

# ─────────────────────────────────────────────────────────────────
# GPT-4 pricing (as of 2025) — update if rates change
# ─────────────────────────────────────────────────────────────────
GPT4_INPUT_COST_PER_1K  = 0.03   # USD per 1K input tokens
GPT4_OUTPUT_COST_PER_1K = 0.06   # USD per 1K output tokens
AVG_INPUT_TOKENS        = 600    # estimated per pipeline run
AVG_OUTPUT_TOKENS       = 150    # estimated per pipeline run
GPT4_CPQ = (AVG_INPUT_TOKENS / 1000 * GPT4_INPUT_COST_PER_1K) + \
           (AVG_OUTPUT_TOKENS / 1000 * GPT4_OUTPUT_COST_PER_1K)


# ─────────────────────────────────────────────────────────────────
# 15 TEST QUERIES — cover all metric categories + complexity levels
# ─────────────────────────────────────────────────────────────────
TEST_QUERIES = [
    # ── EASY (5) — single filter, single metric ──────────────────
    {
        "id": "Q01",
        "difficulty": "Easy",
        "category": "Occupancy",
        "question": "Which room has the highest occupancy?",
    },
    {
        "id": "Q02",
        "difficulty": "Easy",
        "category": "CO2",
        "question": "What is the average CO2 level across all rooms?",
    },
    {
        "id": "Q03",
        "difficulty": "Easy",
        "category": "Temperature",
        "question": "What is the average temperature across all rooms?",
    },
    {
        "id": "Q04",
        "difficulty": "Easy",
        "category": "Occupancy",
        "question": "Which room is the least utilised on average?",
    },
    {
        "id": "Q05",
        "difficulty": "Easy",
        "category": "Humidity",
        "question": "What is the average humidity across all rooms?",
    },

    # ── MEDIUM (6) — multi-filter or multi-column ─────────────────
    {
        "id": "Q06",
        "difficulty": "Medium",
        "category": "CO2",
        "question": "Which room had the highest CO2 reading during working hours?",
    },
    {
        "id": "Q07",
        "difficulty": "Medium",
        "category": "Occupancy",
        "question": "What are the top 5 most occupied rooms on average?",
    },
    {
        "id": "Q08",
        "difficulty": "Medium",
        "category": "Temperature",
        "question": "Which rooms have an average temperature above 23 degrees?",
    },
    {
        "id": "Q09",
        "difficulty": "Medium",
        "category": "Building Health",
        "question": "Which rooms have the highest preservation index?",
    },
    {
        "id": "Q10",
        "difficulty": "Medium",
        "category": "Occupancy",
        "question": "Show me the average occupancy per room during working hours only.",
    },
    {
        "id": "Q11",
        "difficulty": "Medium",
        "category": "Device Health",
        "question": "Which sensors have a battery level below 20 percent?",
    },

    # ── HARD (4) — temporal, multi-metric, edge case ─────────────
    {
        "id": "Q12",
        "difficulty": "Hard",
        "category": "CO2",
        "question": "Show me the daily average CO2 trend across all rooms for the last 7 days of data.",
    },
    {
        "id": "Q13",
        "difficulty": "Hard",
        "category": "Occupancy",
        "question": "Which rooms had zero occupancy during working hours on more than 10 days?",
    },
    {
        "id": "Q14",
        "difficulty": "Hard",
        "category": "Building Health",
        "question": "Which rooms have the highest metal corrosion risk score?",
    },
    {
        "id": "Q15",
        "difficulty": "Hard",
        "category": "Temperature",
        "question": "What is the average temperature per room for each month in the dataset?",
    },
]


# ─────────────────────────────────────────────────────────────────
# EXPERIMENT CONFIGURATIONS
# ─────────────────────────────────────────────────────────────────
EXPERIMENTS = {
    "E1": {"model": "gpt4",     "use_rag": True,  "use_validator": True,  "label": "GPT-4 + RAG + Validator (baseline)"},
    "E2": {"model": "sqlcoder", "use_rag": True,  "use_validator": True,  "label": "SQLCoder + RAG + Validator"},
    "E3": {"model": "gemma3",   "use_rag": True,  "use_validator": True,  "label": "Gemma3 + RAG + Validator"},
    "E4": {"model": "gpt4",     "use_rag": True,  "use_validator": True,  "label": "GPT-4 + RAG + Validator (consistency)"},
    "E5": {"model": "gpt4",     "use_rag": False, "use_validator": True,  "label": "GPT-4 + NO RAG + Validator (ablation RQ2)"},
    "E6": {"model": "gpt4",     "use_rag": True,  "use_validator": False, "label": "GPT-4 + RAG + NO Validator (ablation RQ3)"},
}


# ─────────────────────────────────────────────────────────────────
# SINGLE QUERY RUNNER
# ─────────────────────────────────────────────────────────────────
def run_single(question: str, model: str, use_rag: bool, use_validator: bool) -> dict:
    """
    Run one query through the pipeline and return metrics.
    Returns a dict with: ea, err, arc, latency, sql, error_msg
    """
    start = time.time()
    result = {
        "ea":        0,
        "err":       0,
        "arc":       0,
        "latency":   0.0,
        "sql":       "",
        "error_msg": "",
        "rows":      0,
    }

    try:
        # Agent 1 — always runs
        plan = plan_query(question)

        # Agent 2 — RAG or fallback static schema
        if use_rag:
            schema_context = retrieve_schema(plan)
        else:
            schema_context = FALLBACK_SCHEMA

        # Agent 3 — SQL generation
        sql = generate_sql(plan, schema_context, model=model)
        result["sql"] = sql

        if not sql.strip().upper().startswith(("SELECT", "WITH")):
            result["error_msg"] = "Agent 3 did not return valid SQL"
            result["latency"] = round(time.time() - start, 2)
            return result

        # Agent 4 — Validator or direct execute
        if use_validator:
            cols, rows, final_sql, attempts = validate_and_execute(sql, question)
            result["arc"] = attempts - 1  # retries = attempts - 1
        else:
            # No validator — execute directly, catch errors
            import psycopg2
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            cur = conn.cursor()
            cur.execute(sql)
            cols = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            conn.close()
            attempts = 1
            result["arc"] = 0

        result["latency"] = round(time.time() - start, 2)

        if rows:
            result["ea"]   = 1
            result["err"]  = 0
            result["rows"] = len(rows)
        else:
            result["ea"]   = 0
            result["err"]  = 1  # empty result = ERR

    except Exception as e:
        result["error_msg"] = str(e)[:200]
        result["latency"]   = round(time.time() - start, 2)

    return result


# ─────────────────────────────────────────────────────────────────
# EXPERIMENT RUNNER
# ─────────────────────────────────────────────────────────────────
def run_experiment(exp_id: str, config: dict, dry_run: bool = False) -> list:
    """Run all 15 queries for one experiment. Returns list of result rows."""
    print(f"\n{'='*65}")
    print(f"  {exp_id}: {config['label']}")
    print(f"{'='*65}")

    rows = []
    model         = config["model"]
    use_rag       = config["use_rag"]
    use_validator = config["use_validator"]
    cpq           = GPT4_CPQ if model == "gpt4" else 0.0

    for q in TEST_QUERIES:
        qid        = q["id"]
        question   = q["question"]
        difficulty = q["difficulty"]
        category   = q["category"]

        print(f"  [{qid}] {question[:60]}{'...' if len(question)>60 else ''}", end="", flush=True)

        if dry_run:
            print(" → DRY RUN")
            rows.append({
                "experiment": exp_id,
                "model":      model,
                "use_rag":    use_rag,
                "use_validator": use_validator,
                "query_id":   qid,
                "difficulty": difficulty,
                "category":   category,
                "question":   question,
                "ea":         "",
                "sa":         "",
                "arc":        "",
                "latency":    "",
                "err":        "",
                "cpq":        "",
                "rows":       "",
                "sql":        "",
                "error_msg":  "DRY RUN",
            })
            continue

        metrics = run_single(question, model, use_rag, use_validator)

        status = "✓" if metrics["ea"] else ("∅" if metrics["err"] else "✗")
        print(f" → {status}  {metrics['latency']}s  retries:{metrics['arc']}")

        rows.append({
            "experiment":    exp_id,
            "model":         model,
            "use_rag":       use_rag,
            "use_validator": use_validator,
            "query_id":      qid,
            "difficulty":    difficulty,
            "category":      category,
            "question":      question,
            "ea":            metrics["ea"],
            "sa":            "",          # filled in manually after review
            "arc":           metrics["arc"],
            "latency":       metrics["latency"],
            "err":           metrics["err"],
            "cpq":           round(cpq, 4) if metrics["ea"] else 0.0,
            "rows":          metrics["rows"],
            "sql":           metrics["sql"].replace("\n", " "),
            "error_msg":     metrics["error_msg"],
        })

    return rows


# ─────────────────────────────────────────────────────────────────
# SUMMARY PRINTER
# ─────────────────────────────────────────────────────────────────
def print_summary(all_rows: list):
    print(f"\n{'='*65}")
    print("  EVALUATION SUMMARY")
    print(f"{'='*65}")
    print(f"  {'Exp':<4} {'Model':<10} {'RAG':<5} {'Val':<5} {'EA%':>6} {'ERR%':>6} {'AvgARC':>8} {'AvgLat':>8} {'Cost':>8}")
    print(f"  {'-'*64}")

    exp_ids = []
    for row in all_rows:
        if row["experiment"] not in exp_ids:
            exp_ids.append(row["experiment"])

    for exp_id in exp_ids:
        exp_rows = [r for r in all_rows if r["experiment"] == exp_id]
        if not exp_rows or exp_rows[0]["ea"] == "":
            continue

        ea_vals  = [r["ea"]      for r in exp_rows if r["ea"] != ""]
        err_vals = [r["err"]     for r in exp_rows if r["err"] != ""]
        arc_vals = [r["arc"]     for r in exp_rows if r["arc"] != ""]
        lat_vals = [r["latency"] for r in exp_rows if r["latency"] != ""]
        cpq_vals = [r["cpq"]     for r in exp_rows if r["cpq"] != ""]

        ea_pct   = round(sum(ea_vals)  / len(ea_vals)  * 100, 1) if ea_vals  else 0
        err_pct  = round(sum(err_vals) / len(err_vals) * 100, 1) if err_vals else 0
        avg_arc  = round(sum(arc_vals) / len(arc_vals), 2)        if arc_vals else 0
        avg_lat  = round(sum(lat_vals) / len(lat_vals), 2)        if lat_vals else 0
        tot_cost = round(sum(cpq_vals), 4)                         if cpq_vals else 0

        cfg   = EXPERIMENTS[exp_id]
        model = cfg["model"]
        rag   = "Yes" if cfg["use_rag"]       else "No"
        val   = "Yes" if cfg["use_validator"] else "No"

        print(f"  {exp_id:<4} {model:<10} {rag:<5} {val:<5} {ea_pct:>5}% {err_pct:>5}% {avg_arc:>8} {avg_lat:>7}s ${tot_cost:>6}")

    print(f"{'='*65}")
    print("  SA (Semantic Accuracy) requires manual review — fill 'sa' column in CSV")
    print(f"{'='*65}\n")


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SmartViz Evaluation Harness")
    parser.add_argument("--exp",     type=str, default="ALL",
                        help="Experiment to run: E1 E2 E3 E4 E5 E6 or ALL")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print queries without running the pipeline")
    args = parser.parse_args()

    # Select experiments to run
    if args.exp.upper() == "ALL":
        exps_to_run = list(EXPERIMENTS.keys())
    elif args.exp.upper() in EXPERIMENTS:
        exps_to_run = [args.exp.upper()]
    else:
        print(f"Unknown experiment: {args.exp}. Choose from: {list(EXPERIMENTS.keys())} or ALL")
        sys.exit(1)

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = f"evaluation_results_{timestamp}.csv"

    print(f"\n SmartViz Evaluation Harness")
    print(f" Experiments : {', '.join(exps_to_run)}")
    print(f" Queries     : {len(TEST_QUERIES)}")
    print(f" Total runs  : {len(exps_to_run) * len(TEST_QUERIES)}")
    print(f" Output      : {output_csv}")
    if args.dry_run:
        print(f" Mode        : DRY RUN — no pipeline calls")

    # CSV columns
    fieldnames = [
        "experiment", "model", "use_rag", "use_validator",
        "query_id", "difficulty", "category", "question",
        "ea", "sa", "arc", "latency", "err", "cpq", "rows",
        "sql", "error_msg"
    ]

    all_rows = []

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for exp_id in exps_to_run:
            config = EXPERIMENTS[exp_id]
            rows   = run_experiment(exp_id, config, dry_run=args.dry_run)
            all_rows.extend(rows)
            writer.writerows(rows)
            f.flush()  # write after each experiment so data is safe

    print_summary(all_rows)
    print(f" Results saved to: {output_csv}")
    print(f" Next step: open CSV, review results, fill in 'sa' column manually\n")


if __name__ == "__main__":
    main()