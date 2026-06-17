import pytest
import numpy as np
from click.testing import CliRunner

from minerva.db import Database
from minerva.embeddings import EmbeddingModel
from minerva.retrieval import RetrievalEngine
from minerva.prompt_builder import PromptBuilder
from minerva.cli import main as cli_main


def test_db_migration_and_audit(tmp_path):
    """Test clean schema creation, projects/audit_log presence, and soft-delete/restore."""
    db_file = tmp_path / "migration_test.db"
    db = Database(str(db_file))
    
    # Check default project was inserted
    rows = db.conn.execute("SELECT * FROM projects").fetchall()
    assert len(rows) == 1
    assert rows[0]["id"] == "default"
    
    # Test insert logs to audit
    gid = db.add_goal("Migration Goal", priority=3)
    audits = db.conn.execute("SELECT * FROM audit_log WHERE record_type = 'goal'").fetchall()
    assert len(audits) == 1
    assert audits[0]["action"] == "insert"
    
    # Test soft delete
    success = db.delete_goal(gid, hard=False)
    assert success is True
    
    # Verify soft-deleted item is excluded from lists/gets
    assert db.get_goal(gid) is None
    assert len(db.list_goals()) == 0
    
    # Check audit log contains soft_delete
    audits = db.conn.execute("SELECT * FROM audit_log WHERE record_type = 'goal' ORDER BY id DESC").fetchall()
    assert audits[0]["action"] == "soft_delete"
    
    # Test restore
    success = db.restore_goal(gid)
    assert success is True
    assert db.get_goal(gid) is not None
    assert len(db.list_goals()) == 1
    
    # Check audit log contains restore
    audits = db.conn.execute("SELECT * FROM audit_log WHERE record_type = 'goal' ORDER BY id DESC").fetchall()
    assert audits[0]["action"] == "restore"
    
    # Test hard delete
    success = db.delete_goal(gid, hard=True)
    assert success is True
    assert db.get_goal(gid) is None
    assert len(db.list_goals()) == 0
    
    audits = db.conn.execute("SELECT * FROM audit_log WHERE record_type = 'goal' ORDER BY id DESC").fetchall()
    assert audits[0]["action"] == "hard_delete"


def test_project_id_scoping(tmp_path):
    """Test scoping by project_id across lists and searches."""
    db = Database(":memory:")
    
    # Insert custom project
    db.conn.execute("INSERT INTO projects (id, name) VALUES ('custom', 'Custom Project')")
    
    # Add goals to default and custom projects
    gid_default = db.add_goal("Default Goal", project_id="default")
    gid_custom = db.add_goal("Custom Goal", project_id="custom")
    
    # Verify list scoping
    default_goals = db.list_goals(project_id="default")
    assert len(default_goals) == 1
    assert default_goals[0]["id"] == gid_default
    
    custom_goals = db.list_goals(project_id="custom")
    assert len(custom_goals) == 1
    assert custom_goals[0]["id"] == gid_custom
    
    # Verify FTS scoping
    res_default = db.fts_search("goal", "Goal", project_id="default")
    assert len(res_default) == 1
    assert res_default[0]["id"] == gid_default
    
    res_custom = db.fts_search("goal", "Goal", project_id="custom")
    assert len(res_custom) == 1
    assert res_custom[0]["id"] == gid_custom


def test_retrieval_superseded_filtering(tmp_path):
    """Test retrieval filters out superseded decisions and achieved goals."""
    db = Database(str(tmp_path / "super_test.db"))
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)
    
    # Goals
    g_active = db.add_goal("Active Goal text to match", status="active")
    g_achieved = db.add_goal("Achieved Goal text to match", status="achieved")
    db.set_embedding('goal', g_active, embedder.embed_text("Active Goal text to match"))
    db.set_embedding('goal', g_achieved, embedder.embed_text("Achieved Goal text to match"))
    
    # Decisions
    d_current = db.add_decision("Current Decision to match", "rationale")
    d_superseded = db.add_decision("Superseded Decision to match", "rationale", status="superseded")
    db.set_embedding('decision', d_current, embedder.embed_text("Decision: Current Decision to match | Rationale: rationale"))
    db.set_embedding('decision', d_superseded, embedder.embed_text("Decision: Superseded Decision to match | Rationale: rationale"))
    
    res = engine.retrieve("match", limit=10)
    retrieved_types_ids = {(r["type"], r["id"]) for r in res}
    
    # Verify active goal and current decision are present
    assert ("goal", g_active) in retrieved_types_ids
    assert ("decision", d_current) in retrieved_types_ids
    
    # Verify achieved goal and superseded decision are excluded
    assert ("goal", g_achieved) not in retrieved_types_ids
    assert ("decision", d_superseded) not in retrieved_types_ids


def test_mmr_diversity(db, embedder):
    """Test MMR diversity reranking filters out near-duplicate embeddings."""
    engine = RetrievalEngine(db, embedder)
    
    # Create 3 facts: 2 very similar, 1 different
    f1 = db.add_fact("The server nodes run on Python 3.12", category="infra")
    f2 = db.add_fact("The backend servers use Python 3.12", category="infra")  # Near-duplicate
    f3 = db.add_fact("The database uses SQLite in WAL mode", category="db")     # Different
    
    db.set_embedding('fact', f1, embedder.embed_text("The server nodes run on Python 3.12"))
    db.set_embedding('fact', f2, embedder.embed_text("The backend servers use Python 3.12"))
    db.set_embedding('fact', f3, embedder.embed_text("The database uses SQLite in WAL mode"))
    
    # Retrieve with limit=2. Standard retrieval would return f1 and f2 because they match "Python server database".
    # MMR should choose f1 or f2 (highest relevance) and f3 (more diverse than the other duplicate).
    res = engine.retrieve("Python server database", limit=2)
    assert len(res) == 2
    retrieved_ids = [r["id"] for r in res]
    
    # Check that one of the duplicates is first, and f3 is selected instead of the other duplicate
    assert retrieved_ids[0] in (f1, f2)
    assert retrieved_ids[1] == f3


def test_dynamic_budget_redistribution(tmp_path):
    """Test prompt builder budget redistribution underfills context but fills history."""
    db = Database(str(tmp_path / "budget_test.db"))
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)
    builder = PromptBuilder(db, engine, embedder.tokenizer)
    
    # Add a single goal to keep project_context tiny
    db.add_goal("Tiny Context Goal", status="active")
    
    # Add many facts to fill history
    for i in range(10):
        fid = db.add_fact(f"Dynamic Fact #{i} containing keyword test", category="test")
        db.set_embedding('fact', fid, embedder.embed_text(f"Dynamic Fact #{i} containing keyword test"))
        
    # Build prompt with small budget (500 tokens).
    prompt = builder.compile_prompt("test", total_budget=500)
    
    # Ensure all sections are generated and history was filled by redistribution
    assert "<system>" in prompt
    assert "<project_context>" in prompt
    assert "<relevant_history>" in prompt
    assert "<conversation>" in prompt
    assert "<user_message>" in prompt
    assert "Dynamic Fact #" in prompt


def test_cli_updates_and_unlink(tmp_path, monkeypatch):
    """Test constraint, decision, and fact updates, and unlink command via click CLI."""
    db_file = tmp_path / "cli_test.db"
    monkeypatch.setenv("MINERVA_DB_PATH", str(db_file))
    runner = CliRunner()
    
    # Initialize DB
    runner.invoke(cli_main, ["init"])
    
    # Add items
    res = runner.invoke(cli_main, ["add", "constraint", "Original Constraint Text"])
    assert "Added Constraint #1" in res.output
    
    res = runner.invoke(cli_main, ["add", "decision", "Original Decision Title", "Original Rationale"])
    assert "Added Decision #1" in res.output
    
    res = runner.invoke(cli_main, ["add", "fact", "Original Fact Text"])
    assert "Added Fact #1" in res.output
    
    # Link them
    res = runner.invoke(cli_main, ["link", "decision", "1", "fact", "1"])
    assert "Linked" in res.output
    
    # Update constraint
    res = runner.invoke(cli_main, ["update", "constraint", "1", "--text", "Updated Constraint Text", "--severity", "soft"])
    assert res.exit_code == 0
    assert "Constraint #1 updated" in res.output
    
    # Update decision
    res = runner.invoke(cli_main, ["update", "decision", "1", "--decision", "Updated Decision Title", "--rationale", "Updated Rationale"])
    assert res.exit_code == 0
    assert "Decision #1 updated" in res.output
    
    # Update fact
    res = runner.invoke(cli_main, ["update", "fact", "1", "--text", "Updated Fact Text", "--confidence", "0.8"])
    assert res.exit_code == 0
    assert "Fact #1 updated" in res.output
    
    # Check in DB
    db = Database(str(db_file))
    assert db.get_constraint(1)["text"] == "Updated Constraint Text"
    assert db.get_constraint(1)["severity"] == "soft"
    assert db.get_decision(1)["decision"] == "Updated Decision Title"
    assert db.get_fact(1)["text"] == "Updated Fact Text"
    assert db.get_fact(1)["confidence"] == 0.8
    
    # Unlink
    res = runner.invoke(cli_main, ["unlink", "decision", "1", "fact", "1"])
    assert res.exit_code == 0
    assert "Unlinked decision #1 and fact #1" in res.output
    
    # Verify link is deleted
    assert len(db.get_links_for_entity("decision", 1)) == 0


def test_mcp_server_update_tools(tmp_path):
    """Test server update functions directly."""
    db_file = tmp_path / "server_test.db"
    
    # Setup global db instance in server
    import minerva.server as server
    server.db = Database(str(db_file))
    
    # Add constraint, decision, fact
    cid = server.db.add_constraint("Test Constraint")
    did = server.db.add_decision("Test Decision", "rationale")
    fid = server.db.add_fact("Test Fact")
    
    # Test tool minerva_update_constraint
    res = server.minerva_update_constraint(cid, text="MCP Constraint", severity="soft")
    assert "Constraint #1 updated successfully" in res
    assert server.db.get_constraint(cid)["text"] == "MCP Constraint"
    assert server.db.get_constraint(cid)["severity"] == "soft"
    
    # Test tool minerva_update_decision
    res = server.minerva_update_decision(did, decision="MCP Decision", rationale="new rationale", decided_by="Architect")
    assert "Decision #1 updated successfully" in res
    assert server.db.get_decision(did)["decision"] == "MCP Decision"
    assert server.db.get_decision(did)["rationale"] == "new rationale"
    assert server.db.get_decision(did)["decided_by"] == "Architect"
    
    # Test tool minerva_update_fact
    res = server.minerva_update_fact(fid, text="MCP Fact", confidence=0.9, verified=1)
    assert "Fact #1 updated successfully" in res
    assert server.db.get_fact(fid)["text"] == "MCP Fact"
    assert server.db.get_fact(fid)["confidence"] == 0.9
    assert server.db.get_fact(fid)["verified"] == 1
