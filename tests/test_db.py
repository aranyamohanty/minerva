import pytest
import numpy as np
from minerva.db import Database

@pytest.fixture
def db():
    # Use in-memory database for testing
    database = Database(":memory:")
    yield database
    database.close()

def test_goals_crud(db):
    # Create
    gid = db.add_goal("Finish Minerva Phase 1 MVP", priority=5)
    assert gid > 0
    
    # Read
    goal = db.get_goal(gid)
    assert goal is not None
    assert goal['text'] == "Finish Minerva Phase 1 MVP"
    assert goal['priority'] == 5
    assert goal['status'] == 'active'
    
    # List
    goals = db.list_goals(status='active')
    assert len(goals) == 1
    assert goals[0]['id'] == gid
    
    # FTS5 search (Trigger sync validation)
    fts_res = db.fts_search('goal', 'Finish')
    assert len(fts_res) == 1
    assert fts_res[0]['id'] == gid
    
    # Update
    success = db.update_goal(gid, text="Finish Minerva Phase 1 MVP Now", priority=4, status="achieved")
    assert success is True
    updated_goal = db.get_goal(gid)
    assert updated_goal['text'] == "Finish Minerva Phase 1 MVP Now"
    assert updated_goal['priority'] == 4
    assert updated_goal['status'] == "achieved"
    
    # FTS5 search updated text
    fts_res_updated = db.fts_search('goal', 'Now')
    assert len(fts_res_updated) == 1
    
    # Delete
    del_success = db.delete_goal(gid)
    assert del_success is True
    assert db.get_goal(gid) is None
    
    # FTS5 should be deleted
    assert len(db.fts_search('goal', 'Finish')) == 0

def test_constraints_crud(db):
    cid = db.add_constraint("Must run on CPU locally", severity="hard", type_val="technical")
    assert cid > 0
    
    constraint = db.get_constraint(cid)
    assert constraint['text'] == "Must run on CPU locally"
    assert constraint['severity'] == "hard"
    
    # List
    constraints = db.list_constraints(type_val="technical")
    assert len(constraints) == 1
    
    # Search
    assert len(db.fts_search('constraint', 'CPU')) == 1
    
    # Delete
    assert db.delete_constraint(cid) is True
    assert db.get_constraint(cid) is None

def test_decisions_crud(db):
    did = db.add_decision("Use SQLite", "Zero-config embedded DB")
    assert did > 0
    
    decision = db.get_decision(did)
    assert decision['decision'] == "Use SQLite"
    assert decision['status'] == 'current'
    
    # Add superseding decision
    did2 = db.add_decision("Use SQLite WAL Mode", "For concurrent reads", supersedes_id=did)
    assert did2 > 0
    
    # Old decision should be marked superseded
    assert db.get_decision(did)['status'] == 'superseded'
    assert db.get_decision(did2)['status'] == 'current'
    
    # Search
    assert len(db.fts_search('decision', 'WAL')) == 1

def test_tasks_crud(db):
    tid = db.add_task("Write db tests", "Tests for SQLite layer", priority=4)
    assert tid > 0
    
    task = db.get_task(tid)
    assert task['title'] == "Write db tests"
    assert task['status'] == 'todo'
    
    # Update status to done
    db.update_task(tid, status='done', outcome="Finished tests")
    updated_task = db.get_task(tid)
    assert updated_task['status'] == 'done'
    assert updated_task['completed_at'] is not None
    assert updated_task['outcome'] == "Finished tests"

def test_facts_crud(db):
    fid = db.add_fact("BGE-small has 384 dimensions", category="ml")
    assert fid > 0
    
    fact = db.get_fact(fid)
    assert fact['text'] == "BGE-small has 384 dimensions"
    assert fact['reference_count'] == 1
    
    # Reference increment
    db.increment_fact_reference(fid)
    assert db.get_fact(fid)['reference_count'] == 2

def test_linking_entities(db):
    gid = db.add_goal("Goal to resolve", priority=4)
    did = db.add_decision("Decision that resolves goal", "Rationale detail")
    
    # Link
    link_id = db.link_entities("decision", did, "goal", gid)
    assert link_id > 0
    
    # Retrieve links for goal
    links = db.get_links_for_entity("goal", gid)
    assert len(links) == 1
    assert links[0]['type'] == 'decision'
    assert links[0]['id'] == did
    assert links[0]['details']['decision'] == "Decision that resolves goal"
    
    # Unlink
    success = db.unlink_entities("decision", did, "goal", gid)
    assert success is True
    assert len(db.get_links_for_entity("goal", gid)) == 0

def test_embeddings_storage(db):
    vector = np.random.rand(384).astype(np.float32)
    db.set_embedding('goal', 10, vector)
    
    retrieved_vector = db.get_embedding('goal', 10)
    assert retrieved_vector is not None
    assert retrieved_vector.shape == (384,)
    assert np.allclose(vector, retrieved_vector)
    
    # Get all embeddings
    all_emb = db.get_all_embeddings('goal')
    assert len(all_emb) == 1
    assert all_emb[0][0] == 10
    assert np.allclose(vector, all_emb[0][1])
