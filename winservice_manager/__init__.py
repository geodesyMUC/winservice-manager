"""Windows service manager"""
import importlib.metadata
import logging

__version__ = importlib.metadata.version("winservice_manager")

# Set default null logging handler to avoid "No handler found" warnings
logging.getLogger(__name__).addHandler(logging.NullHandler())
