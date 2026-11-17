"""
Legacy Logger Config Shim.
"""
from core.utils.logger_config import setup_logger as modern_setup_logger


def setup_logger(name: str = "LegacyLogger", enableDebug: bool = False):
    return modern_setup_logger(name)
