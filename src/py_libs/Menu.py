import subprocess
from typing import List, Optional

from rich import print
from rich.console import Console
from rich.text import Text

from py_libs.MyTable import MyTable
from py_libs.Print import Print
from py_libs.Select import Select


INDEX_COLOR = "magenta"


def _markup_to_ansi(label: str) -> str:
    console = Console(force_terminal=True, color_system="standard")
    with console.capture() as capture:
        console.print(Text.from_markup(label), end="")
    return capture.get()


class Menu:
    rows_count = 0

    @classmethod
    def display(
        cls, title: str, columns: List[str], rows: List[List[str]], row_styles=None
    ):
        """
        Display the main menu options.
        """

        cls.rows_count = 0
        cls.rows_count += len(rows)

        if row_styles is None:
            row_styles = {}

        tb = MyTable()
        tb.show(title, columns, rows, row_styles=row_styles)

    @classmethod
    def print_grid(cls, items: List[str], color: str = "blue"):
        """
        Print a list of items laid out in a multi-column grid,
        auto-sized to the terminal width.
        """
        tb = MyTable()
        tb.show_grid(items, color=color)

    @classmethod
    def choose_option(cls):
        """
        Prompt the user to choose an option from the menu.
        """
        while True:
            try:
                count_range = (
                    f"Please enter a number between 0 and {cls.rows_count - 1}: "
                )
                choice = int(input(count_range))
                if choice in range(0, cls.rows_count):
                    return choice
                else:
                    print(
                        f"[red]Invalid input."
                        f"Enter a number between 0 and {cls.rows_count - 1}."
                    )
            except ValueError:
                Print.error("Input must be a number. Please try again.")

    @classmethod
    def select_with_fzf(cls, options: List[str]) -> int:
        option = Select.select_one(options)
        return options.index(option) if option else -1

    @classmethod
    def select_fzf(cls, options: List[str]) -> int:
        option = Select.select_with_fzf(options)
        return options.index(option[0]) if option else -1

    @classmethod
    def select_fzf_multi(cls, options: List[str]) -> List[int]:
        Print.info("Use <Tab> to select multiple items, <Enter> to confirm.")
        selected = Select.select_with_fzf(options)
        return [options.index(o) for o in selected if o in options]

    @classmethod
    def select_fzf_menu(
        cls,
        labels: List[str],
        title: Optional[str] = None,
        exit_label: Optional[str] = "[red]Exit",
    ) -> Optional[int]:
        """
        Colored fzf menu with indexes:
            01) [green]First
            02) [blue]Second
            00) [red]Exit

        labels may contain rich markup ("[green]ACF").
        Filter by text, or type an index and press Enter.
        Returns 1..len(labels) for an item, 0 for the exit item
        (exit_label=None hides it), None on Esc/Ctrl-C.
        """
        lines = [
            _markup_to_ansi(f"[{INDEX_COLOR}]{i:02d})[/] {label}")
            for i, label in enumerate(labels, start=1)
        ]
        if exit_label:
            lines.append(_markup_to_ansi(f"[{INDEX_COLOR}]00)[/] {exit_label}"))
        cmd = [
            "fzf",
            "--ansi",
            "--reverse",
            "--no-mouse",
            "--no-sort",
            "--height",
            "50%",
            "--print-query",
        ]
        if title:
            cmd += ["--header", title]
        result = subprocess.run(
            cmd, input="\n".join(lines).encode(), stdout=subprocess.PIPE
        )
        if result.returncode not in (0, 1):
            return None
        output = result.stdout.decode().split("\n")
        query = output[0].strip()
        max_index = len(labels)
        if query.isdigit() and int(query) <= max_index:
            if int(query) or exit_label:
                return int(query)
        if len(output) > 1 and output[1].strip():
            return int(output[1].split(")", 1)[0])
        return None
