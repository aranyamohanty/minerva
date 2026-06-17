# Minerva Benchmark Methodology

This document details the testing architecture, metrics, and methodology used to evaluate Minerva context retrieval performance.

---

## 1. Evaluation Philosophy

Modern long-context LLMs can ingest large context dumps, but suffer from **context-drift** and **hallucination** when drowned in noise. 

Minerva is designed to solve this by managing context. To prove its effectiveness, we evaluate:
- **Retrieval Accuracy**: Does it find the exact facts required to answer the query?
- **Token Efficiency**: How much does it reduce the prompt context footprint?
- **Noiselessness**: Does it filter out irrelevant details that might distract the model?

---

## 2. Evaluation Metrics

Minerva runs a deterministic evaluator comparing a **Naive Long-Context Dump** against **Minerva-Augmented Compilation** over 30 adversarial queries.

Each candidate context is graded on three metrics:
1. **Correctness (0–10)**: Measures the retrieval coverage of required ground truth terms matching the database exactly.
   $$\text{Correctness} = \frac{\text{Found Ground Truth Terms}}{\text{Total Ground Truth Terms}} \cdot 10$$
2. **Completeness (0–10)**: Aligned with correctness, but penalizes short responses (sub-200 characters) to ensure that the compiled context has enough detail to be actionable.
3. **Hallucination Risk (0–10)**:
   - The **Naive Baseline** receives a high baseline hallucination risk score (**7.5**) because it includes 100+ distracting, irrelevant project details in the prompt.
   - **Minerva** starts with a baseline risk score of **1.0** and is penalized by **+2.0** for every noise keyword (e.g. coffee machine, saunas) that leaks into the retrieved prompt.
4. **Overall Quality Index**: A unified measure of context utility:
   $$\text{Quality Index} = \text{Correctness} + \text{Completeness} - \text{Hallucination Risk}$$

---

## 3. Adversarial Dataset Structure

Benchmarks are evaluated against precompiled SQLite databases (located under `tests/`):
- **Adversarial Database (`adversarial_v4.db`)**: Contains 350+ relational records mimicking telemetry service development. It includes complex design migrations (e.g. replacing BadgerDB with SQLite FTS5) and explicit link graph connections.
- **Noise Terms**: Includes highly distracting unrelated facts (e.g., details about chess matches, wombats, and office coffee setups) to test the retrieval filter.

---

## 4. Benchmark Execution

The benchmark script `tests/run_v5_benchmark.py` runs locally, requiring no LLM calls:
1. It queries the `adversarial_v4.db` database using 30 adversarial questions.
2. It generates naive prompts and Minerva prompts for each question.
3. It computes token sizes and calculates correctness, completeness, and hallucination metrics.
4. It writes a structured report comparing the performance metrics.
