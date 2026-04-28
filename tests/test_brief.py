import unittest
from pathlib import Path

from kickstart.brief import (
    PROJECT_TYPE_EXISTING,
    PROJECT_TYPE_NEW,
    ProjectAnswers,
    RepoSnapshot,
    generate_files,
    quality_bar_for_preset,
)


class BriefGenerationTests(unittest.TestCase):
    def test_new_project_generates_expected_files(self):
        answers = ProjectAnswers(
            project_type=PROJECT_TYPE_NEW,
            name="Example",
            goal="Build a useful thing.",
            users="Solo builders",
            stack="Python",
            constraints="Keep it small.",
            done="A working first release.",
            risks="Scope creep.",
            quality_bar="Tested and maintainable.",
        )

        generated = generate_files(answers)

        self.assertEqual(["PROJECT.md", "TASKS.md", "KICKOFF.md"], [file.path for file in generated])
        self.assertIn("Build a useful thing.", generated[0].content)
        self.assertIn("kickoff instruction for an implementation session", generated[2].content)
        self.assertIn("Do not rush into code", generated[2].content)

    def test_existing_repo_includes_snapshot_context(self):
        answers = ProjectAnswers(
            project_type=PROJECT_TYPE_EXISTING,
            name="Existing",
            goal="Improve current repo.",
            users="Maintainers",
            stack="Go",
            constraints="Preserve current behavior.",
            done="Tests pass.",
            risks="Hidden coupling.",
            quality_bar="Small verified changes.",
            repo_snapshot=RepoSnapshot(
                path=Path("/tmp/example"),
                detected_files=("README.md", "go.mod"),
                git_branch="main",
                dirty=True,
            ),
        )

        generated = generate_files(answers)
        project_md = generated[0].content
        kickoff_md = generated[2].content

        self.assertIn("Existing Repo Snapshot", project_md)
        self.assertIn("README.md, go.mod", project_md)
        self.assertIn("inspect the existing repository", kickoff_md)

    def test_quality_preset_expands_into_specific_quality_bar(self):
        quality_bar = quality_bar_for_preset("production")

        self.assertIn("tested", quality_bar.lower())
        self.assertIn("operationally clear", quality_bar.lower())
        self.assertIn("maintainable", quality_bar.lower())

    def test_detailed_output_style_adds_more_planning_guidance(self):
        answers = ProjectAnswers(
            project_type=PROJECT_TYPE_NEW,
            name="Detailed",
            goal="Plan a careful build.",
            users="Operators",
            stack="Python",
            constraints="Keep dependencies low.",
            done="A reviewed first release.",
            risks="Unclear requirements.",
            quality_bar="Production-ready enough for careful local use.",
            output_style="detailed",
        )

        kickoff_md = generate_files(answers)[2].content

        self.assertIn("Include acceptance checks", kickoff_md)
        self.assertIn("Call out tradeoffs", kickoff_md)

    def test_suggested_stack_marks_stack_as_recommendation_needed(self):
        answers = ProjectAnswers(
            project_type=PROJECT_TYPE_NEW,
            name="Friendly",
            goal="Make a simple game.",
            users="Friends",
            stack="Needs recommendation from the assistant based on the project goal and constraints.",
            constraints="Minimal features.",
            done="Playable locally.",
            risks="Unsure about networking.",
            quality_bar=quality_bar_for_preset("prototype"),
        )

        kickoff_md = generate_files(answers)[2].content

        self.assertIn("Needs recommendation", kickoff_md)
        self.assertIn("compare stack choices", kickoff_md.lower())


if __name__ == "__main__":
    unittest.main()
