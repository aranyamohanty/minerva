# Contributing to Minerva

Thank you for your interest in contributing to Minerva! As a local-first, model-agnostic context management layer for AI assistants, we welcome developer contributions to make prompt engineering and context retrieval more efficient, structured, and private.

---

## 1. Code of Conduct
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.

---

## 2. Setting Up the Development Environment

Minerva uses a polyglot codebase:
- **Backend Service & MCP**: Written in Python, managed by `uv`.
- **Frontend Visualizer**: Written in React + TypeScript + Vite, managed by `npm`/`pnpm`.

### Python Backend Setup
1. **Prerequisites**: Ensure you have Python 3.10+ installed.
2. **Install `uv`** (recommended):
   ```bash
   pip install uv
   ```
3. **Install Dependencies**:
   ```bash
   uv sync
   ```
4. **Initialize Database & Download Local Embedding Model**:
   ```bash
   uv run minerva init
   ```
5. **Start MCP Server**:
   ```bash
   uv run minerva start
   ```

### Frontend Visualizer Setup
1. **Install Node.js** (v18+ recommended).
2. **Install Dependencies**:
   ```bash
   npm install
   ```
3. **Run Dev Server**:
   ```bash
   npm run dev
   ```

---

## 3. Running Tests & Benchmarks

Before submitting any code changes, ensure all tests pass and benchmarks are verified.

### Running Unit & E2E Tests
Tests are implemented using `pytest`:
```bash
uv run pytest
```

### Running Retrieval Benchmarks
Verify prompt compilation efficiency and correctness:
```bash
uv run python tests/run_v5_benchmark.py
```

---

## 4. Architectural Principles
When submitting modifications or new features, respect the following constraints:
1. **Local-First**: All computations (including embeddings, database transactions, FTS search, and ranking) must run on the user's local machine. Do NOT introduce dependencies on remote cloud APIs.
2. **Low Overhead**: Minerva is designed as a lightweight middleware. Keep execution and IPC latency sub-15ms.
3. **Modular IPC**: Maintain the separation between the local service (the brain) and the user-facing interfaces (MCP, extensions, CLI).

---

## 5. Submitting Pull Requests
1. Fork the repository and create your branch from `main`.
2. Implement your changes, including appropriate tests.
3. Verify that `uv run pytest` passes successfully.
4. Open a Pull Request referencing the issue you are addressing and complete the PR template.
