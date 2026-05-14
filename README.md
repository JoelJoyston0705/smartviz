# SmartViz

A 5-agent LLM pipeline for natural language querying of real IoT sensor data from a smart building.

MSc AI for Business Intelligence — University of Leicester (2026)
Industry Partner: SmartViz Ltd, London
IEEE DTPI 2026 — Paper #1571276780

## Architecture
Agent 1 (Planner) → Agent 2 (RAG) → [Function Router] → Agent 3 (SQL) → Agent 4 (Validator) → Agent 5 (Graph)

## Key Finding
Gemma3 silent hallucination — 100% EA, 46.7% SA. Valid SQL for wrong metric. Undetectable by validator or RAGAS.

## Author
Joel Joyston Cecil Kumar — https://joel-joyston-portfolio.vercel.app
