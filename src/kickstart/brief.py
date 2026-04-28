from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


PROJECT_TYPE_NEW = "new"
PROJECT_TYPE_EXISTING = "existing"


@dataclass(frozen=True)
class RepoSnapshot:
    path: Path
    detected_files: tuple[str, ...] = ()
    git_branch: str | None = None
    dirty: bool | None = None


@dataclass(frozen=True)
class ProjectAnswers:
    project_type: str
    name: str
    goal: str
    users: str
    stack: str
    constraints: str
    done: str
    risks: str
    quality_bar: str
    output_style: str = "concise"
    repo_snapshot: RepoSnapshot | None = None
    extra_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GeneratedFile:
    path: str
    content: str


def generate_files(answers: ProjectAnswers) -> list[GeneratedFile]:
    return [
        GeneratedFile("PROJECT.md", render_project_md(answers)),
        GeneratedFile("TASKS.md", render_tasks_md(answers)),
        GeneratedFile("KICKOFF.md", render_kickoff_md(answers)),
    ]


def render_project_md(answers: ProjectAnswers) -> str:
    repo_context = _render_repo_context(answers.repo_snapshot)
    return f"""# {answers.name}

## Purpose

{answers.goal}

## Project Type

{_project_type_label(answers.project_type)}

## Target Users

{answers.users}

## Stack

{answers.stack}

## Constraints

{answers.constraints}

## Definition Of Done

{answers.done}

## Quality Bar

{answers.quality_bar}

## Known Risks And Unknowns

{answers.risks}
{repo_context}
## Decisions

- Initial workflow starts with clarification, architecture comparison, execution planning, then the first small implementation slice.

## Key Commands

```bash
Record the validation command after the first successful run.
```
"""


def render_tasks_md(answers: ProjectAnswers) -> str:
    repo_task = ""
    if answers.project_type == PROJECT_TYPE_EXISTING:
        repo_task = "- Review existing docs and source files before proposing changes.\n"

    return f"""# TASKS

## Current Goal

Turn the project brief for `{answers.name}` into the first verified implementation slice.

## Active Tasks

- Confirm requirements, users, constraints, and definition of done.
- Compare 2-3 implementation approaches before writing code.
- Choose the smallest slice that proves the direction.
{repo_task}- Identify the repeatable validation command.
- Run edge-case, security, performance, and strict review passes before calling the slice done.

## Next Up

- Execute the kickoff brief in `KICKOFF.md`.

## Blocked

- Nothing currently blocked.

## Done

- Created initial project brief packet.

## Notes / Risks / Suggestions

- Keep this file short and current.
- Move stable context into `PROJECT.md`.
- Record meaningful architecture or product decisions in `PROJECT.md` or `docs/DECISIONS.md`.

## Session Log

- Initialized project from Kickstart.
"""


def render_kickoff_md(answers: ProjectAnswers) -> str:
    repo_instruction = ""
    if answers.project_type == PROJECT_TYPE_EXISTING:
        repo_instruction = """
Before proposing changes, inspect the existing repository structure, docs, tests, and git status. Ground recommendations in the current codebase rather than generic advice.
"""
    stack_instruction = ""
    if "needs recommendation" in answers.stack.lower():
        stack_instruction = """
Stack note:

- The user does not know the best technical stack yet. Compare stack choices in plain English before recommending one.
"""
    output_instruction = _render_output_instruction(answers.output_style)

    return f"""# Kickoff Brief

Use this as the first instruction for a coding assistant.

```text
You are my senior engineering partner for this project.

Project: {answers.name}

Goal:
{answers.goal}

Users:
{answers.users}

Stack:
{answers.stack}

Constraints:
{answers.constraints}

Definition of done:
{answers.done}

Known risks and unknowns:
{answers.risks}

Quality bar:
{answers.quality_bar}
{repo_instruction}
{stack_instruction}
Work in this order:

1. Clarify: Ask focused questions about vague requirements, scale, users, constraints, and edge cases.
2. Design: Propose 2-3 possible approaches and compare them on simplicity, maintainability, cost, speed, and risk.
3. Plan: Break the chosen approach into components, data flow, interfaces, and the first small implementation slice.
4. Build: Implement only the first slice after the plan is clear.
5. Verify: Run the relevant validation command and report exact results.
6. Review: Check edge cases, failure modes, security risks, performance bottlenecks, and code quality before calling the work done.
{output_instruction}

Do not rush into code. Tailor every recommendation to this project's context.
```
"""


def quality_bar_for_preset(preset: str) -> str:
    presets = {
        "prototype": "Fast, simple, and easy to change. Prefer working behavior over polish, but keep the code understandable.",
        "production": "Tested, maintainable, operationally clear, and defensive around realistic failures.",
        "learning": "Clear, beginner-friendly, and explanatory. Prefer readable structure and brief notes over clever shortcuts.",
        "repo-cleanup": "Truth-aligned docs, clean repository hygiene, passing validation, and no stale or private project artifacts.",
    }
    return presets[preset]


def _render_output_instruction(output_style: str) -> str:
    if output_style == "detailed":
        return """

Output style:

- Include acceptance checks for the first implementation slice.
- Call out tradeoffs and assumptions explicitly.
- Keep explanations practical, but include enough detail for a fresh maintainer to continue.
"""
    return """

Output style:

- Keep the response concise and action-oriented.
"""


def _render_repo_context(snapshot: RepoSnapshot | None) -> str:
    if snapshot is None:
        return ""

    files = ", ".join(snapshot.detected_files) if snapshot.detected_files else "No common project files detected"
    branch = snapshot.git_branch or "unknown"
    dirty = "unknown" if snapshot.dirty is None else ("yes" if snapshot.dirty else "no")

    return f"""
## Existing Repo Snapshot

- Path: `{snapshot.path}`
- Detected files: {files}
- Git branch: {branch}
- Uncommitted changes: {dirty}

"""


def _project_type_label(project_type: str) -> str:
    if project_type == PROJECT_TYPE_EXISTING:
        return "Existing repository"
    return "New project"
