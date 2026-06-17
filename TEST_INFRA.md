# E2E Test Infra: Minerva Phase 1

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation design.
- Methodology: Category-Partition + BVA + Pairwise + Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | Goals Management | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 2 | Constraints Management | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 3 | Decisions Management | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 4 | Tasks Management | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 5 | Facts Management | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 6 | Entity Linking | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 7 | Hybrid Search Retrieval | ORIGINAL_REQUEST | 5 | 5 | ✓ |
| 8 | Prompt Assembly | ORIGINAL_REQUEST | 5 | 5 | ✓ |

## Test Architecture
- Test runner: pytest (`uv run pytest`)
- Test case format: pytest unit/E2E assertions using Click CliRunner and subprocess CLI invocation
- Directory layout:
  - `tests/test_e2e.py`: main E2E test suite
  - `tests/benchmark.py`: latency and performance benchmarks

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Hybrid search ranking with links | goals, decisions, constraints, tasks, facts, linking | High |
| 2 | Real-world workload scalability | 100+ entities database population & multi-query rank validation | High |

## Coverage Thresholds
- Tier 1: ≥5 per feature
- Tier 2: ≥5 per feature (where boundaries exist)
- Tier 3: pairwise coverage of major feature interactions
- Tier 4: ≥5 realistic application scenarios
