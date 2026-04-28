from __future__ import annotations

import os
import shutil
import sys
import textwrap


class Tui:
    def __init__(self, color: bool | None = None) -> None:
        if color is None:
            color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
        self.color = color

    def panel(self, title: str, lines: list[str], width: int | None = None) -> str:
        if width is None:
            width = shutil.get_terminal_size(fallback=(80, 24)).columns
        content_width = max(1, width - 4)
        content = self.wrap_lines([title, "", *lines], content_width)
        width = max(len(line) for line in content)
        border = "+" + "-" * (width + 2) + "+"
        body = [border]
        for line in content:
            body.append(f"| {line.ljust(width)} |")
        body.append(border)
        return "\n".join(body)

    def wrap_lines(self, lines: list[str], width: int) -> list[str]:
        wrapped = []
        for line in lines:
            if line == "":
                wrapped.append(line)
                continue
            subsequent_indent = self._continuation_indent(line)
            wrapped.extend(
                textwrap.wrap(
                    line,
                    width=width,
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent=subsequent_indent,
                )
                or [line]
            )
        return wrapped

    def _continuation_indent(self, line: str) -> str:
        if ": " not in line:
            return ""
        label, _ = line.split(": ", 1)
        return " " * (len(label) + 2)

    def heading(self, text: str) -> str:
        if not self.color:
            return text
        return f"\033[1;36m{text}\033[0m"

    def prompt(self, text: str) -> str:
        if not self.color:
            return text
        return f"\033[1m{text}\033[0m"

    def choice_lines(self, choices: list[tuple[str, str]], selected_index: int | None = None) -> list[str]:
        if selected_index is None:
            return [f"  {index}. {label}" for index, (_, label) in enumerate(choices, start=1)]

        lines = []
        for index, (_, label) in enumerate(choices):
            prefix = ">" if index == selected_index else " "
            line = f"{prefix} {index + 1}. {label}"
            if self.color and index == selected_index:
                line = f"\033[7m{line}\033[0m"
            lines.append(line)
        return lines

    def menu_help_line(self) -> str:
        line = "Up/Down or j/k move | 1-9 jump | Enter select | q/Esc quit"
        if not self.color:
            return line
        return f"\033[2m{line}\033[0m"

    def selected_line(self, label: str) -> str:
        line = f"Selected: {label}"
        if not self.color:
            return line
        return f"\033[32m{line}\033[0m"
