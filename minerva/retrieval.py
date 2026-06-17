import numpy as np
import math
from datetime import datetime, timezone
from minerva.db import Database
from minerva.embeddings import EmbeddingModel

class RetrievalEngine:
    def __init__(self, db: Database, embedder: EmbeddingModel):
        self.db = db
        self.embedder = embedder

    def calculate_recency(self, timestamp_str: str, half_life_days: float = 7.0) -> float:
        """
        Calculates a recency factor in [0, 1] using an exponential decay formula.
        """
        if not timestamp_str:
            return 0.0
            
        try:
            # Try parsing SQLite standard format: YYYY-MM-DD HH:MM:SS
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            try:
                # Try parsing ISO format
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                return 0.5  # Fallback if parsing fails
                
        now = datetime.now(timezone.utc)
        delta = (now - dt).total_seconds() / (24 * 3600)  # delta in days
        delta = max(0.0, delta)
        return float(math.exp(-delta / half_life_days))

    def get_importance_score(self, record_type: str, item: dict) -> float:
        """
        Returns a normalized importance score in [0, 1] based on the record fields.
        """
        if record_type == 'goal':
            return float(item.get('priority', 3)) / 5.0
        elif record_type == 'constraint':
            return 1.0 if item.get('severity') == 'hard' else 0.5
        elif record_type == 'decision':
            return 1.0 if item.get('status') == 'current' else 0.3
        elif record_type == 'task':
            return float(item.get('priority', 3)) / 5.0
        elif record_type == 'fact':
            ref_count = int(item.get('reference_count', 1))
            #decouple from confidence: importance is based solely on reference count (popularity)
            ref_factor = min(1.0, ref_count / 10.0)
            return float(0.5 + ref_factor * 0.5)
        return 0.5

    def mmr_rerank(self, candidates: list, query_vector: np.ndarray, vectors_by_type: dict, limit: int, lambda_val: float = 0.7) -> list:
        if not candidates:
            return []
        
        selected = []
        remaining = list(candidates)
        
        while len(selected) < limit and remaining:
            best_mmr = -float('inf')
            best_cand = None
            
            for cand in remaining:
                # Base scores are already normalized within [0, 1]
                relevance = cand['score']
                
                # Max similarity to already selected candidates
                max_sim = 0.0
                cand_vec = vectors_by_type.get(cand['type'], {}).get(cand['id'])
                
                if cand_vec is not None and selected:
                    sims = []
                    for sel in selected:
                        sel_vec = vectors_by_type.get(sel['type'], {}).get(sel['id'])
                        if sel_vec is not None:
                            # Both are pre-normalized float32 vectors, so dot product is cosine similarity
                            sim = float(np.dot(cand_vec, sel_vec))
                            # Normalize from [-1, 1] to [0, 1]
                            sim_norm = (sim + 1.0) / 2.0
                            sims.append(sim_norm)
                    if sims:
                        max_sim = max(sims)
                
                # MMR formula: lambda * relevance - (1 - lambda) * max_sim
                mmr_score = lambda_val * relevance - (1.0 - lambda_val) * max_sim
                
                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_cand = cand
            
            if best_cand:
                best_cand['score'] = float(best_mmr)
                selected.append(best_cand)
                remaining.remove(best_cand)
            else:
                break
                
        return selected

    def classify_query(self, query: str) -> str:
        """
        Classifies incoming query into one of:
        - BROAD_REVIEW
        - DEPENDENCY_ANALYSIS
        - HISTORICAL_AUDIT
        - OPERATIONAL
        """
        query_lower = query.lower()
        
        # 1. Broad Review Mode
        broad_keywords = [
            "summarize", "summary", "overview", "all migrations", "all abandoned", 
            "audit trail", "evolutionary shifts", "milestones", "project history", 
            "history of the project", "history of all", "broad review", "entire project"
        ]
        if any(kw in query_lower for kw in broad_keywords):
            return "BROAD_REVIEW"
            
        # 2. Dependency Analysis Mode
        dependency_keywords = [
            "linked to", "depends on", "dependency", "relationship", "blocked by", 
            "blocks", "connection between", "forced the rejection", "depend on",
            "dependencies", "linked"
        ]
        if any(kw in query_lower for kw in dependency_keywords):
            return "DEPENDENCY_ANALYSIS"
            
        # 3. Historical Audit Mode
        historical_keywords = [
            "superseded", "supersedes", "old", "previous", "historical", "revert", 
            "replace", "prior", "achieved", "completed", "done", "past", "history", 
            "earlier", "audit", "was changed", "what did we", "why did we", 
            "rejected", "abandoned", "before the migration", "alternatives", 
            "did we try", "was renamed", "renamed", "renaming", "originally", 
            "replaced", "reject", "rejection", "alternative", "before"
        ]
        if any(kw in query_lower for kw in historical_keywords):
            return "HISTORICAL_AUDIT"
            
        # 4. Operational Mode (Default)
        return "OPERATIONAL"

    def retrieve(self, query: str, limit: int = 15) -> list:
        """
        Performs hybrid retrieval (BM25 + Semantic Vector + Recency + Importance + Confidence)
        across all memory tables.
        Returns a list of dicts: {"type": str, "id": int, "score": float, "details": dict}
        ordered by score descending, with MMR diversity applied.
        """
        if not query or not query.strip():
            return []

        # Multi-mode intent classification
        mode = self.classify_query(query)
        include_superseded = mode in ["HISTORICAL_AUDIT", "BROAD_REVIEW", "DEPENDENCY_ANALYSIS"]

        # 1. Compute query vector
        query_vector = self.embedder.embed_query(query)
        
        record_types = ['goal', 'constraint', 'decision', 'task', 'fact']
        all_candidates = []
        vectors_by_type = {}

        for r_type in record_types:
            # Pre-load all embeddings of this type
            cached_vectors = self.db.get_all_embeddings(r_type)
            vectors_by_type[r_type] = {rec_id: vec for rec_id, vec in cached_vectors}

            # Fetch all items of this type from DB (applying active/current filtering by default)
            if r_type == 'goal':
                if include_superseded:
                    items = self.db.list_goals()
                else:
                    items = [item for item in self.db.list_goals() if item.get('status') == 'active']
            elif r_type == 'constraint':
                items = self.db.list_constraints()
            elif r_type == 'decision':
                if include_superseded:
                    items = self.db.list_decisions()
                else:
                    items = [item for item in self.db.list_decisions() if item.get('status') == 'current']
            elif r_type == 'task':
                if include_superseded:
                    items = self.db.list_tasks()
                else:
                    items = [item for item in self.db.list_tasks() if item.get('status') != 'done']
            elif r_type == 'fact':
                items = self.db.list_facts()
            else:
                items = []

            if not items:
                continue

            # Index items by ID for quick access
            item_map = {item['id']: item for item in items}

            # Calculate neighborhood density for statistical noise detection
            neighbor_counts = {}
            for rec_id, vec in vectors_by_type[r_type].items():
                if rec_id not in item_map:
                    continue
                num_neighbors = 0
                for other_id, other_vec in vectors_by_type[r_type].items():
                    if other_id == rec_id:
                        continue
                    sim = float(np.dot(vec, other_vec))
                    sim_norm = (sim + 1.0) / 2.0
                    if sim_norm > 0.88:
                        num_neighbors += 1
                neighbor_counts[rec_id] = num_neighbors

            # Run FTS keyword search
            fts_results = self.db.fts_search(r_type, query, limit=limit * 2)
            fts_scores = {r['id']: r['score'] for r in fts_results}

            # Fetch all cached vectors for this record type
            vector_scores = {}
            for rec_id, vec in vectors_by_type[r_type].items():
                if rec_id in item_map:
                    sim = self.embedder.cosine_similarity(query_vector, vec)
                    sim_norm = (sim + 1.0) / 2.0
                    vector_scores[rec_id] = sim_norm

            all_ids = set(item_map.keys())

            # Perform min-max normalization on FTS scores for this category
            max_fts = max(fts_scores.values()) if fts_scores else 0.0
            min_fts = min(fts_scores.values()) if fts_scores else 0.0
            fts_diff = max_fts - min_fts

            for rec_id in all_ids:
                item = item_map[rec_id]

                # Keyword score (FTS BM25)
                raw_fts = fts_scores.get(rec_id, 0.0)
                if rec_id in fts_scores:
                    if fts_diff > 0:
                        keyword_score = (raw_fts - min_fts) / fts_diff
                    else:
                        keyword_score = 1.0
                else:
                    keyword_score = 0.0

                # Semantic score
                semantic_score = vector_scores.get(rec_id, 0.5)

                # Recency score
                if r_type == 'goal':
                    time_str = item.get('updated_at') or item.get('created_at')
                elif r_type == 'constraint':
                    time_str = item.get('created_at')
                elif r_type == 'decision':
                    time_str = item.get('decided_at')
                elif r_type == 'task':
                    time_str = item.get('completed_at') if item.get('status') == 'done' else item.get('created_at')
                elif r_type == 'fact':
                    time_str = item.get('last_referenced_at') or item.get('created_at')
                else:
                    time_str = item.get('created_at')
                recency_score = self.calculate_recency(time_str)

                # Importance score
                importance_score = self.get_importance_score(r_type, item)

                # Confidence score (decoupled independent term)
                confidence_score = float(item.get('confidence') if item.get('confidence') is not None else 1.0)

                # Combined score: 20% keyword, 40% semantic, 15% recency, 15% importance, 10% confidence
                score = (
                    0.20 * keyword_score +
                    0.40 * semantic_score +
                    0.15 * recency_score +
                    0.15 * importance_score +
                    0.10 * confidence_score
                )

                # Statistical semantic redundancy detection
                num_neighbors = neighbor_counts.get(rec_id, 0)
                is_noise = (num_neighbors >= 3)
                if is_noise:
                    # Do not penalize if the query explicitly targets this item
                    if keyword_score >= 0.20 or semantic_score >= 0.85:
                        is_noise = False

                if is_noise:
                    score *= 0.1
                    semantic_score *= 0.1

                all_candidates.append({
                    "type": r_type,
                    "id": rec_id,
                    "score": float(score),
                    "semantic_score": float(semantic_score),
                    "details": item
                })

        # Apply link boost
        candidates_map = {(cand['type'], cand['id']): cand for cand in all_candidates}
        for (r_type, rec_id), cand in candidates_map.items():
            links = self.db.get_links_for_entity(r_type, rec_id)
            for link in links:
                linked_key = (link['type'], link['id'])
                if linked_key in candidates_map:
                    # Multiplicative link boost: scale by current candidate's base score
                    cand['score'] += 0.2 * candidates_map[linked_key]['score'] * cand['score']

        # Determine lambda_val dynamically based on mode to prevent over-penalization of highly relevant facts/tasks
        if mode in ["HISTORICAL_AUDIT", "BROAD_REVIEW"]:
            lambda_val = 0.95
        elif mode == "DEPENDENCY_ANALYSIS":
            lambda_val = 0.90
        else:  # OPERATIONAL
            lambda_val = 0.90

        # Apply MMR diversity re-ranking to select the top limit items
        reranked = self.mmr_rerank(all_candidates, query_vector, vectors_by_type, limit, lambda_val=lambda_val)

        # Inject historical lineage for decisions and goals (Iteration 2 - after MMR to avoid suppression)
        lineage_candidates = []
        candidates_map = {(cand['type'], cand['id']): cand for cand in reranked}
        to_process = list(reranked)
        visited = set(candidates_map.keys())
        
        while to_process:
            cand = to_process.pop(0)
            c_type = cand['type']
            c_id = cand['id']
            c_score = cand['score']
            item = cand['details']
            
            if c_type == 'decision' and item.get('supersedes_id'):
                parent_id = item['supersedes_id']
                parent_key = ('decision', parent_id)
                if parent_key not in visited:
                    visited.add(parent_key)
                    parent_row = self.db.conn.execute("SELECT * FROM decisions WHERE id = ? AND deleted_at IS NULL", (parent_id,)).fetchone()
                    if parent_row:
                        parent_cand = {
                            "type": "decision",
                            "id": parent_id,
                            "score": c_score * 0.85,
                            "semantic_score": cand.get('semantic_score', c_score) * 0.85,
                            "details": dict(parent_row)
                        }
                        lineage_candidates.append(parent_cand)
                        to_process.append(parent_cand)
                        
            elif c_type == 'goal':
                superseded_rows = self.db.conn.execute("SELECT * FROM goals WHERE superseded_by = ? AND deleted_at IS NULL", (c_id,)).fetchall()
                for row in superseded_rows:
                    parent_id = row['id']
                    parent_key = ('goal', parent_id)
                    if parent_key not in visited:
                        visited.add(parent_key)
                        parent_cand = {
                            "type": "goal",
                            "id": parent_id,
                            "score": c_score * 0.85,
                            "semantic_score": cand.get('semantic_score', c_score) * 0.85,
                            "details": dict(row)
                        }
                        lineage_candidates.append(parent_cand)
                        to_process.append(parent_cand)
                        
        reranked.extend(lineage_candidates)

        # Inject dependency neighbors for DEPENDENCY_ANALYSIS mode (after MMR to avoid suppression)
        if mode == "DEPENDENCY_ANALYSIS":
            dep_candidates = []
            candidates_map = {(cand['type'], cand['id']): cand for cand in reranked}
            to_process = [(cand['type'], cand['id'], cand['score'], 0) for cand in reranked]
            visited = set(candidates_map.keys())
            
            while to_process:
                c_type, c_id, c_score, hop = to_process.pop(0)
                if hop >= 2:  # Limit depth to 2 hops
                    continue
                    
                links = self.db.get_links_for_entity(c_type, c_id)
                for link in links:
                    link_key = (link['type'], link['id'])
                    if link_key not in visited:
                        visited.add(link_key)
                        # Find the parent candidate to propagate semantic_score
                        parent_cand = candidates_map.get((c_type, c_id))
                        parent_sem = parent_cand.get('semantic_score', c_score) if parent_cand else c_score
                        link_cand = {
                            "type": link['type'],
                            "id": link['id'],
                            "score": c_score * 0.90,  # Slight decay
                            "semantic_score": parent_sem * 0.90,
                            "details": link['details']
                        }
                        dep_candidates.append(link_cand)
                        to_process.append((link['type'], link['id'], link_cand['score'], hop + 1))
            reranked.extend(dep_candidates)

        return reranked

