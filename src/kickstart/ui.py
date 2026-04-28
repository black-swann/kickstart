from __future__ import annotations

import os
import sys


class Tui:
    def __init__(self, color: bool | None = None) -> None:
        if color is None:
            color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
        self.color = color

    def panel(self, title: str, lines: list[str]) -> str:
        content = [title, "", *lines]
        width = max(len(line) for line in content)
        border = "+" + "-" * (width + 2) + "+"
        body = [border]
        for line in content:
            body.append(f"| {line.ljust(width)} |")
        body.append(border)
        return "\n".join(body)

    def heading(self, text: str) -> str:
        if not self.color:
            return text
        return f"\033[1;36m{text}\033[0m"

    def prompt(self, text: str) -> str:
        if not self.color:
            return text
        return f"\033[1m{text}\033[0m"

    def choice_lines(self, choices: list[tuple[str, str]]) -> list[str]:
        return [f"  {index}. {label}" for index, (_, label) in enumerate(choices, start=1)]
