from colorama import Fore, Style, init as colorama_init
from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:
    from modules.windows import Window


colorama_init()

SUPRESS_LOGS = "-s" in sys.argv or "--supress" in sys.argv
ITALIC = "\033[3m"
RESET = Fore.RESET + Style.RESET_ALL


def window_log(window: "Window", content: str) -> None:
    """ Write window's log content if logs are not suppressed. """

    if SUPRESS_LOGS:
        return

    win_info = f"[{Fore.CYAN}{window.text}{RESET} {ITALIC}{Style.DIM}@{window.hwnd}{RESET}]"
    print(f"{win_info} - {content}")


def system_log(content: str) -> None:
    """ Write system's log content if logs are not suppressed. """

    if SUPRESS_LOGS:
        return

    print(f"{Fore.BLUE}{content}{RESET}")
