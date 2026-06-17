import os
import sys
import pytest
import subprocess
import sqlite3
from click.testing import CliRunner

from minerva.db import Database
from minerva.cli import main as cli_main
from minerva.embeddings import EmbeddingModel
from minerva.retrieval import RetrievalEngine

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "minerva_test.db"
    db_path = str(db_file)
    monkeypatch.setenv("MINERVA_DB_PATH", db_path)
    # Explicitly set model directory to the default pre-downloaded path
    monkeypatch.setenv("MINERVA_MODEL_DIR", os.path.expanduser("~/.minerva/models"))
    
    # Initialize the database to create schema
    database = Database(db_path)
    database.close()
    
    yield db_path
    
    # Clean up
    if db_file.exists():
        try:
            os.remove(db_file)
        except Exception:
            pass

def test_tier1_feature_coverage(temp_db):
    """
    Tier 1: Feature coverage.
    CRUD for goals, constraints, decisions, tasks, facts, and linking.
    Tested via Click CliRunner (in-process) and standalone CLI invocations (out-of-process subprocess).
    """
    runner = CliRunner()
    
    # 1. Add entities via click CliRunner
    res = runner.invoke(cli_main, ["add", "goal", "Deliver the core MVP feature set", "--priority", "5"])
    assert res.exit_code == 0
    assert "Added Goal #1" in res.output

    res = runner.invoke(cli_main, ["add", "constraint", "Must run fully local without external API calls", "--severity", "hard", "--type", "technical"])
    assert res.exit_code == 0
    assert "Added Constraint #1" in res.output

    res = runner.invoke(cli_main, ["add", "decision", "Use SQLite database for persistence", "SQLite is zero-config and provides fast disk access"])
    assert res.exit_code == 0
    assert "Added Decision #1" in res.output

    res = runner.invoke(cli_main, ["add", "task", "Setup initial database schemas", "--description", "Create tables and triggers", "--priority", "4"])
    assert res.exit_code == 0
    assert "Added Task #1" in res.output

    res = runner.invoke(cli_main, ["add", "fact", "Model size of bge-small is ~133MB", "--category", "embeddings", "--confidence", "1.0"])
    assert res.exit_code == 0
    assert "Added Fact #1" in res.output

    # 2. List entities to verify creation
    res = runner.invoke(cli_main, ["list", "goals"])
    assert res.exit_code == 0
    assert "Deliver the core MVP" in res.output

    res = runner.invoke(cli_main, ["list", "constraints"])
    assert res.exit_code == 0
    assert "Must run fully local" in res.output

    res = runner.invoke(cli_main, ["list", "decisions"])
    assert res.exit_code == 0
    assert "Use SQLite database" in res.output

    res = runner.invoke(cli_main, ["list", "tasks"])
    assert res.exit_code == 0
    assert "Setup initial database" in res.output

    res = runner.invoke(cli_main, ["list", "facts"])
    assert res.exit_code == 0
    assert "Model size of bge-small" in res.output

    # 3. Link entities via click CliRunner
    res = runner.invoke(cli_main, ["link", "decision", "1", "goal", "1"])
    assert res.exit_code == 0
    assert "Linked decision #1 and goal #1" in res.output

    # 4. Standalone CLI invocations via subprocesses
    env = os.environ.copy()
    env["MINERVA_DB_PATH"] = temp_db
    env["MINERVA_MODEL_DIR"] = os.path.expanduser("~/.minerva/models")

    # Add second goal via subprocess
    sub_res = subprocess.run(
        ["uv", "run", "minerva", "add", "goal", "Subprocess-based E2E Goal", "--priority", "3"],
        capture_output=True,
        text=True,
        check=True,
        env=env
    )
    assert "Added Goal #2" in sub_res.stdout

    # List goals via subprocess
    sub_res = subprocess.run(
        ["uv", "run", "minerva", "list", "goals"],
        capture_output=True,
        text=True,
        check=True,
        env=env
    )
    assert "Subprocess-based E2E Goal" in sub_res.stdout

def test_tier2_boundary_and_corner_cases(temp_db):
    """
    Tier 2: Boundary & corner cases.
    Verifies SQLite constraint checks (NOT NULL, CHECK constraints) and CLI error handling.
    Covers bounds: priority [1, 5], confidence [0.0, 1.0], empty strings, duplicate links, large texts.
    """
    db = Database(temp_db)
    
    # 1. Null / Empty checks on Database level
    with pytest.raises(sqlite3.IntegrityError):
        db.add_goal(None)  # type: ignore

    # 2. Priority bounds constraint checking (priority=0 or 6)
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db.add_goal("Priority underflow test", priority=0)
    assert "CHECK constraint failed" in str(excinfo.value)

    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db.add_goal("Priority overflow test", priority=6)
    assert "CHECK constraint failed" in str(excinfo.value)

    # 3. Confidence bounds checking (confidence=-0.5 or 1.5)
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db.add_fact("Confidence underflow test", confidence=-0.5)
    assert "CHECK constraint failed" in str(excinfo.value)

    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db.add_fact("Confidence overflow test", confidence=1.5)
    assert "CHECK constraint failed" in str(excinfo.value)

    # 4. Large text inputs
    large_text = "A" * 10000
    goal_id = db.add_goal(large_text, priority=3)
    assert goal_id > 0
    assert db.get_goal(goal_id)["text"] == large_text

    # 5. Duplicate links resolution verification (ON CONFLICT DO UPDATE)
    # DB handles it gracefully by returning or updating without raising IntegrityError
    link_id_1 = db.link_entities("goal", 1, "task", 1)
    link_id_2 = db.link_entities("goal", 1, "task", 1)
    assert link_id_1 == link_id_2

    # 6. Verify graceful CLI exit/failures
    runner = CliRunner()
    res = runner.invoke(cli_main, ["add", "goal", "Invalid Priority via CLI", "--priority", "10"])
    assert res.exit_code != 0
    err_text = res.output
    if res.exception and not isinstance(res.exception, SystemExit):
        err_text += "\n" + str(res.exception)
    assert "CHECK constraint failed" in err_text or "Error" in err_text

    db.close()

def test_tier3_cross_feature_combinations(temp_db):
    """
    Tier 3: Cross-feature combinations.
    Adds a goal and two decisions, links only one decision to the goal, and checks that hybrid
    retrieval weights prioritize the linked decision when searching for query matching the goal.
    """
    db = Database(temp_db)
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)

    # 1. Add Goal
    goal_text = "Migrate user authentication to OAuth2 standards"
    gid = db.add_goal(goal_text, priority=5)
    db.set_embedding('goal', gid, embedder.embed_text(goal_text))

    # 2. Add Decision A (linked later)
    dec_a_title = "Use Auth0 Identity Provider"
    dec_a_rat = "Auth0 supports OAuth2 protocols out-of-the-box and reduces infrastructure overhead."
    did_a = db.add_decision(dec_a_title, dec_a_rat)
    db.set_embedding('decision', did_a, embedder.embed_text(f"Decision: {dec_a_title} | Rationale: {dec_a_rat}"))

    # 3. Add Decision B (unlinked comparison)
    dec_b_title = "Use Custom SQLite User Tables"
    dec_b_rat = "Write basic username password login system manually using local table storage."
    did_b = db.add_decision(dec_b_title, dec_b_rat)
    db.set_embedding('decision', did_b, embedder.embed_text(f"Decision: {dec_b_title} | Rationale: {dec_b_rat}"))

    # 4. Query before linking
    query = "OAuth2 standard migration solution"
    results_before = engine.retrieve(query, limit=5)
    
    score_a_before = next(r["score"] for r in results_before if r["type"] == "decision" and r["id"] == did_a)
    score_b_before = next(r["score"] for r in results_before if r["type"] == "decision" and r["id"] == did_b)

    # 5. Link Decision A to the Goal
    db.link_entities("decision", did_a, "goal", gid)

    # 6. Query after linking
    results_after = engine.retrieve(query, limit=5)

    score_a_after = next(r["score"] for r in results_after if r["type"] == "decision" and r["id"] == did_a)
    score_b_after = next(r["score"] for r in results_after if r["type"] == "decision" and r["id"] == did_b)

    # Decision A is boosted because it is linked to the matched Goal, while Decision B is not.
    assert score_a_after > score_before_check(score_a_before)
    assert score_b_after == pytest.approx(score_b_before, abs=1e-5)
    assert score_a_after > score_b_after

    db.close()

def score_before_check(score):
    return score

def test_tier4_real_world_workload_scenario(temp_db):
    """
    Tier 4: Real-world workload scenario.
    Generates a complex graph of 100+ records (goals, decisions, constraints, tasks, facts),
    establishes multiple bidirectional links, and runs hybrid search queries to verify ranking.
    """
    db = Database(temp_db)
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)

    goals = []
    decisions = []
    constraints = []
    tasks = []
    facts = []

    # 1. Populate 100+ records (20 of each type = 100 total)
    for i in range(1, 21):
        # Goals
        g_text = f"Objective {i}: Optimize transaction processing speed and data pipeline throughput"
        gid = db.add_goal(g_text, priority=4)
        db.set_embedding('goal', gid, embedder.embed_text(g_text))
        goals.append(gid)

        # Decisions
        d_title = f"Decision {i}: Implement Redis memory database cluster"
        d_rat = f"Rationale {i}: In-memory key-value caching reduces SQL querying latency significantly"
        did = db.add_decision(d_title, d_rat)
        db.set_embedding('decision', did, embedder.embed_text(f"Decision: {d_title} | Rationale: {d_rat}"))
        decisions.append(did)

        # Constraints
        c_text = f"Constraint {i}: System memory must remain under 512 megabytes on CPU"
        cid = db.add_constraint(c_text, severity="hard", type_val="technical")
        db.set_embedding('constraint', cid, embedder.embed_text(c_text))
        constraints.append(cid)

        # Tasks
        t_title = f"Task {i}: Configure parallel ingestion threads"
        t_desc = f"Task details {i}: Tune thread pool size to match physical core counts"
        tid = db.add_task(t_title, description=t_desc, priority=3)
        db.set_embedding('task', tid, embedder.embed_text(f"Title: {t_title} | Description: {t_desc}"))
        tasks.append(tid)

        # Facts
        f_text = f"Fact {i}: Production server nodes contain 64 cores each"
        fid = db.add_fact(f_text, category="infrastructure", confidence=1.0)
        db.set_embedding('fact', fid, embedder.embed_text(f_text))
        facts.append(fid)

    # Verify total record count in SQLite
    total_goals = len(db.list_goals())
    total_decisions = len(db.list_decisions())
    total_constraints = len(db.list_constraints())
    total_tasks = len(db.list_tasks())
    total_facts = len(db.list_facts())
    assert (total_goals + total_decisions + total_constraints + total_tasks + total_facts) == 100

    # 2. Establish complex linking relationship graph (80 links)
    for i in range(20):
        # Link: Goal[i] <-> Decision[i]
        db.link_entities("goal", goals[i], "decision", decisions[i])
        # Link: Decision[i] <-> Constraint[i]
        db.link_entities("decision", decisions[i], "constraint", constraints[i])
        # Link: Constraint[i] <-> Task[i]
        db.link_entities("constraint", constraints[i], "task", tasks[i])
        # Link: Task[i] <-> Fact[i]
        db.link_entities("task", tasks[i], "fact", facts[i])

    # 3. Verify retrieval and ranking on hybrid queries
    queries = [
        "optimize throughput of data pipeline",
        "redis cluster database decision",
        "latency and memory footprint constraint",
        "parallel threads physical CPU cores",
        "production server RAM and core infrastructure"
    ]

    for q in queries:
        results = engine.retrieve(q, limit=15)
        assert len(results) > 0
        
        # Verify ranking order correctness (scores must descend)
        scores = [r["score"] for r in results]
        assert all(scores[idx] >= scores[idx+1] for idx in range(len(scores)-1))

        # Verify linked entity retrieval
        for r in results:
            links = db.get_links_for_entity(r["type"], r["id"])
            # Ensure links are retrievable and correct (each entity in our chain has at least 1 link)
            assert len(links) >= 1
            for link in links:
                assert link["type"] in ["goal", "decision", "constraint", "task", "fact"]
                assert link["id"] > 0
                assert link["details"] is not None

    db.close()
