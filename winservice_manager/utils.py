"""
Utility functions
"""
import ctypes
import logging
from typing import Optional
from typing_extensions import Literal
import colorama
from colorama import Fore, Style


def is_admin():
    """Returns true if script is running with admin priviledges"""
    return ctypes.windll.shell32.IsUserAnAdmin()


def log(
    msg: str,
    tag: Literal["ok", "error", "warning", "info", ""] = "",
    set_quiet: Optional[bool] = None,
) -> None:
    """
    Prints a log message.
    Adds current time, and an optional colored tag to the message.
    """
    logger = logging.getLogger("default")
    if set_quiet:
        # This will disable all prints
        logger.propagate = False
    elif set_quiet is not None:
        # This will (re-)enable all prints
        logger.propagate = True

    if tag == "error":
        msg = Fore.RED + "[ERROR] " + Style.RESET_ALL + msg
        logger.error(msg)
    elif tag == "warning":
        msg = Fore.YELLOW + "[WARNING] " + Style.RESET_ALL + msg
        logger.warning(msg)
    elif tag == "ok":
        msg = Fore.GREEN + "[OK] " + Style.RESET_ALL + msg
        logger.info(msg)
    elif tag == "info":
        msg = Fore.BLUE + "[INFO] " + Style.RESET_ALL + msg
        logger.info(msg)
    else:
        # Everything else is a debug message
        logger.debug(msg)


# Set logging config (logger named "default")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler()],
)

# Set up colorama for colored strings
colorama.init()
