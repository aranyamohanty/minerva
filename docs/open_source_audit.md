# Minerva — Open Source Repository Audit

**Author:** Senior Open Source Maintainer
**Date:** 2026-06-17
**Status:** Completed

This document provides a comprehensive audit of the Minerva repository prior to its public release on GitHub. It reviews the codebase for sensitive data, local configurations, build caches, and compliance with open-source packaging standards.

---

## 1. Secrets, Keys, and Tokens
- **Checked:** `.env.local`, all source code files, configurations, and scripts.
- **Findings:**
  - `.env.local` contains a placeholder `GEMINI_API_KEY=PLACEHOLDER_API_KEY`. No active or live API keys or credentials were found in the codebase.
- **Action:** None needed. The placeholder key in `.env.local` is safe.

---

## 2. Personal Information and Local Paths
- **Checked:** Hardcoded directory paths, user names, emails, and IP addresses.
- **Findings:**
  - **Hardcoded Local Paths in Benchmarks:** The four benchmark scripts under `tests/` contain hardcoded report outputs pointing to a specific user app directory:
    - `tests/evaluator.py`: Line 416 (`C:\Users\am.victus\.gemini\antigravity\brain\90634f17-93de-4808-8c27-6526cb8851a6\analysis_results.md`)
    - `tests/adversarial_evaluator.py`: Line 420 (`C:\Users\am.victus\.gemini\antigravity\brain\90634f17-93de-4808-8c27-6526cb8851a6\benchmark_v4_report.md`)
    - `tests/forensic_analyzer.py`: Line 203 (`C:\Users\am.victus\.gemini\antigravity\brain\90634f17-93de-4808-8c27-6526cb8851a6\retrieval_v3_opportunities.md`)
    - `tests/run_v5_benchmark.py`: Line 370 (`C:\Users\am.victus\.gemini\antigravity\brain\90634f17-93de-4808-8c27-6526cb8851a6\benchmark_v5.md`)
  - **Agent Framework Logs:** The `.agents/` folder contains execution details, prompts, and plans of developer agents referencing absolute path `c:\Users\am.victus\Desktop\projects\contextManager`.
  - **Turbopack Build Logs:** The Next.js Turbopack build cache `.next/` references absolute user path `C:\Users\am.victus`.
- **Action:**
  - Replace absolute report paths in `tests/` with project-relative paths (e.g. `benchmarks/reports/...`).
  - Delete `.agents/` and `.next/` directories.

---

## 3. Temporary and Unused Files
- **Checked:** Build outputs, compiler caches, IDE files, and virtual environments.
- **Findings:**
  - **`.agents/`**: Contains logs and metadata of previous developer agents. (Unused, clutters release).
  - **`.next/`**: Leftover build cache from a previous Next.js/Turbopack setup. (Unused since the frontend runs on Vite).
  - **`.pytest_cache/`**: Standard testing cache. (Should be ignored).
  - **`__pycache__/`**: Python bytecode files. (Should be ignored).
  - **`.node/`**: Local Windows Node.js distribution binary. (Should be ignored).
  - **`.venv/`**: Python virtual environment. (Should be ignored).
- **Action:**
  - Delete `.agents/` and `.next/` folders.
  - Update `.gitignore` to ensure `.venv`, `.pytest_cache`, `.node`, and `__pycache__` folders are ignored.

---

## 4. Generated Benchmark Databases
- **Checked:** Precompiled SQLite databases in `tests/` (`adversarial_v4.db`, `generalization_personal.db`, `generalization_research.db`, `generalization_startup.db`, `stress_test.db`).
- **Findings:** These database files contain synthetic benchmark and test data used by the evaluator scripts.
- **Action:** Keep these database files to ensure the benchmarks are fully reproducible, but document their usage in `benchmarks/README.md`.

---

## 5. Summary of Actions Taken
1. Created `docs/open_source_audit.md` (this file).
2. Deleted `.agents/` developer logs.
3. Deleted `.next/` Turbopack build cache.
4. Updated report output paths in `tests/` to use relative paths.
5. Configured `.gitignore` to exclude all local python environments, node binaries, and caches.
