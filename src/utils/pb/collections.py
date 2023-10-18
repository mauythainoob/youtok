from typing import Optional, Union
from pathlib import Path

from typeguard import typechecked

from pocketbase.models.record import Record

from .classes import SingletonPocketBase, CollectionBaseClass
from .typehints import *
from .helpers import *
from ...compilation.models import CompilationMeatadata, VideoCompilation
from ...utils.helpers import validate_path_exists
from ...logger import SingletonLogger

pb = SingletonPocketBase()
logger = SingletonLogger()


class TiktokCollection(CollectionBaseClass):
    """
    Class representing the tiktok collection.
    """

    @staticmethod
    @typechecked
    def create_record(url: str, origin: str, query: str) -> TiktokCollectionRecord:
        """
        Creates a record. The passed [raw] URL will be parsed to match the schema of the collection.

        Args:
            url (str): The raw URL of the tiktok.
            origin (str): Where the URL was discovered (channel, hashtag, etc).
            query (str): The query used to obtain the URL.

        Returns:
            Record
        """
        logger.info(f"Attempting to insert {url} into TiktokCollection.")
        if origin not in [
            TiktokCollectionInfo.OriginOoptions.TopVideos,
            TiktokCollectionInfo.OriginOoptions.Channel,
            TiktokCollectionInfo.OriginOoptions.Hashtag,
        ]:
            message = f"Invalid origin passed! Passed: {origin}"
            logger.error(message)
            raise ValueError(message)

        pb.create(
            TiktokCollectionInfo.CollectionName,
            {
                TiktokCollectionInfo.Fields.URL: url,
                TiktokCollectionInfo.Fields.Origin: origin,
                TiktokCollectionInfo.Fields.Query: query,
                TiktokCollectionInfo.Fields.VideoId: str(get_video_id_from_url(url)),
            },
        )
        logger.info(f"Successfully inserted {url} into TiktokCollection.")

        return pb.search_single_record(
            TiktokCollectionInfo.CollectionName,
            TiktokCollectionInfo.Fields.URL,
            url,
        )

    @staticmethod
    @typechecked
    def validate_record(
        field: str, value: PocketBaseValueOptions, exists: bool
    ) -> Optional[TiktokCollectionRecord]:
        """
        Validates if a record does or does not exist.

        Args:
            field (str): The field you want to test against.
            value (PocketBaseValueOptions): The value to test against the field.
            exists (bool): Check if the record exists or doesn't exist.

        Raises:
            ValueError: Does not meet the expected exist value.

        Returns:
            Optional[TiktokCollectionRecord]
        """
        logger.info(
            f"Validating TiktokCollection record. Field: {field}. Value: {value}. Exists: {exists}"
        )
        record: Optional[Record] = pb.search_single_record(
            TiktokCollectionInfo.CollectionName, field, value
        )

        record_exists = True if record is not None else False
        if record_exists != exists:
            message = f"Did not match expected exist value"
            logger.error(message)
            raise ValueError(message)
        logger.info(f"Record validated! Exists: {exists}")

        return record


class MetadataCollection(CollectionBaseClass):
    """
    Class representing the metadata collection.
    """

    @staticmethod
    @typechecked
    def create_record(
        tiktok_url: str, views: int, likes: int, everything: dict
    ) -> MetadataCollectionRecord:
        """
        Creates a record.

        Args:
            tiktok_url (str): Tiktok URL.
            views (int):
            likes (int):
            everything (dict): Any extra metadata not in the args.

        Returns:
            MetadataCollectionRecord: _description_
        """
        logger.info(
            f"Attempting to insert metadata for {tiktok_url} into MetadataCollection."
        )
        tiktok_record: TiktokCollectionRecord = TiktokCollection.validate_record(
            TiktokCollectionInfo.Fields.URL,
            tiktok_url,
            exists=True,
        )
        titkok_record_id: str = getattr(tiktok_record, TiktokCollectionInfo.Fields.Id)

        data: dict = {
            MetadataCollectionInfo.Fields.TiktokForeignKey: titkok_record_id,
            MetadataCollectionInfo.Fields.Views: views,
            MetadataCollectionInfo.Fields.Likes: likes,
            MetadataCollectionInfo.Fields.Everything: everything,
        }

        pb.create(MetadataCollectionInfo.CollectionName, data)
        logger.info(f"Successfully inserted {tiktok_url} into MetadataCollection.")

        return pb.search_single_record(
            MetadataCollectionInfo.CollectionName,
            MetadataCollectionInfo.Fields.TiktokForeignKey,
            titkok_record_id,
        )

    @staticmethod
    def validate_record(
        tiktok_record_id: str, exists: bool
    ) -> Optional[MetadataCollectionRecord]:
        """
        Validates if a record does or does not exist. Only uses a Tiktok record's ID to search
        for a metadata record (as views and likes are not good indicators of unique values).

        Args:
            tiktok_record_id (str): The ID of the tiktok record.
            exists (bool): Test if the record exists or doesn't exist.

        Raises:
            ValueError: Does not meet the expected exist value.

        Returns:
            Optional[MetadataCollectionRecord]
        """
        logger.info(
            f"Validating MetadataCollection record. Tiktok record: {tiktok_record_id}. Exists: {exists}"
        )
        record: Optional[MetadataCollectionRecord] = pb.search_single_record(
            MetadataCollectionInfo.CollectionName,
            MetadataCollectionInfo.Fields.TiktokForeignKey,
            tiktok_record_id,
        )

        record_exists = True if record is not None else False
        if record_exists != exists:
            message = f"Did not match expected exist value"
            logger.error(message)
            raise ValueError(message)
        logger.info(f"Record validated! Exists: {exists}")

        return record


class VideoCollection(CollectionBaseClass):
    """
    CLass representing the video collection.
    """

    @staticmethod
    @typechecked
    def create_record(tiktok_url: str, video: Path) -> VideoCollectionRecord:
        """
        Creates a record. Uses the tiktok url for ease of association.

        Args:
            tiktok_url (str): The tiktok video.
            video (Path): The download video path.

        Returns:
            VideoCollectionRecord
        """
        logger.info(f"Attempting to insert {str(video)} into VideoCollection.")

        validate_path_exists(video)

        tiktok_record: TiktokCollectionRecord = TiktokCollection.validate_record(
            TiktokCollectionInfo.Fields.URL, tiktok_url, exists=True
        )
        pb.create(
            VideosCollectionInfo.CollectionName,
            {
                VideosCollectionInfo.Fields.TiktokForeignKey: getattr(
                    tiktok_record, TiktokCollectionInfo.Fields.Id
                ),
                VideosCollectionInfo.Fields.VideoPath: str(video),
                VideosCollectionInfo.Fields.Deleted: False,
                VideosCollectionInfo.Fields.UsedInCompilation: False,
            },
        )
        logger.info(f"Successfully inserted {str(video)} into VideoCollection.")

        return pb.search_single_record(
            VideosCollectionInfo.CollectionName,
            VideosCollectionInfo.Fields.TiktokForeignKey,
            getattr(tiktok_record, TiktokCollectionInfo.Fields.Id),
        )

    @staticmethod
    @typechecked
    def validate_record(
        field: str, value: PocketBaseValueOptions, exists: bool
    ) -> Optional[VideoCollectionRecord]:
        """
        Validates if a record does or does not exist.

        Args:
            field (str): The field you want to test against.
            value (PocketBaseValueOptions): The value to test against the field.
            exists (bool): Check if the record exists or doesn't exist.

        Raises:
            ValueError: Does not meet the expected exist value.

        Returns:
            Optional[VideoCollectionRecord]
        """
        logger.info(
            f"Validating VideoCollection record. Field {field}; value {value}. Exists: {exists}"
        )
        record: Optional[VideoCollectionRecord] = pb.search_single_record(
            VideosCollectionInfo.CollectionName, field, value
        )

        record_exists = True if record is not None else False
        if record_exists != exists:
            message = f"Did not match expected exist value"
            logger.error(message)
            raise ValueError(message)
        logger.info(f"Record validated! Exists: {exists}")

        return record

    @typechecked
    @staticmethod
    def mark_video_as_deleted(video: Path) -> VideoCollectionRecord:
        """
        Mark's a record as deleted in PB.

        Args:
            video (Path)

        Returns:
            VideoCollectionRecord
        """
        validate_path_exists(video)

        args = {
            "field": VideosCollectionInfo.Fields.VideoPath,
            "value": str(video),
            "exists": True,
        }

        record: Optional[VideoCollectionRecord] = VideoCollection.validate_record(
            **args
        )

        setattr(record, VideosCollectionInfo.Fields.Deleted, True)
        pb.update(
            VideosCollectionInfo.CollectionName,
            getattr(record, VideosCollectionInfo.Fields.Id),
            transform_record_to_dict(record, VideosCollectionInfo),
        )

        return VideoCollection.validate_record(**args)

    @typechecked
    @staticmethod
    def mark_video_as_used(video: Path) -> VideoCollectionRecord:
        """
        Mark's a record as used_in_compilation in PB.

        Args:
            video (Path)

        Returns:
            VideoCollectionRecord
        """
        validate_path_exists(video)

        args = {
            "field": VideosCollectionInfo.Fields.VideoPath,
            "value": str(video),
            "exists": True,
        }

        record: Optional[VideoCollectionRecord] = VideoCollection.validate_record(
            **args
        )

        setattr(record, VideosCollectionInfo.Fields.UsedInCompilation, True)
        pb.update(
            VideosCollectionInfo.CollectionName,
            getattr(record, VideosCollectionInfo.Fields.Id),
            transform_record_to_dict(record, VideosCollectionInfo),
        )

        return VideoCollection.validate_record(**args)

    @staticmethod
    def mark_video_as_unused(video: Path) -> bool:
        """
        Mark's a record as used (True) in PB.

        Args:
            video (Path)

        Returns:
            VideoCollectionRecord
        """
        validate_path_exists(video)

        args = {
            "field": VideosCollectionInfo.Fields.VideoPath,
            "value": str(video),
            "exists": True,
        }

        record: Optional[VideoCollectionRecord] = VideoCollection.validate_record(
            **args
        )

        setattr(record, VideosCollectionInfo.Fields.UsedInCompilation, False)
        pb.update(
            VideosCollectionInfo.CollectionName,
            getattr(record, VideosCollectionInfo.Fields.Id),
            transform_record_to_dict(record, VideosCollectionInfo),
        )

        return VideoCollection.validate_record(**args)

    @typechecked
    @staticmethod
    def find_unsed_videos_by_query(
        query: str,
    ) -> list[VideoCollectionRecord]:
        """
        Find all unsued records from a query.

        Args:
            query (str): The query!

        Returns:
            list[VideoCollectionRecord]: The results!
        """
        pb_query: str = (
            f"{VideosCollectionInfo.Fields.UsedInCompilation} = false && "
            f"{VideosCollectionInfo.Fields.Deleted} = false && "
            f"{VideosCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.Query} = {SingletonPocketBase.serialize_value(query)}"
        )
        return pb.search(VideosCollectionInfo.CollectionName, {"filter": pb_query})


class Compilation:
    """
    Class representing a Compilation of Tiktok videos.
    """

    @typechecked
    @staticmethod
    def create_record(compilation: VideoCompilation) -> CompilationRecord:
        # TODO: Docstring
        validate_path_exists(compilation.video_path)

        # We need the video record IDs, which can be grabbed using the
        # tiktok record ids.
        video_ids: list[TiktokRecordVideoId] = [
            getattr(
                VideoCollection.validate_record(
                    f"{VideosCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.VideoId}",
                    str(video_id),
                    True,
                ),
                VideosCollectionInfo.Fields.Id,
            )
            for video_id in compilation.tiktok_record_ids
        ]

        pb.create(
            CompilationsCollectionInfo.CollectionName,
            {
                CompilationsCollectionInfo.Fields.Title: compilation.title,
                CompilationsCollectionInfo.Fields.VideoPath: str(
                    compilation.video_path
                ),
                CompilationsCollectionInfo.Fields.UsedVideos: video_ids,
                CompilationsCollectionInfo.Fields.Metadata: {
                    video_index: metadata.as_dict()
                    for (video_index, metadata) in compilation.metadata.items()
                },
            },
        )

        # Now mark the videos used in the compilation as used so we don't include them
        # in any other compilations.
        for video in compilation.videos:
            VideoCollection.mark_video_as_used(video)

        return pb.search_single_record(
            CompilationsCollectionInfo.CollectionName,
            CompilationsCollectionInfo.Fields.Title,
            compilation.title,
        )

    @staticmethod
    def validate_record(title: str, exists: bool) -> Optional[Record]:
        """
        Validates if a record does, or doesn't, exist.

        Args:
            title (str): Title of the compilation.
            exists (bool): Check if the record exists or doesn't exist.

        Raises:
            ValueError: Does not meet the expect exist value.

        Returns:
            Optional[Record]
        """
        logger.info(f"Validating compilation record. Title: {title}. Exists: {exists}")
        record: Optional[Record] = pb.search_single_record(
            CompilationsCollectionInfo.CollectionName,
            CompilationsCollectionInfo.Fields.Title,
            title,
        )

        record_exists = True if record is not None else False
        if record_exists != exists:
            message = f"Did not match expected exist value"
            logger.error(message)
            raise ValueError(message)

        logger.info(f"Record validated! Exists: {exists}")
        return record

    # TODO: Add tests
    @staticmethod
    def get_video_in_compilation_by_timestamp(
        title: str, timestamp: float
    ) -> Optional[CompilationMeatadata]:
        record: CompilationRecord = Compilation.validate_record(title, True)
        metadata = getattr(record, CompilationsCollectionInfo.Fields.Metadata)

        if not metadata:
            raise ValueError(f"Compilation {title} has no metadata!")

        for video in metadata:
            if (
                video[CompilationMeatadata.Fields.StartTimeInSeconds]
                <= timestamp
                <= video[CompilationMeatadata.Fields.FinishTimeInSeconds]
            ):
                return CompilationMeatadata(**video)

        return None
