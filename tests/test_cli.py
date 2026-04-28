import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from kickstart.cli import collect_answers
from kickstart.brief import PROJECT_TYPE_NEW


class CliFlowTests(unittest.TestCase):
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

        with patch("builtins.input", fake_input), redirect_stdout(StringIO()):
            collect_answers(PROJECT_TYPE_NEW, None)

        prompt_text = "\n".join(prompts)

        self.assertLess(prompt_text.index("Project name"), prompt_text.index("What do you want to make?"))
        self.assertLess(prompt_text.index("What do you want to make?"), prompt_text.index("Any must-haves"))
