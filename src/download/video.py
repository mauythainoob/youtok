"""
Helpers to help downloading tiktoks.
"""
import requests
from pathlib import Path

from typeguard import typechecked

from ..utils.helpers import validate_path_exists
from ..logger import SingletonLogger

logger = SingletonLogger()


@typechecked
def download_video(url: str, filepath: Path) -> Path:
    """
    Download a video from a given URL and saves it to a file.

    Args:
        url (str): The URL of the video to download.
        filepath (str): The name of the file to save the downloaded video content.

    Raises:
        requests.exceptions.HTTPError: If the response status code indicates an error.
    """
    logger.info(f"Downloading {url} and saving it to {str(filepath)}")
    # Check if the directory exists first
    validate_path_exists(Path(filepath).parent)

    response = requests.get(url)
    response.raise_for_status()

    logger.info(f"Saving contents of {url}")
    with open(filepath, "wb") as file:
        file.write(response.content)

    return filepath
