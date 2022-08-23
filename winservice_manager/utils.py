"""
Utility functions
"""
import ctypes

def is_admin():
    """Returns true if script is running with admin priviledges"""
    return ctypes.windll.shell32.IsUserAnAdmin()

def log(msg: str) -> None:
    """Prints a log message"""
    print(msg)
