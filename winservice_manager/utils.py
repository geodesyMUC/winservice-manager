"""
Utility functions
"""
import ctypes
from dataclasses import dataclass
import logging
from typing import Optional
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
        msg = BColors.FAIL + "[ERROR] " + BColors.ENDC + msg
        logger.error(msg)
    elif tag == "warning":
        msg = BColors.WARNING + "[WARNING] " + BColors.ENDC + msg
        logger.warning(msg)
    elif tag == "ok":
        msg = BColors.OKGREEN + "[OK] " + BColors.ENDC + msg
        logger.info(msg)
    elif tag == "info":
        msg = BColors.OKBLUE + "[INFO] " + BColors.ENDC + msg
        logger.info(msg)
    else:
        logger.debug(msg)


# Set logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler()],
)
