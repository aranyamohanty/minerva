# Minerva — Strategic Architecture Document

**Document type:** Product & Architecture Design (no implementation code)
**Author role:** Principal Software Architect / Product Strategist / AI Infrastructure Engineer
**Version:** 1.0
**Date:** 2026-06-16

---

## 1. Executive Summary

### 1.1 The Problem
Modern AI assistants suffer from a class of failures that share a single root cause: **the model receives a degraded, polluted, or stale context window**. As conversations grow, projects evolve, and multiple tools are used, the prompt that reaches the model becomes:

- Polluted with duplicated, contradictory, or outdated text
- Drifted from the project's actual current state
- Bloated, wasting tokens and attention budget
- Missing critical facts (architecture, decisions, constraints) that were mentioned once and forgotten
- Inconsistent across tools (Cursor knows something ChatGPT doesn't, and vice versa)

This is true for every major AI product on the market today, including Cursor, Windsurf, Claude Code, and ChatGPT Projects. The user pays the cost in degraded output quality, hallucinations, and lost productivity.

### 1.2 The Insight
The model is not the bottleneck. **Context is the bottleneck.** The single highest-leverage intervention in any AI workflow is not a better model — it is a better context. Yet no product today treats context as a first-class system to be engineered, versioned, and maintained.

### 1.3 The Product
**Minerva is a Context Operating System for AI.** It is a middleware layer that sits between the user (and their tools) and the AI model. Its job is to **continuously organize, compress, clean, rank, and optimize context** before it reaches the model.

Minerva is:
- **Model-agnostic** — works with OpenAI, Anthropic, Google, open-source, future models
- **Provider-agnostic** — works with web UIs, IDEs, CLIs, and APIs
- **Local-first** — the user's context and project memory live on their machine
- **Token-efficient** — typically reduces prompt size by 40–70% while improving relevance
- **Quality-focused** — measurably improves task success rate, factual consistency, and instruction adherence

### 1.4 The Strategic Bet
The current AI ecosystem is fragmenting along two axes: **interface** (web/IDE/CLI) and **model** (OpenAI/Anthropic/Google/local). Every product today is locked to one cell of that matrix. Minerva sits **orthogonal** to both axes — it is the layer underneath both. This makes it the rare product that becomes *more* valuable as the ecosystem fragments, not less. Every new model and every new interface increases Minerva's addressable surface area.

### 1.5 The Recommendation (One Sentence)
**Build Minerva as a Hybrid Architecture: a Local Background Service (the brain) exposed via an MCP Server (for AI-native clients), a Browser Extension (for web UIs), an IDE Extension (for coding workflows), and a Python/Node SDK (for everything else) — owned by the user, running on their machine, with no required cloud dependency.**

---

## 2. Product Form Factor Recommendation

### 2.1 Comparative Analysis

Eight options were evaluated against nine criteria. Scores are qualitative (● = strong, ◐ = partial, ○ = weak).

| # | Option | Adoption Friction | Coding Coverage | Web UI Coverage | Local LLM Coverage | Cross-Platform | Vendor Independence | Scalability | Future-Proof | Tech Complexity |
|---|--------|-------------------|-----------------|-----------------|--------------------|----------------|---------------------|-------------|--------------|-----------------|
| 1 | Browser Extension | ● (1-click) | ○ | ● | ◐ | ● | ● | ● | ◐ | ● |
| 2 | Desktop App | ◐ (download/install) | ◐ | ● (if hooks) | ● | ◐ | ● | ● | ● | ◐ |
| 3 | VS Code Extension | ● (1-click) | ● (Cursor/Windsurf/VSCode) | ○ | ◐ | ◐ | ● | ◐ | ◐ | ● |
| 4 | Local Background Service | ◐ (install once) | ● (via hooks) | ● (via ext) | ● | ● | ● | ● | ● | ◐ |
| 5 | SaaS Web App | ● (sign-up) | ○ | ● (only itself) | ○ | ● | ● | ● | ◐ | ● |
| 6 | Hybrid Architecture | ◐ | ● | ● | ● | ● | ● | ● | ● | ◐ |
| 7 | MCP-Based Architecture | ● (config file) | ● (Claude/Cursor) | ○ | ● | ● | ● | ● | ● | ● |
| 8 | API Gateway Architecture | ● (API key swap) | ● | ○ | ● | ● | ○ (locks to gateway) | ● | ● | ◐ |

### 2.2 Detailed Pros / Cons

#### 1. Browser Extension
- **Advantages:** Zero install friction; reaches the largest existing user base (ChatGPT/Claude.ai/Gemini web users); updates are instant; can read and inject into chat inputs directly; no OS-level permissions needed.
- **Disadvantages:** Cannot intercept desktop IDE traffic (Cursor, Windsurf); limited to Chrome/Edge/Firefox; no system-level access for filesystem awareness; can't easily run heavy ML models locally; web UI DOMs change frequently and break injectors; no access to project files unless user explicitly uploads.
- **Technical complexity:** Low–medium. Mostly DOM observation, message injection, IndexedDB for storage.
- **User friction:** Very low. Already a known pattern.
- **Scalability:** High for web users, zero for IDE users.
- **Cross-platform:** Excellent (any browser, any OS).
- **Vendor independence:** Strong, but depends on third-party web UIs not breaking.
- **Long-term viability:** Medium. Web UIs are the most volatile surface — vendors may add anti-bot measures or change layouts.

#### 2. Desktop Application
- **Advantages:** Full system access (filesystem, processes, network); can hook into any app; runs persistent background services; ideal home for the "brain" of Minerva.
- **Disadvantages:** Highest install friction (download, OS permissions, code-signing, notarization); platform-specific builds (macOS/Windows/Linux); update mechanism is a burden; many users will not install an AI product that isn't already well-known; sandboxing on macOS is increasingly restrictive.
- **Technical complexity:** High. Native + cross-platform framework (Tauri/Electron), auto-update, OS permissions, daemon lifecycle.
- **User friction:** High. This is the single biggest barrier.
- **Scalability:** Excellent once installed.
- **Cross-platform:** Medium (Tauri helps; Linux is always a second-class citizen).
- **Vendor independence:** Strong.
- **Long-term viability:** Strong, but adoption curve is slow.

#### 3. VS Code Extension
- **Advantages:** Perfect target for the highest-value AI user (developer using Cursor/Windsurf); 1-click install; can read project files, LSP, git state, terminal output; huge existing marketplace; low technical complexity.
- **Disadvantages:** Limited to VS Code/Cursor/Windsurf only (huge market, but not universal); doesn't help ChatGPT/Claude.ai web users; subject to Microsoft's extension marketplace rules; can only observe what the IDE exposes.
- **Technical complexity:** Low.
- **User friction:** Very low for developers, irrelevant for everyone else.
- **Scalability:** Excellent within the developer segment.
- **Cross-platform:** Excellent (VS Code is cross-platform).
- **Vendor independence:** Medium (subject to Microsoft marketplace policies).
- **Long-term viability:** Strong while VS Code/Cursor/Windsurf remain dominant, which is 3–5+ years.

#### 4. Local Background Service
- **Advantages:** The natural home for the "context engine"; runs persistently, low resource footprint; OS-agnostic via daemon pattern; can be queried by any client (browser ext, IDE ext, MCP server, CLI); survives reboots; can hold the canonical project memory.
- **Disadvantages:** Requires install; needs a control UI or CLI for visibility; OS service management differs across platforms (launchd / systemd / Task Scheduler); silent failures are hard to diagnose without good observability.
- **Technical complexity:** Medium–high.
- **User friction:** Medium (one-time install, then invisible).
- **Scalability:** Excellent.
- **Cross-platform:** Excellent with a thin wrapper.
- **Vendor independence:** Strong.
- **Long-term viability:** Strong. This is the foundational layer.

#### 5. SaaS Web Application
- **Advantages:** Zero install; instant updates; easy to market; simple to monetize.
- **Disadvantages:** Defeats the core value proposition — users would have to copy context INTO the SaaS, breaking their existing workflow; creates a new silo rather than solving the silo problem; privacy concerns (project data on someone else's server); no access to local files; high CAC for a non-viral product; competes head-on with ChatGPT/Claude/Gemini rather than complementing them.
- **Technical complexity:** Low.
- **User friction:** Low to start, high to adopt (workflow change).
- **Scalability:** High server-side.
- **Cross-platform:** Excellent.
- **Vendor independence:** Weak — by definition a competitor to the model providers.
- **Long-term viability:** Poor as a *primary* form factor. Viable as a *companion* dashboard.

#### 6. Hybrid Architecture
- **Advantages:** Each surface optimized for its job; covers web + IDE + CLI + local LLM; local service as canonical brain; user can adopt one surface at a time (progressive onboarding); resilient to changes in any single surface.
- **Disadvantages:** Highest engineering investment; needs a clear shared protocol between surfaces; risk of feature fragmentation; coordination overhead; harder to ship v1.
- **Technical complexity:** High.
- **User friction:** Low *per surface*; medium to understand the full product.
- **Scalability:** Excellent.
- **Cross-platform:** Excellent.
- **Vendor independence:** Strongest of all options.
- **Long-term viability:** Strongest.

#### 7. MCP-Based Architecture
- **Advantages:** MCP (Model Context Protocol) is the emerging standard for exactly this problem; Anthropic, Cursor, Windsurf, Claude Desktop, and a growing ecosystem support it natively; works with local LLMs (Ollama, LM Studio) via MCP-aware clients; zero UI of its own — leverages the host's UI; clean conceptual model (tools/resources/prompts).
- **Disadvantages:** Does not reach web UIs (ChatGPT/Claude.ai/Gemini) which have no MCP support; adoption is still maturing; users must configure MCP servers manually today; cannot observe what the user types outside the MCP client.
- **Technical complexity:** Low for the MCP server itself; high for the context engine behind it.
- **User friction:** Low for technical users; medium for non-technical users (config file).
- **Scalability:** Excellent.
- **Cross-platform:** Excellent.
- **Vendor independence:** Strong (open protocol).
- **Long-term viability:** Strong. MCP is the most likely long-term standard.

#### 8. API Gateway Architecture
- **Advantages:** Most general — anything that calls an LLM API can be routed through it; model-agnostic by construction; clean monetization (per-token, with margin); can offer caching, optimization, observability; B2B angle (sell to app developers).
- **Disadvantages:** Users must swap their API base URL and provide keys; no help for users on web UIs; requires users to already be using APIs (i.e., developers, not the general public); competes with OpenRouter, LiteLLM, Portkey; vendor lock-in risk if Minerva becomes the gateway.
- **Technical complexity:** Medium.
- **User friction:** Medium (developer-level).
- **Scalability:** Excellent.
- **Cross-platform:** Excellent.
- **Vendor independence:** Weak by design — you're now in the routing business.
- **Long-term viability:** Medium. Commodity layer with thin margins over time.

### 2.3 Recommended Form Factor: **Hybrid Architecture**

The decision matrix reveals that **no single surface covers the full target market**, but a combination of four surfaces does, with each surface chosen for the job it does best:

| Surface | Role | Target User |
|---------|------|-------------|
| **Local Background Service** ("the Brain") | Canonical project memory, context engine, lifecycle manager, scoring, compression. The single source of truth. | All users (installed once) |
| **MCP Server** | Primary interface for AI-native clients: Claude Desktop, Cursor, Windsurf, future MCP-aware tools. Exposes Minerva as tools/resources/prompts. | Developers, power users |
| **Browser Extension** | Primary interface for web UIs: ChatGPT, Claude.ai, Gemini. Observes DOM, augments prompts, shows project context panel. | General users |
| **IDE Extension (VS Code/Cursor/Windsurf)** | Deep coding-workflow integration: reads project files, git state, terminal; injects context inline; shows inline context annotations. | Developers |
| **Python/Node SDK + CLI** | Programmatic access; open-source LLM workflows; CI/CD integration; enterprise embedding. | Developers, OSS LLM users |
| **Companion Web Dashboard** (optional, not primary) | Read-only visibility into memory, scoring, token savings. | All users |

### 2.4 Why Not Single-Surface?
- **Browser extension alone** leaves the entire developer market unreachable.
- **VS Code extension alone** leaves the entire non-developer market unreachable.
- **MCP alone** leaves web UI users unreachable (and MCP-aware clients are still <50% of the market).
- **API gateway alone** forces a workflow change and competes with existing routing layers.
- **Desktop app alone** has the highest adoption friction and slowest growth.

### 2.5 Why Not "Pure" Any of Them?
The deciding factor is **adoption without workflow change**. The user must not have to switch tools. Minerva must reach into the tools they already use. This is only possible with multiple surfaces sharing a common engine.

### 2.6 Progressive Onboarding Strategy
A user can adopt Minerva one surface at a time:
1. **Day 0:** Install the Local Service (the brain) + Browser Extension (instant value on ChatGPT).
2. **Day 7:** Install the IDE Extension (developer value).
3. **Day 30:** Configure the MCP Server (Claude Desktop / Cursor power features).
4. **Day 90:** SDK/CLI for advanced workflows.

Each surface ships independently. Each is monetizable independently. None requires the others.

---

## 3. High-Level Architecture Diagram (Text)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           USER'S MACHINE (Local-First)                   │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  Browser    │  │  IDE        │  │  Claude     │  │  CLI /      │      │
│  │  Extension  │  │  Extension  │  │  Desktop /  │  │  Scripts    │      │
│  │  (Web UI)   │  │  (Cursor,   │  │  Cursor /   │  │  (OSS LLMs) │      │
│  │             │  │  Windsurf)  │  │  Windsurf   │  │             │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
│         │                │                │                │             │
│         │    All surfaces speak one protocol (gRPC over local socket)    │
│         │                │                │                │             │
│         └────────────────┴────────┬───────┴────────────────┘             │
│                                  │                                      │
│                                  ▼                                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │              MINERVA LOCAL SERVICE  (the Brain)                  │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │                    MCP SERVER (port, stdio, http)            │  │ │
│  │  │  Exposes: tools, resources, prompts                          │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │                  CONTEXT ENGINE (core)                       │  │ │
│  │  │                                                              │  │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │ │
│  │  │  │  Planner     │  │  Memory      │  │  Retrieval       │   │  │ │
│  │  │  │  Agent       │  │  Agent       │  │  Agent           │   │  │ │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────┘   │  │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │ │
│  │  │  │  Compression │  │  Scoring     │  │  Prompt          │   │  │ │
│  │  │  │  Agent       │  │  Agent       │  │  Builder         │   │  │ │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────┘   │  │ │
│  │  │                                                              │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │              MEMORY SUBSYSTEM (on disk, encrypted)            │  │ │
│  │  │                                                              │  │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │  │ │
│  │  │  │ SQLite   │  │ Vector   │  │ Graph    │  │ Working     │  │  │ │
│  │  │  │ (facts,  │  │ Store    │  │ (entity  │  │ Memory      │  │  │ │
│  │  │  │ tasks,   │  │ (semantic│  │ relation-│  │ (current    │  │  │ │
│  │  │  │ decisions│  │ search)  │  │ ships)   │  │ session)    │  │  │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                      │
│                                  │ HTTPS (only with explicit consent)  │
│                                  ▼                                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │      OPTIONAL CLOUD (paid tier only, opt-in, E2E encrypted)        │ │
│  │      - Cross-device sync (user's keys, not ours)                   │ │
│  │      - Shared team memory (B2B)                                    │ │
│  │      - Heavier embedding models (opt-in)                           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │  Outbound (user's keys, user-controlled)
                                  ▼
              ┌─────────────────────────────────────────────┐
              │   AI MODELS  (user's choice)                │
              │   OpenAI / Anthropic / Google / Local / ... │
              └─────────────────────────────────────────────┘
```

### 3.1 Architectural Principles (encoded in the diagram)
1. **The Local Service is the only required component.** Everything else is an interface to it.
2. **One canonical protocol** (gRPC over local socket + HTTP for browser) between surfaces and the brain. No surface talks to the model directly without going through the brain.
3. **All memory is on disk, encrypted, owned by the user.** The cloud is optional and end-to-end encrypted.
4. **The brain holds the user's API keys**, not the cloud. The cloud, if used, never sees plaintext context or keys.
5. **Each surface can be removed** without losing core functionality. The product degrades gracefully.

---

## 4. Component Breakdown

### 4.1 Surface Layer (clients, optional and additive)

#### 4.1.1 Browser Extension
- **Platforms:** Chrome, Edge, Firefox, Safari (via WebExtensions API).
- **Responsibilities:**
  - Observe ChatGPT / Claude.ai / Gemini / Perplexity DOM events (input field, response received).
  - Inject optimized context into the input field before send.
  - Render a side panel showing project memory, recent decisions, current task state.
  - Forward observation events (what the user typed, what the model said) to the Local Service for memory updates.
- **Out of scope:** Direct model calls. No API keys stored in the extension.
- **Communication:** HTTP/WebSocket to localhost service; falls back to a bundled WASM core if no service is running (graceful degradation).

#### 4.1.2 IDE Extension (VS Code / Cursor / Windsurf)
- **Platforms:** VS Code Marketplace, Open VSX (for Cursor/Windsurf).
- **Responsibilities:**
  - Read project state: file tree, active files, git branch, recent diffs, language server diagnostics, terminal output.
  - Watch files for changes and stream events to the Local Service.
  - Provide inline commands ("@minerva add this to project memory", "@minerva what's the current architecture decision?").
  - Render a sidebar tree of project memory, tasks, and decisions.
  - Augment the in-IDE AI chat (Cursor's Cmd-K, Windsurf's Cascade, Copilot Chat) by intercepting and rewriting prompts.
- **Out of scope:** Replacing the IDE's AI; the IDE remains the source of model calls.
- **Communication:** Same localhost HTTP/WS protocol.

#### 4.1.3 MCP Server
- **Protocol:** Model Context Protocol (stdio, HTTP+SSE, or streamable HTTP).
- **Responsibilities:**
  - Expose Minerva as MCP **tools** (e.g., `minerva_search_project`, `minerva_add_decision`, `minerva_compress_history`).
  - Expose project memory as MCP **resources** (e.g., `minerva://project/goals`, `minerva://project/active-tasks`).
  - Expose canned **prompts** (e.g., "Continue task X with full project context").
- **Out of scope:** Hosting a UI. The MCP host (Claude Desktop, Cursor, etc.) provides the UI.
- **Communication:** Speaks MCP natively on top of the Local Service.

#### 4.1.4 SDK (Python, Node, Go)
- **API surface:** A typed client that mirrors the MCP tools plus higher-level helpers.
- **Use cases:** Scripting, CI/CD integration, building custom agents on top of Minerva, open-source LLM workflows, embedding Minerva into other products (B2B).

#### 4.1.5 CLI
- **Responsibilities:** TUI for power users; scripting; init a project; show memory stats; replay context for debugging.

### 4.2 Brain Layer (the Local Service)

The Local Service is a single binary (or Python/Node process) running on the user's machine. It exposes a localhost API and is the only component that owns the canonical state.

#### 4.2.1 MCP Server (front door)
- The MCP server is the public surface of the brain. It accepts MCP requests, validates them, dispatches to agents, returns results.

#### 4.2.2 Context Engine (the core)
This is where the multi-agent system lives. See §8.

#### 4.2.3 Memory Subsystem
See §6.

#### 4.2.4 Security & Identity
- Holds user API keys in OS-native secure storage (Keychain / Credential Manager / libsecret).
- Owns encryption keys for the local memory store.
- Enforces scope (per-project, per-workspace).

#### 4.2.5 Telemetry & Observability
- Local logs, optional opt-in anonymous usage stats.
- Token-savings dashboard.

### 4.3 Cloud Layer (optional)

Only used by paying users for:
- **Cross-device encrypted sync** (keys held by user, not by us).
- **Team shared memory** (B2B).
- **Optional heavier embedding models** for users on weak hardware.
- **Hosting a marketplace of community-contributed context plugins** (e.g., "Legal context pack", "ML project context pack").

### 4.4 Why This Decomposition?
- **Each surface can ship and monetize independently.** Browser extension can be free + paid; MCP server can be free; SDK is OSS.
- **The brain is the moat.** Anyone can wrap a UI; the engine is the hard part.
- **No circular dependencies.** The brain does not depend on the surfaces. The surfaces depend on the brain.
- **Failure isolation.** If the MCP server crashes, the IDE extension still works. If the browser extension is uninstalled, the IDE integration still works.

---

## 5. Data Flow Diagram (Text)

This is the canonical request lifecycle for a single "AI call" through Minerva.

```
USER                CLIENT                 BRAIN                   MODEL
 │                    │                      │                       │
 │ 1. types prompt    │                      │                       │
 │ ─────────────────► │                      │                       │
 │                    │                      │                       │
 │                    │ 2. observation event │                       │
 │                    │ ───────────────────► │                       │
 │                    │   {surface, raw_     │                       │
 │                    │    prompt, context}  │                       │
 │                    │                      │                       │
 │                    │                      │ 3. PLAN: which agents │
 │                    │                      │    run?               │
 │                    │                      │ ─┐                   │
 │                    │                      │  │ Planner Agent      │
 │                    │                      │ ◄┘                   │
 │                    │                      │                       │
 │                    │                      │ 4. RETRIEVE: relevant │
 │                    │                      │    memory            │
 │                    │                      │ ─┐                   │
 │                    │                      │  │ Retrieval Agent    │
 │                    │                      │  │ (keyword + vector  │
 │                    │                      │  │  + graph + rerank) │
 │                    │                      │ ◄┘                   │
 │                    │                      │                       │
 │                    │                      │ 5. COMPRESS: dedupe,  │
 │                    │                      │    remove outdated,   │
 │                    │                      │    summarize         │
 │                    │                      │ ─┐                   │
 │                    │                      │  │ Compression Agent  │
 │                    │                      │ ◄┘                   │
 │                    │                      │                       │
 │                    │                      │ 6. SCORE: rank by    │
 │                    │                      │    recency, importance│
 │                    │                      │ ─┐                   │
 │                    │                      │  │ Scoring Agent      │
 │                    │                      │ ◄┘                   │
 │                    │                      │                       │
 │                    │                      │ 7. UPDATE MEMORY:    │
 │                    │                      │    persist new facts  │
 │                    │                      │ ─┐                   │
 │                    │                      │  │ Memory Agent       │
 │                    │                      │ ◄┘                   │
 │                    │                      │                       │
 │                    │                      │ 8. BUILD PROMPT      │
 │                    │                      │ ─┐                   │
 │                    │                      │  │ Prompt Builder     │
 │                    │                      │ ◄┘                   │
 │                    │                      │                       │
 │                    │                      │ 9. CALL MODEL        │
 │                    │                      │ ────────────────────►│
 │                    │                      │   {optimized prompt} │
 │                    │                      │                       │
 │                    │                      │ ◄────────────────────│
 │                    │                      │   {model response}   │
 │                    │                      │                       │
 │                    │                      │ 10. OBSERVE & LEARN  │
 │                    │                      │   (extract new facts, │
 │                    │                      │    update scores)     │
 │                    │                      │ ─┐                   │
 │                    │                      │  │ Memory Agent       │
 │                    │                      │ ◄┘                   │
 │                    │                      │                       │
 │                    │ 11. augmented result │                       │
 │                    │ ◄─────────────────── │                       │
 │ 12. sees result    │                      │                       │
 │ ◄───────────────── │                      │                       │
```

### 5.1 Asynchronous Data Flows (background)

```
USER ACTION                BRAIN                           STORAGE
 │                          │                                 │
 │ edits a project file     │                                 │
 │ ───────────────────────► │                                 │
 │   (IDE ext observes)     │                                 │
 │                          │ 1. detect change                │
 │                          │ 2. re-embed relevant chunks     │
 │                          │ ──────────────────────────────► │
 │                          │   {vector store}                │
 │                          │ 3. update graph relationships   │
 │                          │ ──────────────────────────────► │
 │                          │   {graph store}                │
 │                          │ 4. detect contradictions        │
 │                          │    vs. current memory           │
 │                          │ 5. notify user (optional)       │
 │                          │                                 │
 │ closes laptop            │                                 │
 │ ───────────────────────► │                                 │
 │   (system suspend)       │ 1. flush working memory to disk │
 │                          │ 2. encrypt at rest              │
 │                          │ ──────────────────────────────► │
 │                          │ 3. release locks                │
 │                          │                                 │
 │ 24 hours pass            │                                 │
 │                          │ 1. lifecycle job: summarize old  │
 │                          │    conversations, archive       │
 │                          │ ──────────────────────────────► │
 │                          │ 2. decay old scores             │
 │                          │ 3. dedupe across projects        │
 │                          │                                 │
```

### 5.2 Failure Modes per Flow Step
Each step is independently retryable. If the model call fails, the brain has the prepared prompt cached and can retry. If the memory subsystem fails, the brain falls back to last-known-good memory and surfaces a warning. If a surface disconnects, the brain continues to work and surfaces re-sync on reconnect.

---

## 6. Memory System Design

### 6.1 Knowledge Representation: Hybrid Memory System

**Recommendation: Hybrid (Structured Records + Vector Store + Graph).**

A single representation cannot serve all access patterns:

| Access pattern | Best store | Why |
|----------------|-----------|-----|
| "What is the project's goal?" | Structured record (SQLite) | Atomic, exact, fast |
| "Have we discussed OAuth before?" | Vector store | Semantic similarity across past conversations |
| "Which files does the auth module depend on?" | Graph | Relationships, traversal |
| "What did we decide about Postgres vs SQLite?" | Graph + structured | Decision log with linked entities |
| "Show me the current state of work" | Structured + vector | Hybrid query |

### 6.2 Memory Tiers

Minerva uses four memory tiers, mirroring human cognitive architecture:

| Tier | Name | Lifetime | Storage | Size |
|------|------|----------|---------|------|
| **M0** | Working Memory | Current conversation | In-process RAM + WAL | ~50 KB |
| **M1** | Project Memory | Project lifetime | SQLite + vectors + graph | 1–100 MB |
| **M2** | Archive Memory | Months–years | Compressed SQLite + vectors | 100 MB – 1 GB |
| **M3** | Ephemeral Memory | Single prompt cycle | None (computed, not stored) | 0 |

### 6.3 Project Memory Schema (M1)

The project memory is organized into seven record types. These directly map to the user-specified "Project Memory Store" requirements.

#### 6.3.1 Goals
- **Purpose:** Stable, long-lived objectives for the project.
- **Schema:**
  - id, project_id, text, priority (1–5), created_at, updated_at, source, confidence, status (active/superseded/achieved), superseded_by
- **Examples:** "Ship MVP by Q3", "Reduce p99 latency below 200ms", "Pass SOC 2 audit".

#### 6.3.2 Constraints
- **Purpose:** Hard limits the project must respect.
- **Schema:**
  - id, project_id, text, type (technical/business/legal/budget/time), severity (hard/soft), created_at, source
- **Examples:** "Must run on Python 3.11+", "Cannot use GPL libraries", "Team size is 3 engineers", "GDPR applies".

#### 6.3.3 Decisions
- **Purpose:** Architectural and product decisions with rationale.
- **Schema:**
  - id, project_id, decision, rationale, alternatives_considered, decided_by, decided_at, status (current/superseded), supersedes, linked_constraints[], linked_goals[]
- **Examples:** "Use Postgres over MongoDB because [rationale]". Crucial: every decision links to its constraints and goals, enabling impact analysis.
- **Note:** Superseded decisions are *never deleted* — they are kept with `superseded_by` so the model can understand why an old approach was abandoned.

#### 6.3.4 Architecture
- **Purpose:** Stable descriptions of the system's structure.
- **Schema:**
  - id, project_id, component_name, description, technology, relationships[], diagram_ref, last_verified_at, owner
- **Stored as a graph of components.** Each component is a node; relationships (depends_on, calls, deploys_with) are edges.

#### 6.3.5 Active Tasks
- **Purpose:** Work in progress.
- **Schema:**
  - id, project_id, title, description, status (todo/in_progress/blocked/done), assignee, priority, depends_on[], blocks[], created_at, updated_at, last_touched_at, context_refs[]
- **Stored as a directed acyclic graph (DAG) of dependencies.** Context refs point into M0/M1 for the task's working context.

#### 6.3.6 Completed Tasks
- **Purpose:** Historical record of what was done.
- **Schema:** Same as active tasks but `status = done` plus `completed_at`, `outcome`, `learned_facts[]`.
- **Why keep it?** Prevents re-asking "did we already try X?" and provides training signal.

#### 6.3.7 Important Facts
- **Purpose:** Any atomic fact that has proven to matter repeatedly.
- **Schema:**
  - id, project_id, text, category, confidence (0.0–1.0), source (observation/user-stated/inferred), created_at, last_referenced_at, reference_count, verified, contradicts[]
- **Includes:** "The staging DB is read-only on Tuesdays", "Customer X requires invoices in EUR", "Library Y has a memory leak in v2.3".
- **The `contradicts` field** is critical: it links facts that conflict so the model (and the user) can resolve them.

### 6.4 Memory Lifecycle (Creation, Update, Summarization, Archive, Deletion)

#### 6.4.1 Creation Triggers
A new memory record is created when:
- **Explicit user command** ("remember this", "@minerva add decision").
- **Inferred from conversation** — a heuristic or LLM-based extractor identifies a goal/decision/fact in the user's text or the model's response. The user is shown what was extracted and can edit/delete.
- **Observed from the environment** (file changes, git commits, test results) via the IDE extension.
- **Imported** from existing project documentation (README, ADRs, Linear/Jira export).

#### 6.4.2 Update Rules
- A record is **never overwritten in place**. Each update creates a new version with `supersedes` linking.
- The latest version is the "head"; older versions remain queryable but are deprioritized.
- **Contradiction detection:** when a new fact conflicts with an existing fact, both are kept; the user is prompted to resolve.

#### 6.4.3 Summarization
- Triggered when a project's memory exceeds a size threshold (e.g., 50 MB) OR when a record has not been referenced in N days AND the project has >5000 records.
- **Algorithm:** Hierarchical clustering of related facts → LLM-generated summary per cluster → original facts archived with summary as the new queryable record.
- **Invariant:** No information is destroyed. Originals remain in M2 archive and can be promoted back to M1.

#### 6.4.4 Archiving
- Records move from M1 to M2 when:
  - Project is marked inactive.
  - Record age > 90 days AND reference count = 0 AND confidence < 0.5.
  - User explicitly archives.
- Archived records are compressed, optionally encrypted, and excluded from default retrieval but available on explicit query.

#### 6.4.5 Deletion
- **User-initiated only.** Minerva never deletes user data autonomously.
- "Soft delete" by default (recoverable for 30 days).
- "Hard delete" requires explicit command and is irreversible.
- All deletions are logged in an audit trail.

### 6.5 Memory Indexing

Three indexes, kept in sync:
1. **SQLite FTS5** for exact and BM25 keyword search.
2. **Vector index** (HNSW or IVF) for semantic search. Embeddings generated locally by a small embedding model (e.g., BGE-small, ~130MB) so no data leaves the machine.
3. **Graph index** (KùzuDB or equivalent) for relationship traversal.

Sync strategy: write to SQLite first (source of truth), then async-update vectors and graph. A periodic reconciliation job ensures consistency.

---

## 7. Retrieval System Design

### 7.1 What Should Be Included (and Why)

A piece of information is included in the prompt when it scores above a threshold on a weighted combination of five signals.

### 7.2 Context Scoring System

Each candidate context item receives a score:

```
score(item, query, project) =
    w_r · recency(item)
  + w_i · importance(item)
  + w_s · semantic_relevance(item, query)
  + w_k · keyword_relevance(item, query)
  + w_g · graph_proximity(item, focus_entity)
  + w_c · confidence(item)
  + w_u · user_priority(item)
```

Where the weights `w_*` sum to 1 and are dynamically adjusted per query type (e.g., bug-fix queries weight recency higher; architecture queries weight graph proximity higher).

#### 7.2.1 Recency
- `recency(item) = exp(-Δt / τ)` where Δt is time since last reference and τ is a half-life (default 7 days).
- **Bumped** by `last_referenced_at` — items the user has recently read or referenced get a recency boost regardless of age.

#### 7.2.2 Importance
- Manually set by user (1–5) OR auto-derived from: how often referenced, how many other items link to it, whether it's a decision or constraint.

#### 7.2.3 Semantic Relevance
- Cosine similarity of query embedding to item embedding.
- Embeddings produced by a local model. No data egress.

#### 7.2.4 Keyword Relevance
- BM25 score from SQLite FTS5.

#### 7.2.5 Graph Proximity
- Shortest-path distance in the project graph from the query's focus entity (the file/component the user is currently working on, or the entity named in the query).
- `graph_proximity = 1 / (1 + distance)`.

#### 7.2.6 Confidence
- Confidence score stored on the item (0–1). User can correct.

#### 7.2.7 User Priority
- Manual pinning. Items the user explicitly pins are always included unless budget exhausted, in which case they win the budget allocation.

### 7.3 Retrieval Pipeline

```
Query
  │
  ▼
[1] Query Understanding
  │   - Extract entities (files, components, decisions)
  │   - Classify query type (debug, design, explain, implement, review)
  │   - Determine focus entity
  │
  ▼
[2] Candidate Generation (parallel)
  │   - BM25 over SQLite FTS        → top 50
  │   - Vector search over embeddings → top 50
  │   - Graph neighborhood of focus → top 30
  │   - Recent working memory       → top 20
  │   → Union, dedupe ≈ 150 candidates
  │
  ▼
[3] Scoring
  │   - Compute weighted score per candidate
  │   - Apply hard filters (excluded tags, contradictions)
  │
  ▼
[4] Diversity (MMR — Maximal Marginal Relevance)
  │   - λ · relevance − (1−λ) · max_sim_to_selected
  │   - Ensures we don't return 5 nearly-identical snippets
  │
  ▼
[5] Token Budget Allocation
  │   - Allocate budget: 70% to top scored items, 20% to project
  │     preamble (goals/constraints/decisions), 10% to recent
  │     conversation buffer
  │   - Greedy fill until budget exhausted
  │
  ▼
[6] Re-ranking (optional, larger model)
  │   - Use a local cross-encoder model to re-rank top 20
  │   - Only invoked when ambiguity is high
  │
  ▼
Ordered list of context items
```

### 7.4 What Should Be Excluded

Hard exclusions (configurable per project):
- **Outdated facts** whose `superseded_by` is set.
- **Contradicted facts** unless explicitly invoked.
- **Archived records** unless explicitly invoked.
- **Tokens the user has marked private** (e.g., API keys pasted in chat).
- **PII the user has flagged**.
- **Items that fail a freshness check** (e.g., file content referenced by a fact no longer matches the file on disk → demote or drop).

Soft exclusions (down-weighted):
- Items rarely referenced.
- Items with low confidence.
- Items in unrelated projects (multi-project installations).

### 7.5 Retrieval Latency Target
- Candidate generation: <50 ms (local, on-disk).
- Scoring: <100 ms.
- Total retrieval budget: **<200 ms p99** on a 5-year-old laptop.
- This is a hard constraint: Minerva must feel instant or users will turn it off.

---

## 8. Prompt Builder Design

### 8.1 Universal Prompt Format

Minerva produces prompts in a **universal XML-tagged Markdown** format that all major LLMs understand. XML tags survive tokenization cleanly and are honored by GPT-4+, Claude 3+, Gemini, and most open-source models.

```
<system>
  You are [persona]. [Operating principles].
</system>

<project_context>
  ## Project Goals
  <goals>
    - [Goal 1 — priority 5]
    - [Goal 2 — priority 3]
  </goals>

  ## Active Constraints
  <constraints>
    - [Hard constraint 1]
    - [Soft constraint 2]
  </constraints>

  ## Architectural Decisions
  <decisions>
    - [Current decision] — because [rationale]. Supersedes [old decision].
  </decisions>

  ## Active Tasks
  <tasks>
    - [In progress] [Task A] — last touched 2h ago, blocked by [B]
    - [Todo] [Task C] — priority 4
  </tasks>
</project_context>

<relevant_history>
  <!-- Top-k retrieved context items, in score order -->
  <item id="..." type="decision" score="0.87">
    [Content of retrieved item]
  </item>
  <item id="..." type="fact" score="0.73">
    [Content of retrieved item]
  </item>
  <!-- ... -->
</relevant_history>

<conversation>
  <!-- Recent turns, compressed. Older turns summarized. -->
  <turn role="user" t="...">[User message or summary]</turn>
  <turn role="assistant" t="...">[Assistant message or summary]</turn>
</conversation>

<user_message>
[Current user query]
</user_message>
```

### 8.2 Why This Structure?

- **`<system>`** is honored by every major model. Persona and operating principles go here.
- **`<project_context>`** is stable, small (typically <2K tokens), and makes the model aware of goals/constraints/decisions before it sees anything else.
- **`<relevant_history>`** is the retrieval output. Items are tagged with `type` and `score` so the model can self-prioritize if needed.
- **`<conversation>`** is a sliding window of recent turns. Older turns are summarized; very old turns are dropped unless explicitly relevant.
- **`<user_message>`** is the actual query, isolated so the model treats it as the immediate ask.

### 8.3 Token Budget Management

A model has a fixed context window. Minerva allocates the budget:

| Section | Default % | Notes |
|---------|-----------|-------|
| `<system>` | 5% | Fixed persona and principles |
| `<project_context>` | 15% | Trimmed to top-priority items if over budget |
| `<relevant_history>` | 50% | The main retrieval output |
| `<conversation>` | 25% | Sliding window; older turns summarized |
| `<user_message>` | 5% | Always preserved verbatim |

The budget is configurable per-model. For Claude with 200K context, the budget is generous. For a local 8B model with 8K context, the budget is tight and aggressive truncation applies.

### 8.4 Prompt Builder Algorithm

```
build_prompt(query, project, model_spec):
    budget = model_spec.context_window - reserved_for_response
    budget = budget · safety_margin (default 0.85)

    sections = {
        system:        render_persona(project),
        project_ctx:   trim_to_budget(render_project_context(project), 0.15·budget),
        history:       trim_to_budget(render_retrieval(retrieve(query, project)), 0.50·budget),
        conversation:  trim_to_budget(render_recent_turns(project.session), 0.25·budget),
        user_message:  query  // never trimmed
    }

    # Re-balance if any section underfilled its allocation
    redistribute(sections, budget)

    return assemble_xml(sections)
```

### 8.5 Compression Within the Builder

When a section exceeds its allocation, the builder applies:
1. **Summarization** (LLM-based, using a small local model) for long conversation turns.
2. **Truncation with marker** for retrieval items (drop lowest-scored first; mark drops with `[N lower-priority items omitted]`).
3. **Hard truncation** of project context, but only after warning the user.

### 8.6 Model-Specific Adaptations

| Model | Adaptation |
|-------|-----------|
| OpenAI (GPT-4+) | Native XML tag honoring; use `developer` role for `<system>`. |
| Anthropic (Claude 3+) | Excellent XML comprehension; system goes in `system` parameter; can use `<thinking>` tags for extended reasoning. |
| Google (Gemini) | XML works; system instruction prepended. |
| Local (Llama, Mistral, Qwen) | XML works for most modern models; older models (<7B) may need Markdown fallback. |

The Prompt Builder detects the target model and adjusts:
- Which parameter holds the system prompt.
- Whether to enable extended thinking (`<thinking>`).
- The token budget per section.
- Whether to include safety preamble (some providers require it).

---

## 9. Technology Stack Recommendation

### 9.1 Principles
- **Local-first.** Default everything runs on the user's machine.
- **Polyglot where it helps.** Use the right tool per job.
- **Boring for infrastructure, novel for the engine.** Postgres-tier boringness for the plumbing; LLM-graded novelty for the context engine.
- **Embeddable.** Any component can be used standalone.

### 9.2 Recommended Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Local Service (brain)** | **Python (FastAPI) or Rust** | Python: rich AI ecosystem, fast iteration. Rust: performance, single binary, lower memory. Default: **Rust core + Python bindings** for the engine. |
| **MCP Server** | Official MCP SDK (Python or Rust) | MCP is the standard; no reason to deviate. |
| **Browser Extension** | TypeScript + React (Manifest V3) | Industry standard; small bundle; works on all major browsers. |
| **IDE Extension** | TypeScript, VS Code Extension API | Open VSX distribution for Cursor/Windsurf; one codebase. |
| **SDK** | Python (primary), TypeScript, Go | Python and TS cover >90% of developers. |
| **CLI** | Python (Click) or Rust (Clap) | Either works; Rust for single-binary distribution. |
| **Local DB (structured)** | **SQLite + FTS5** | Zero-config, embedded, FTS5 is excellent. |
| **Vector store** | **LanceDB** or **SQLite-VSS** | Embedded, no server, performant. LanceDB preferred for larger projects. |
| **Graph store** | **KùzuDB** (embedded graph DB) | Embedded, fast, Cypher-compatible. |
| **Embedding model** | **BGE-small (local)** | ~130MB, runs on CPU, strong quality. |
| **Re-ranking model** | **bge-reranker-base (local)** | Optional, used only on ambiguous queries. |
| **Summarization model** | **Phi-3-mini or Qwen2.5-3B (local)** | For conversation summarization; user can swap in larger. |
| **IPC** | **gRPC over Unix socket** (machine-local) + **HTTP/WS** (for browser) | Fast, typed, debuggable. |
| **Encryption** | **AES-256-GCM** (data) + **libsodium** (key management) | Standard, audited. |
| **Packaging** | **Tauri** for any desktop UI elements | Tiny binaries, cross-platform. |
| **Cloud (optional)** | **Supabase** or **Postgres + S3** | Boring, scalable, encrypted-at-rest. |
| **Auth (cloud)** | **OAuth + WebAuthn** | No password storage burden. |

### 9.3 What We Are Explicitly *Not* Using
- **No LangChain / LlamaIndex as a dependency.** Both are too opinionated and too heavy. We borrow patterns but ship our own primitives.
- **No required cloud service for v1.** Every paid feature in v1 must work offline.
- **No telemetry by default.** Opt-in only.
- **No proprietary embedding model that requires a cloud API.** Local embeddings keep data on-device.

### 9.4 Build vs. Buy
- **Build:** Context engine, scoring, lifecycle, prompt builder. This is the moat.
- **Buy/embed:** SQLite, LanceDB, KùzuDB, embedding models, MCP SDK. These are commodities.
- **Reuse via MCP:** Avoid reimplementing what the MCP host (Claude Desktop, Cursor) already does well.

---

## 10. MVP Scope

### 10.1 Phase 1 — "Project Memory via MCP" *(ship independently)*
**Goal:** Prove the brain works for AI-native developers.

**In scope:**
- Local service with MCP server (stdio).
- SQLite-backed project memory (Goals, Constraints, Decisions, Active Tasks, Completed Tasks, Important Facts).
- Basic retrieval: BM25 + vector.
- Basic prompt builder.
- CLI for project init, memory CRUD, prompt preview.
- Single embedding model (BGE-small, local).
- Documentation: how to configure Cursor / Claude Desktop / Windsurf.

**Out of scope:**
- Browser extension.
- IDE extension.
- Graph store (use simple relationships in SQLite for now).
- Cloud sync.
- Team features.

**Success criteria:**
- A developer configures the MCP server in Cursor and sees project goals/constraints/decisions automatically prepended to every prompt.
- 200 beta users ship to daily-driver status.

**Monetization:** Free. Building the install base.

**Effort estimate:** 8–12 weeks, 2 engineers.

---

### 10.2 Phase 2 — "Web UI Augmentation" *(ship independently)*
**Goal:** Reach the non-developer / ChatGPT web audience.

**In scope:**
- Browser extension (Chrome, then Edge/Firefox).
- DOM observer for ChatGPT, Claude.ai, Gemini.
- Prompt injection before send.
- Side panel showing project memory.
- Shared brain protocol (browser ext ↔ local service).
- WASM fallback so the extension works even without the local service installed (read-only mode).

**Out of scope:**
- Direct web-UI manipulation beyond prompt injection.
- Web UI for memory editing (use the CLI/SDK).
- Mobile browsers.

**Success criteria:**
- 5,000 browser extension installs.
- Measured token savings ≥30% on average.
- Measured user-reported quality improvement ≥20%.

**Monetization:** Free tier (1 project), paid tier (unlimited projects, cloud sync).

**Effort estimate:** 10–14 weeks, 2 engineers + 1 designer.

---

### 10.3 Phase 3 — "IDE-Native" *(ship independently)*
**Goal:** Capture the developer workflow fully.

**In scope:**
- VS Code extension (also distributed via Open VSX for Cursor/Windsurf).
- File watcher → memory updates.
- Git integration → decisions inferred from commits.
- Inline commands (add to memory, query memory).
- Sidebar UI.
- Hook into Cursor's Cmd-K, Windsurf's Cascade, Copilot Chat prompt rewriting.

**Out of scope:**
- Replacing the IDE's AI.
- Cross-IDE sync (each IDE has its own extension).

**Success criteria:**
- 10,000 IDE extension installs.
- 50% of Phase 1 MCP users also install IDE extension.

**Monetization:** Bundled with paid tier.

**Effort estimate:** 10–12 weeks, 2 engineers.

---

### 10.4 Phase 4 — "The Real Engine" *(ship independently)*
**Goal:** Make the brain genuinely smart.

**In scope:**
- Graph store (KùzuDB).
- Knowledge graph relationships between components, files, decisions, tasks.
- Multi-agent system (Planner, Retrieval, Compression, Scoring, Memory, Prompt Builder) — fully wired.
- Re-ranking model.
- Cross-encoder reranker.
- Local LLM for summarization.
- Conversation lifecycle (auto-summarize, archive, decay).
- Cross-project deduplication.

**Out of scope:**
- Cloud features.
- Team features.
- Mobile.

**Success criteria:**
- Measurable quality lift vs. Phase 1 (A/B test: with-graph vs. without).
- Token reduction ≥50% vs. raw conversation.

**Monetization:** Paid tier.

**Effort estimate:** 16–20 weeks, 3 engineers (one ML, two systems).

---

### 10.5 Phase 5 — "Ecosystem" *(ship independently)*
**Goal:** Become the default context layer.

**In scope:**
- Cloud sync (E2E encrypted).
- Team shared memory (B2B).
- Plugin marketplace ("Legal context pack", "ML research context pack").
- SDK GA (Python, TS, Go).
- Public API (for developers building on top).
- Public benchmark ("Minerva Quality Score") — publish a leaderboard of models × context quality.
- Enterprise features (SSO, audit logs, on-prem deployment).
- Mobile companion app (read-only).

**Out of scope (yet):**
- Our own model.
- Our own chat UI.

**Success criteria:**
- 100K active users.
- 10 paying B2B teams.
- Cited as "the context layer" by at least 3 major AI vendors.

**Monetization:** Multi-tier (free, pro, team, enterprise).

**Effort estimate:** 24+ weeks, 5+ engineers.

---

## 11. Future Expansion Plan

### 11.1 Near-Term (6–12 months)
- **Voice input integration** with web UIs (Whisper local).
- **Screenshot/image context** — capture and reference visual UI states.
- **MCP-native memory marketplace** — community-contributed context packs.
- **Per-provider prompt optimization** — fine-tuned prompt structures per model family.

### 11.2 Mid-Term (12–24 months)
- **Minerva Cloud** — hosted version for users who don't want to install locally.
- **Team plans** — shared project memory with role-based access.
- **Cross-device sync** — phone, tablet, laptop, all seeing the same project memory.
- **Workflow automations** — "after every commit, summarize changes and add to project memory".
- **Time-travel debugging for AI** — replay any past conversation with current context to see how the model would respond now.

### 11.3 Long-Term (24–48 months)
- **Open Minerva standard** — publish the memory schema and retrieval API as an open spec. Compete with the model layer, not against it.
- **Minerva for agents** — when AI agents become ubiquitous, Minerva becomes the shared memory layer they all read from. This is the highest-leverage future: every agent in an org reads/writes through Minerva.
- **Minerva for training data curation** — use the memory store to generate high-quality fine-tuning datasets from a team's actual project history.
- **Minerva for compliance** — every prompt is logged, every fact is traceable. Required for regulated industries.

### 11.4 The 10-Year Vision
Minerva becomes the **filesystem of AI**. Every AI interaction assumes a Minerva underneath. The model is the CPU; the context is the memory; Minerva is the OS.

---

## 12. Risks and Failure Modes

### 12.1 Adoption Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Users don't understand the value | High | High | Show token savings and quality lift in the first 60 seconds. Demo before install. |
| Installation friction too high | High | High | Browser extension first (zero install), MCP second (one config line), local service third (one binary). |
| Competing with the model providers | Medium | Fatal | Don't. Be orthogonal. The model is the CPU; Minerva is the OS. We never compete on model quality. |
| Vendor blocks our integration | Medium | Medium | Multiple surfaces. If OpenAI blocks browser ext, we still have MCP + IDE. |

### 12.2 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Embedding model quality insufficient | Medium | Medium | Allow swap. Provide multiple defaults. |
| Local performance too slow | Medium | High | Rust for hot paths; aggressive caching; on-device model selection by hardware tier. |
| Browser UI DOM changes break injection | High | Medium | Robust observation via accessibility tree + DOM diffing, not brittle selectors. Multi-signal confirmation. |
| Vector store corruption | Low | High | SQLite WAL + periodic snapshots + repair tools. |
| Privacy leak via cloud | Low | Fatal | E2E encryption. Cloud never sees plaintext. Keys never leave device unless user opts in. |

### 12.3 Product Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Users dump everything into memory, degrading quality | High | High | Default to selective capture. Show memory stats. Provide easy "forget" commands. |
| Memory becomes a liability (stale facts) | Medium | High | Confidence scores, contradiction detection, periodic freshness audits. |
| Token budget miscalculation causes output truncation | Medium | High | Always reserve response budget; never trim user message; show warning. |
| Over-engineering delays ship | High | High | Ship Phase 1 in 12 weeks. Every phase must be independently shippable. |

### 12.4 Business Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Model providers build their own context layer | Medium | Fatal | We are already local-first, model-agnostic, and across all surfaces. They will likely not build all of this. |
| Open-source clones | High | Low | OSS the SDK and basic engine; monetize the hosted service, team features, and benchmark. |
| Slow user growth | Medium | High | Browser extension virality; MCP discoverability; developer word-of-mouth. |

### 12.5 The Single Biggest Failure Mode
**Building a SaaS instead of a middleware.** If Minerva becomes "yet another chat UI" it dies. It must remain the layer *under* the user's existing tools. Every product decision should pass the test: *"Does this make Minerva sit orthogonal to the model and the interface, or does it make us a competitor?"* The answer must always be orthogonal.

---

## 13. Competitive Analysis

| Dimension | Cursor | Windsurf | Claude Code | ChatGPT Projects | **Minerva** |
|-----------|--------|----------|-------------|------------------|---------------|
| **Owns context across tools?** | No (Cursor only) | No (Windsurf only) | No (Claude Code only) | No (ChatGPT web only) | **Yes** |
| **Model-agnostic?** | Partial (Anthropic-first, supports others) | Partial (multi-model but locked to Windsurf) | No (Claude only) | No (OpenAI only) | **Yes** |
| **Provider-agnostic (web/IDE/CLI)?** | No (IDE only) | No (IDE only) | No (CLI only) | No (web only) | **Yes** |
| **Local-first?** | No (cloud) | No (cloud) | No (cloud) | No (cloud) | **Yes** |
| **User owns memory?** | Partial (server-side) | Partial (server-side) | No | No | **Yes** (on disk, encrypted) |
| **Token-efficient?** | No | No | No | No | **Yes** (primary feature) |
| **Cross-project memory?** | No | No | No | Manual projects | **Yes** (graph) |
| **Works offline?** | No | No | No | No | **Yes** |
| **Works with local LLMs?** | Partial | Partial | No | No | **Yes** |
| **Open standard?** | No (proprietary) | No (proprietary) | No | No | **Yes** (publishes schema) |
| **Reduces hallucination?** | No | No | No | No | **Yes** (contradiction detection, freshness) |
| **Long-term viability** | Strong | Strong | Strong | Strong | **Strong + immune to model wars** |

### 13.1 Why Competitors Cannot Easily Replicate Minerva

- **Cursor/Windsurf** are locked to the IDE form factor. Building a browser extension and a model-agnostic memory layer is a major pivot away from their current identity.
- **Claude Code** is locked to Anthropic and the CLI. Becoming model-agnostic contradicts Anthropic's strategic interest in being the model layer.
- **ChatGPT Projects** is locked to the web UI and OpenAI. Becoming model-agnostic contradicts OpenAI's interest.
- **All of them** are cloud-first; becoming local-first is a 180-degree turn in architecture and business model.

Minerva occupies the only cell of the matrix that none of them want: **model-agnostic, provider-agnostic, local-first, orthogonal to both axes.** This is not just a feature — it is the strategic moat.

### 13.2 The One Risk We Share With All of Them
The biggest existential risk to all AI products, including Minerva, is that the **model becomes so good it doesn't need context management.** A model with effectively infinite context, perfect recall, and built-in contradiction detection would obsolete much of Minerva's value.

Mitigation: even in that future, Minerva remains the **user-owned, cross-tool, cross-model memory layer** — the place where the *user's* structured knowledge lives, regardless of what model reads it. The product evolves from "context cleaner" to "personal knowledge layer for AI", which is a larger and more durable category.

---

## 14. Final Recommendation Summary

| Decision | Recommendation |
|----------|---------------|
| Form factor | **Hybrid** (Local Service + MCP + Browser Ext + IDE Ext + SDK) |
| Memory model | **Hybrid** (SQLite + Vector + Graph) |
| Multi-agent | **Yes** (Planner, Retrieval, Compression, Scoring, Memory, Prompt Builder) |
| Cloud dependency | **None for v1**; opt-in E2E-encrypted cloud later |
| Pricing model | **Freemium**, paid for power features and team |
| MVP (Phase 1) | **MCP server with project memory** — ship in 12 weeks |
| Primary moat | **Local-first, model-agnostic, provider-agnostic, orthogonal positioning** |
| Strategic identity | **The filesystem of AI** |

**One-sentence positioning:** *Minerva is to AI models what a filesystem is to a CPU — without it, the model is fast but forgetful; with it, the model becomes a real collaborator.*

---

*End of design document.*
