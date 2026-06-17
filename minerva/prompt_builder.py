import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tokenizers import Tokenizer
from minerva.db import Database
from minerva.retrieval import RetrievalEngine

# Static system persona — no LLM call needed
_SYSTEM_PROMPT = """You are an AI assistant augmented with Minerva, a local project memory system.
Minerva maintains structured knowledge about this project: goals, constraints, architectural decisions,
active tasks, and important facts. This context is injected before your response to ensure accuracy,
consistency, and alignment with project requirements.
Always prioritise the project context provided below when answering. If context conflicts with your
training data, defer to the project context — it reflects the current, user-verified state of this project."""


class PromptBuilder:
    def __init__(self, db: Database, engine: RetrievalEngine, tokenizer: "Tokenizer"):
        self.db = db
        self.engine = engine
        self.tokenizer = tokenizer

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.tokenizer.encode(text).ids)

    def format_goal(self, item: dict) -> str:
        return f"- [Goal #{item['id']}] {item['text']} (Priority: {item['priority']}, Status: {item['status']})"

    def format_constraint(self, item: dict) -> str:
        return f"- [Constraint #{item['id']}] [{item['severity'].upper()} - {item['type'].upper()}] {item['text']}"

    def format_decision(self, item: dict) -> str:
        base = f"- [Decision #{item['id']}] Decision: {item['decision']} | Rationale: {item['rationale']}"
        if item.get('supersedes_id'):
            base += f" (Supersedes Decision #{item['supersedes_id']})"
        return base

    def format_task(self, item: dict) -> str:
        desc = f" - {item['description']}" if item.get('description') else ""
        return f"- [Task #{item['id']}] [{item['status'].upper()}] {item['title']}{desc} (Priority: {item['priority']})"

    def format_fact(self, item: dict) -> str:
        return f"Fact #{item['id']} ({item['category']}): {item['text']}"

    def build_system_section(self) -> str:
        """Builds the <system> block (static persona, no budget constraint)."""
        return f"<system>\n{_SYSTEM_PROMPT}\n</system>"

    def build_project_context_section(self, budget: int) -> tuple:
        """
        Builds the <project_context> block fitting within the specified token budget.
        Returns a tuple: (content_str, set_of_included_entity_tuples)
        """
        # Fetch active records from DB
        goals = self.db.list_goals(status='active')
        constraints = self.db.list_constraints()
        decisions = self.db.list_decisions(status='current')
        tasks = [t for t in self.db.list_tasks() if t['status'] != 'done']

        # Sort elements logically to ensure critical records survive truncation
        goals.sort(key=lambda x: (-x.get('priority', 3), x.get('id', 0)))
        constraints.sort(key=lambda x: (0 if x.get('severity') == 'hard' else 1, x.get('id', 0)))
        decisions.sort(key=lambda x: (x.get('decided_at') or '', x.get('id', 0)), reverse=True)
        tasks.sort(key=lambda x: (0 if x.get('status') == 'in_progress' else 1, -x.get('priority', 3), x.get('id', 0)))

        # Format elements
        formatted_goals = [self.format_goal(g) for g in goals]
        formatted_constraints = [self.format_constraint(c) for c in constraints]
        formatted_decisions = [self.format_decision(d) for d in decisions]
        formatted_tasks = [self.format_task(t) for t in tasks]

        # Greedy assembly with respect to budget
        goals_text = "\n  ".join(formatted_goals) if formatted_goals else "(none)"
        constraints_text = "\n  ".join(formatted_constraints) if formatted_constraints else "(none)"
        decisions_text = "\n  ".join(formatted_decisions) if formatted_decisions else "(none)"
        tasks_text = "\n  ".join(formatted_tasks) if formatted_tasks else "(none)"

        template = (
            "<project_context>\n"
            "  ## Project Goals\n"
            "  <goals>\n"
            "    {goals}\n"
            "  </goals>\n\n"
            "  ## Active Constraints\n"
            "  <constraints>\n"
            "    {constraints}\n"
            "  </constraints>\n\n"
            "  ## Architectural Decisions\n"
            "  <decisions>\n"
            "    {decisions}\n"
            "  </decisions>\n\n"
            "  ## Active Tasks\n"
            "  <tasks>\n"
            "    {tasks}\n"
            "  </tasks>\n"
            "</project_context>"
        )

        content = template.format(
            goals=goals_text,
            constraints=constraints_text,
            decisions=decisions_text,
            tasks=tasks_text
        )

        if self.count_tokens(content) <= budget:
            included_set = set()
            for g in goals: included_set.add(('goal', g['id']))
            for c in constraints: included_set.add(('constraint', c['id']))
            for d in decisions: included_set.add(('decision', d['id']))
            for t in tasks: included_set.add(('task', t['id']))
            return content, included_set

        # Progressive truncation stages: (max_goals, max_constraints, max_decisions, max_tasks)
        stages = [
            (None, None, 3, 5),   # Stage 1: default tasks/decisions limits
            (10, 10, 3, 5),       # Stage 2: limit goals/constraints to 10
            (5, 5, 2, 3),         # Stage 3: limit goals/constraints to 5, decisions to 2, tasks to 3
            (3, 3, 1, 1),         # Stage 4: strict limit of 3 goals/constraints, 1 decision/task
        ]

        for max_goals, max_constraints, max_decisions, max_tasks in stages:
            sub_goals = list(formatted_goals)
            if max_goals is not None and len(sub_goals) > max_goals:
                sub_goals = sub_goals[:max_goals] + ["... [additional goals omitted due to token budget]"]

            sub_constraints = list(formatted_constraints)
            if max_constraints is not None and len(sub_constraints) > max_constraints:
                sub_constraints = sub_constraints[:max_constraints] + ["... [additional constraints omitted due to token budget]"]

            sub_decisions = list(formatted_decisions)
            if max_decisions is not None and len(sub_decisions) > max_decisions:
                sub_decisions = sub_decisions[:max_decisions] + ["... [additional decisions omitted due to token budget]"]

            sub_tasks = list(formatted_tasks)
            if max_tasks is not None and len(sub_tasks) > max_tasks:
                sub_tasks = sub_tasks[:max_tasks] + ["... [additional tasks omitted due to token budget]"]

            goals_text = "\n  ".join(sub_goals) if sub_goals else "(none)"
            constraints_text = "\n  ".join(sub_constraints) if sub_constraints else "(none)"
            decisions_text = "\n  ".join(sub_decisions) if sub_decisions else "(none)"
            tasks_text = "\n  ".join(sub_tasks) if sub_tasks else "(none)"

            content = template.format(
                goals=goals_text,
                constraints=constraints_text,
                decisions=decisions_text,
                tasks=tasks_text
            )

            if self.count_tokens(content) <= budget:
                included_set = set()
                included_goals = goals if max_goals is None else goals[:max_goals]
                included_constraints = constraints if max_constraints is None else constraints[:max_constraints]
                included_decisions = decisions if max_decisions is None else decisions[:max_decisions]
                included_tasks = tasks if max_tasks is None else tasks[:max_tasks]
                for g in included_goals: included_set.add(('goal', g['id']))
                for c in included_constraints: included_set.add(('constraint', c['id']))
                for d in included_decisions: included_set.add(('decision', d['id']))
                for t in included_tasks: included_set.add(('task', t['id']))
                return content, included_set

        # Hard fallback if even Stage 4 exceeds the budget
        return "<project_context>\n  <!-- [Project context omitted: size exceeded token limit] -->\n</project_context>", set()

    def build_relevant_history_section(self, query: str, budget: int, limit: int = 20, sort_by_semantic: bool = True, exclude_entities: set = None) -> str:
        """
        Builds the <relevant_history> block fitting within the specified token budget.
        """
        candidates = self.engine.retrieve(query, limit=limit)
        if not candidates:
            return "<relevant_history>\n  <!-- No relevant history found -->\n</relevant_history>"

        # Exclude active entities already present in <project_context>
        if exclude_entities:
            candidates = [cand for cand in candidates if (cand['type'], cand['id']) not in exclude_entities]

        # Sort candidates by semantic score descending to ensure direct semantic matches survive truncation
        if sort_by_semantic:
            candidates.sort(key=lambda x: x.get('semantic_score', x['score']), reverse=True)

        items_xml = []
        tokens_used = 0
        omitted_count = 0

        start_tag = "<relevant_history>\n"
        end_tag = "</relevant_history>"
        tokens_base = self.count_tokens(start_tag + end_tag)
        budget_left = budget - tokens_base

        for idx, cand in enumerate(candidates):
            c_type = cand['type']
            c_id = cand['id']
            score = cand['score']
            details = cand['details']

            if c_type == 'goal':
                body = self.format_goal(details)
            elif c_type == 'constraint':
                body = self.format_constraint(details)
            elif c_type == 'decision':
                body = self.format_decision(details)
            elif c_type == 'task':
                body = self.format_task(details)
            elif c_type == 'fact':
                body = self.format_fact(details)
            else:
                body = str(details)

            item_xml = f'  <item id="{c_id}" type="{c_type}" score="{score:.2f}">\n    {body}\n  </item>'
            item_tokens = self.count_tokens(item_xml + "\n")

            if tokens_used + item_tokens <= budget_left:
                items_xml.append(item_xml)
                tokens_used += item_tokens
            else:
                omitted_count = len(candidates) - idx
                break

        if omitted_count > 0:
            items_xml.append(f"  <!-- [Omitted {omitted_count} lower-scoring items due to token budget limits] -->")

        return start_tag + "\n".join(items_xml) + "\n" + end_tag

    def build_conversation_section(self) -> str:
        """
        Builds the <conversation> block.
        Phase 1: stub with no conversation history (conversation tracking is Phase 4+).
        """
        return "<conversation>\n  <!-- No conversation history (Phase 1: session memory not yet implemented) -->\n</conversation>"

    def build_user_message_section(self, query: str) -> str:
        """
        Builds the <user_message> block. Always verbatim — never truncated.
        """
        return f"<user_message>\n{query}\n</user_message>"

    def compile_prompt(self, query: str, total_budget: int = 4000) -> str:
        """
        Compiles the full 5-section XML prompt context for the given search query.

        Sections and target budget allocations (per §8.3 of the design spec):
          <system>           —  5% (static, always included)
          <project_context>  — 15%
          <relevant_history> — 50%
          <conversation>     — 25% (stub in Phase 1)
          <user_message>     —  5% (always verbatim, never truncated)
        """
        # Classify the query mode
        mode = self.engine.classify_query(query)

        # Dynamic retrieval limit and budget ratios per mode
        if mode == "BROAD_REVIEW":
            limit = 150
            project_ctx_ratio = 5.0
            history_ratio = 95.0
        elif mode == "HISTORICAL_AUDIT":
            limit = 120
            project_ctx_ratio = 10.0
            history_ratio = 90.0
        elif mode == "DEPENDENCY_ANALYSIS":
            limit = 120
            project_ctx_ratio = 15.0
            history_ratio = 50.0  # standard budget split ratio
        else:  # OPERATIONAL
            limit = 100
            project_ctx_ratio = 15.0
            history_ratio = 50.0

        # Apply safety margin (spec §8.4)
        total_budget = int(total_budget * 0.85)

        # 1. Build sections that are simple/static/always verbatim
        system_section = self.build_system_section()
        conversation = self.build_conversation_section()
        user_message = self.build_user_message_section(query)

        # 2. Count tokens of static sections
        static_tokens = (
            self.count_tokens(system_section) +
            self.count_tokens(conversation) +
            self.count_tokens(user_message) +
            10  # 10 tokens buffer for newline joining delimiters
        )

        # 3. Calculate remaining budget
        remaining_budget = total_budget - static_tokens
        if remaining_budget < 100:
            remaining_budget = 100

        # Target relative budgets dynamically scaled by ratios
        ratio_sum = project_ctx_ratio + history_ratio
        target_project_ctx = int(remaining_budget * (project_ctx_ratio / ratio_sum))
        target_history = remaining_budget - target_project_ctx

        # 4. Build project context using target budget
        project_ctx, included_entities = self.build_project_context_section(target_project_ctx)
        actual_project_ctx_tokens = self.count_tokens(project_ctx)

        # 5. Redistribute unused project context budget to relevant history
        unused_project_ctx = target_project_ctx - actual_project_ctx_tokens
        if unused_project_ctx > 0:
            history_budget = target_history + unused_project_ctx
        else:
            history_budget = target_history

        # Broad review needs diversity, so we keep MMR order. Other modes sort by semantic score.
        sort_by_semantic = (mode != "BROAD_REVIEW")

        # 6. Build relevant history with final redistributed budget and mode-specific limit
        relevant_history = self.build_relevant_history_section(
            query, history_budget, limit=limit, sort_by_semantic=sort_by_semantic, exclude_entities=included_entities
        )

        return "\n\n".join([
            system_section,
            project_ctx,
            relevant_history,
            conversation,
            user_message,
        ])

