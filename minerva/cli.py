import click
import sys
import os

# DLL loading helper is handled in embeddings.py which is imported lazily.

from minerva.db import Database
import sqlite3
import functools

def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.IntegrityError as e:
            click.echo(f"Error: Database integrity constraint failed: {e}", err=True)
            sys.exit(1)
        except sqlite3.Error as e:
            click.echo(f"Error: Database error: {e}", err=True)
            sys.exit(1)
    return wrapper

@click.group()
def main():
    """Minerva CLI tool for managing local project memory."""
    pass

@main.command()
@handle_db_errors
def init():
    """Initialize the Minerva local database and download BGE embedding models."""
    click.echo("Initializing database...")
    db = Database()
    
    click.echo("Downloading and preparing local embedding models (BGE-small)...")
    from minerva.embeddings import EmbeddingModel
    embedder = EmbeddingModel()
    embedder.ensure_model_downloaded()
    
    click.echo("Minerva initialized successfully!")

@main.command()
def start():
    """Start the Model Context Protocol (MCP) stdio server."""
    # Imported lazily to prevent loading it for simple CLI operations
    from minerva.server import mcp
    click.echo("Starting Minerva MCP stdio server...", err=True)
    mcp.run()

# =====================================================================
# ADD SUBCOMMANDS (CRUD Create)
# =====================================================================

@click.group()
def add():
    """Add a new item to the project memory."""
    pass

@add.command(name="goal")
@click.argument("text")
@click.option("--priority", default=3, help="Priority from 1 (lowest) to 5 (highest)")
@handle_db_errors
def add_goal(text, priority):
    """Add a project goal."""
    from minerva.embeddings import EmbeddingModel
    db = Database()
    embedder = EmbeddingModel()
    goal_id = db.add_goal(text, priority=priority)
    
    # Embedding
    vector = embedder.embed_text(text)
    db.set_embedding('goal', goal_id, vector)
    
    click.echo(f"Added Goal #{goal_id}")

@add.command(name="constraint")
@click.argument("text")
@click.option("--severity", default="hard", type=click.Choice(["hard", "soft"]), help="Constraint severity")
@click.option("--type", "type_val", default="technical", type=click.Choice(["technical", "business", "legal", "budget", "time"]), help="Constraint type")
@handle_db_errors
def add_constraint(text, severity, type_val):
    """Add a project constraint."""
    from minerva.embeddings import EmbeddingModel
    db = Database()
    embedder = EmbeddingModel()
    cid = db.add_constraint(text, severity=severity, type_val=type_val)
    
    # Embedding
    vector = embedder.embed_text(text)
    db.set_embedding('constraint', cid, vector)
    
    click.echo(f"Added Constraint #{cid}")

@add.command(name="decision")
@click.argument("decision")
@click.argument("rationale")
@click.option("--supersedes", "supersedes_id", type=int, default=None, help="ID of the decision this decision replaces")
@handle_db_errors
def add_decision(decision, rationale, supersedes_id):
    """Add an architectural or product decision."""
    from minerva.embeddings import EmbeddingModel
    db = Database()
    embedder = EmbeddingModel()
    did = db.add_decision(decision, rationale, status='current', supersedes_id=supersedes_id)
    
    # Embedding
    text_to_embed = f"Decision: {decision} | Rationale: {rationale}"
    vector = embedder.embed_text(text_to_embed)
    db.set_embedding('decision', did, vector)
    
    click.echo(f"Added Decision #{did}")

@add.command(name="task")
@click.argument("title")
@click.option("--description", default="", help="Detailed task description")
@click.option("--priority", default=3, help="Priority from 1 (lowest) to 5 (highest)")
@handle_db_errors
def add_task(title, description, priority):
    """Add an active task."""
    from minerva.embeddings import EmbeddingModel
    db = Database()
    embedder = EmbeddingModel()
    tid = db.add_task(title, description=description, status='todo', priority=priority)
    
    # Embedding
    text_to_embed = f"Title: {title} | Description: {description or ''}"
    vector = embedder.embed_text(text_to_embed)
    db.set_embedding('task', tid, vector)
    
    click.echo(f"Added Task #{tid}")

@add.command(name="fact")
@click.argument("text")
@click.option("--category", default="general", help="Category category (e.g. environment, tech)")
@click.option("--confidence", default=1.0, help="Confidence rating (0.0 to 1.0)")
@handle_db_errors
def add_fact(text, category, confidence):
    """Add an atomic project fact."""
    from minerva.embeddings import EmbeddingModel
    db = Database()
    embedder = EmbeddingModel()
    fid = db.add_fact(text, category=category, confidence=confidence)
    
    # Embedding
    vector = embedder.embed_text(text)
    db.set_embedding('fact', fid, vector)
    
    click.echo(f"Added Fact #{fid}")

# =====================================================================
# LIST SUBCOMMANDS (CRUD Read)
# =====================================================================

@click.group(name="list")
def list_group():
    """List items in the project memory."""
    pass

@list_group.command(name="goals")
@handle_db_errors
def list_goals():
    """List active goals."""
    db = Database()
    goals = db.list_goals()
    if not goals:
        click.echo("No goals found.")
        return
    for g in goals:
        click.echo(f"[Goal #{g['id']}] [{g['status'].upper()}] (Priority: {g['priority']}) {g['text']}")

@list_group.command(name="constraints")
@handle_db_errors
def list_constraints():
    """List all constraints."""
    db = Database()
    constraints = db.list_constraints()
    if not constraints:
        click.echo("No constraints found.")
        return
    for c in constraints:
        click.echo(f"[Constraint #{c['id']}] [{c['severity'].upper()} - {c['type'].upper()}] {c['text']}")

@list_group.command(name="decisions")
@handle_db_errors
def list_decisions():
    """List architectural decisions."""
    db = Database()
    decisions = db.list_decisions()
    if not decisions:
        click.echo("No decisions found.")
        return
    for d in decisions:
        sup_str = f" (Supersedes #{d['supersedes_id']})" if d['supersedes_id'] else ""
        click.echo(f"[Decision #{d['id']}] [{d['status'].upper()}] Decision: {d['decision']}{sup_str}\n  Rationale: {d['rationale']}")

@list_group.command(name="tasks")
@handle_db_errors
def list_tasks():
    """List tasks."""
    db = Database()
    tasks = db.list_tasks()
    if not tasks:
        click.echo("No tasks found.")
        return
    for t in tasks:
        desc = f" - {t['description']}" if t['description'] else ""
        click.echo(f"[Task #{t['id']}] [{t['status'].upper()}] (Priority: {t['priority']}) {t['title']}{desc}")

@list_group.command(name="facts")
@handle_db_errors
def list_facts():
    """List key facts."""
    db = Database()
    facts = db.list_facts()
    if not facts:
        click.echo("No facts found.")
        return
    for f in facts:
        click.echo(f"[Fact #{f['id']}] ({f['category']}) (Refs: {f['reference_count']}) {f['text']}")

# =====================================================================
# LINK & SEARCH & PREVIEW
# =====================================================================

@main.command()
@click.argument("target_type")
@click.argument("target_id", type=int)
@click.argument("source_type")
@click.argument("source_id", type=int)
@handle_db_errors
def link(target_type, target_id, source_type, source_id):
    """Link two memory entities (e.g. link decision 3 goal 1)."""
    db = Database()
    try:
        link_id = db.link_entities(target_type, target_id, source_type, source_id)
        click.echo(f"Linked {target_type} #{target_id} and {source_type} #{source_id} (Link #{link_id})")
    except Exception as e:
        click.echo(f"Error establishing link: {e}", err=True)

@main.command()
@click.argument("target_type")
@click.argument("target_id", type=int)
@click.argument("source_type")
@click.argument("source_id", type=int)
@handle_db_errors
def unlink(target_type, target_id, source_type, source_id):
    """Unlink two memory entities (e.g. unlink decision 3 goal 1)."""
    db = Database()
    success = db.unlink_entities(target_type, target_id, source_type, source_id)
    if success:
        click.echo(f"Unlinked {target_type} #{target_id} and {source_type} #{source_id}")
    else:
        click.echo("Error: Link not found between specified entities.", err=True)

@main.command()
@click.argument("query")
@click.option("--limit", default=10, help="Maximum number of results to display")
@handle_db_errors
def search(query, limit):
    """Search project memory using hybrid search (BM25 + vector)."""
    from minerva.embeddings import EmbeddingModel
    from minerva.retrieval import RetrievalEngine
    db = Database()
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)
    
    results = engine.retrieve(query, limit=limit)
    if not results:
        click.echo("No matching memories found.")
        return
        
    for r in results:
        click.echo(f"[{r['type'].upper()} #{r['id']}] (Score: {r['score']:.2f})")
        if r['type'] == 'decision':
            click.echo(f"  Decision: {r['details']['decision']}\n  Rationale: {r['details']['rationale']}")
        elif r['type'] == 'task':
            desc = f" - {r['details']['description']}" if r['details']['description'] else ""
            click.echo(f"  {r['details']['title']}{desc} (Status: {r['details']['status']})")
        elif r['type'] == 'constraint':
            click.echo(f"  [{r['details']['severity'].upper()}] {r['details']['text']}")
        else:
            text_val = r['details'].get('text') or r['details'].get('title') or ""
            click.echo(f"  {text_val}")

@main.command()
@click.argument("query")
@click.option("--budget", default=4000, help="Total token budget for prompt")
@handle_db_errors
def preview(query, budget):
    """Compile and preview the XML prompt context for a query."""
    from minerva.embeddings import EmbeddingModel
    from minerva.retrieval import RetrievalEngine
    from minerva.prompt_builder import PromptBuilder
    db = Database()
    embedder = EmbeddingModel()
    engine = RetrievalEngine(db, embedder)
    builder = PromptBuilder(db, engine, embedder.tokenizer)
    
    compiled = builder.compile_prompt(query, total_budget=budget)
    click.echo(compiled)

# =====================================================================
# DELETE SUBCOMMANDS (CRUD Delete)
# =====================================================================

@click.group(name="delete")
def delete_group():
    """Delete an item from project memory by ID."""
    pass

@delete_group.command(name="goal")
@click.argument("goal_id", type=int)
@handle_db_errors
def delete_goal(goal_id):
    """Delete a goal by ID."""
    db = Database()
    success = db.delete_goal(goal_id)
    if success:
        click.echo(f"Goal #{goal_id} deleted.")
    else:
        click.echo(f"Error: Goal #{goal_id} not found.", err=True)

@delete_group.command(name="constraint")
@click.argument("constraint_id", type=int)
@handle_db_errors
def delete_constraint(constraint_id):
    """Delete a constraint by ID."""
    db = Database()
    success = db.delete_constraint(constraint_id)
    if success:
        click.echo(f"Constraint #{constraint_id} deleted.")
    else:
        click.echo(f"Error: Constraint #{constraint_id} not found.", err=True)

@delete_group.command(name="decision")
@click.argument("decision_id", type=int)
@handle_db_errors
def delete_decision(decision_id):
    """Delete a decision by ID."""
    db = Database()
    success = db.delete_decision(decision_id)
    if success:
        click.echo(f"Decision #{decision_id} deleted.")
    else:
        click.echo(f"Error: Decision #{decision_id} not found.", err=True)

@delete_group.command(name="task")
@click.argument("task_id", type=int)
@handle_db_errors
def delete_task(task_id):
    """Delete a task by ID."""
    db = Database()
    success = db.delete_task(task_id)
    if success:
        click.echo(f"Task #{task_id} deleted.")
    else:
        click.echo(f"Error: Task #{task_id} not found.", err=True)

@delete_group.command(name="fact")
@click.argument("fact_id", type=int)
@handle_db_errors
def delete_fact(fact_id):
    """Delete a fact by ID."""
    db = Database()
    success = db.delete_fact(fact_id)
    if success:
        click.echo(f"Fact #{fact_id} deleted.")
    else:
        click.echo(f"Error: Fact #{fact_id} not found.", err=True)

# =====================================================================
# UPDATE SUBCOMMANDS (CRUD Update)
# =====================================================================

@click.group(name="update")
def update_group():
    """Update fields of an existing item in project memory."""
    pass

@update_group.command(name="goal")
@click.argument("goal_id", type=int)
@click.option("--text", default=None, help="New goal text")
@click.option("--priority", default=None, type=int, help="New priority (1-5)")
@click.option("--status", default=None, type=click.Choice(["active", "superseded", "achieved"]), help="New status")
@handle_db_errors
def update_goal(goal_id, text, priority, status):
    """Update a goal's text, priority, or status."""
    if text is None and priority is None and status is None:
        click.echo("Error: Provide at least one of --text, --priority, or --status.", err=True)
        return
    db = Database()
    success = db.update_goal(goal_id, text=text, priority=priority, status=status)
    if success:
        # Re-embed if text changed
        if text:
            from minerva.embeddings import EmbeddingModel
            embedder = EmbeddingModel()
            vector = embedder.embed_text(text)
            db.set_embedding('goal', goal_id, vector)
        click.echo(f"Goal #{goal_id} updated.")
    else:
        click.echo(f"Error: Goal #{goal_id} not found.", err=True)

@update_group.command(name="task")
@click.argument("task_id", type=int)
@click.option("--status", default=None, type=click.Choice(["todo", "in_progress", "blocked", "done"]), help="New task status")
@click.option("--outcome", default=None, help="Outcome summary (especially when marking done)")
@handle_db_errors
def update_task(task_id, status, outcome):
    """Update a task's status or outcome."""
    if status is None and outcome is None:
        click.echo("Error: Provide at least one of --status or --outcome.", err=True)
        return
    db = Database()
    success = db.update_task(task_id, status=status, outcome=outcome)
    if success:
        click.echo(f"Task #{task_id} updated.")
    else:
        click.echo(f"Error: Task #{task_id} not found.", err=True)

@update_group.command(name="constraint")
@click.argument("constraint_id", type=int)
@click.option("--text", default=None, help="New constraint text")
@click.option("--severity", default=None, type=click.Choice(["hard", "soft"]), help="New severity")
@click.option("--type", "type_val", default=None, type=click.Choice(["technical", "business", "legal", "budget", "time"]), help="New type")
@handle_db_errors
def update_constraint(constraint_id, text, severity, type_val):
    """Update a constraint's text, severity, or type."""
    if text is None and severity is None and type_val is None:
        click.echo("Error: Provide at least one update option.", err=True)
        return
    db = Database()
    success = db.update_constraint(constraint_id, text=text, severity=severity, type_val=type_val)
    if success:
        if text:
            from minerva.embeddings import EmbeddingModel
            embedder = EmbeddingModel()
            vector = embedder.embed_text(text)
            db.set_embedding('constraint', constraint_id, vector)
        click.echo(f"Constraint #{constraint_id} updated.")
    else:
        click.echo(f"Error: Constraint #{constraint_id} not found.", err=True)

@update_group.command(name="decision")
@click.argument("decision_id", type=int)
@click.option("--decision", "decision_val", default=None, help="New decision text")
@click.option("--rationale", default=None, help="New rationale text")
@click.option("--status", default=None, type=click.Choice(["current", "superseded"]), help="New status")
@click.option("--supersedes", "supersedes_id", type=int, default=None, help="ID of decision this replaces")
@click.option("--alternatives", "alternatives_considered", default=None, help="Alternatives considered")
@click.option("--decided-by", default=None, help="Who decided this")
@handle_db_errors
def update_decision(decision_id, decision_val, rationale, status, supersedes_id, alternatives_considered, decided_by):
    """Update a decision's text, rationale, status, or metadata."""
    if decision_val is None and rationale is None and status is None and supersedes_id is None and alternatives_considered is None and decided_by is None:
        click.echo("Error: Provide at least one update option.", err=True)
        return
    db = Database()
    success = db.update_decision(
        decision_id, decision=decision_val, rationale=rationale, status=status,
        supersedes_id=supersedes_id, alternatives_considered=alternatives_considered, decided_by=decided_by
    )
    if success:
        if decision_val or rationale:
            cur = db.get_decision(decision_id)
            text_to_embed = f"Decision: {cur['decision']} | Rationale: {cur['rationale']}"
            from minerva.embeddings import EmbeddingModel
            embedder = EmbeddingModel()
            vector = embedder.embed_text(text_to_embed)
            db.set_embedding('decision', decision_id, vector)
        click.echo(f"Decision #{decision_id} updated.")
    else:
        click.echo(f"Error: Decision #{decision_id} not found.", err=True)

@update_group.command(name="fact")
@click.argument("fact_id", type=int)
@click.option("--text", default=None, help="New fact text")
@click.option("--category", default=None, help="New category")
@click.option("--confidence", default=None, type=float, help="New confidence rating")
@click.option("--source", default=None, help="New source")
@click.option("--verified", default=None, type=int, help="Verified status (0 or 1)")
@click.option("--contradicts", default=None, help="Fact IDs this fact contradicts")
@handle_db_errors
def update_fact(fact_id, text, category, confidence, source, verified, contradicts):
    """Update a fact's text, category, confidence, or metadata."""
    if text is None and category is None and confidence is None and source is None and verified is None and contradicts is None:
        click.echo("Error: Provide at least one update option.", err=True)
        return
    db = Database()
    success = db.update_fact(
        fact_id, text=text, category=category, confidence=confidence,
        source=source, verified=verified, contradicts=contradicts
    )
    if success:
        if text:
            from minerva.embeddings import EmbeddingModel
            embedder = EmbeddingModel()
            vector = embedder.embed_text(text)
            db.set_embedding('fact', fact_id, vector)
        click.echo(f"Fact #{fact_id} updated.")
    else:
        click.echo(f"Error: Fact #{fact_id} not found.", err=True)

# Register groups
main.add_command(add)
main.add_command(list_group)
main.add_command(delete_group)
main.add_command(update_group)

if __name__ == "__main__":
    main()
