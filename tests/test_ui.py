import unittest

from kickstart.ui import Tui


class TuiTests(unittest.TestCase):
    def test_panel_uses_ascii_box_for_readable_terminal_output(self):
        tui = Tui(color=False)

        panel = tui.panel("Kickstart", ["Forge rough ideas into project briefs."])

        self.assertIn("+", panel)
        self.assertIn("Kickstart", panel)
        self.assertIn("Forge rough ideas", panel)

    def test_choice_lines_are_numbered(self):
        tui = Tui(color=False)

        lines = tui.choice_lines([("preview", "Preview first"), ("write", "Write files")])

        self.assertEqual(["  1. Preview first", "  2. Write files"], lines)
