# Minerva V5 Clean Benchmark Report

This report details the final clean benchmark results for Minerva V4 Multi-Mode Retrieval compared with the Naive baseline.

## 1. Executive Performance Metrics Summary

| Performance Metric | Naive Long-Context (Control) | Minerva (V4 Multi-Mode) | Delta / Change |
| :--- | :---: | :---: | :---: |
| **Average Correctness (0-10)** | 10.00 | 9.92 | -0.08 |
| **Average Completeness (0-10)** | 10.00 | 9.92 | -0.08 |
| **Average Hallucination Risk (0-10)** | 7.50 | 2.07 | -5.43 |
| **Total Tokens Consumed** | 317,794 | 98,413 | **69.03% reduction** |
| **Overall Quality Index** | 12.50 | 17.77 | **+42.13% change** |

## 2. Detailed Performance Table per Question

| QID | Category | Naive Tokens | Minerva Tokens | Naive Corr/Comp/Hall | Minerva Corr/Comp/Hall | Status |
| :---: | --- | :---: | :---: | :---: | :---: | :---: |
| 1 | Historical Audit | 10592 | 3264 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 2 | Historical Audit | 10596 | 3290 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 3 | Historical Audit | 10593 | 3296 | 10.0/10.0/7.5 | 10.0/10.0/5.0 | ✅ Pass |
| 4 | Historical Audit | 10594 | 3288 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 5 | Historical Audit | 10597 | 3296 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 6 | Decision History | 10594 | 3298 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 7 | Decision History | 10594 | 3268 | 10.0/10.0/7.5 | 10.0/10.0/3.0 | ✅ Pass |
| 8 | Decision History | 10592 | 3260 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 9 | Current State | 10593 | 3262 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 10 | Current State | 10590 | 3291 | 10.0/10.0/7.5 | 10.0/10.0/5.0 | ✅ Pass |
| 11 | Current State | 10592 | 3278 | 10.0/10.0/7.5 | 10.0/10.0/5.0 | ✅ Pass |
| 12 | Current State | 10592 | 3275 | 10.0/10.0/7.5 | 10.0/10.0/3.0 | ✅ Pass |
| 13 | Current State | 10594 | 3283 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 14 | Active Tasks | 10595 | 3273 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 15 | Active Tasks | 10594 | 3253 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 16 | Active Tasks | 10593 | 3276 | 10.0/10.0/7.5 | 10.0/10.0/3.0 | ✅ Pass |
| 17 | Active Tasks | 10590 | 3293 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 18 | Active Tasks | 10590 | 3290 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 19 | Architecture | 10593 | 3294 | 10.0/10.0/7.5 | 10.0/10.0/3.0 | ✅ Pass |
| 20 | Architecture | 10598 | 3294 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 21 | Architecture | 10592 | 3276 | 10.0/10.0/7.5 | 10.0/10.0/3.0 | ✅ Pass |
| 22 | Architecture | 10589 | 3280 | 10.0/10.0/7.5 | 10.0/10.0/5.0 | ✅ Pass |
| 23 | Architecture | 10598 | 3275 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 24 | Dependency Analysis | 10588 | 3280 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 25 | Dependency Analysis | 10593 | 3309 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 26 | Dependency Analysis | 10595 | 3270 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 27 | Broad Project Review | 10596 | 3292 | 10.0/10.0/7.5 | 7.5/7.5/3.0 | ❌ Fail |
| 28 | Broad Project Review | 10593 | 3253 | 10.0/10.0/7.5 | 10.0/10.0/1.0 | ✅ Pass |
| 29 | Broad Project Review | 10592 | 3273 | 10.0/10.0/7.5 | 10.0/10.0/3.0 | ✅ Pass |
| 30 | Broad Project Review | 10592 | 3283 | 10.0/10.0/7.5 | 10.0/10.0/3.0 | ✅ Pass |

## 3. Category Performance Summary

| Category | Questions | Naive Avg | Minerva Avg | Delta |
| --- | :---: | :---: | :---: | :---: |
| Broad Project Review | 4 | 10.00 | 9.38 | -0.62 |
| Historical Audit | 5 | 10.00 | 10.00 | +0.00 |
| Decision History | 3 | 10.00 | 10.00 | +0.00 |
| Current State | 5 | 10.00 | 10.00 | +0.00 |
| Active Tasks | 5 | 10.00 | 10.00 | +0.00 |
| Architecture | 5 | 10.00 | 10.00 | +0.00 |
| Dependency Analysis | 3 | 10.00 | 10.00 | +0.00 |
