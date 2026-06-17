import os
import sys
import numpy as np

# Ensure contexts package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from minerva.db import Database
from minerva.embeddings import EmbeddingModel

def seed_adversarial_db():
    db_file = os.path.join(os.path.dirname(__file__), "adversarial_v4.db")
    if os.path.exists(db_file):
        os.remove(db_file)
        
    print(f"Creating adversarial database at {db_file}...")
    db = Database(db_file)
    embedder = EmbeddingModel()
    
    # Trackers for IDs
    goals_ids = []
    constraints_ids = []
    decisions_ids = []
    tasks_ids = []
    facts_ids = []
    
    # =========================================================================
    # 1. GOALS (40 items: active, achieved, superseded)
    # =========================================================================
    print("Generating 40 Goals...")
    goals = []
    
    # Active goals (Goals 1-25)
    for i in range(1, 26):
        if i == 1:
            text = "Achieve sub-15ms query response time for SQLite FTS5 metadata search."
        elif i == 2:
            text = "Ensure 100% local-first private telemetry collection using stdio MCP transport."
        elif i == 3:
            text = "Implement numpy-based matrix dot-products for local cosine similarity."
        elif i == 4:
            text = "Support Windows, macOS, and Linux telemetry collection out-of-the-box."
        elif i == 5:
            text = "Maintain test coverage above 95% on the Collector component."
        else:
            text = f"Goal #{i}: Implement system isolation framework level {i} for Project Orion."
        goals.append({"text": text, "priority": (i % 5) + 1, "status": "active"})
        
    # Achieved goals (Goals 26-35)
    for i in range(26, 36):
        if i == 26:
            text = "Successfully port config system from local JSON files to sqlite db config table."
        elif i == 27:
            text = "Complete the Collector's initial metrics collection pipeline."
        else:
            text = f"Goal #{i} (Achieved): Verify compliance of component audit logging layer {i}."
        goals.append({"text": text, "priority": (i % 5) + 1, "status": "achieved"})
        
    # Superseded goals (Goals 36-40)
    goals.append({"text": "Support cloud-based OpenAI embedding models like text-embedding-3-small.", "priority": 2, "status": "superseded"})
    goals.append({"text": "Use BadgerDB for heavy write telemetry database storage.", "priority": 4, "status": "superseded"})
    goals.append({"text": "Implement FAISS vector similarity search plugin for local retrieval.", "priority": 3, "status": "superseded"})
    goals.append({"text": "Use external gRPC services for metric ingestion.", "priority": 4, "status": "superseded"})
    goals.append({"text": "Implement a Rust-based WASM plug-in framework for core telemetry hooks.", "priority": 3, "status": "superseded"})

    for g in goals:
        gid = db.add_goal(text=g["text"], priority=g["priority"], status=g["status"])
        goals_ids.append(gid)
        vec = embedder.embed_text(g["text"])
        db.set_embedding('goal', gid, vec)

    # Link superseded goals
    # Goal 36 (OpenAI API) superseded by Goal 2 (local stdio MCP)
    db.update_goal(goals_ids[35], superseded_by=goals_ids[1])
    # Goal 37 (BadgerDB) superseded by Goal 1 (SQLite FTS5)
    db.update_goal(goals_ids[36], superseded_by=goals_ids[0])
    # Goal 38 (FAISS) superseded by Goal 3 (numpy dot-products)
    db.update_goal(goals_ids[37], superseded_by=goals_ids[2])
    # Goal 39 (gRPC) superseded by Goal 2 (local stdio MCP)
    db.update_goal(goals_ids[38], superseded_by=goals_ids[1])
    # Goal 40 (WASM) superseded by Goal 5 (Collector coverage)
    db.update_goal(goals_ids[39], superseded_by=goals_ids[4])

    # =========================================================================
    # 2. CONSTRAINTS (30 items)
    # =========================================================================
    print("Generating 30 Constraints...")
    constraints = [
        {"text": "All telemetry database storage and vector indexes must reside strictly on the user's local machine.", "severity": "hard", "type": "technical"},
        {"text": "The telemetry agent must not initiate any outbound HTTP connections for inference or data transmission.", "severity": "hard", "type": "technical"},
        {"text": "Local disk usage for the metrics cache directory must be bounded under 200MB.", "severity": "hard", "type": "budget"},
        {"text": "Minimum supported Python runtime version is 3.11.", "severity": "hard", "type": "technical"},
        {"text": "Third-party packages must be compatible with permissive open-source licenses (MIT/BSD/Apache-2.0).", "severity": "hard", "type": "legal"},
        {"text": "The agent must complete local database initialization in less than 150 milliseconds.", "severity": "soft", "type": "time"},
        {"text": "All telemetry buffering files must survive unexpected kernel panics or agent crashes.", "severity": "hard", "type": "technical"},
    ]
    # Add filler constraints up to 30
    for i in range(len(constraints) + 1, 31):
        constraints.append({
            "text": f"Constraint #{i}: Ensure Orion subsystem {i} operates within standard dev limits.",
            "severity": "soft",
            "type": "technical"
        })
        
    for c in constraints:
        cid = db.add_constraint(text=c["text"], severity=c["severity"], type_val=c["type"])
        constraints_ids.append(cid)
        vec = embedder.embed_text(c["text"])
        db.set_embedding('constraint', cid, vec)

    # =========================================================================
    # 3. DECISIONS (50 items: including historical chain)
    # =========================================================================
    print("Generating 50 Decisions...")
    decisions = [
        # Chain 1: Database Storage
        {"decision": "Use BadgerDB for metrics storage.", "rationale": "BadgerDB is a fast pure-Go LSM key-value store optimized for SSDs.", "status": "superseded", "supersedes": None},
        {"decision": "Use SQLite FTS5 for metrics storage.", "rationale": "BadgerDB caused heavy SSD wear and memory footprint due to excessive write amplification. SQLite FTS5 provides superior structured queries and BM25 indexing.", "status": "current", "supersedes": 1},
        
        # Chain 2: Similarity search
        {"decision": "Use FAISS library for vector similarity search.", "rationale": "FAISS provides fast C++ implementation of similarity index.", "status": "superseded", "supersedes": None},
        {"decision": "Use NumPy vector dot-product for pre-normalized cosine similarity.", "rationale": "FAISS required external C++ compilation binaries that fail on Windows arm64 architectures. NumPy is local, fast, and pre-compiled.", "status": "current", "supersedes": 3},
        
        # Chain 3: Communication Protocol
        {"decision": "Use gRPC for remote client metric ingestion.", "rationale": "Provides high performance client libraries and schema enforcement.", "status": "superseded", "supersedes": None},
        {"decision": "Use localized MCP stdio protocol for client metric ingestion.", "rationale": "gRPC introduced firewall configuration issues and complex API key management. MCP stdio transport is zero-config and highly secure.", "status": "current", "supersedes": 5},
        
        # Chain 4: WASM Plug-ins
        {"decision": "Use Rust WASM plug-in system for custom telemetry hooks.", "rationale": "Allows developers to upload high-performance custom metrics filters safely.", "status": "superseded", "supersedes": None},
        {"decision": "Use simple local Python plug-in loader for telemetry hooks.", "rationale": "Rust WASM toolchain was too complex for custom developers. A simple Python loader satisfies requirements without compiler complexity.", "status": "current", "supersedes": 7},
        
        # Other standalone decisions
        {"decision": "Use memory-mapped files (mmap) for telemetry buffering.", "rationale": "Mmap allows writing metrics directly to memory and letting OS sync to disk, ensuring crash recovery on panic.", "status": "current", "supersedes": None},
        {"decision": "Use tiktoken library with cl100k_base vocabulary for context budget checks.", "rationale": "Tiktoken is extremely fast and matches the exact vocabulary of Claude, preventing overflows.", "status": "current", "supersedes": None},
        {"decision": "Use lock-free ring buffer in Collector metric stream.", "rationale": "Allows the Collector to ingest concurrent metric streams without lock contention.", "status": "current", "supersedes": None},
        {"decision": "Use local ONNX Runtime with Xenova/bge-small for local embeddings.", "rationale": "Protects data privacy by running embedding inference locally on CPU without external API calls.", "status": "current", "supersedes": None},
    ]
    # Add filler decisions up to 50
    for i in range(len(decisions) + 1, 51):
        decisions.append({
            "decision": f"Standardize on component registration pattern #{i}.",
            "rationale": f"Decided to use registration pattern #{i} to ensure telemetry Collector registration safety.",
            "status": "current",
            "supersedes": None
        })

    for idx, d in enumerate(decisions):
        sup_id = None
        if d["supersedes"] is not None:
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

    # =========================================================================
    # 4. TASKS (80 items)
    # =========================================================================
    print("Generating 80 Tasks...")
    tasks = []
    
    # 10 Abandoned tasks (Superseded by migrations)
    tasks.append({"title": "Task #1: Tune BadgerDB LSM tree sstable sizes", "desc": "Optimize LSM write performance.", "status": "done", "outcome": "BadgerDB sstable sizes tuned, but LSM store was later abandoned due to SSD wear."})
    tasks.append({"title": "Task #2: Compile FAISS binaries for Windows Arm64", "desc": "Resolve C++ toolchain compiler errors.", "status": "done", "outcome": "Failed to compile. C++ compiler compatibility issues on Windows arm64 forced abandonment of FAISS."})
    tasks.append({"title": "Task #3: Implement gRPC authorization headers", "desc": "Enforce secure API keys.", "status": "done", "outcome": "Implemented, but metric transport was later migrated to MCP stdio."})
    tasks.append({"title": "Task #4: Implement Rust WASM builder scripts", "desc": "Write scripts to compile plug-ins.", "status": "done", "outcome": "Scripts written, but WASM was abandoned in favor of python loader."})
    for i in range(5, 11):
        tasks.append({"title": f"Task #{i}: Test obsolete gRPC endpoint {i}", "desc": "Write integration test for old transport.", "status": "done", "outcome": f"Integration tests completed, but transport was later abandoned."})

    # Active / Blocked / Todo tasks (Tasks 11-40)
    tasks.append({"title": "Task #11: Debug Collector memory leaks in heap profile", "desc": "Collector leaks memory under heavy metrics flow. Profile heap allocations.", "status": "in_progress"})
    tasks.append({"title": "Task #12: Resolve SQLite connection pool lock contention", "desc": "SQLite database throws connection pool locks under concurrent writes. Fix contention.", "status": "in_progress"})
    tasks.append({"title": "Task #13: Write Developer Setup Guide for Cursor settings", "desc": "Create guide for setting up Cursor MCP.", "status": "todo"})
    tasks.append({"title": "Task #14: Write Developer Setup Guide for Windsurf settings", "desc": "Create guide for setting up Windsurf MCP.", "status": "todo"})
    tasks.append({"title": "Task #15: Resolve zstandard library compression compilation mismatch", "desc": "zstandard headers fail to compile under Windows C++ runtime. Blocked by library version mismatch.", "status": "blocked"})
    tasks.append({"title": "Task #16: Implement lock-free ring buffer in Collector", "desc": "Collector ring buffer overflows. Rewrite metric ingestion to use lock-free channels.", "status": "in_progress"})
    
    for i in range(17, 41):
        tasks.append({"title": f"Task #{i}: Verify telemetry registration #{i}", "desc": "Test registration validation logic.", "status": "todo"})
        
    # Completed tasks (Tasks 41-80)
    for i in range(41, 81):
        tasks.append({"title": f"Task #{i}: Implement core Collector telemetry interface {i}", "desc": "Write basic metric interfaces.", "status": "done", "outcome": f"Collector metric interface {i} completed and integrated with 100% test coverage."})

    for t in tasks:
        tid = db.add_task(title=t["title"], description=t.get("desc"), status=t["status"])
        tasks_ids.append(tid)
        if "outcome" in t:
            db.update_task(tid, outcome=t["outcome"])
            
        text_to_embed = f"Title: {t['title']} | Description: {t.get('desc', '')} | Outcome: {t.get('outcome', '')}"
        vec = embedder.embed_text(text_to_embed)
        db.set_embedding('task', tid, vec)

    # =========================================================================
    # 5. FACTS (150 items: historical, bug reports, contradictions, noise)
    # =========================================================================
    print("Generating 150 Facts...")
    facts = []
    
    # Historical facts
    facts.append({"text": "The core metrics gathering component was originally named 'Tracker' in month 1 and was later renamed to 'Collector' in month 3.", "cat": "history"})
    facts.append({"text": "Project Orion migrated from BadgerDB to SQLite FTS5 due to write amplification causing excessive SSD wear.", "cat": "history"})
    facts.append({"text": "The Rust WASM plug-in experiment was abandoned in month 4 due to builder complexity and developer compile bottlenecks.", "cat": "history"})
    
    # Bug reports
    facts.append({"text": "Collector memory leaks are occurring in heap allocations during concurrent client metric streams.", "cat": "bugs"})
    facts.append({"text": "Connection pool contention is causing SQLite database lock timeouts under concurrent writes.", "cat": "bugs"})
    facts.append({"text": "zstandard compression library compilation fails on Windows C++ runtime due to header mismatch.", "cat": "bugs"})
    
    # Standalone important facts (mentioned once)
    facts.append({"text": "The reserved port number for the backup sync socket in the current design is 9876.", "cat": "network"})
    facts.append({"text": "Maximum allowed disk usage for the local telemetry cache directory is 200MB.", "cat": "technical"})
    facts.append({"text": "The BGE-small embedding model is executed locally on CPU via ONNX Runtime CPUExecutionProvider.", "cat": "technical"})
    facts.append({"text": "Collector uses memory-mapped files (mmap) for metric buffering to survive OS kernel panic crash recoveries.", "cat": "architecture"})
    facts.append({"text": "The stdio-based transport protocol avoids firewall setup and ensures zero-config security isolation.", "cat": "architecture"})
    facts.append({"text": "Tiktoken library with cl100k_base is utilized to verify context budgets to prevent token overflow.", "cat": "compiler"})
    facts.append({"text": "Collector ingests concurrent metric streams without locking via a lock-free ring buffer.", "cat": "architecture"})

    # Contradictory information (only the latest is correct)
    facts.append({"text": "The telemetry backup sync transport uses gRPC protocol on port 8080 (Deprecated, superseded by MCP stdio).", "cat": "network"})
    facts.append({"text": "The telemetry backup sync transport uses standard TCP sockets on port 9090 (Deprecated, superseded by MCP stdio).", "cat": "network"})
    facts.append({"text": "The telemetry backup sync transport resides strictly on port 9876 via localized MCP stdio connection.", "cat": "network"})

    # Add 100 general noise facts (coffee machine, office lease, trivia, etc.)
    noise_facts = [
        "The office coffee machine on level 3 requires weekly descaling on Tuesday mornings.",
        "Developer vacation schedules are tracked in the Slack channel #dev-vacation-records.",
        "The annual company picnic is scheduled for September 12th at Central Park.",
        "Office lease contract was successfully renewed for another 2 years in May.",
        "The office chess tournament was won by senior developer Dave in month 2.",
        "Weekly status meetings are held on Monday at 9:30 AM in the Orion conference room.",
        "The main office kitchen is stocked with milk, oats, and organic apples.",
        "Venus has a thick atmosphere composed mostly of carbon dioxide and nitrogen clouds.",
        "Sauna temperatures should be kept between 75 and 85 degrees Celsius for safety.",
        "A standard soccer field is between 100 and 110 meters in length.",
        "Wombat scat is cubic, allowing it to mark territory without rolling away.",
        "Zanzibar is an archipelago off the coast of East Africa famous for spices.",
        "The local library offers free coding workshops for kids on Saturday mornings.",
        "Developer setup requires git to be installed on the local system.",
        "Git branches should be named using the prefix feature/ or bugfix/.",
        "Orion telemetry agent code format checks run automatically on every pull request.",
        "The company gym subscription is subsidized up to fifty percent for full time staff.",
        "The office thermostat is set to 22 degrees Celsius by default.",
        "Project Orion's Slack channel is named #project-orion-telemetry.",
        "Developer Dave prefers dark theme in VS Code while Sarah prefers light theme.",
    ]
    # Replicate noise facts to reach 100
    for i in range(21, 101):
        noise_facts.append(f"Noise fact #{i}: Subsystem {i} general note on trivia detail {i}.")

    for nf in noise_facts:
        facts.append({"text": nf, "cat": "noise"})

    # Populate facts up to 150 total
    while len(facts) < 150:
        facts.append({"text": f"Telemetry fact #{len(facts)}: Fact detail concerning telemetry subsystem metric validation.", "cat": "general"})

    for f in facts:
        fid = db.add_fact(text=f["text"], category=f["cat"])
        facts_ids.append(fid)
        vec = embedder.embed_text(f["text"])
        db.set_embedding('fact', fid, vec)

    # =========================================================================
    # 6. LINKS (Generic relations)
    # =========================================================================
    print("Generating 150 links...")
    # Link Goal 1 (SQLite) with Decision 2 (SQLite)
    db.link_entities('goal', goals_ids[0], 'decision', decisions_ids[1])
    # Link Goal 2 (stdio MCP) with Decision 6 (stdio MCP)
    db.link_entities('goal', goals_ids[1], 'decision', decisions_ids[5])
    # Link Goal 3 (numpy dot-products) with Decision 4 (numpy)
    db.link_entities('goal', goals_ids[2], 'decision', decisions_ids[3])
    
    # Link constraints to decisions
    db.link_entities('constraint', constraints_ids[0], 'decision', decisions_ids[11]) # local ONNX Runtime
    db.link_entities('constraint', constraints_ids[1], 'decision', decisions_ids[11])
    db.link_entities('constraint', constraints_ids[2], 'decision', decisions_ids[1]) # SQLite
    db.link_entities('constraint', constraints_ids[3], 'decision', decisions_ids[11])

    # Link tasks to decisions
    db.link_entities('task', tasks_ids[10], 'decision', decisions_ids[11]) # leak task to ONNX
    db.link_entities('task', tasks_ids[11], 'decision', decisions_ids[1])  # pool lock task to SQLite
    db.link_entities('task', tasks_ids[14], 'fact', facts_ids[5])          # zstandard task to zstd fact
    db.link_entities('task', tasks_ids[15], 'decision', decisions_ids[10]) # ring buffer task to lock-free decision

    # Link facts to tasks
    db.link_entities('fact', facts_ids[3], 'task', tasks_ids[10]) # memory leak fact to task 11
    db.link_entities('fact', facts_ids[4], 'task', tasks_ids[11]) # pool contention fact to task 12
    db.link_entities('fact', facts_ids[5], 'task', tasks_ids[14]) # zstd bug fact to task 15

    # Generate random connections to reach 150 links
    np.random.seed(42)
    while db.conn.execute("SELECT count(*) FROM links").fetchone()[0] < 150:
        g_id = int(np.random.choice(goals_ids))
        d_id = int(np.random.choice(decisions_ids))
        try:
            db.link_entities('goal', g_id, 'decision', d_id)
        except Exception:
            pass

        t_id = int(np.random.choice(tasks_ids))
        f_id = int(np.random.choice(facts_ids))
        try:
            db.link_entities('task', t_id, 'fact', f_id)
        except Exception:
            pass

    print(f"Database seeded successfully with:")
    print(f"- {len(goals_ids)} goals")
    print(f"- {len(constraints_ids)} constraints")
    print(f"- {len(decisions_ids)} decisions")
    print(f"- {len(tasks_ids)} tasks")
    print(f"- {len(facts_ids)} facts")
    print(f"- {db.conn.execute('SELECT count(*) FROM links').fetchone()[0]} links")
    db.close()

if __name__ == "__main__":
    seed_adversarial_db()
