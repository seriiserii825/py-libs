import os
import subprocess
import warnings

import plyer
import pyperclip


class Clipboard:
    """Clipboard manager: Wayland/X11-aware, falls back to pyperclip."""

    @staticmethod
    def _is_wayland() -> bool:
        return bool(os.getenv("WAYLAND_DISPLAY"))

    @staticmethod
    def _is_x11() -> bool:
        return bool(os.getenv("DISPLAY"))

    @staticmethod
    def read() -> str:
        """Return the current text from the clipboard."""
        try:
            if Clipboard._is_wayland():
                return subprocess.check_output(["wl-paste"]).decode().strip()
            elif Clipboard._is_x11():
                return (
                    subprocess.check_output(["xclip", "-o", "-selection", "clipboard"])
                    .decode()
                    .strip()
                )
            else:
                return pyperclip.paste().strip()
        except Exception:
            return pyperclip.paste().strip()

    @staticmethod
    def write(text: str, show: bool = True) -> None:
        """Copy the given text to the clipboard and notify the desktop.

        Pass ``show=False`` for secrets (e.g. passwords) so the text itself
        is not displayed in the desktop notification.
        """
        text = text.strip()

        try:
            if Clipboard._is_wayland():
                subprocess.run(["wl-copy"], input=text.encode(), check=True)
            elif Clipboard._is_x11():
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode(),
                    check=True,
                )
            else:
                pyperclip.copy(text)
        except Exception:
            pyperclip.copy(text)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            plyer.notification.notify(
                title="Buffer",
                message=text if show else "Copied to clipboard (hidden)",
                app_name="Buffer",
                timeout=5,
            )
