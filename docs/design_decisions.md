# Minerva Design Decisions

This document summarizes the core technical design decisions, trade-offs, and library choices made during the development of **Minerva**.

---

## 1. Local-First Architecture

### Decision
All databases, embeddings, and search operations run locally on the user's machine.

### Rationale
- **Data Privacy**: Codebases, tasks, and architectural decisions are sensitive IP. Local execution ensures that no raw data leaks to third-party endpoints.
- **Sub-millisecond Latency**: Local databases and vector operations eliminate round-trip network delays.
- **Cost Efficiency**: Eliminates token fees for embedding calls.

### Trade-off
Users on highly constrained hardware might experience CPU spikes during initial indexing or embedding generation. We mitigate this by using a lightweight embedding model.

---

## 2. SQLite with FTS5 for Primary Storage

### Decision
Use **SQLite** with the **FTS5** full-text search extension for structured memory and keyword indexing.

### Rationale
- **Zero Configuration**: SQLite requires no background daemon setup. It is a single file on disk, making onboarding simple.
- **ACID Compliance**: Ensures robust transactional integrity during concurrent IDE edits.
- **Automatic FTS Sync**: SQLite triggers automatically sync updates from raw tables (`goals`, `decisions`, etc.) into virtual text index tables.

### Alternatives Considered
- **PostgreSQL**: Rejected due to high installation friction for local developer environments.
- **LSM Key-Value Stores (e.g. BadgerDB)**: Rejected due to complex full-text search requirements and wear concerns on consumer SSDs.

---

## 3. Xenova/bge-small-en-v1.5 ONNX Embeddings

### Decision
Embed text queries locally using `Xenova/bge-small-en-v1.5` executing via the `ONNX Runtime` CPU provider.

### Rationale
- **High Performance**: BGE-small yields competitive retrieval accuracy on retrieval leaderboards (MTEB) while being small (~130MB).
- **CPU Optimized**: The ONNX runtime provider runs efficiently on standard developer laptop CPUs without requiring dedicated GPU architectures.
- **Fast Similarity**: Pre-normalizing vectors allows similarity calculation via simple dot products (NumPy matrix operations).

---

## 4. Rejection of LangChain and LlamaIndex

### Decision
Do not use LangChain or LlamaIndex in core dependencies.

### Rationale
- **Opinionated Bloat**: Standard agent frameworks introduce hundreds of dependencies and layers of abstraction, making debugging difficult.
- **Startup Latency**: Minerva CLI commands and MCP startup must be fast. Stripping out heavy frameworks keeps command invocations under 100ms.
- **Custom Primitives**: Writing our own SQLite connectors and ONNX wrapper gives us precise control over prompt packaging and token budgets.

---

## 5. Stdio-based Model Context Protocol (MCP)

### Decision
Expose Minerva tools and resources using stdio transport via the official Model Context Protocol (MCP) Python SDK.

### Rationale
- **Industry Standard**: MCP is supported natively by major AI-native IDEs (Cursor, Windsurf, Claude Desktop).
- **Security Isolation**: Stdio-based communication avoids exposing local HTTP ports, preventing malicious web applications from accessing local context databases.
