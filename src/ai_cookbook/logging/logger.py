from ..config import LOGGING_CONFIG
import logging
import logging.config
import sys
import os


logging.config.fileConfig(LOGGING_CONFIG)

log = logging.getLogger("root")


def handle_exception(exc_type, exc_value, exc_traceback):
    # Ignore KeyboardInterrupt so a console python program can exit with Ctrl + C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Don't use custom exception handling during testing
    if "pytest" in sys.modules:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Log the exception with traceback
    log.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))


# Set the global exception handler
sys.excepthook = handle_exception
