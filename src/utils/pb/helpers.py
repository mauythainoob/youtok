"""
Helper functions, classes, etc... 
"""
import re
from pathlib import Path
from typing import Union

from typeguard import typechecked
from pocketbase.models import Record

from ...utils.helpers import validate_path_exists
from ...logger import SingletonLogger

logger = SingletonLogger()


class TiktokCollectionInfo:
    """
    Fields in the collection.
    """

    CollectionName: str = "tiktok"

    class Fields:
        Id: str = "id"
        URL: str = "url"
        Origin: str = "origin"
        Query: str = "query"
        VideoId: str = "video_id"

    class OriginOoptions:
        TopVideos: str = "top_videos"
        Channel: str = "channel"
        Trending: str = "trending"
        Hashtag: str = "hashtag"


class MetadataCollectionInfo:

    """
    Fields in the collection.
    """

    CollectionName: str = "metadata"

    class Fields:
        Id: str = "id"
        TiktokForeignKey: str = "tiktok"
        Views: str = "views"
        Likes: str = "likes"
        Everything: str = "everything"


class VideosCollectionInfo:
    CollectionName: str = "videos"

    class Fields:
        """
        Fields in the collection.
        """

        Id: str = "id"
        TiktokForeignKey: str = "tiktok"
        VideoPath: str = "path"
        Deleted: str = "deleted"
        UsedInCompilation: str = "used"


class CompilationsCollectionInfo:
    CollectionName: str = "compilations"

    class Fields:
        """
        Fields in the collection.
        """

        Id: str = "id"
        Title: str = "title"
        VideoPath: str = "video_path"
        UsedVideos: str = "used_videos"
        Metadata: str = "metadata"


class CollectionNames:
    """
    List of collections to ease development.
    """

    tiktok: str = TiktokCollectionInfo.CollectionName
    metadata: str = MetadataCollectionInfo.CollectionName
    videos: str = VideosCollectionInfo.CollectionName
    compilations: str = CompilationsCollectionInfo.CollectionName


@typechecked
def get_video_id_from_video_file(video: Path) -> int:
    """
    Gets the video ID from a file. The filename SHOULD be the Tiktok's video id.

    Args:
        video (Path): The video of the Tiktok.

    Returns:
        int
    """
    logger.info(f"Getting id from {str(video)}")
    validate_path_exists(video)

    id: str = video.stem
    logger.info(f"Returning id {id} from video {video}")

    return int(video.stem)


@typechecked
def get_video_id_from_url(url: str) -> int:
    """
    Extract the video id from a TikTok video URL.

    Args:
        url (str): The TikTok video URL.

    Returns:
        str: The extracted video id.
    """
    logger.info(f"Getting id from {url}")
    # Regular expression pattern to match the video id in the URL
    pattern: str = r"/(\d+)/?$"

    match = re.search(pattern, url)
    if not match:
        message = f"Invalid TikTok video URL {url}"
        logger.error(message)
        raise ValueError(message)

    id: int = int(match.group(1))
    logger.info(f"Returning id {id} from Tiktok URL {url}")

    return id


@typechecked
def transform_record_to_dict(record: Record, record_blueprint) -> dict:
    """
    Transforms a record into a dict. Only supports *CollectionInfo
    classes with the subclass Fields.

    Args:
        record (Record): The record to transform.
        record_blueprint: The class we should reference for its Fields.

    Raises:
        ValueError: If the record_blueprint is not CompilationsCollectionInfo,
        TiktokCollectionInfo, VideosCollectionInfo, or MetadataCollectionInfo.

    Returns:
        dict
    """
    logger.info(f"Transforming record {record} with blueprint {record_blueprint}")
    if not issubclass(
        record_blueprint,
        (
            CompilationsCollectionInfo,
            TiktokCollectionInfo,
            VideosCollectionInfo,
            MetadataCollectionInfo,
        ),
    ):
        message: str = f"Invalid record blueprint passed. Check func for expected types. Current type: {type(record_blueprint)}"
        logger.error(message)
        raise ValueError(message)

    # Gets user defined class attributes by removing all other details
    attributes: list[str] = list(
        {
            key: value
            for key, value in vars(record_blueprint.Fields).items()
            if not key.startswith("__") and not key.endswith("__")
        }.values()
    )

    return {attribute: getattr(record, attribute) for attribute in attributes}


@typechecked
def transform_raw_tiktok_video_metadata_to_pocketbase_metadata_schema(
    response: dict,
) -> dict:
    """
    Transform raw TikTok video metadata into the PocketBase metadata schema.

    Args:
        response (dict): A dictionary containing raw TikTok video metadata.

    Returns:
        dict: A dictionary containing transformed metadata in the PocketBase schema,
            with keys 'likes', 'views', and 'everything'.
    """
    return {
        "likes": response["stats"]["diggCount"],
        "views": response["stats"]["playCount"],
        "everything": response,
    }
