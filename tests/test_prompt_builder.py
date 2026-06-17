import pytest
from minerva.db import Database
from minerva.retrieval import RetrievalEngine
from minerva.prompt_builder import PromptBuilder

class MockTokenizer:
    def encode(self, text):
        class MockEncoding:
            def __init__(self, t):
                # Simple word-level tokenization for mock token counting
                self.ids = [1] * len(t.split())
        return MockEncoding(text)

class MockEmbedder:
    def embed_text(self, text: str):
        import numpy as np
        return np.zeros(384, dtype=np.float32)
    def embed_query(self, query: str):
        import numpy as np
        return np.zeros(384, dtype=np.float32)
    def cosine_similarity(self, vec1, vec2):
        return 1.0

@pytest.fixture
def db():
    database = Database(":memory:")
    yield database
    database.close()

def test_prompt_builder_formatting(db):
    embedder = MockEmbedder()
    engine = RetrievalEngine(db, embedder)
    tokenizer = MockTokenizer()
    builder = PromptBuilder(db, engine, tokenizer)
    
    # Add project context data
    db.add_goal("Deliver Phase 1", priority=5)
    db.add_constraint("Must run offline", severity="hard", type_val="technical")
    db.add_decision("SQLite for DB", "Fast local storage")
    db.add_task("Write code", "Complete prompt builder", priority=3)
    db.add_fact("Facts are cool", category="general")
    
    # Embed them
    db.set_embedding('goal', 1, embedder.embed_text(""))
    db.set_embedding('constraint', 1, embedder.embed_text(""))
    db.set_embedding('decision', 1, embedder.embed_text(""))
    db.set_embedding('task', 1, embedder.embed_text(""))
    db.set_embedding('fact', 1, embedder.embed_text(""))
    
    # Compile prompt
    prompt = builder.compile_prompt("what is the project state?", total_budget=1000)
    
    # Verify XML structure
    assert "<project_context>" in prompt
    assert "<goals>" in prompt
    assert "Deliver Phase 1" in prompt
    
    assert "<constraints>" in prompt
    assert "Must run offline" in prompt
    
    assert "<decisions>" in prompt
    assert "SQLite for DB" in prompt
    
    assert "<tasks>" in prompt
    assert "Write code" in prompt
    
    assert "<relevant_history>" in prompt
    assert 'type="fact"' in prompt or 'type="goal"' in prompt

def test_prompt_builder_truncation(db):
    embedder = MockEmbedder()
    engine = RetrievalEngine(db, embedder)
    tokenizer = MockTokenizer()
    builder = PromptBuilder(db, engine, tokenizer)
    
    # Add data
    for i in range(10):
        db.add_goal(f"Goal number {i} containing lots of words to fill up the token budget", priority=3)
        db.set_embedding('goal', i+1, embedder.embed_text(""))
        
    # Compile with small budget to trigger truncation
    prompt = builder.compile_prompt("test query", total_budget=20)
    
    # The output should contain omission comments/warnings rather than crashing
    assert "omitted" in prompt or "Omitted" in prompt or "No relevant history" in prompt
