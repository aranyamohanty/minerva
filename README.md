<div align="center">
  <h1>Minerva</h1>
  <p><strong>The Context Operating System for AI Assistants. Shrink prompts, reduce drift, and keep your data local.</strong></p>
  <p>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License" /></a>
    <a href="https://github.com/mcp-protocol/spec"><img src="https://img.shields.io/badge/MCP-Protocol-orange.svg" alt="Model Context Protocol" /></a>
    <a href="https://pytest.org"><img src="https://img.shields.io/badge/Tests-24%20Passed-green.svg" alt="Tests" /></a>
  </p>
</div>

---

## 1. Problem Statement

Modern AI assistants suffer from a fundamental bottleneck: **degraded, polluted, or bloated context windows**. 

As developer conversations grow, project codebases evolve, and multiple chat tools are used, the context sent to the LLM becomes:
- **Polluted** with duplicated, contradictory, or stale text.
- **Drifted** from the project's actual, current state.
- **Bloated**, wasting tokens and attention budget.
- **Missing critical facts** (decisions, constraints, goals) that were mentioned once and forgotten.

Existing products lock your context to specific vendor silos. Minerva solves this by running as a **local, model-agnostic middleware** that continuously organizes, cleans, ranks, and optimizes your project context before it reaches the model.

---

## 2. How Minerva Works

Minerva sits orthogonal to both **AI models** (OpenAI, Anthropic, Gemini, local LLMs) and **interfaces** (IDEs like Cursor/Windsurf, CLIs, web UIs). It provides a unified **Local Service** that maintains project memory across all these tools.

```
                  ┌───────────────────────────────────────────────┐
                  │                 USER'S MACHINE                │
                  │                                               │
                  │  ┌───────────────┐   ┌─────────────────────┐  │
                  │  │   Web Browser │   │     Developer IDE   │  │
                  │  │   (Claude.ai, │   │    (Cursor/Windsurf │  │
                  │  │    ChatGPT)   │   │     via stdio MCP)  │  │
                  │  └───────┬───────┘   └──────────┬──────────┘  │
                  │          │                      │             │
                  │          └───────────┬──────────┘             │
                  │                      ▼                        │
                  │     ┌───────────────────────────────────┐     │
                  │     │      MINERVA LOCAL SERVICE        │     │
                  │     │        - Hybrid Memory (SQLite)   │     │
                  │     │        - Local ONNX Embeddings    │     │
                  │     │        - SQLite FTS5 BM25 Engine  │     │
                  │     └────────────────┬──────────────────┘     │
                  └──────────────────────┼────────────────────────┘
                                         ▼ (Optimized Prompt Context)
                        ┌─────────────────────────────────┐
                        │        ANY LLM PROVIDER         │
                        │    Claude / Gemini / OpenAI     │
                        └─────────────────────────────────┘
```

---

## 3. Core Architectural Pillars

1. **Hybrid Memory Architecture**: Minerva splits memory into SQLite tables for structured relational records (Goals, Constraints, Decisions, Tasks, Facts) and virtual FTS5 tables for keyword search.
2. **Local Vector Search**: Embeds and retrieves context semantically using a local ONNX instance of `Xenova/bge-small-en-v1.5` (~130MB, no data leaves your machine).
3. **Link Graph Traversal**: Establishes connections between entities (e.g., linking a *decision* to a *constraint*) and dynamically boosts linked elements during retrieval.
4. **Token-Budget Packing**: Fills the prompt context sequentially, prioritizing high-scoring items and scaling down context size to respect safety limits.

---

## 4. Rigorous Retrieval Benchmarks

Minerva was benchmarked against a **Naive Long-Context Baseline** (which dumps all project context into the prompt) over 30 adversarial engineering audit questions.

### Performance Summary
- **Token Reduction**: **69.03%** prompt token savings (shrinking input context from 317k to 98k tokens).
- **Hallucination Risk**: Reduced from **7.50** (Naive baseline) to **2.07** (Minerva).
- **Quality Index**: Increased by **+42.13%** (measured as Correctness + Completeness - Hallucination Risk).
- **Average Correctness**: **9.92 / 10.0** (retaining near-perfect retrieval accuracy).

---

## 5. Installation & Quick Start

### Prerequisites
- Python 3.10+
- `pip` or [`uv`](https://github.com/astral-sh/uv) (recommended)

### Setup
1. Clone this repository and navigate to the project directory:
   ```bash
   git clone https://github.com/your-username/minerva.git
   cd minerva
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Initialize the database and download the local embedding model:
   ```bash
   uv run minerva init
   ```
4. Start the Model Context Protocol (MCP) server:
   ```bash
   uv run minerva start
   ```

---

## 6. CLI Usage Examples

You can manage your local context store directly from the command line:

```bash
# Add a project goal
uv run minerva add goal "Reduce API server response latency to sub-200ms" --priority 5

# Add an architectural decision
uv run minerva add decision "Use SQLite WAL mode" "WAL mode enables concurrent reads and improves write throughput"

# Link a decision to a goal
uv run minerva link decision 1 goal 1

# Search memory
uv run minerva search "database concurrency"

# Preview compiled context context for an LLM prompt
uv run minerva preview "Why did we choose SQLite?" --budget 4000
```

---

## 7. Roadmap & Future Work

- **Phase 1 (MVP)**: Local service, SQLite FTS5, local BGE embeddings, and MCP stdio integration. (Current)
- **Phase 2 (Browser Extension)**: Inject context directly into Claude.ai, ChatGPT, and Gemini web interfaces.
- **Phase 3 (IDE Extensions)**: Direct VS Code & Cursor extensions for file tree watching and git history integration.
- **Phase 4 (Graph Database)**: Integration of `KùzuDB` for deep network traversal of dependencies.
- **Phase 5 (Ecosystem)**: E2E-encrypted cross-device synchronization and team shared memory.

---

## 8. Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on setting up your environment and submitting code.

---

## 9. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
