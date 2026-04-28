# Kickstart

## Purpose

Improve the existing project kickoff generator without changing its public CLI contract.

## Project Type

Existing repository

## Target Users

A team or coworkers

## Stack

Needs recommendation from the assistant based on the project goal and constraints.

## Constraints

Keep behavior covered by unit tests and avoid extra runtime dependencies.

## Definition Of Done

The README, tests, and generated examples all match the implemented behavior.

## Quality Bar

Tested, maintainable, operationally clear, and defensive around realistic failures.

## Known Risks And Unknowns

Existing users may rely on current preview and write behavior.

## Existing Repo Snapshot

- Path: `/path/to/project`
- Detected files: README.md, PROJECT.md, TASKS.md, pyproject.toml
- Git branch: main
- Uncommitted changes: no


## Decisions

- Initial workflow starts with clarification, architecture comparison, execution planning, then the first small implementation slice.

## Key Commands

```bash
Record the validation command after the first successful run.
```
