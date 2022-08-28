"""
Utility functions
"""
import ctypes
from dataclasses import dataclass
from datetime import datetime
from typing_extensions import Literal


@dataclass(frozen=True)
class BColors:
    """
    Colors for colored stdout print
    """

    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def is_admin():
    """Returns true if script is running with admin priviledges"""
    return ctypes.windll.shell32.IsUserAnAdmin()


def log(msg: str, tag: Literal["ok", "error", "warning", "info", ""] = "") -> None:
    """
    Prints a log message.
    Adds current time, and an optional colored tag to the message.
    """

    if tag == "ok":
        msg = BColors.OKGREEN + "[OK] " + BColors.ENDC + msg

    if tag == "error":
        msg = BColors.FAIL + "[ERROR] " + BColors.ENDC + msg

    if tag == "warning":
        msg = BColors.WARNING + "[WARNING] " + BColors.ENDC + msg

    if tag == "info":
        msg = BColors.OKBLUE + "[INFO] " + BColors.ENDC + msg

    print(" ".join([datetime.strftime(datetime.now(), "%H:%M:%S"), msg]))
