import math
import os

from rich.console import Console
from rich.table import Table


class MyTable:
    def __init__(self):
        self.console = Console()

    def show(self, title: str, columns, rows, *, row_styles={}):
        """
        Print a Rich table.

        Parameters
        ----------
        title : str
            Table title.
        columns : list[dict]
            Each dict must have keys "title" and "style".
        rows : list[list[str]]
            2‑D list of cell values.
        row_styles : dict[int, str] | None
            Map of row index → Rich style string.
            Example: {0: "bold green", 3: "bright_red"}
            (row index is **zero‑based** inside this method)
        """

        table = Table(title=title, show_lines=False, expand=False)

        for col in columns:
            table.add_column(col)

        for idx, row in enumerate(rows):
            style = row_styles.get(idx, "")
            table.add_row(*row, style=style)

        self.console.print(table)

    def show_grid(self, items: list[str], color: str = "blue"):
        """
        Print a list of items laid out in a multi-column grid,
        auto-sized to the terminal width.
        """
        term = os.get_terminal_size()
        max_len = max(len(i) for i in items) + 2
        num_cols = max(1, term.columns // max_len)
        num_rows = math.ceil(len(items) / num_cols)

        table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
        for _ in range(num_cols):
            table.add_column()

        for row_i in range(num_rows):
            row = []
            for col_i in range(num_cols):
                idx = col_i * num_rows + row_i
                row.append(f"[{color}]{items[idx]}" if idx < len(items) else "")
            table.add_row(*row)

        self.console.print(table)
