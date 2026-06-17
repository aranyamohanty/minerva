# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-06-17

### Added
- **Local Context Engine**: Local-first background context service exposing goals, constraints, decisions, active tasks, completed tasks, and important facts.
- **Model Context Protocol (MCP)**: Native stdio-based MCP server integration for Cursor, Windsurf, and Claude Desktop.
- **CLI Management Tool**: Command-line interface with `init`, `start`, `add`, `list`, `delete`, `update`, `search`, and `preview` commands.
- **Hybrid Search**: Unified retrieval combining BM25 keyword search via SQLite FTS5 and vector similarity search.
- **Local Embeddings**: CPU-optimized local embedding generator using Xenova/bge-small-en-v1.5 and ONNX Runtime.
- **FTS5 Sync Triggers**: Automatic SQLite triggers to synchronize modifications to virtual search tables.
- **Comprehensive Test Suite**: 24 unit and E2E tests validating CRUD database features, prompt builder token budgets, and hybrid ranking algorithms.
- **Interactive Visualizer**: Vite-powered frontend visualizer displaying cognitive architectures, memory graphs, and prompt pipelines.
