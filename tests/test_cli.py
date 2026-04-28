import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from kickstart.brief import PROJECT_TYPE_EXISTING, PROJECT_TYPE_NEW, GeneratedFile, ProjectAnswers, RepoSnapshot
from kickstart.cli import (
    ask_choice,
    ask_text,
    collect_answers,
    edit_answers,
    existing_generated_paths,
    resolve_write_conflicts,
    review_lines,
    run_init,
)


class TtyStringIO(StringIO):
    def isatty(self):
        return True


def sample_answers(name: str = "gogo") -> ProjectAnswers:
    return ProjectAnswers(
        project_type=PROJECT_TYPE_NEW,
        name=name,
        goal="make a tic-tac-toe app",
        users="Me and friends",
        stack="Python",
        constraints="minimal features",
        done="playable first version",
        risks="networking is unclear",
        quality_bar="Fast and simple",
        output_style="concise",
    )


def sample_existing_answers() -> ProjectAnswers:
    return ProjectAnswers(
        project_type=PROJECT_TYPE_EXISTING,
        name="existing-app",
        goal="improve the repo",
        users="A team or coworkers",
        stack="Python",
        constraints="keep current behavior",
        done="tests pass",
        risks="dirty worktree",
        quality_bar="Production",
        output_style="detailed",
        repo_snapshot=RepoSnapshot(
            path=Path("/tmp/existing-app"),
            detected_files=("README.md", "pyproject.toml"),
            git_branch="main",
            dirty=True,
        ),
    )


def init_args(output_dir: Path = Path("."), write: bool = False, preview: bool = True, force: bool = False) -> Namespace:
    return Namespace(
        project_type=PROJECT_TYPE_NEW,
        preview=preview,
        write=write,
        output_dir=output_dir,
        repo_path=None,
        force=force,
    )


class CliFlowTests(unittest.TestCase):
    def test_ask_choice_uses_arrow_key_selection_in_terminal(self):
        keys = iter(["\x1b[B", "\r"])

        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout", TtyStringIO()),
            patch("kickstart.cli.read_key", side_effect=lambda: next(keys)),
        ):
            choice = ask_choice(
                "Pick one",
                [("preview", "Preview first"), ("write", "Write files")],
            )

        self.assertEqual("write", choice)

    def test_ask_choice_uses_number_key_selection_in_terminal(self):
        keys = iter(["2", "\r"])

        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout", TtyStringIO()),
            patch("kickstart.cli.read_key", side_effect=lambda: next(keys)),
        ):
            choice = ask_choice(
                "Pick one",
                [("preview", "Preview first"), ("write", "Write files")],
            )

        self.assertEqual("write", choice)

    def test_ask_choice_confirms_terminal_selection(self):
        keys = iter(["2", "\r"])
        stdout = TtyStringIO()

        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout", stdout),
            patch("kickstart.cli.read_key", side_effect=lambda: next(keys)),
        ):
            ask_choice(
                "Pick one",
                [("preview", "Preview first"), ("write", "Write files")],
            )

        self.assertIn("Selected: Write files", stdout.getvalue())

    def test_ask_choice_q_quits_terminal_menu(self):
        keys = iter(["q"])

        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout", TtyStringIO()),
            patch("kickstart.cli.read_key", side_effect=lambda: next(keys)),
        ):
            with self.assertRaises(KeyboardInterrupt):
                ask_choice(
                    "Pick one",
                    [("preview", "Preview first"), ("write", "Write files")],
                )

    def test_ask_choice_escape_quits_terminal_menu(self):
        keys = iter(["\x1b"])

        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout", TtyStringIO()),
            patch("kickstart.cli.read_key", side_effect=lambda: next(keys)),
        ):
            with self.assertRaises(KeyboardInterrupt):
                ask_choice(
                    "Pick one",
                    [("preview", "Preview first"), ("write", "Write files")],
                )

    def test_collect_answers_asks_plain_english_questions_before_stack(self):
        prompts = []
        answers = iter(
            [
                "gogo",
                "make a tic-tac-toe app",
                "2",
                "1",
                "minimal features",
                "playable first version",
                "networking is unclear",
                "1",
                "2",
            ]
        )

        def fake_input(prompt):
            prompts.append(prompt)
            return next(answers)

        stdout = StringIO()

        with patch("builtins.input", fake_input), redirect_stdout(stdout):
            collect_answers(PROJECT_TYPE_NEW, None)

        prompt_text = "\n".join([*prompts, stdout.getvalue()])

        self.assertLess(prompt_text.index("Project name"), prompt_text.index("What do you want to make?"))
        self.assertLess(prompt_text.index("What do you want to make?"), prompt_text.index("Any must-haves"))

    def test_ask_text_prints_prompt_on_own_line_for_non_tty_input(self):
        stdout = StringIO()

        with (
            patch("sys.stdin.isatty", return_value=False),
            patch("builtins.input", return_value="gogo") as input_mock,
            redirect_stdout(stdout),
        ):
            answer = ask_text("Project name", default="kickstart")

        self.assertEqual("gogo", answer)
        self.assertEqual("Project name [kickstart]\n", stdout.getvalue())
        input_mock.assert_called_once_with("> ")

    def test_review_lines_summarize_answers_before_generation(self):
        lines = review_lines(sample_answers())

        summary = "\n".join(lines)

        self.assertIn("Project: gogo", summary)
        self.assertIn("Goal: make a tic-tac-toe app", summary)
        self.assertIn("Users: Me and friends", summary)
        self.assertIn("Output: concise", summary)

    def test_review_lines_include_existing_repo_snapshot(self):
        lines = review_lines(sample_existing_answers())

        summary = "\n".join(lines)

        self.assertIn("Repo path: /tmp/existing-app", summary)
        self.assertIn("Repo files: README.md, pyproject.toml", summary)
        self.assertIn("Repo branch: main", summary)
        self.assertIn("Repo dirty: yes", summary)

    def test_run_init_quit_from_review_skips_generation(self):
        stdout = StringIO()

        with (
            patch("kickstart.cli.collect_answers", return_value=sample_answers()),
            patch("kickstart.cli.confirm_answers", return_value="quit"),
            patch("kickstart.cli.generate_files") as generate_files,
            redirect_stdout(stdout),
        ):
            exit_code = run_init(init_args())

        self.assertEqual(0, exit_code)
        generate_files.assert_not_called()
        self.assertIn("No files generated.", stdout.getvalue())

    def test_run_init_back_from_review_collects_answers_again(self):
        first = sample_answers("first")
        revised = sample_answers("revised")

        with (
            patch("kickstart.cli.collect_answers", side_effect=[first, revised]) as collect,
            patch("kickstart.cli.confirm_answers", side_effect=["back", "confirm"]),
            patch("kickstart.cli.generate_files", return_value=[]) as generate_files,
            patch("kickstart.cli.print_preview"),
            redirect_stdout(StringIO()),
        ):
            exit_code = run_init(init_args())

        self.assertEqual(0, exit_code)
        self.assertEqual(2, collect.call_count)
        generate_files.assert_called_once_with(revised)

    def test_run_init_edit_from_review_updates_one_answer(self):
        generated_answers = []

        def fake_generate_files(answers):
            generated_answers.append(answers)
            return []

        with (
            patch("kickstart.cli.collect_answers", return_value=sample_answers("first")) as collect,
            patch("kickstart.cli.confirm_answers", side_effect=["edit", "confirm"]),
            patch("kickstart.cli.edit_answers", return_value=sample_answers("revised")) as edit,
            patch("kickstart.cli.generate_files", side_effect=fake_generate_files),
            patch("kickstart.cli.print_preview"),
            redirect_stdout(StringIO()),
        ):
            exit_code = run_init(init_args())

        self.assertEqual(0, exit_code)
        self.assertEqual(1, collect.call_count)
        edit.assert_called_once()
        self.assertEqual("revised", generated_answers[0].name)

    def test_edit_answers_can_update_project_goal(self):
        answers = sample_answers()

        with (
            patch("kickstart.cli.ask_choice", return_value="goal"),
            patch("kickstart.cli.ask_text", return_value="make a better app"),
        ):
            updated = edit_answers(answers)

        self.assertEqual("make a better app", updated.goal)
        self.assertEqual(answers.name, updated.name)

    def test_run_init_previews_instead_when_write_conflicts(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            (output_dir / "PROJECT.md").write_text("existing", encoding="utf-8")
            generated = [GeneratedFile("PROJECT.md", "new")]
            stdout = StringIO()

            with (
                patch("kickstart.cli.collect_answers", return_value=sample_answers()),
                patch("kickstart.cli.confirm_answers", return_value="confirm"),
                patch("kickstart.cli.generate_files", return_value=generated),
                patch("kickstart.cli.resolve_write_conflicts", return_value="preview"),
                redirect_stdout(stdout),
            ):
                exit_code = run_init(init_args(output_dir=output_dir, write=True, preview=False))

            self.assertEqual(0, exit_code)
            self.assertEqual("existing", (output_dir / "PROJECT.md").read_text(encoding="utf-8"))
            self.assertIn("--- PROJECT.md ---", stdout.getvalue())

    def test_run_init_overwrites_when_write_conflict_is_approved(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            (output_dir / "PROJECT.md").write_text("existing", encoding="utf-8")
            generated = [GeneratedFile("PROJECT.md", "new")]

            with (
                patch("kickstart.cli.collect_answers", return_value=sample_answers()),
                patch("kickstart.cli.confirm_answers", return_value="confirm"),
                patch("kickstart.cli.generate_files", return_value=generated),
                patch("kickstart.cli.resolve_write_conflicts", return_value="overwrite"),
                redirect_stdout(StringIO()),
            ):
                exit_code = run_init(init_args(output_dir=output_dir, write=True, preview=False))

            self.assertEqual(0, exit_code)
            self.assertEqual("new", (output_dir / "PROJECT.md").read_text(encoding="utf-8"))

    def test_run_init_quit_from_write_conflict_leaves_files_unchanged(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            (output_dir / "PROJECT.md").write_text("existing", encoding="utf-8")
            generated = [GeneratedFile("PROJECT.md", "new")]
            stdout = StringIO()

            with (
                patch("kickstart.cli.collect_answers", return_value=sample_answers()),
                patch("kickstart.cli.confirm_answers", return_value="confirm"),
                patch("kickstart.cli.generate_files", return_value=generated),
                patch("kickstart.cli.resolve_write_conflicts", return_value="quit"),
                redirect_stdout(stdout),
            ):
                exit_code = run_init(init_args(output_dir=output_dir, write=True, preview=False))

            self.assertEqual(0, exit_code)
            self.assertEqual("existing", (output_dir / "PROJECT.md").read_text(encoding="utf-8"))
            self.assertIn("No files written.", stdout.getvalue())

    def test_existing_generated_paths_reports_only_conflicts(self):
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            (output_dir / "PROJECT.md").write_text("existing", encoding="utf-8")

            conflicts = existing_generated_paths(
                output_dir,
                [GeneratedFile("PROJECT.md", "new"), GeneratedFile("TASKS.md", "new")],
            )

        self.assertEqual([output_dir / "PROJECT.md"], conflicts)

    def test_resolve_write_conflicts_refuses_non_tty_overwrite(self):
        with (
            patch("sys.stdin.isatty", return_value=False),
            patch("sys.stdout.isatty", return_value=False),
            redirect_stdout(StringIO()),
        ):
            with self.assertRaises(SystemExit) as raised:
                resolve_write_conflicts([Path("PROJECT.md")])

        self.assertIn("Refusing to overwrite", str(raised.exception))
