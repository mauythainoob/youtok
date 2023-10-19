"""
Common queries used in the codebase.
"""
from typeguard import typechecked

from .classes import SingletonPocketBase
from .collections import (
    MetadataCollectionInfo,
    TiktokCollectionRecord,
    TiktokCollectionInfo,
    TiktokCollection,
    MetadataCollectionRecord,
    VideoCollectionRecord,
    CompilationRecord,
    VideosCollectionInfo,
)
from ...logger import SingletonLogger


pb = SingletonPocketBase()
logger = SingletonLogger()


@typechecked
def number_of_records_of_channel(query: str) -> int:
    """
    Returns the number of records associated with a specific query.

    Args:
        query (str): The query for which you want to count records.

    Returns:
        int: The number of records associated with the specified query.
    """
    return len(
        pb.search_multiple_records(
            TiktokCollectionInfo.CollectionName,
            TiktokCollectionInfo.Fields.Query,
            query,
        )
    )


@typechecked
def all_pb_records_of_channel(
    channel_name: str,
) -> dict[
    str, list[TiktokCollectionRecord | MetadataCollectionRecord | VideoCollectionRecord]
]:
    """
    # TODO: Write tests
    Fetches all records that are related to a channel (query field in pocketbase).

    Args:
        channel_name (str)

    Returns:
        dict:

    Example:

    all_pb_records_of_channel('mrbeast')

    Returns:
    {
        "tiktoks": [Optional[PocketbaseRecord(s)]],
        "metadata": [Optional[PocketbaseRecord(s)]],
        "videos": [Optional[PocketbaseRecord(s)]],
        "compilations": [Optional[PocketbaseRecord(s)]]
    }

    """
    logger.info(
        f"Fetching all pocketbase records which involve channel: {channel_name}"
    )
    return {
        "tiktoks": pb.search_multiple_records(
            TiktokCollectionInfo.CollectionName,
            TiktokCollectionInfo.Fields.Query,
            channel_name,
        ),
        "metadata": pb.search_multiple_records(
            MetadataCollectionInfo.CollectionName,
            f"{MetadataCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.Query}",
            channel_name,
        ),
        "videos": pb.search_multiple_records(
            VideosCollectionInfo.CollectionName,
            f"{VideosCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.Query}",
            channel_name,
        ),
        "compilations": [],  # TODO: Figure out how we grab this info
    }


@typechecked
def most_viewed_tiktoks_from_channel(
    channel: str, number_records: int = 10
) -> list[TiktokCollectionRecord]:
    """
    Retrieve the most viewed TikToks from a specific channel.

    Args:
        channel (str): The name of the TikTok channel.
        number_records (int, optional): The number of records to retrieve. (Default is 10).

    Returns:
        list[MetadataCollectionRecord]: A list of MetadataCollectionRecord objects representing the most viewed TikToks.

    Raises:
        ValueError: If no results are returned from the search.

    Example:
        To retrieve the top 5 most viewed TikToks from the channel "mrbeast":
        most_viewed_tiktoks = most_viewed_tiktoks_from_channel("mrbeast", 5)
    """
    logger.info(f"Retrieving most viewed TikToks from channel '{channel}'")

    # Perform the search
    pb_results: list[MetadataCollectionRecord] = pb.search_multiple_records(
        MetadataCollectionInfo.CollectionName,
        f"{MetadataCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.Query}",
        channel,
    )

    # Check if results are empty
    if not pb_results:
        message: str = "No results returned!"
        logger.warning(message)
        raise ValueError(message)

    # Sort and return the top records
    logger.info("Sorting results by most viewed")
    top_sorted_records: list[MetadataCollectionRecord] = sorted(
        pb_results,
        key=lambda record: getattr(record, MetadataCollectionInfo.Fields.Views),
        reverse=True,
    )
    top_records: list[MetadataCollectionRecord] = top_sorted_records[0:number_records]

    logger.info(
        f"Searching for tiktok records from the sorted records (0-{len(top_records)})"
    )
    tiktok_records: list[TiktokCollectionRecord] = []
    for metadata_record in top_records:
        tiktok_records.append(
            TiktokCollection.validate_record(
                TiktokCollectionInfo.Fields.Id,
                getattr(
                    metadata_record, MetadataCollectionInfo.Fields.TiktokForeignKey
                ),
                True,
            )
        )

    logger.info(f"Retrieved {len(top_records)} most viewed TikToks")

    return tiktok_records
