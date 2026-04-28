import unittest

from kickstart.ui import Tui


class TuiTests(unittest.TestCase):
    def test_panel_uses_ascii_box_for_readable_terminal_output(self):
        tui = Tui(color=False)

        panel = tui.panel("Kickstart", ["Forge rough ideas into project briefs."])

        self.assertIn("+", panel)
        self.assertIn("Kickstart", panel)
        self.assertIn("Forge rough ideas", panel)

    def test_panel_wraps_long_lines_to_requested_width(self):
        tui = Tui(color=False)

        panel = tui.panel(
            "Review Answers",
            ["Quality: Fast, simple, and easy to change without making the terminal too wide."],
            width=40,
        )

        self.assertIn("Quality: Fast, simple, and easy", panel)
        self.assertIn("change without making the", panel)
        for line in panel.splitlines():
            self.assertLessEqual(len(line), 40)

    def test_panel_continuation_lines_align_after_label(self):
        tui = Tui(color=False)

        panel = tui.panel(
            "Review Answers",
            ["Quality: Fast, simple, and easy to change without making the terminal too wide."],
            width=40,
        )

        self.assertIn("|          change without making the |", panel)

    def test_choice_lines_are_numbered(self):
        tui = Tui(color=False)

        lines = tui.choice_lines([("preview", "Preview first"), ("write", "Write files")])

        self.assertEqual(["  1. Preview first", "  2. Write files"], lines)

    def test_choice_lines_can_show_selected_choice(self):
        tui = Tui(color=False)

        lines = tui.choice_lines(
            [("preview", "Preview first"), ("write", "Write files")],
            selected_index=1,
        )

        self.assertEqual(["  1. Preview first", "> 2. Write files"], lines)

    def test_menu_help_line_documents_keyboard_controls(self):
        tui = Tui(color=False)

        line = tui.menu_help_line()

        self.assertIn("Up/Down", line)
        self.assertIn("j/k", line)
        self.assertIn("Enter", line)
        self.assertIn("q/Esc", line)

    def test_selected_line_confirms_choice(self):
        tui = Tui(color=False)

        line = tui.selected_line("Write files")

        self.assertEqual("Selected: Write files", line)
