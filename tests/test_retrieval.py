import pytest
import numpy as np
from datetime import datetime, timedelta, timezone
from minerva.db import Database
from minerva.retrieval import RetrievalEngine

class MockEmbedder:
    def embed_text(self, text: str) -> np.ndarray:
        # Return a simple mock 384-dimensional normalized vector
        vec = np.zeros(384, dtype=np.float32)
        # Create a simple deterministic pattern based on characters in text
        char_sum = sum(ord(c) for c in text)
        vec[0] = float(char_sum % 10) / 10.0
        vec[1] = float((char_sum * 7) % 10) / 10.0
        vec[2] = 1.0
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_text(query)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return float(np.dot(vec1, vec2))

@pytest.fixture
def db():
    database = Database(":memory:")
    yield database
    database.close()

def test_recency_calculation(db):
    embedder = MockEmbedder()
    engine = RetrievalEngine(db, embedder)
    
    # Format standard SQLite timestamp
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Recency of current item should be close to 1.0
    assert engine.calculate_recency(now_str) > 0.95
    
    # Recency of an item 7 days ago (1 half-life) should be close to exp(-1) = 0.367
    seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    assert 0.30 < engine.calculate_recency(seven_days_ago) < 0.40
    
    # Recency of an extremely old item should be close to 0.0
    thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    assert engine.calculate_recency(thirty_days_ago) < 0.05

def test_importance_score(db):
    embedder = MockEmbedder()
    engine = RetrievalEngine(db, embedder)
    
    # Goal priority
    assert engine.get_importance_score('goal', {'priority': 5}) == 1.0
    assert engine.get_importance_score('goal', {'priority': 1}) == 0.2
    
    # Constraint severity
    assert engine.get_importance_score('constraint', {'severity': 'hard'}) == 1.0
    assert engine.get_importance_score('constraint', {'severity': 'soft'}) == 0.5
    
    # Decision status
    assert engine.get_importance_score('decision', {'status': 'current'}) == 1.0
    assert engine.get_importance_score('decision', {'status': 'superseded'}) == 0.3

def test_hybrid_retrieval(db):
    embedder = MockEmbedder()
    engine = RetrievalEngine(db, embedder)
    
    # Insert facts
    fid1 = db.add_fact("The database uses WAL mode for concurrency.", category="database")
    fid2 = db.add_fact("Frontend built with React and Tailwind.", category="frontend")
    
    # Embed and store
    db.set_embedding('fact', fid1, embedder.embed_text("The database uses WAL mode for concurrency."))
    db.set_embedding('fact', fid2, embedder.embed_text("Frontend built with React and Tailwind."))
    
    # Query database -> should trigger keyword and vector matches
    results = engine.retrieve("database concurrency", limit=5)
    
    assert len(results) > 0
    # The first result should be the database fact due to both keyword and semantic matching
    assert results[0]['type'] == 'fact'
    assert results[0]['id'] == fid1
    assert results[0]['score'] > 0.5
