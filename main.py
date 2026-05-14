from agents.agent1_planner import plan_query
from agents.agent2_rag import retrieve_schema
from agents.agent3_sql import generate_sql
from agents.agent4_validator import validate_and_execute
from agents.agent5_graph import generate_chart

import os
import platform


def open_chart(path):
    """Open the chart image using the default system viewer"""
    try:
        if platform.system() == "Darwin":  # macOS
            os.system(f'open "{path}"')
        elif platform.system() == "Windows":
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}"')
    except:
        pass


def run_pipeline(user_question: str):
    print(f"\n{'='*60}")
    print(f"❓ USER QUESTION: {user_question}")
    print(f"{'='*60}")

    # ──────────────────────────────────────────
    # Agent 1 — Planner
    # ──────────────────────────────────────────
    plan = plan_query(user_question)

    # ──────────────────────────────────────────
    # Agent 2 — RAG Retrieval (pgvector)
    # ──────────────────────────────────────────
    schema_context = retrieve_schema(plan)

    # ──────────────────────────────────────────
    # Agent 3 — SQL Generator (uses dynamic schema from Agent 2)
    # ──────────────────────────────────────────
    sql = generate_sql(plan, schema_context)

    if not sql.strip().upper().startswith(("SELECT", "WITH")):
        print("⚠️  Agent 3 did not return valid SQL. Please try rephrasing.")
        return

    # ──────────────────────────────────────────
    # Agent 4 — Validator
    # ──────────────────────────────────────────
    cols, results, final_sql, attempts = validate_and_execute(sql, user_question)

    if not results:
        print("\n❌ No results found after validation. Try rephrasing your question.")
        return

    if final_sql != sql:
        print(f"\n🔧 Note: Validator corrected the SQL (took {attempts} attempts)")

    # ──────────────────────────────────────────
    # Agent 5 — Graph Builder
    # ──────────────────────────────────────────
    chart_path = generate_chart(cols, results, user_question, final_sql)

    # Display text results
    print(f"\n✅ FINAL ANSWER:")
    for row in results:
        for col, val in zip(cols, row):
            print(f"   {col}: {val}")

    # Show chart if generated
    if chart_path != "TEXT_ONLY":
        print(f"\n📊 Chart saved: {chart_path}")
        open_chart(chart_path)

    print(f"{'='*60}")


if __name__ == "__main__":
    while True:
        print("\n" + "=" * 60)
        question = input(" Enter your question (or 'quit' to exit): ").strip()
        if question.lower() == "quit":
            break
        if question:
            run_pipeline(question)