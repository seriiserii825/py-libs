from datetime import datetime
import os
from pathlib import Path

from rich import print

from py_libs.Command import Command
from py_libs.InputValidator import InputValidator
from py_libs.Menu import Menu
from py_libs.Print import Print
from py_libs.Select import Select


class FilesHandle:
    def list_files(
        self, path_to_list, file_extension=None, mtime=False, newest_first=False
    ) -> None:
        abs_path = Path(path_to_list).resolve()
        Print.info(f"Listing files in {abs_path}")

        files = [f for f in abs_path.iterdir() if f.is_file()]
        if not files:
            Print.warning("No files found in this directory.")
            return
        if newest_first:
            sorted_files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        else:
            sorted_files = sorted(files, key=lambda f: f.name.lower())

        for f in sorted_files:
            if file_extension:
                if f.name.endswith(file_extension):
                    self._show_file(f, mtime)
            else:
                self._show_file(f, mtime)

    def _show_file(self, file_path, mtime):
        file_name = file_path.name
        if mtime:
            human_mtime = datetime.fromtimestamp(file_path.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print(f"[blue]{file_name} - {human_mtime}")
        else:
            print(f"[blue]{file_name}")

    def list_dir(self, path_to_list="") -> list[str]:
        abs_path = Path(path_to_list).resolve()
        Print.info(f"Listing directories in {abs_path}")
        with os.scandir(abs_path) as entries:
            sorted_dirs = sorted(
                (entry for entry in entries if entry.is_dir()),
                key=lambda e: e.name.lower(),
            )
            names = [entry.name for entry in sorted_dirs]
        terminal_lines = os.get_terminal_size().lines
        if len(names) > terminal_lines - 4:
            Menu.print_grid(names)
        else:
            for name in names:
                print(f"[yellow]{name}")
        return names

    def directory_is_empty(self, path_to_dir) -> bool:
        return os.path.exists(path_to_dir) and len(os.listdir(path_to_dir)) == 0

    def ensure_dir(self, path_to_dir) -> str:
        """Create the directory (and parents) if it doesn't exist, silently."""
        os.makedirs(path_to_dir, exist_ok=True)
        return path_to_dir

    def create_or_choose_directory(self, path_to_dir="") -> str:
        abs_path = str(Path(path_to_dir).resolve())
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        self.list_dir(abs_path)

        if not self._has_dirs(path_to_dir):
            return self._create_dir(abs_path)

        select_or_create = Select.select_one(["Select", "Create"])
        if select_or_create == "Create":
            return self._create_dir(abs_path)
        else:
            selected_dir = self.choose_dir(abs_path)
            return str(Path(path_to_dir) / selected_dir)

    def _create_dir(self, abs_path):
        dir_name = InputValidator.get_string("Enter directory name: ")
        current_path = str(Path(abs_path) / dir_name)
        if Path(current_path).exists():
            Print.error(f"Directory '{dir_name}' already exists.")
            exit(1)
        os.makedirs(current_path)
        Print.success("Directory created")
        return current_path

    def choose_dir(self, path_to_dir):
        choosed_dir = []
        abs_path = Path(path_to_dir).resolve()
        with os.scandir(abs_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    choosed_dir.append(entry.name)
        choosed_dir.sort()
        return Select.select_fzf_one(choosed_dir)

    def _has_dirs(self, path_to_dir):
        abs_path = Path(path_to_dir).resolve()
        with os.scandir(abs_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    return True
        return False

    def choose_file(self, path_to_dir, extension=None, newest_first=False):
        choosed_files = []
        for entry in os.listdir(path_to_dir):
            if os.path.isfile(os.path.join(path_to_dir, entry)):
                if extension:
                    if entry.endswith(extension):
                        choosed_files.append(entry)
                else:
                    choosed_files.append(entry)
        if len(choosed_files) == 0:
            Print.error("No files found")
            exit()
        if newest_first:
            choosed_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(path_to_dir, f)),
                reverse=True,
            )
        return Select.select_one(choosed_files)

    def append_to_file(self, file_path, text):
        with open(file_path, "a") as f:
            f.write(text)
        Command.run(f"bat '{file_path}'")

    def draw_tree(self, path_to_dir):
        Command.run(f"tree '{path_to_dir}'")
