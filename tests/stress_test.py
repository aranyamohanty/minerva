import os
import sys
import time
import argparse
import numpy as np

# Ensure contexts package can be imported from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from minerva.db import Database
from minerva.embeddings import EmbeddingModel
from minerva.retrieval import RetrievalEngine
from minerva.prompt_builder import PromptBuilder

def create_stress_dataset(db: Database, embedder: EmbeddingModel):
    print("=== SEEDING HIGH-DENSITY RELATIONAL PROJECT MEMORY ===")
    
    # Track generated IDs
    goals_ids = []
    constraints_ids = []
    decisions_ids = []
    tasks_ids = []
    facts_ids = []

    # 1. Add 20 Goals (active, achieved, superseded)
    print("Generating 20 Goals...")
    goals_data = [
        # active
        {"text": "Achieve sub-10ms sqlite FTS match query latency for project metadata search.", "priority": 5, "status": "active"},
        {"text": "Ensure 100% local-first private embedding generation using Xenova/bge-small.", "priority": 4, "status": "active"},
        {"text": "Provide a full-featured web console dashboard for visual debugging.", "priority": 3, "status": "active"},
        {"text": "Support Windows, macOS, and Linux platform deployments.", "priority": 4, "status": "active"},
        {"text": "Maintain unit test coverage above 90% across the codebase.", "priority": 5, "status": "active"},
        {"text": "Integrate with multiple IDEs including Cursor, VS Code, and Windsurf.", "priority": 4, "status": "active"},
        {"text": "Implement zero-config sqlite storage with automatic schema migration.", "priority": 5, "status": "active"},
        {"text": "Achieve database compression using zstandard for long-term archiving.", "priority": 1, "status": "active"},
        {"text": "Create a high-performance C++ binding for embeddings generation.", "priority": 2, "status": "active"},
        {"text": "Integrate real-time memory synchronization via WebSockets.", "priority": 3, "status": "active"},
        {"text": "Support multi-user concurrent read/write transactions.", "priority": 2, "status": "active"},
        {"text": "Deploy to PyPI package manager under name minerva.", "priority": 4, "status": "active"},
        {"text": "Write a detailed developer setup guide for Windsurf.", "priority": 3, "status": "active"},
        {"text": "Perform security audit for local command injections.", "priority": 4, "status": "active"},
        {"text": "Implement Cosine Similarity via NumPy for vector retrieval.", "priority": 4, "status": "active"},
        # achieved
        {"text": "Implement an automated token budget compiler with 85% safety margin.", "priority": 5, "status": "achieved"},
        {"text": "Complete Phase 1 spec requirements including hybrid search.", "priority": 5, "status": "achieved"},
        # superseded (we will back-link superseded_by after inserts)
        {"text": "Support cloud-based OpenAI embedding models like text-embedding-3-small.", "priority": 2, "status": "superseded"},
        {"text": "Implement a file-based JSON configuration file for metadata.", "priority": 2, "status": "superseded"},
        {"text": "Implement a naive vector search algorithm in pure Python.", "priority": 1, "status": "superseded"},
    ]

    for g in goals_data:
        gid = db.add_goal(text=g["text"], priority=g["priority"], status=g["status"])
        goals_ids.append(gid)
        # Generate & store embedding
        vec = embedder.embed_text(g["text"])
        db.set_embedding('goal', gid, vec)

    # Link superseded goals
    # Goal 18 (OpenAI embeddings) superseded by Goal 2 (Local BGE embeddings)
    db.update_goal(goals_ids[17], superseded_by=goals_ids[1])
    # Goal 19 (JSON config) superseded by Goal 7 (SQLite storage)
    db.update_goal(goals_ids[18], superseded_by=goals_ids[6])
    # Goal 20 (naive vector search) superseded by Goal 15 (NumPy Cosine Similarity)
    db.update_goal(goals_ids[19], superseded_by=goals_ids[14])


    # 2. Add 15 Constraints (severity: hard/soft, type: technical/business/legal/budget/time)
    print("Generating 15 Constraints...")
    constraints_data = [
        {"text": "All vector and text data must reside strictly on the user's local machine.", "severity": "hard", "type": "technical"},
        {"text": "The application must not initiate any outbound HTTP connections for inference.", "severity": "hard", "type": "technical"},
        {"text": "Total memory footprint during embedding inference must remain under 128MB.", "severity": "hard", "type": "technical"},
        {"text": "CLI initialization commands must complete in less than 250 milliseconds.", "severity": "hard", "type": "time"},
        {"text": "The embedding model must fit within standard git repositories (less than 100MB).", "severity": "soft", "type": "technical"},
        {"text": "Third-party packages must be compatible with permissive open-source licenses (MIT/BSD/Apache-2.0).", "severity": "hard", "type": "legal"},
        {"text": "Minimum supported Python runtime version is 3.10.", "severity": "hard", "type": "technical"},
        {"text": "Database schema migrations must never lose historical project audit logs.", "severity": "hard", "type": "technical"},
        {"text": "Code formatting must strictly adhere to the PEP 8 guidelines.", "severity": "soft", "type": "technical"},
        {"text": "Unit tests must run concurrently to fit within CI/CD runner time limits.", "severity": "soft", "type": "time"},
        {"text": "The prompt compiler's output must not exceed the target context budget.", "severity": "hard", "type": "technical"},
        {"text": "Local disk usage for the cache directory must be bounded under 500MB.", "severity": "soft", "type": "technical"},
        {"text": "The codebase must not depend on external database daemons like PostgreSQL or Redis.", "severity": "hard", "type": "technical"},
        {"text": "Project documentation must be written in standard Markdown format.", "severity": "soft", "type": "business"},
        {"text": "Hybrid retrieval must use a deterministic weighting of score components.", "severity": "soft", "type": "technical"},
    ]

    for c in constraints_data:
        cid = db.add_constraint(text=c["text"], severity=c["severity"], type_val=c["type"])
        constraints_ids.append(cid)
        vec = embedder.embed_text(c["text"])
        db.set_embedding('constraint', cid, vec)


    # 3. Add 40 Decisions (including historical chains with supersedes/superseded_by)
    print("Generating 40 Decisions...")
    decisions_data = [
        # Hand-crafted decisions to form historical chains
        {"decision": "Use SQLite instead of PostgreSQL for metadata.", "rationale": "SQLite is self-contained, requires no server daemon, is highly fast, and fits local developer environments perfectly.", "status": "current", "supersedes": None},
        {"decision": "Use HuggingFace Cloud API for embeddings generation.", "rationale": "Allows rapid prototyping and avoids downloading model files locally.", "status": "superseded", "supersedes": None},
        {"decision": "Use local ONNX Runtime with Xenova/bge-small for local embeddings.", "rationale": "Resolves user privacy constraints, avoids api keys, and runs 100% locally.", "status": "current", "supersedes": 2}, # Index offset will be handled below
        {"decision": "Use token count based on character length approximation.", "rationale": "Simple and quick to calculate without library dependencies.", "status": "superseded", "supersedes": None},
        {"decision": "Use HuggingFace tokenizers library for exact token counting.", "rationale": "Prevents context window overflows by matching the exact vocabulary of BGE-small.", "status": "current", "supersedes": 4},
        {"decision": "Use SQLite FTS4 virtual tables for keyword matching.", "rationale": "Standard full-text search capability available in older SQLite versions.", "status": "superseded", "supersedes": None},
        {"decision": "Use SQLite FTS5 virtual tables with external content content_rowid.", "rationale": "Provides superior query performance, BM25 scoring out-of-the-box, and triggers for auto-updating.", "status": "current", "supersedes": 6},
        {"decision": "Use pure Python loop matrix computations for cosine similarity.", "rationale": "Avoids NumPy compilation binaries for Windows users.", "status": "superseded", "supersedes": None},
        {"decision": "Use NumPy vector dot-product for pre-normalized cosine similarity.", "rationale": "NumPy vectorization speeds up retrieval by orders of magnitude for large datasets.", "status": "current", "supersedes": 8},
        {"decision": "Write click-based CLI using explicit command registrations.", "rationale": "Standard tool for building Python CLIs with excellent help generation.", "status": "current", "supersedes": None},
    ]

    # Insert hand-crafted decisions
    for d in decisions_data:
        # Resolve supersedes ID if any
        sup_id = None
        if d["supersedes"] is not None:
            # The superseded decisions are already inserted, we can fetch their database IDs
            sup_id = decisions_ids[d["supersedes"] - 1]
            
        did = db.add_decision(
            decision=d["decision"],
            rationale=d["rationale"],
            status=d["status"],
            supersedes_id=sup_id
        )
        decisions_ids.append(did)
        text_to_embed = f"Decision: {d['decision']} | Rationale: {d['rationale']}"
        vec = embedder.embed_text(text_to_embed)
        db.set_embedding('decision', did, vec)

    # Programmatically generate Decisions 11-40 to reach 40 total
    for i in range(11, 41):
        decision_text = f"Standardize on architecture component layer #{i} for contexts."
        rationale_text = f"Decided to use modular architecture layer #{i} to isolate SQLite database connections from the prompt builder and ensure unit test isolation."
        did = db.add_decision(
            decision=decision_text,
            rationale=rationale_text,
            status="current"
        )
        decisions_ids.append(did)
        text_to_embed = f"Decision: {decision_text} | Rationale: {rationale_text}"
        vec = embedder.embed_text(text_to_embed)
        db.set_embedding('decision', did, vec)


    # 4. Add 50 Tasks with priority, outcome, and status (todo, in_progress, blocked, done)
    print("Generating 50 Tasks...")
    # Generate 25 Done tasks
    for i in range(1, 26):
        title = f"Task #{i}: Implement core component {i}"
        desc = f"Implement component {i} and cover it with comprehensive unit tests."
        outcome = f"Component {i} was successfully written, integrated, and verified to have 100% test coverage."
        tid = db.add_task(title=title, description=desc, status="done", priority=(i % 5) + 1)
        db.update_task(tid, outcome=outcome)
        tasks_ids.append(tid)
        text_to_embed = f"Title: {title} | Description: {desc} | Outcome: {outcome}"
        vec = embedder.embed_text(text_to_embed)
        db.set_embedding('task', tid, vec)

    # Generate 10 In Progress tasks
    for i in range(26, 36):
        title = f"Task #{i}: Debug integration interface {i}"
        desc = f"Resolve integration mismatch in module interface {i} for SQLite binding."
        tid = db.add_task(title=title, description=desc, status="in_progress", priority=(i % 5) + 1)
        tasks_ids.append(tid)
        text_to_embed = f"Title: {title} | Description: {desc}"
        vec = embedder.embed_text(text_to_embed)
        db.set_embedding('task', tid, vec)

    # Generate 5 Blocked tasks
    for i in range(36, 41):
        title = f"Task #{i}: Profile memory footprint {i}"
        desc = f"Analyze heap allocations under high thread contention for task runner {i}."
        tid = db.add_task(title=title, description=desc, status="blocked", priority=(i % 5) + 1)
        tasks_ids.append(tid)
        text_to_embed = f"Title: {title} | Description: {desc}"
        vec = embedder.embed_text(text_to_embed)
        db.set_embedding('task', tid, vec)

    # Generate 10 Todo tasks
    for i in range(41, 51):
        title = f"Task #{i}: Write documentation section {i}"
        desc = f"Create guides for Cursor and Windsurf settings in config file {i}."
        tid = db.add_task(title=title, description=desc, status="todo", priority=(i % 5) + 1)
        tasks_ids.append(tid)
        text_to_embed = f"Title: {title} | Description: {desc}"
        vec = embedder.embed_text(text_to_embed)
        db.set_embedding('task', tid, vec)


    # 5. Add 100 Technical Facts (including near-duplicates to test MMR diversity)
    print("Generating 100 Facts (including near-duplicates for MMR)...")
    facts_data = [
        # Cluster 1: SQLite FTS5 uses BM25
        {"text": "SQLite FTS5 uses the BM25 algorithm for scoring matching documents.", "cat": "database", "ref": 5},
        {"text": "The BM25 scoring algorithm is implemented in SQLite FTS5 for text matches.", "cat": "database", "ref": 4},
        {"text": "SQLite FTS5 ranks matching documents using the BM25 weighting formula.", "cat": "database", "ref": 3},
        {"text": "In SQLite FTS5, document matching and scoring is done via BM25.", "cat": "database", "ref": 2},
        {"text": "FTS5 virtual tables in SQLite leverage BM25 to calculate match scores.", "cat": "database", "ref": 1},
        
        # Cluster 2: BGE-small dimension is 384
        {"text": "Xenova bge-small-en-v1.5 has an embedding dimension of 384.", "cat": "ml", "ref": 8},
        {"text": "The vector dimension for the BGE-small model is exactly 384.", "cat": "ml", "ref": 6},
        {"text": "BGE-small outputs normalized vectors with a length of 384.", "cat": "ml", "ref": 5},
        {"text": "Each vector generated by the BGE-small embedding model contains 384 dimensions.", "cat": "ml", "ref": 4},
        {"text": "The output dimension of Xenova's bge-small-en-v1.5 model is 384 float values.", "cat": "ml", "ref": 2},

        # Cluster 3: ONNX runtime execution
        {"text": "Xenova's bge-small model runs on CPU using the ONNX Runtime library.", "cat": "ml", "ref": 9},
        {"text": "Embedding inference of the BGE-small model is executed locally on CPU via ONNX Runtime.", "cat": "ml", "ref": 7},
        {"text": "ONNX Runtime is used to run the local BGE-small embedding model on CPU.", "cat": "ml", "ref": 6},
        {"text": "For local embedding generation, BGE-small runs via ONNX Runtime on the CPU.", "cat": "ml", "ref": 4},
        {"text": "ONNX Runtime CPU execution provider is used to run the Xenova BGE-small model.", "cat": "ml", "ref": 3},

        # Cluster 4: Prompt safety margin
        {"text": "Minerva prompt compiler applies an 85% safety margin to the token budget.", "cat": "compiler", "ref": 7},
        {"text": "The total token budget is scaled by 0.85 as a safety buffer during prompt compilation.", "cat": "compiler", "ref": 6},
        {"text": "A safety margin of 85 percent is applied to the context window budget in Minerva.", "cat": "compiler", "ref": 5},
        {"text": "The prompt builder multiplies the token limit by 0.85 to avoid context overflows.", "cat": "compiler", "ref": 3},
        {"text": "An 85% scaling factor is used to calculate the safe token budget for prompt compilation.", "cat": "compiler", "ref": 2},
    ]

    # Insert clustered facts
    for f in facts_data:
        fid = db.add_fact(text=f["text"], category=f["cat"], confidence=1.0)
        # Set reference count
        db.conn.execute("UPDATE facts SET reference_count = ? WHERE id = ?", (f["ref"], fid))
        facts_ids.append(fid)
        vec = embedder.embed_text(f["text"])
        db.set_embedding('fact', fid, vec)

    # Programmatically generate remaining 80 facts (Facts 21-100)
    for i in range(21, 101):
        fact_text = f"Technical fact #{i}: Minerva uses module isolation pattern #{i} to ensure thread safety under concurrent SQLite writes."
        category = "concurrency" if i % 2 == 0 else "python"
        fid = db.add_fact(text=fact_text, category=category, confidence=1.0)
        facts_ids.append(fid)
        vec = embedder.embed_text(fact_text)
        db.set_embedding('fact', fid, vec)


    # 6. Add 100 Links connecting these records
    print("Generating 100 Links...")
    link_count = 0
    # Core architectural links
    # Goal #1 (FTS5 latency) <-> Decision #7 (FTS5 external content)
    db.link_entities("goal", goals_ids[0], "decision", decisions_ids[6])
    # Goal #2 (Local embeddings) <-> Decision #3 (Local ONNX)
    db.link_entities("goal", goals_ids[1], "decision", decisions_ids[2])
    # Goal #16 (Token budget compiler) <-> Decision #5 (Tokenizers library)
    db.link_entities("goal", goals_ids[15], "decision", decisions_ids[4])
    # Constraint #1 (Local data) <-> Decision #3 (Local ONNX)
    db.link_entities("constraint", constraints_ids[0], "decision", decisions_ids[2])
    # Constraint #2 (No outbound HTTP) <-> Decision #3 (Local ONNX)
    db.link_entities("constraint", constraints_ids[1], "decision", decisions_ids[2])
    # Constraint #3 (Memory footprint) <-> Decision #3 (Local ONNX)
    db.link_entities("constraint", constraints_ids[2], "decision", decisions_ids[2])
    # Decision #3 (Local ONNX) <-> Task #26 (Debug SQLite interface)
    db.link_entities("decision", decisions_ids[2], "task", tasks_ids[25])
    # Task #26 <-> Fact #11 (ONNX runs on CPU)
    db.link_entities("task", tasks_ids[25], "fact", facts_ids[10])
    link_count += 8

    # Generate other links programmatically
    for i in range(92):
        # Let's connect tasks, decisions, constraints, facts, and goals
        target_id = tasks_ids[i % len(tasks_ids)]
        source_id = facts_ids[(i * 3) % len(facts_ids)]
        try:
            db.link_entities("task", target_id, "fact", source_id)
            link_count += 1
        except Exception:
            pass # ignore unique constraint conflicts

    print(f"Links generated: {link_count}")
    print("=== SEEDING COMPLETED SUCCESSFULY ===")
    return {
        "goals": goals_ids,
        "constraints": constraints_ids,
        "decisions": decisions_ids,
        "tasks": tasks_ids,
        "facts": facts_ids
    }

def run_stress_test_analysis(db_path: str):
    print("\n" + "="*80)
    print("RUNNING RETRIEVAL AND PROMPT COMPILATION ANALYSIS")
    print("="*80)

    db = Database(db_path)
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)
    builder = PromptBuilder(db, engine, embedder.tokenizer)

    # 1. Total records check
    total_goals = len(db.list_goals())
    total_constraints = len(db.list_constraints())
    total_decisions = len(db.list_decisions())
    total_tasks = len(db.list_tasks())
    total_facts = len(db.list_facts())
    print(f"Total Goals: {total_goals} (including active/achieved/superseded)")
    print(f"Total Constraints: {total_constraints}")
    print(f"Total Decisions: {total_decisions}")
    print(f"Total Tasks: {total_tasks}")
    print(f"Total Facts: {total_facts}")
    
    # 2. MMR Diversity Filter Test
    print("\n--- TEST A: MMR Diversity Filter Test ---")
    query = "BM25 scoring algorithm in SQLite FTS5"
    print(f"Query: '{query}'")
    
    # We retrieve the top 15 results
    results = engine.retrieve(query, limit=15)
    
    print("\nTop 10 retrieved candidates with MMR (diverse results):")
    for idx, r in enumerate(results[:10]):
        details = r['details']
        text = details.get('text') or details.get('decision') or details.get('title')
        print(f"  {idx+1}. [Score: {r['score']:.4f}] [{r['type'].upper()} #{r['id']}] {text[:90]}...")

    # Let's count how many facts from Cluster 1 (BM25 near-duplicates) are in the top 10 results
    bm25_facts_retrieved = [r for r in results if r['type'] == 'fact' and r['id'] in [1, 2, 3, 4, 5]]
    print(f"\nNumber of near-duplicate BM25 facts in top results: {len(bm25_facts_retrieved)} out of 5 inserted.")
    if len(bm25_facts_retrieved) <= 2:
        print("SUCCESS: MMR successfully diversified the results and suppressed the redundant near-duplicates!")
    else:
        print("WARNING: MMR did not sufficiently suppress the redundant facts.")

    # 3. Superseded Goal/Decision Filtering Test
    print("\n--- TEST B: Superseded Goal/Decision Filtering Test ---")
    
    # Retrieve active goals
    active_goals = db.list_goals(status='active')
    superseded_goals = db.conn.execute("SELECT * FROM goals WHERE status = 'superseded'").fetchall()
    
    print(f"Total active goals listed: {len(active_goals)}")
    print(f"Total superseded goals in database: {len(superseded_goals)}")
    
    # Check if superseded goals are retrieved in standard queries
    superseded_retrieved = [r for r in results if r['type'] == 'goal' and r['details'].get('status') == 'superseded']
    print(f"Superseded goals retrieved in search results: {len(superseded_retrieved)}")
    if len(superseded_retrieved) == 0:
        print("SUCCESS: Superseded goals are filtered out from search results by default to avoid polluting context!")
    else:
        print("WARNING: Superseded goals were found in search results.")

    # 4. Link Boosting Test
    print("\n--- TEST C: Link Boosting Test ---")
    query_boost = "Debug SQLite interface"
    print(f"Query: '{query_boost}'")
    results_boost = engine.retrieve(query_boost, limit=15)
    
    print("\nTop results for linked search:")
    for idx, r in enumerate(results_boost[:5]):
        details = r['details']
        text = details.get('text') or details.get('decision') or details.get('title')
        print(f"  {idx+1}. [Score: {r['score']:.4f}] [{r['type'].upper()} #{r['id']}] {text[:90]}...")

    # Check if Fact #11 (which is linked to Task #26) or Decision #3 (linked to Task #26) bubbled up
    linked_found = [r for r in results_boost if (r['type'] == 'fact' and r['id'] == 11) or (r['type'] == 'decision' and r['id'] == 3)]
    for item in linked_found:
        print(f"Found linked item in results: [{item['type'].upper()} #{item['id']}] score={item['score']:.4f}")
    if linked_found:
        print("SUCCESS: Link boosting successfully surfaced linked architectural decisions or facts in response to task search!")
    else:
        print("INFO: Linked items did not make it to the top 15 results.")

    # 5. Verify Prompt Compiler & Budget Management
    print("\n--- TEST D: Verify Prompt Compiler & Budget Management ---")
    query_compile = "Explain how FTS5 is integrated and the local embedding dimension"
    
    print("\n1. Compiling prompt with 4,000 token budget...")
    t0 = time.perf_counter()
    prompt_4k = builder.compile_prompt(query_compile, total_budget=4000)
    t1 = time.perf_counter()
    
    tokens_4k = builder.count_tokens(prompt_4k)
    print(f"Compilation time: {(t1 - t0)*1000.0:.2f} ms")
    print(f"Total compiled prompt tokens: {tokens_4k} (Safety target: <= 3400 tokens)")
    
    sections = ["<system>", "</system>", "<project_context>", "</project_context>", 
                "<relevant_history>", "</relevant_history>", "<conversation>", "</conversation>", 
                "<user_message>", "</user_message>"]
    all_sections_present = all(sec in prompt_4k for sec in sections)
    print(f"Contains all 5 XML sections: {all_sections_present}")
    
    print("\nExcerpt of compiled prompt (First 200 chars and last 200 chars):")
    print("-" * 50)
    print(prompt_4k[:200] + "\n...\n" + prompt_4k[-200:])
    print("-" * 50)

    print("\n2. Compiling prompt with tight 1,000 token budget (forces truncation)...")
    prompt_1k = builder.compile_prompt(query_compile, total_budget=1000)
    tokens_1k = builder.count_tokens(prompt_1k)
    print(f"Total compiled prompt tokens: {tokens_1k} (Safety target: <= 850 tokens)")
    
    has_omission = "omitted" in prompt_1k.lower() or "..." in prompt_1k
    print(f"Contains omission markers / truncation indicators: {has_omission}")
    
    print("\nExcerpt of relevant history in 1,000-token prompt:")
    start_hist = prompt_1k.find("<relevant_history>")
    end_hist = prompt_1k.find("</relevant_history>") + len("</relevant_history>")
    if start_hist != -1 and end_hist != -1:
        print("-" * 50)
        print(prompt_1k[start_hist:end_hist])
        print("-" * 50)
    else:
        print("Relevant history section omitted completely due to tight budget.")

    print("\n=== PERFORMANCE & RETRIEVAL TESTING COMPLETED ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default=None, help="Database path. Defaults to stress_test.db in current folder.")
    args = parser.parse_args()

    db_file = args.db_path
    if db_file is None:
        db_file = os.path.join(os.path.dirname(__file__), "stress_test.db")
        
    print(f"Running stress test on: {db_file}")
    
    # Ensure any old stress test DB is deleted first for clean run
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception as e:
            print(f"Could not remove existing database: {e}")

    db = Database(db_file)
    embedder = EmbeddingModel()
    
    t_start = time.perf_counter()
    create_stress_dataset(db, embedder)
    t_end = time.perf_counter()
    print(f"\nGenerated 225+ record dataset with vector embeddings in {t_end - t_start:.2f} seconds.")
    
    db.close()
    
    # Run analysis
    run_stress_test_analysis(db_file)
