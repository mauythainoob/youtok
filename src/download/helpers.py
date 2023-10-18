""" 


As of time of writing (16/08/2023), FailT's api doesn't directly download a 
tiktok video. Rather, it provides this information. 
"""
import requests
from pathlib import Path

from typeguard import typechecked

from ..config import Config
from ..logger import SingletonLogger
from ..utils.helpers import validate_path_exists

logger: SingletonLogger = SingletonLogger()


@typechecked
def get_tiktok_video_download_link(url: str, request_timeout: int = 15) -> str:
    """
    Get the download link for a TikTok video. Will attempt to download the video
    at the highest resolution. We use http://tik.fail for this.


    Args:
        url (str): The TikTok video URL to get the download link for.
        request_timeout (int): How long the request [lib] should wait before timing out.
                               (Defaults 15).

    Returns:
        str: The download link of the TikTok video.

    Raises:
        KeyError: If the download link source is not found in the response.
        requests.exceptions.HTTPError: If the response status code indicates an error.
    """
    logger.info(f"Attempting to find download link for {url}")

    response: requests.models.Response = requests.post(
        url="https://api.tik.fail/api/grab",
        headers={"User-Agent": "MyTikTokBot"},  # Required
        data={"url": url},
        timeout=request_timeout,
    )
    response.raise_for_status()

    video_download_sources: dict = response.json()["data"]["download"]["video"]

    options: list[str] = ["NoWMSource", "NoWM720", "NoWM"]
    for source in options:
        if source in video_download_sources:
            download_link = video_download_sources[source]["url"]

            if requests.get(download_link, timeout=request_timeout).status_code != 200:
                logger.info(f"Option {source} with URL {url} exists but doesn't work.")
                continue

            logger.info(
                f"Returning url {url} with the {source} option. Download link: {download_link}"
            )
            return download_link

    raise ValueError("No download links avaiable.")


@typechecked
def create_download_dir_for_channel(
    channel_name: str, parent_directory: Path = Config.Download.Directory
) -> Path:
    """
    Creates a folder in the directory (default to config.download.directory). The directory will be
    whatever is passed in as the channel_name

    Args:
        channel_name (str)
        parent_directory (Path, optional): Defaults to Config.Download.Directory.

    Returns:
        Path: The created (or existing) directory.
    """
    validate_path_exists(parent_directory)
    download_directory: Path = parent_directory.joinpath(channel_name)

    if not download_directory.exists():
        download_directory.mkdir()

    return download_directory
