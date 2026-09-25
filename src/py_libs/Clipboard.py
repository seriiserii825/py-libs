import pyperclip


class Clipboard:
    """Simple clipboard manager for reading and writing text."""

    @staticmethod
    def read() -> str:
        """Return the current text from the clipboard."""
        try:
            text = pyperclip.paste()
            return text if text else ""
        except pyperclip.PyperclipException as e:
            raise RuntimeError(f"Clipboard read failed: {e}")

    @staticmethod
    def write(text: str) -> None:
        """Copy the given text to the clipboard."""
        try:
            pyperclip.copy(text)
        except pyperclip.PyperclipException as e:
            raise RuntimeError(f"Clipboard write failed: {e}")
