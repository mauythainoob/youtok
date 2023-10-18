"""
Functions to aid the development or process of this project that are concerned around Pocketbase.
"""
from pathlib import Path
from typing import AsyncGenerator, Optional

from typeguard import typechecked

from .classes import SingletonPocketBase
from .typehints import *
from .helpers import (
    TiktokCollectionInfo,
    MetadataCollectionInfo,
    VideosCollectionInfo,
    transform_raw_tiktok_video_metadata_to_pocketbase_metadata_schema,
)
from .collections import VideoCollection, TiktokCollection, MetadataCollection

from ...apis.tiktok.api import TiktokAPI, ChannelDetailsAPI
from ...config import Config
from ...logger import SingletonLogger

pb = SingletonPocketBase()
logger = SingletonLogger()


@typechecked
async def fetch_and_insert_videos_from_tiktok_channel(
    channel: str, user_details: Optional[ChannelDetailsAPI] = None
) -> None:
    """
    Fetches and inserts videos from a TikTok channel into the database.

    Args:
        channel (str): The name of the TikTok channel.
        user_details (Optional[ChannelDetailsAPI]): Optional user details object.
            If not provided, it will be created with default settings.

    Returns:
        None

    Example:
        await fetch_and_insert_videos_from_tiktok_channel("mrbeast")

    # TODO: Write tests for this
    """
    if user_details is None:
        user_details: ChannelDetailsAPI = ChannelDetailsAPI(
            channel, Config.Apis.Tiktok.Cookie
        )

    tiktok_api = TiktokAPI()
    channel_results: AsyncGenerator = tiktok_api.get_all_video_from_channel(
        user_details
    )

    async for result in channel_results:
        url: str = "https://www.tiktok.com/@{username}/video/{video_id}".format(
            username=channel, video_id=result["id"]
        )

        tiktok_record_inserted = True
        try:
            TiktokCollection.create_record(
                url, TiktokCollectionInfo.OriginOoptions.Channel, channel
            )
        except Exception as e:
            logger.warning(
                f"Failed to insert URL '{url}' into the database. Error: {str(e)}"
            )
            tiktok_record_inserted = False

        if not tiktok_record_inserted:
            continue

        metadata: dict = (
            transform_raw_tiktok_video_metadata_to_pocketbase_metadata_schema(result)
        )
        try:
            MetadataCollection.create_record(url, **metadata)
        except Exception as e:
            logger.warning(f"Failed to insert metadata with {url}. Error: {str(e)}")
