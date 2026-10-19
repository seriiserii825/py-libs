import os
import shlex
import subprocess
import sys
import tempfile
from typing import List

from py_libs import fzf_word_filter

import questionary
from simple_term_menu import TerminalMenu


class Select:
    @staticmethod
    def run_fzf(lines: List[str], args: List[str]) -> subprocess.CompletedProcess:
        """
        Run fzf with the word-prefix filter (py_libs.fzf_word_filter)
        instead of fzf's own matching: "resdow" finds "Restore from Downloads".
        """
        with tempfile.NamedTemporaryFile(
            "w", suffix=".fzf", delete=False, encoding="utf-8"
        ) as f:
            f.write("\n".join(lines))
        filter_cmd = " ".join(
            shlex.quote(a)
            for a in (sys.executable, fzf_word_filter.__file__)
        )
        reload_cmd = f"{filter_cmd} {{q}} {shlex.quote(f.name)} || true"
        try:
            return subprocess.run(
                ["fzf", *args, "--disabled", "--bind", f"change:reload({reload_cmd})"],
                input="\n".join(lines).encode(),
                stdout=subprocess.PIPE,
            )
        finally:
            os.unlink(f.name)

    @staticmethod
    def select_with_fzf(options) -> list[str]:
        result = Select.run_fzf(
            options,
            [
                "--multi",
                "--height",
                "50%",
                "--reverse",
                "--no-mouse",
                "--bind",
                "ctrl-a:select-all,ctrl-r:toggle-all",
            ],
        )
        selected = result.stdout.decode().strip().split("\n")
        return selected if selected != [""] else []

    @staticmethod
    def select_questionary(options: List[str]) -> List[str]:
        selected = questionary.checkbox("Select a few options:", choices=options).ask()
        return selected

    @staticmethod
    def select_multiple(options: List[str]) -> List[str]:
        terminal_menu = TerminalMenu(
            options,
            multi_select=True,
            show_multi_select_hint=True,
            show_search_hint=True,
            preview_command="bat --color=always {}",
            preview_size=0.75,
        )
        result = terminal_menu.show()
        print(f"result: {result}")
        selected = terminal_menu.chosen_menu_entries or []
        return selected

    @staticmethod
    def select_one(options):
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        return options[menu_entry_index]

    @staticmethod
    def select_fzf_one(options) -> str | None:
        result = Select.run_fzf(
            options, ["--height", "50%", "--reverse", "--no-mouse"]
        )
        selected = result.stdout.decode().strip()
        return selected if selected else None
