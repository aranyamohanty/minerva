# Release Notes: Minerva v0.1.0 (Phase 1 MVP)

We are thrilled to announce the initial release of **Minerva (v0.1.0)**! 

Minerva is a local-first, model-agnostic context manager for AI assistants. It runs on your local machine, keeping your data private while optimizing your prompt context windows by up to **70%**.

---

## 1. Key Features

- **Relational Memory Store**: A structured local SQLite schema representing Goals, Constraints, Architectural Decisions, Active/Completed Tasks, and atomic Facts.
- **Model Context Protocol (MCP)**: Native stdio-based MCP server built with `FastMCP`, exposing context management tools, resources, and compilation templates to Cursor, Windsurf, and Claude Desktop.
- **Embedded Hybrid Search**: Unified search combining SQLite FTS5 BM25 lexical keyword matching and semantic vector search.
- **Zero-Config Local Embeddings**: CPU-optimized vector embedding generation using `onnxruntime` and `tokenizers` executing Xenova/bge-small-en-v1.5 locally.
- **Robust CLI Manager**: A unified Click-based command-line interface supporting `init`, `start`, `add`, `list`, `delete`, `update`, `search`, and `preview` prompts.

---

## 2. Architecture & Design

Minerva follows a local-first, modular design system:
- **Core Engine**: Implements the IPC logic, ONNX runtime session lifecycle, SQLite FTS synchronization triggers, and token budget packer.
- **Polyglot Stack**: Core backend runs on Python 3.10+; the interactive visualizer runs on React + TypeScript + Vite.
- **Security-First**: Speaks stdio-based MCP, preventing local ports from exposure and protecting local context databases from browser-based cross-site hijacking.

---

## 3. Retrieval Performance Benchmarks

Our v5 adversarial evaluation (consisting of 30 queries tested against a 350-record complex database) yielded the following metrics compared to a Naive long-context dump:

- **Token Footprint Reduction**: **69.03%** prompt token savings (input context compressed from 317,794 to 98,427 tokens).
- **Hallucination Risk**: Slashed from **7.50** to **2.07** on a 10-point scale.
- **Actionable Quality Index**: Improved by **+42.13%** (measured as Correctness + Completeness - Hallucination Risk).
- **Factual Recall Accuracy**: Retained an average Correctness score of **9.92 / 10.0**.

---

## 4. Known Limitations in v0.1.0

- **Strict Text Evaluation**: Correctness metrics rely on exact word matching; synonym matches are not currently evaluated by the benchmark.
- **Local CPU Usage**: Embedding generation is CPU-only, causing brief CPU utilization spikes during heavy operations.
- **No Cloud Synchronization**: Workspace data is stored exclusively on the local disk.

---

## 5. Future Roadmap

- **Q3 2026**: Web UI browser extension for DOM injection on Claude.ai and ChatGPT.
- **Q4 2026**: IDE-native VS Code and Cursor extension.
- **Q1 2027**: KùzuDB graph database traversal.
- **H2 2027**: E2E-encrypted cloud workspace sync.
