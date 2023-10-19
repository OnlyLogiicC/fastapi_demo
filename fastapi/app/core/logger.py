import logging
import colorlog
from enum import Enum

FORMAT: str = "{log_color}{levelname}{reset}:\t  {name} - L{lineno} - {message}"
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LEVEL = logging.INFO


class LogLevel(int, Enum):
    """Enum to store the logging level int values from the logging package"""

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL


def set_log_level(level: LogLevel) -> None:
    """Set the logging level globally for the application"""
    global LEVEL
    LEVEL = level.value


def get_stripped_filename(full_filename: str) -> str:
    """Return the name of the file stripped from its path"""
    names = full_filename.split(".")
    res = ".".join(names[-2:])
    return res.upper()


def logger_factory(full_filename: str) -> logging.Logger:
    """
    Return an instance of a :class:`Logger` for the given file. `__name__` should be passed as the argument

    Args:
        full_filename: The name of the file given by the `__name__` attribute.

    Returns:
        a :class:`Logger` instance
    """
    filename = get_stripped_filename(full_filename)

    logger = logging.getLogger(filename)

    # Set up the ColoredFormatter for colored log messages
    formatter = colorlog.ColoredFormatter(
        fmt=FORMAT,
        datefmt=DATE_FORMAT,
        style="{",
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    # Create a custom handler and set the formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Create a logger and set its level
    logger.setLevel(LEVEL)

    # Clear any existing handlers to avoid duplication
    logger.handlers.clear()

    # Add the custom handler to the logger
    logger.addHandler(console_handler)

    return logger
