import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from minerva.db import Database
from minerva.embeddings import EmbeddingModel
from minerva.retrieval import RetrievalEngine
from minerva.prompt_builder import PromptBuilder

def main():
    print("Minerva Quickstart Example")
    
    # 1. Initialize local SQLite database
    # By default, it accesses ~/.minerva/minerva.db
    db = Database()
    
    # 2. Add some sample data (only run if database is empty)
    goals = db.list_goals()
    if not goals:
        print("Populating database with sample goals...")
        db.add_goal("Complete Phase 1 launch of the developer CLI", priority=5)
        db.add_goal("Establish sub-15ms search latency threshold", priority=4)
        
        # Add constraint
        db.add_constraint("All embeddings must be generated locally via ONNX Runtime", severity="hard", type_val="technical")
        
        # Force embed helper
        embedder = EmbeddingModel()
        for goal in db.list_goals():
            vector = embedder.embed_text(goal['text'])
            db.set_embedding('goal', goal['id'], vector)
            
        for constraint in db.list_constraints():
            vector = embedder.embed_text(constraint['text'])
            db.set_embedding('constraint', constraint['id'], vector)
            
        print("Sample data populated!")

    # 3. Retrieve memories
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)
    
    query = "local embedding constraints"
    print(f"\nSearching for: '{query}'...")
    results = engine.retrieve(query, limit=5)
    
    for r in results:
        print(f"\n[{r['type'].upper()} #{r['id']}] (Score: {r['score']:.2f})")
        details = r['details']
        if r['type'] == 'constraint':
            print(f"  [{details['severity'].upper()}] {details['text']}")
        else:
            text_val = details.get('text') or details.get('title') or ""
            print(f"  {text_val}")

    # 4. Preview compiled XML prompt context
    print("\nCompiling XML prompt context...")
    builder = PromptBuilder(db, engine, embedder.tokenizer)
    prompt = builder.compile_prompt(query, total_budget=2000)
    print(prompt)
    
    db.close()

if __name__ == "__main__":
    main()
