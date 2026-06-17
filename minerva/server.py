import os
from mcp.server.fastmcp import FastMCP
from minerva.db import Database
from minerva.embeddings import EmbeddingModel
from minerva.retrieval import RetrievalEngine
from minerva.prompt_builder import PromptBuilder

# Initialize core services
db = Database()
embedder = EmbeddingModel()
engine = RetrievalEngine(db, embedder)

# Create FastMCP server instance
mcp = FastMCP("Minerva")

# =====================================================================
# MCP TOOLS
# =====================================================================

@mcp.tool()
def minerva_add_goal(text: str, priority: int = 3) -> str:
    """
    Add a stable, long-lived objective (goal) for the project.
    priority is 1 (lowest) to 5 (highest).
    """
    if priority < 1 or priority > 5:
        priority = 3
    goal_id = db.add_goal(text, priority=priority)
    
    # Generate and store embedding
    vector = embedder.embed_text(text)
    db.set_embedding('goal', goal_id, vector)
    
    return f"Goal #{goal_id} added successfully!"

@mcp.tool()
def minerva_add_constraint(text: str, severity: str = "hard", type_val: str = "technical") -> str:
    """
    Add a hard or soft constraint.
    severity: 'hard' or 'soft'
    type_val: 'technical', 'business', 'legal', 'budget', 'time'
    """
    severity = severity.lower() if severity.lower() in ('hard', 'soft') else 'hard'
    type_val = type_val.lower() if type_val.lower() in ('technical', 'business', 'legal', 'budget', 'time') else 'technical'
    
    constraint_id = db.add_constraint(text, severity=severity, type_val=type_val)
    
    # Generate and store embedding
    vector = embedder.embed_text(text)
    db.set_embedding('constraint', constraint_id, vector)
    
    return f"Constraint #{constraint_id} added successfully!"

@mcp.tool()
def minerva_add_decision(decision: str, rationale: str, supersedes_id: int = None) -> str:
    """
    Add an architectural or product decision with rationale.
    Optionally links to a previous decision ID it supersedes.
    """
    decision_id = db.add_decision(decision, rationale, status='current', supersedes_id=supersedes_id)
    
    # Generate and store embedding (combining decision + rationale)
    text_to_embed = f"Decision: {decision} | Rationale: {rationale}"
    vector = embedder.embed_text(text_to_embed)
    db.set_embedding('decision', decision_id, vector)
    
    return f"Decision #{decision_id} added successfully!"

@mcp.tool()
def minerva_add_task(title: str, description: str = "", priority: int = 3) -> str:
    """
    Add an active project task.
    priority is 1 (lowest) to 5 (highest).
    """
    if priority < 1 or priority > 5:
        priority = 3
    task_id = db.add_task(title, description=description, status='todo', priority=priority)
    
    # Generate and store embedding (combining title + description)
    text_to_embed = f"Title: {title} | Description: {description or ''}"
    vector = embedder.embed_text(text_to_embed)
    db.set_embedding('task', task_id, vector)
    
    return f"Task #{task_id} added successfully!"

@mcp.tool()
def minerva_update_task_status(task_id: int, status: str, outcome: str = "") -> str:
    """
    Update the status of a task.
    status: 'todo', 'in_progress', 'blocked', 'done'
    outcome: optional summary of task outcome (especially if status is 'done')
    """
    status = status.lower()
    if status not in ('todo', 'in_progress', 'blocked', 'done'):
        return f"Error: Invalid status '{status}'. Must be one of: todo, in_progress, blocked, done."
    
    success = db.update_task(task_id, status=status, outcome=outcome)
    if success:
        return f"Task #{task_id} updated to status '{status}'."
    return f"Error: Task #{task_id} not found."

@mcp.tool()
def minerva_add_fact(text: str, category: str = "general", confidence: float = 1.0) -> str:
    """
    Add an important atomic project fact (e.g. quirks, guidelines).
    confidence: float between 0.0 and 1.0
    """
    if confidence < 0.0 or confidence > 1.0:
        confidence = 1.0
    fact_id = db.add_fact(text, category=category, confidence=confidence)
    
    # Generate and store embedding
    vector = embedder.embed_text(text)
    db.set_embedding('fact', fact_id, vector)
    
    return f"Fact #{fact_id} added successfully!"

@mcp.tool()
def minerva_link_entities(target_type: str, target_id: int, source_type: str, source_id: int) -> str:
    """
    Link two memory entities together (e.g. linking a decision to a goal, or task to a constraint).
    Types must be one of: goal, constraint, decision, task, fact.
    """
    valid_types = ('goal', 'constraint', 'decision', 'task', 'fact')
    target_type = target_type.lower()
    source_type = source_type.lower()
    
    if target_type not in valid_types or source_type not in valid_types:
        return f"Error: Types must be one of {valid_types}."
        
    try:
        link_id = db.link_entities(target_type, target_id, source_type, source_id)
        return f"Link #{link_id} established between {target_type} #{target_id} and {source_type} #{source_id}."
    except Exception as e:
        return f"Error linking entities: {str(e)}"

@mcp.tool()
def minerva_query_memory(query: str, limit: int = 10) -> str:
    """
    Query all project memory using hybrid (keyword + vector) search.
    Returns a ranked list of relevant items with scores.
    """
    results = engine.retrieve(query, limit=limit)
    if not results:
        return "No relevant memories found."
        
    output_lines = []
    for r in results:
        r_type = r['type'].upper()
        r_id = r['id']
        score = r['score']
        details = r['details']
        
        output_lines.append(f"[{r_type} #{r_id}] (Score: {score:.2f})")
        if r['type'] == 'decision':
            output_lines.append(f"  Decision: {details['decision']}\n  Rationale: {details['rationale']}")
        elif r['type'] == 'task':
            desc = f" - {details['description']}" if details['description'] else ""
            output_lines.append(f"  {details['title']}{desc} (Status: {details['status']})")
        elif r['type'] == 'constraint':
            output_lines.append(f"  [{details['severity'].upper()}] {details['text']}")
        else:
            text_val = details.get('text') or details.get('title') or ""
            output_lines.append(f"  {text_val}")
            
    return "\n".join(output_lines)

# =====================================================================
# MCP TOOLS — DELETE & UPDATE
# =====================================================================

@mcp.tool()
def minerva_delete_goal(goal_id: int) -> str:
    """
    Delete a goal from project memory by its ID.
    This also removes its embedding and any links to other entities.
    """
    success = db.delete_goal(goal_id)
    if success:
        return f"Goal #{goal_id} deleted successfully."
    return f"Error: Goal #{goal_id} not found."

@mcp.tool()
def minerva_delete_constraint(constraint_id: int) -> str:
    """
    Delete a constraint from project memory by its ID.
    This also removes its embedding and any links to other entities.
    """
    success = db.delete_constraint(constraint_id)
    if success:
        return f"Constraint #{constraint_id} deleted successfully."
    return f"Error: Constraint #{constraint_id} not found."

@mcp.tool()
def minerva_delete_decision(decision_id: int) -> str:
    """
    Delete a decision from project memory by its ID.
    This also removes its embedding and any links to other entities.
    Note: superseded decisions are kept by convention; use this only for genuinely erroneous entries.
    """
    success = db.delete_decision(decision_id)
    if success:
        return f"Decision #{decision_id} deleted successfully."
    return f"Error: Decision #{decision_id} not found."

@mcp.tool()
def minerva_delete_task(task_id: int) -> str:
    """
    Delete a task from project memory by its ID.
    This also removes its embedding and any links to other entities.
    """
    success = db.delete_task(task_id)
    if success:
        return f"Task #{task_id} deleted successfully."
    return f"Error: Task #{task_id} not found."

@mcp.tool()
def minerva_delete_fact(fact_id: int) -> str:
    """
    Delete a fact from project memory by its ID.
    This also removes its embedding and any links to other entities.
    """
    success = db.delete_fact(fact_id)
    if success:
        return f"Fact #{fact_id} deleted successfully."
    return f"Error: Fact #{fact_id} not found."

@mcp.tool()
def minerva_update_goal(goal_id: int, text: str = None, priority: int = None, status: str = None) -> str:
    """
    Update fields of an existing goal.
    text: new goal text (optional)
    priority: new priority 1-5 (optional)
    status: 'active', 'superseded', or 'achieved' (optional)
    """
    if status and status not in ('active', 'superseded', 'achieved'):
        return f"Error: status must be one of: active, superseded, achieved."
    if priority is not None and not (1 <= priority <= 5):
        return f"Error: priority must be between 1 and 5."

    success = db.update_goal(goal_id, text=text, priority=priority, status=status)
    if success:
        # Re-embed if text changed
        if text:
            vector = embedder.embed_text(text)
            db.set_embedding('goal', goal_id, vector)
        return f"Goal #{goal_id} updated successfully."
    return f"Error: Goal #{goal_id} not found."

@mcp.tool()
def minerva_update_constraint(constraint_id: int, text: str = None, severity: str = None, type_val: str = None) -> str:
    """
    Update fields of an existing constraint.
    text: new constraint text (optional)
    severity: 'hard' or 'soft' (optional)
    type_val: 'technical', 'business', 'legal', 'budget', 'time' (optional)
    """
    if severity and severity.lower() not in ('hard', 'soft'):
        return "Error: severity must be 'hard' or 'soft'."
    if type_val and type_val.lower() not in ('technical', 'business', 'legal', 'budget', 'time'):
        return "Error: type_val must be technical, business, legal, budget, or time."

    success = db.update_constraint(constraint_id, text=text, severity=severity, type_val=type_val)
    if success:
        if text:
            vector = embedder.embed_text(text)
            db.set_embedding('constraint', constraint_id, vector)
        return f"Constraint #{constraint_id} updated successfully."
    return f"Error: Constraint #{constraint_id} not found."

@mcp.tool()
def minerva_update_decision(decision_id: int, decision: str = None, rationale: str = None, status: str = None, supersedes_id: int = None, alternatives_considered: str = None, decided_by: str = None) -> str:
    """
    Update fields of an existing decision.
    decision: new decision text (optional)
    rationale: new rationale text (optional)
    status: 'current' or 'superseded' (optional)
    supersedes_id: ID of the decision this replaces (optional)
    alternatives_considered: alternatives considered summary (optional)
    decided_by: who decided this (optional)
    """
    if status and status.lower() not in ('current', 'superseded'):
        return "Error: status must be 'current' or 'superseded'."

    success = db.update_decision(
        decision_id, decision=decision, rationale=rationale, status=status,
        supersedes_id=supersedes_id, alternatives_considered=alternatives_considered, decided_by=decided_by
    )
    if success:
        if decision or rationale:
            cur = db.get_decision(decision_id)
            text_to_embed = f"Decision: {cur['decision']} | Rationale: {cur['rationale']}"
            vector = embedder.embed_text(text_to_embed)
            db.set_embedding('decision', decision_id, vector)
        return f"Decision #{decision_id} updated successfully."
    return f"Error: Decision #{decision_id} not found."

@mcp.tool()
def minerva_update_fact(fact_id: int, text: str = None, category: str = None, confidence: float = None, source: str = None, verified: int = None, contradicts: str = None) -> str:
    """
    Update fields of an existing fact.
    text: new fact text (optional)
    category: new category (optional)
    confidence: new confidence rating 0.0-1.0 (optional)
    source: new source (optional)
    verified: verified status (0 or 1) (optional)
    contradicts: comma-separated fact IDs this fact contradicts (optional)
    """
    if confidence is not None and not (0.0 <= confidence <= 1.0):
        return "Error: confidence must be between 0.0 and 1.0."
    if verified is not None and verified not in (0, 1):
        return "Error: verified must be 0 or 1."

    success = db.update_fact(
        fact_id, text=text, category=category, confidence=confidence,
        source=source, verified=verified, contradicts=contradicts
    )
    if success:
        if text:
            vector = embedder.embed_text(text)
            db.set_embedding('fact', fact_id, vector)
        return f"Fact #{fact_id} updated successfully."
    return f"Error: Fact #{fact_id} not found."



@mcp.resource("minerva://project/goals")
def get_goals() -> str:
    """List all active goals."""
    goals = db.list_goals(status='active')
    if not goals:
        return "No active project goals."
    return "\n".join([f"- [Goal #{g['id']}] {g['text']} (Priority: {g['priority']})" for g in goals])

@mcp.resource("minerva://project/constraints")
def get_constraints() -> str:
    """List all constraints."""
    constraints = db.list_constraints()
    if not constraints:
        return "No project constraints."
    return "\n".join([f"- [Constraint #{c['id']}] [{c['severity'].upper()}] {c['text']}" for c in constraints])

@mcp.resource("minerva://project/decisions")
def get_decisions() -> str:
    """List all current architectural decisions."""
    decisions = db.list_decisions(status='current')
    if not decisions:
        return "No architectural decisions recorded."
    return "\n".join([f"- [Decision #{d['id']}] {d['decision']} (Rationale: {d['rationale']})" for d in decisions])

@mcp.resource("minerva://project/active-tasks")
def get_active_tasks() -> str:
    """List all active (non-completed) tasks."""
    tasks = [t for t in db.list_tasks() if t['status'] != 'done']
    if not tasks:
        return "No active tasks."
    return "\n".join([f"- [Task #{t['id']}] [{t['status'].upper()}] {t['title']} (Priority: {t['priority']})" for t in tasks])

# =====================================================================
# MCP PROMPTS
# =====================================================================

@mcp.prompt()
def compile_context(query: str) -> str:
    """
    Compiles the XML project context (goals, constraints, decisions, active tasks, and relevant history)
    for a given search query.
    """
    builder = PromptBuilder(db, engine, embedder.tokenizer)
    return builder.compile_prompt(query)

# =====================================================================
# RUNNER
# =====================================================================

def main():
    mcp.run()

if __name__ == "__main__":
    main()
