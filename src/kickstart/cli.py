from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .brief import (
    PROJECT_TYPE_EXISTING,
    PROJECT_TYPE_NEW,
    ProjectAnswers,
    RepoSnapshot,
    generate_files,
    quality_bar_for_preset,
)
from .ui import Tui


UI = Tui()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        return run_init(args)

    parser.print_help()
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kickstart",
        description="Forge rough project ideas into structured kickoff briefs.",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Create a project brief packet")
    init_parser.add_argument(
        "--project-type",
        choices=[PROJECT_TYPE_NEW, PROJECT_TYPE_EXISTING],
        help="Use 'new' for a new project or 'existing' for an existing repository.",
    )
    mode = init_parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="Print generated files without writing them.")
    mode.add_argument("--write", action="store_true", help="Write generated files.")
    init_parser.add_argument("--output-dir", type=Path, default=Path.cwd(), help="Directory for generated files.")
    init_parser.add_argument("--repo-path", type=Path, help="Existing repository path to inspect.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite generated files if they exist.")

    return parser


def run_init(args: argparse.Namespace) -> int:
    print(
        UI.panel(
            "Kickstart",
            [
                "Answer a few plain-English questions.",
                "Kickstart will draft PROJECT.md, TASKS.md, and KICKOFF.md.",
            ],
        )
    )
    project_type = args.project_type or ask_choice(
        "Are you starting a new project, or working inside an existing repo?",
        [(PROJECT_TYPE_NEW, "New project"), (PROJECT_TYPE_EXISTING, "Existing repo")],
    )
    write_files = args.write
    if not args.write and not args.preview:
        output_mode = ask_choice(
            "Should I write the generated files directly, or preview them first?",
            [("preview", "Preview first"), ("write", "Write files directly")],
        )
        write_files = output_mode == "write"

    repo_snapshot = None
    repo_path = args.repo_path
    if project_type == PROJECT_TYPE_EXISTING:
        if repo_path is None:
            repo_path = Path(ask_text("Repo path", default=str(Path.cwd())))
        repo_snapshot = inspect_repo(repo_path)

    answers = collect_answers(project_type, repo_snapshot)
    generated_files = generate_files(answers)

    if write_files:
        write_generated_files(args.output_dir, generated_files, force=args.force)
        print(f"Wrote {len(generated_files)} files to {args.output_dir}")
    else:
        print_preview(generated_files)

    return 0


def collect_answers(project_type: str, repo_snapshot: RepoSnapshot | None) -> ProjectAnswers:
    default_name = repo_snapshot.path.name if repo_snapshot else Path.cwd().name
    name = ask_text("Project name", default=default_name)
    goal = ask_text("What do you want to make?")
    users = collect_users()
    stack = collect_stack()
    return ProjectAnswers(
        project_type=project_type,
        name=name,
        goal=goal,
        users=users,
        stack=stack,
        constraints=ask_text("Any must-haves or limits?", default="Keep it simple, affordable, and easy to maintain."),
        done=ask_text("What would make this feel finished?", default="A working version I can try."),
        risks=ask_text("Anything uncertain or worrying?", default="I am not sure yet."),
        quality_bar=collect_quality_bar(),
        output_style=ask_choice(
            "How detailed should the generated kickoff guidance be?",
            [("concise", "Concise"), ("detailed", "Detailed")],
        ),
        repo_snapshot=repo_snapshot,
    )


def collect_users() -> str:
    audience = ask_choice(
        "Who is this for?",
        [
            ("me", "Just me"),
            ("friends", "Me and friends"),
            ("team", "A team or coworkers"),
            ("customers", "Customers or public users"),
            ("custom", "Custom"),
        ],
    )
    labels = {
        "me": "Just me",
        "friends": "Me and friends",
        "team": "A team or coworkers",
        "customers": "Customers or public users",
    }
    if audience == "custom":
        return ask_text("Who is it for?")
    return labels[audience]


def collect_stack() -> str:
    stack_choice = ask_choice(
        "Do you know what technology you want to use?",
        [
            ("suggest", "Suggest one for me"),
            ("enter", "I know the stack"),
            ("none", "Not technical or not relevant"),
        ],
    )
    if stack_choice == "enter":
        return ask_text("Tech stack")
    if stack_choice == "none":
        return "Not technical or not relevant."
    return "Needs recommendation from the assistant based on the project goal and constraints."


def collect_quality_bar() -> str:
    preset = ask_choice(
        "What quality preset fits this work?",
        [
            ("prototype", "Prototype"),
            ("production", "Production"),
            ("learning", "Learning"),
            ("repo-cleanup", "Repo cleanup"),
            ("custom", "Custom"),
        ],
    )
    if preset == "custom":
        return ask_text("Quality bar", default="Small, maintainable, tested, and easy to hand off.")
    return quality_bar_for_preset(preset)


def ask_choice(prompt: str, choices: list[tuple[str, str]]) -> str:
    print(UI.heading(prompt))
    for line in UI.choice_lines(choices):
        print(line)

    while True:
        response = input("> ").strip()
        for index, (value, _) in enumerate(choices, start=1):
            if response == str(index) or response.lower() == value:
                return value
        print("Enter one of the listed numbers.")


def ask_text(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        response = input(f"{UI.prompt(prompt)}{suffix}: ").strip()
        if response:
            return response
        if default is not None:
            return default
        print("Please enter a value.")


def inspect_repo(path: Path) -> RepoSnapshot:
    resolved = path.expanduser().resolve()
    detected_files = tuple(
        name
        for name in [
            "README.md",
            "PROJECT.md",
            "PROJECT.local.md",
            "TASKS.md",
            "TASKS.local.md",
            "pyproject.toml",
            "package.json",
            "go.mod",
            "Cargo.toml",
        ]
        if (resolved / name).exists()
    )
    return RepoSnapshot(
        path=resolved,
        detected_files=detected_files,
        git_branch=git_output(resolved, ["branch", "--show-current"]),
        dirty=repo_is_dirty(resolved),
    )


def git_output(path: Path, args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    return output or None


def repo_is_dirty(path: Path) -> bool | None:
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--short"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def write_generated_files(output_dir: Path, generated_files, force: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for generated_file in generated_files:
        path = output_dir / generated_file.path
        if path.exists() and not force:
            raise SystemExit(f"Refusing to overwrite {path}. Re-run with --force if intended.")
        path.write_text(generated_file.content, encoding="utf-8")


def print_preview(generated_files) -> None:
    for generated_file in generated_files:
        print(f"\n--- {generated_file.path} ---\n")
        print(generated_file.content)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
