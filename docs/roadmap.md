# Minerva Product Roadmap

This document outlines the product phases and future plans for **Minerva**.

---

## Phase 1 — "Developer Core" (Current Release)
**Goal:** Prove the local-first context engine works for AI-native developers.
- **Local Service**: SQLite-backed project memory (Goals, Constraints, Decisions, Tasks, Facts).
- **Model Context Protocol (MCP)**: Native stdio integration for Cursor, Windsurf, and Claude Desktop.
- **CLI Tool**: CLI manager for local memory CRUD and prompt previews.
- **Local Embeddings**: CPU-optimized local ONNX embeddings (`bge-small-en-v1.5`).

---

## Phase 2 — "Web UI Integration" (Q3 2026)
**Goal:** Reach the web UI developer and general audience (ChatGPT, Claude.ai, Gemini web users).
- **Browser Extension**: Chrome, Firefox, and Safari extension supporting manifest V3.
- **DOM Observers**: Seamless observation and injection of context into web UI input fields.
- **Extension Side Panel**: Interactive panel displaying project memory and recent decisions.
- **WASM Fallback**: Local WASM execution core for browser environments when the background service is not running.

---

## Phase 3 — "IDE-Native Integrations" (Q4 2026)
**Goal:** Capture the developer workflow directly inside the IDE.
- **VS Code Extension**: Direct integration distributed via the VS Code Marketplace and Open VSX.
- **File Watchers**: Automatic background syncing of source code tree modifications.
- **Git History Watcher**: Automatically inferring architectural decisions from git commits and branch changes.
- **IDE Sidebar**: In-editor workspace panel to CRUD project memories and check link graphs.

---

## Phase 4 — "The Advanced Context Engine" (Q1 2027)
**Goal:** Enhance the cognitive reasoning and extraction capabilities of the engine.
- **Graph Database**: Deep relationship traversal using `KùzuDB` or similar embedded graph stores.
- **Cross-Encoder Re-ranking**: Integrate local cross-encoders to refine candidate scoring.
- **Local LLM Integration**: Run local models (e.g. Qwen-3B or Phi-3) to automate summarization of older chats and facts.
- **Fact Freshness**: Automatic decay of relevance scores for older facts and contradiction warning notifications.

---

## Phase 5 — "Ecosystem & B2B" (H2 2027)
**Goal:** Support team synchronization and cloud workspaces.
- **E2E Cloud Sync**: Optional, end-to-end encrypted cloud backup (user holds the encryption keys).
- **Shared Team Memory**: Collaborative team context spaces for B2B engineering orgs.
- **Marketplace**: Context packs (e.g., "ISO 27001 constraints", "Next.js 15 template context").
- **Enterprise Features**: Single Sign-On (SSO) and compliance audit logging.
