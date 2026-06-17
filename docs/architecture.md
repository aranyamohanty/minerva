# Minerva Architecture

This document describes the high-level system design and directory structure of **Minerva**.

---

## 1. System Overview

Minerva runs as a local background daemon that serves as a single source of truth for your AI assistant's context.

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
│         │              Speaks Model Context Protocol                     │
│         │                │                │                │             │
│         └────────────────┴────────┬───────┴────────────────┘             │
│                                  │                                      │
│                                  ▼                                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │              MINERVA LOCAL SERVICE  (the Brain)                  │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │                    MCP SERVER (stdio / fastmcp)              │  │ │
│  │  │  Exposes: tools, resources, prompts                          │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │                  CONTEXT ENGINE (core)                       │  │ │
│  │  │  - Embeddings (ONNX Runtime, Xenova/bge-small-en-v1.5)       │  │ │
│  │  │  - Retrieval Engine (Hybrid Search: FTS5 + Embeddings)        │  │ │
│  │  │  - Prompt Builder (Token budgeting & XML assembly)            │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │              MEMORY SUBSYSTEM (SQLite Database)               │  │ │
│  │  │  - Structured records: Goals, Constraints, Decisions, Tasks   │  │ │
│  │  │  - FTS5 Virtual Tables (Full-text indexes)                    │  │ │
│  │  │  - Vectors and relationships (Links table)                     │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Memory Model Tiers

Minerva models human cognition by splitting memory into four tiers:
- **M0: Working Memory**: Current session data and active terminal inputs. (In-RAM/WAL).
- **M1: Project Memory**: Relational facts, active tasks, design decisions, constraints, and goals. (Stored in SQLite).
- **M2: Archive Memory**: Older logs and superseded decisions. Kept queryable but deprioritized during ranking.
- **M3: Ephemeral Memory**: The transient context compiled specifically for a single prompt cycle (recomputed dynamically).

---

## 3. SQLite Database Schema

The SQLite schema represents the core knowledge representation. It is structured into seven record types:
1. **Goals**: Long-lived objectives (`goals` table).
2. **Constraints**: Development constraints, severity, and type (`constraints` table).
3. **Decisions**: Architectural and product decisions, including a self-referential `supersedes_id` to trace migration histories (`decisions` table).
4. **Tasks**: Development task DAG tracking dependencies (`tasks` table).
5. **Facts**: General atomic project facts (`facts` table).
6. **Links**: Relational linking between any two entities (`links` table).
7. **Embeddings**: Local 384-dimensional vector store (`embeddings` table).

---

## 4. Model Context Protocol (MCP) Server

Minerva is exposed via a standard stdio Model Context Protocol (MCP) server:
- **Tools**: CRUD actions such as `minerva_add_goal`, `minerva_add_decision`, and `minerva_link_entities`.
- **Resources**: Exposes lists of active goals (`minerva://project/goals`), constraints (`minerva://project/constraints`), current decisions (`minerva://project/decisions`), and active tasks (`minerva://project/active-tasks`).
- **Prompts**: Provides the `compile_context` prompt template which retrieves relevant items and compiles them into an XML structure.
