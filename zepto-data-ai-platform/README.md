# Zepto Data & AI Platform Capstone

A practical, production-ready capstone project demonstrating end-to-end data engineering, machine learning analytics, and a retrieval-augmented generation (RAG) customer support assistant across three core modules: `/data_pipeline`, `/analytics`, and `/support_assistant`.

---

## Repository Structure

```text
zepto-data-ai-platform/
├── README.md
├── .gitignore
├── data_pipeline/
│   ├── requirements.txt
│   ├── scrape_clean_load.py
│   ├── queries.py
│   ├── books.db
│   └── sql_results.md
├── analytics/
│   ├── requirements.txt
│   ├── 01_eda.ipynb
│   ├── 02_modeling.ipynb
│   ├── titanic.csv
│   ├── titanic_pipeline.joblib
│   └── figures/
└── support_assistant/
    ├── requirements.txt
    ├── Dockerfile
    ├── main.py
    ├── graph.py
    ├── rag.py
    ├── prompts.py
    ├── schemas.py
    ├── test_graph.py
    └── docs/
        ├── doc_01.txt
        └── ... (doc_02 to doc_08)