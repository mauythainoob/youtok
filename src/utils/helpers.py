"""
Helper functions to be used throughout the codebase.
"""
from pathlib import Path

from typeguard import typechecked

from ..logger import SingletonLogger

logger = SingletonLogger()


#
# Path stuff
#
@typechecked
def validate_path_exists(path: Path) -> None:
    """
    Validates whether a file exists at the specified path.

    Args:
        file (Path): The path to the file to validate.

    Raises:
        FileNotFoundError: If the file does not exist.

    Returns:
        None
    """
    path__str = str(path)
    logger.info(f"Validating path {path__str}")
    if not path.exists():
        message: str = f"Path {path__str} does not exist!"
        logger.error(message)
        raise FileNotFoundError(message)
    logger.info(f"File {path__str} exists")
