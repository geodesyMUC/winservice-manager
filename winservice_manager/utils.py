"""
Utility functions
"""
import ctypes
import logging
import colorama
from colorama import Fore, Style


def is_admin():
    """Returns true if script is running with admin priviledges"""
    return ctypes.windll.shell32.IsUserAnAdmin()


class ScriptLoggingFormatter(logging.Formatter):
    """
    Custom formatter for logging of scripts in this package
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Adds a colored tag ([TAG]) to log messages,
        depending on the log level
        """
        if record.levelno == logging.ERROR:
            record.msg = Fore.RED + "[ERROR] " + Style.RESET_ALL + record.msg
        elif record.levelno == logging.WARNING:
            record.msg = Fore.YELLOW + "[WARNING] " + Style.RESET_ALL + record.msg
        elif record.levelno == logging.INFO:
            record.msg = Fore.GREEN + "[OK] " + Style.RESET_ALL + record.msg
        elif record.levelno == logging.DEBUG:
            record.msg = Fore.CYAN + "[INFO] " + Style.RESET_ALL + record.msg
        return super().format(record)


def setup_script_logger(logger_name: str = __name__) -> None:
    """
    Sets up the logger for scripts in this package
    """

    # Set logging config with logger named according to the input name
    logger = logging.getLogger(logger_name)

    # We want ALL log messages for the script log messages, so use debug level
    logger.setLevel(logging.DEBUG)

    stream_h = logging.StreamHandler()
    stream_h.setLevel(logging.DEBUG)
    formatter = ScriptLoggingFormatter("%(asctime)s %(message)s", datefmt="%H:%M:%S")
    stream_h.setFormatter(formatter)

    # Finally, add the handler to logger
    logger.addHandler(stream_h)


# Set up colorama for colored strings
colorama.init()
