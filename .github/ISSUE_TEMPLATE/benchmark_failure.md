---
name: Benchmark Failure
about: Report a failure, regression, or low accuracy in retrieval benchmarks
title: '[BENCHMARK-FAIL] '
labels: bug, benchmark
assignees: ''

---

**Failed Benchmark Category**
Identify which benchmark category or question failed (e.g. Historical Audit, Dependency Analysis).

**Reproduced Score & Metrics**
Provide the output metrics from your local execution of:
```bash
uv run python tests/run_v5_benchmark.py
```
- Correctness Score:
- Completeness Score:
- Hallucination Score:
- Token Count:

**Ground Truth Terms Missed**
List the exact database entries or terms that the retrieval engine failed to pull.

**Proposed Solution**
Do you have ideas on adjusting the BM25 vs semantic search weights, link graph boosting parameters, or token packer logic to fix this failure?
