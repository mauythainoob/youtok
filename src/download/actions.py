"""
Actions to aid the download process.
"""
from typing import TypeAlias
from pathlib import Path

from typeguard import typechecked
from requests.exceptions import HTTPError
from pocketbase.utils import ClientResponseError

from .helpers import get_tiktok_video_download_link
from .video import download_video
from ..utils.helpers import validate_path_exists
from ..utils.pb.classes import SingletonPocketBase
from ..utils.pb.collections import VideoCollection
from ..utils.pb.helpers import (
    VideosCollectionInfo,
    TiktokCollectionInfo,
    get_video_id_from_url,
)
from ..utils.pb.typehints import TiktokCollectionRecord, VideoCollectionRecord
from ..logger import SingletonLogger

pb = SingletonPocketBase()
logger: SingletonLogger = SingletonLogger()

#
# Typehints
#
_Url: TypeAlias = str
_Error: TypeAlias = str
_FailedDownloads: TypeAlias = list[tuple[_Url, _Error]]
_SuccessfulDownloads: TypeAlias = list[VideoCollectionRecord]


def download_tiktok_videos_from_same_channel_and_update_pb(
    tiktok_pb_records: list[TiktokCollectionRecord], directory: Path
) -> tuple[_SuccessfulDownloads, _FailedDownloads]:
    """
    Exactly what is says on the tin... the reason we same "same channel" is that
    we only pass in one directly, where all the videos will be downloaded to.

    Args:
        tiktok_pb_records (list[TiktokCollectionRecord]): _description_
        directory (Path): _description_

    Returns:
        _type_: _description_
    """
    validate_path_exists(directory)

    failed_downloads: _FailedDownloads = []
    videos: _SuccessfulDownloads = []

    # This is created so this str is only created once and it keeps pylint happy
    tiktok_id_pb_query = (
        f"{VideosCollectionInfo.Fields.TiktokForeignKey}"
        f".{TiktokCollectionInfo.Fields.VideoId}"
    )

    for url in [
        getattr(record, TiktokCollectionInfo.Fields.URL) for record in tiktok_pb_records
    ]:
        tiktok_video_id: int = get_video_id_from_url(url)
        try:
            # Check the video doesn't already exist in Pocketbase
            VideoCollection.validate_record(
                tiktok_id_pb_query,
                tiktok_video_id,
                False,
            )
        except ValueError as error:
            failed_downloads.append((url, str(error)))
            continue

        tiktok_video_download_link: str = get_tiktok_video_download_link(url)
        video: Path = directory.joinpath(f"{tiktok_video_id}.mp4")

        try:
            download_video(tiktok_video_download_link, video)
            videos.append(VideoCollection.create_record(url, video))
        except (HTTPError, ClientResponseError) as error:
            failed_downloads.append((url, error))
            continue

    return videos, failed_downloads
