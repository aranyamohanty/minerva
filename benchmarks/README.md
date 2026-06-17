# Minerva Retrieval Benchmarks

This directory contains the documentation and reports for Minerva retrieval performance.

---

## 1. Benchmark Overview

Minerva uses a local, multi-mode retrieval engine designed to select highly relevant project details and compress prompt context. To validate this engine, we run an adversarial benchmark that evaluates context compilation over **30 complex, real-world development questions** against a pre-populated telemetry project database.

The benchmark compares:
1. **Naive Baseline (Control Group)**: A direct dump of all project goals, constraints, decisions, tasks, and facts into the context window.
2. **Minerva (V4 Multi-Mode)**: Prompts compiled dynamically by the Minerva engine using a weighted combination of lexical, semantic, and relational search within a 4,000-token budget.

---

## 2. Key Performance Metrics (v5 Benchmark Results)

The benchmark is run locally and calculates metrics deterministically. Here are the results of the latest **Minerva v5 clean benchmark**:

| Performance Metric | Naive Long-Context (Control) | Minerva (V4 Multi-Mode) | Delta / Change |
| :--- | :---: | :---: | :---: |
| **Average Correctness (0-10)** | 10.00 | 9.92 | -0.08 |
| **Average Completeness (0-10)** | 10.00 | 9.92 | -0.08 |
| **Average Hallucination Risk (0-10)** | 7.50 | 2.07 | -5.43 (Lower is better) |
| **Total Tokens Consumed** | 317,794 | 98,427 | **69.03% token reduction** |
| **Overall Quality Index** | 12.50 | 17.77 | **+42.13% change** (Higher is better) |

### Key Takeaways
- **Massive Token Savings**: Minerva reduces input token size by **69.03%**, leading to significantly lower API model costs and faster model response times (Time-To-First-Token).
- **Reduced Hallucination**: By filtering out over 100+ distracting, irrelevant facts, the hallucination risk drops from **7.50** to **2.07**, allowing the model to focus attention weights exclusively on relevant context.
- **High Recall Retention**: Correctness only drops by **0.08**, proving that the hybrid search engine almost never misses critical facts.

---

## 3. Benchmark Datasets

The benchmarks run against precompiled SQLite databases located in the `tests/` directory:
- **`tests/adversarial_v4.db`**: Precompiled database containing 350+ records (goals, constraints, decisions, tasks, and facts) modeling a complex telemetry daemon project.
- **Other Datasets**:
  - `generalization_personal.db`
  - `generalization_research.db`
  - `generalization_startup.db`
  - `stress_test.db`

---

## 4. How to Reproduce Benchmarks

Ensure your Python environment is set up (see [CONTRIBUTING.md](../CONTRIBUTING.md)) and the embedding models are initialized.

Run the benchmark runner:
```bash
uv run python tests/run_v5_benchmark.py
```

Upon completion, the script will write a detailed markdown report to:
`benchmarks/reports/benchmark_v5.md`

---

## 5. Known Limitations

- **Strict Term Matching**: The correctness metric searches for exact ground truth string matches (e.g. matching `sqlite fts5` exactly). It does not currently account for semantic equivalents or synonyms during scoring.
- **Domain Specificity**: The current adversarial dataset is focused on systems engineering and telemetry codebases. Retrieval patterns might differ in other domains (e.g., frontend design, copywriting).
- **Offline Scoring**: The hallucination risk is modeled using static keyword filters rather than dynamic LLM-based evaluation to keep the benchmark run 100% local, fast, and free.
