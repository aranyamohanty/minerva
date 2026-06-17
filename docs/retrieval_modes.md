# Minerva Retrieval Engine & Search Modes

This document explains the search and retrieval mechanisms implemented in the **Minerva** engine.

---

## 1. Multi-Mode Hybrid Search

Minerva uses a hybrid retrieval pipeline combining lexical, semantic, and relational search to extract relevant context from project databases.

```
                  Search Query
                       │
                       ▼
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
    Lexical Search             Semantic Search
    (SQLite FTS5 BM25)         (ONNX BGE-small)
         │                           │
         ▼                           ▼
    Lexical Matches            Semantic Matches
         │                           │
         └─────────────┬─────────────┘
                       │
                       ▼
              Relational Boosting
             (Link Graph Lookup)
                       │
                       ▼
              Ranked Context Items
```

---

## 2. Lexical Search (SQLite FTS5)

Minerva leverages SQLite's native **FTS5** virtual tables for keyword searching. 
- Virtual tables are maintained for `goals`, `constraints`, `decisions`, `tasks`, and `facts`.
- Automatic triggers propagate insertions, updates, and deletions from raw tables into FTS virtual tables.
- Lexical matching uses SQLite's built-in **BM25** ranking algorithm to query and retrieve matches in sub-millisecond latencies.

---

## 3. Semantic Search (ONNX BGE-small)

To match concepts rather than raw keywords, Minerva runs an embedded vector search engine:
- **Embedding Model**: `Xenova/bge-small-en-v1.5` (384 dimensions).
- **Execution Provider**: CPU-optimized `ONNX Runtime` execution provider.
- **Normalization**: Vectors are L2 normalized and stored as binary blobs.
- **Similarity Measure**: Dot product comparison (equivalent to cosine similarity on pre-normalized vectors).
- **Retrieval Prefix**: Queries are prefixed with `"Represent this sentence for searching relevant passages: "` as required by BGE models to maximize retrieval recall.

---

## 4. Link-Graph Relational Boosting

Once lexical and semantic candidates are fetched, they are ranked. Minerva boosts items that share explicit relationships.
- The `links` table defines unique target-source entity couplings (e.g. `decision` #5 linked to `goal` #2).
- When a candidate is retrieved with a high score, Minerva queries the link graph for related nodes.
- Linked items are given a score boost or pulled directly into the candidate set, ensuring that design decisions or constraints relevant to a retrieved goal or task are not omitted.

---

## 5. Context Compilation & Packing

The retrieved candidates are formatted and packed into the prompt:
1. **Deduplication**: Candidates from lexical and semantic passes are merged.
2. **Relevance Scoring**: Candidates are ranked using a weighted score:
   $$\text{Score} = w_{\text{semantic}} \cdot \text{Similarity} + w_{\text{lexical}} \cdot \text{BM25} + \text{Boost}_{\text{graph}}$$
3. **Diversity (Maximal Marginal Relevance)**: Prompts are filtered to ensure high information diversity and reduce duplicate facts.
4. **Token Packing**: The prompt builder iteratively formats candidates in XML structures until the token budget (default `4000`, scaling down to `3400` safety threshold) is consumed.
