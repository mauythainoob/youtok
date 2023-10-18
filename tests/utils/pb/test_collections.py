"""
Tests for everything related to collections.
"""

import unittest
from random import randint
from pathlib import Path
from typeguard import typechecked

from . import *

from src.utils.pb.collections import (
    TiktokCollection,
    MetadataCollection,
    VideoCollection,
    Compilation,
)
from src.utils.pb.typehints import *
from src.utils.pb.helpers import TiktokCollectionInfo, VideosCollectionInfo
from src.utils.pb.classes import SingletonPocketBase
from src.compilation.models import VideoCompilation


pb = SingletonPocketBase()


class TestTiktokCollection(unittest.TestCase):
    """
    Tests the TiktokCollection model.
    """

    @typechecked
    def test_01_validate_record(self):
        """
        Test the TiktokCollection.validate_record method.
        """
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        try:
            TiktokCollection.validate_record("url", tiktok_record.url, exists=True)
        except Exception as error:
            delete_tiktok_record(tiktok_record)
            raise error

        try:
            with self.assertRaises(ValueError):
                TiktokCollection.validate_record("url", tiktok_record.url, exists=False)
        except Exception as error:
            delete_tiktok_record(tiktok_record)
            raise error

        delete_tiktok_record(tiktok_record)
        TiktokCollection.validate_record("url", tiktok_record.url, exists=False)

    @typechecked
    def test_02_create_record(self):
        """
        Testing the TiktokCollection.create_record method.
        """
        url: str = (
            f"https://www.tiktok.com/@test/video/{randint(1_000_000, 10_000_000)}"
        )

        record: TiktokCollectionRecord = TiktokCollection.create_record(
            url, "channel", "testing"
        )
        self.assertEqual(record.url, url)
        delete_tiktok_record(record)


class MetadataCollectionCollectionModel(unittest.TestCase):
    """
    Tests the MetadataCollection model.
    """

    @typechecked
    def test_01_validate_record(self):
        """
        Test the MetadataCollection.validate_record method.
        """
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        metadata_record: MetadataCollectionRecord = create_metadata_record(
            tiktok_record
        )

        try:
            MetadataCollection.validate_record(tiktok_record.id, exists=True)
        except Exception as error:
            delete_metadata_record(metadata_record)
            delete_tiktok_record(tiktok_record)
            raise error

        try:
            with self.assertRaises(ValueError):
                MetadataCollection.validate_record(tiktok_record.id, exists=False)
        except Exception as error:
            delete_metadata_record(metadata_record)
            delete_tiktok_record(tiktok_record)
            raise error

        delete_metadata_record(metadata_record)
        delete_tiktok_record(tiktok_record)
        MetadataCollection.validate_record(tiktok_record.id, exists=False)

    @typechecked
    def test_02_create_record(self):
        """
        Testing the Metadata.create_record method
        """
        tiktok_record = create_tiktok_record()

        try:
            metadata_record: MetadataCollectionRecord = (
                MetadataCollection.create_record(tiktok_record.url, 1, 1, {})
            )
        except Exception as error:
            delete_tiktok_record(tiktok_record)
            raise error

        self.assertEqual(metadata_record.likes, 1)
        self.assertEqual(metadata_record.views, 1)

        delete_metadata_record(metadata_record)
        delete_tiktok_record(tiktok_record)


class VideoCollectionCollectionModel(unittest.TestCase):
    """
    Tests the VideoCollection model.
    """

    @typechecked
    def test_01_validate_record(self):
        """
        Test the VideoCollection.validate_record method.
        """
        video: Path = create_mock_video()
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        video_record: VideoCollectionRecord = create_video_record(tiktok_record, video)

        try:
            VideoCollection.validate_record("path", video_record.path, exists=True)
        except Exception as error:
            delete_mock_video(video)
            delete_video_record(video_record)
            delete_tiktok_record(tiktok_record)
            raise error

        try:
            with self.assertRaises(ValueError):
                VideoCollection.validate_record("path", video_record.path, exists=False)
        except Exception as error:
            delete_mock_video(video)
            delete_video_record(video_record)
            delete_tiktok_record(tiktok_record)
            raise error

        delete_mock_video(video)
        delete_video_record(video_record)
        delete_tiktok_record(tiktok_record)
        VideoCollection.validate_record("path", video_record.path, exists=False)

    @typechecked
    def test_02_create_record(self):
        """
        Testing the VideoaCollection.create_record staticmethod.
        """
        video: Path = create_mock_video()
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()

        try:
            video_record = VideoCollection.create_record(tiktok_record.url, video)
        except Exception as error:
            delete_mock_video(video)
            delete_video_record(video_record)
            raise error

        self.assertEqual(video_record.path, str(video))

        delete_mock_video(video)
        delete_video_record(video_record)
        delete_tiktok_record(tiktok_record)

    def test_03_mark_video_as_deleted(self) -> None:
        """
        Testing the VideoaCollection.mark_video_as_deleted staticmethod
        """
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        mock_video: Path = create_mock_video(
            getattr(tiktok_record, TiktokCollectionInfo.Fields.VideoId)
        )
        video_record: VideoCollectionRecord = create_video_record(
            tiktok_record, mock_video
        )

        result = VideoCollection.mark_video_as_deleted(mock_video)

        self.assertTrue(getattr(result, VideosCollectionInfo.Fields.Deleted))

        delete_mock_video(mock_video)
        delete_video_record(video_record)
        delete_tiktok_record(tiktok_record)

    def test_04_mark_video_as_used(self) -> None:
        """
        Testing the VideoaCollection.mark_video_as_deleted staticmethod
        """
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        mock_video: Path = create_mock_video(
            getattr(tiktok_record, TiktokCollectionInfo.Fields.VideoId)
        )
        video_record: VideoCollectionRecord = create_video_record(
            tiktok_record, mock_video
        )

        result = VideoCollection.mark_video_as_used(mock_video)

        self.assertTrue(getattr(result, VideosCollectionInfo.Fields.UsedInCompilation))

        delete_mock_video(mock_video)
        delete_video_record(video_record)
        delete_tiktok_record(tiktok_record)

    def test_05_mark_video_as_unused(self) -> None:
        """
        Testing the VideoaCollection.mark_video_as_deleted staticmethod
        """
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        mock_video: Path = create_mock_video(
            getattr(tiktok_record, TiktokCollectionInfo.Fields.VideoId)
        )
        video_record: VideoCollectionRecord = create_video_record(
            tiktok_record, mock_video
        )

        result = VideoCollection.mark_video_as_unused(mock_video)

        self.assertFalse(getattr(result, VideosCollectionInfo.Fields.UsedInCompilation))

        delete_mock_video(mock_video)
        delete_video_record(video_record)
        delete_tiktok_record(tiktok_record)

    def test_06_find_unsed_videos_by_query(self) -> None:
        """
        Testing the VideoaCollection.video_already_downloaded staticmethod

        For set up, we'll create two records of each (tiktok and video) and update
        one. Then, since one is updated, we should only expect 1 item from the testing
        function.
        """
        # Records 1
        tiktok_record_1: TiktokCollectionRecord = create_tiktok_record()
        mock_video_1: Path = create_mock_video(
            getattr(tiktok_record_1, TiktokCollectionInfo.Fields.VideoId)
        )
        video_record_1: VideoCollectionRecord = create_video_record(
            tiktok_record_1, mock_video_1
        )
        video_record_1 = VideoCollection.mark_video_as_used(mock_video_1)

        query = getattr(tiktok_record_1, TiktokCollectionInfo.Fields.Query)

        # Records 2
        # Make sure the query is the same as the first tiktok record (as it's random)
        tiktok_record_2: TiktokCollectionRecord = pb.create(
            CollectionNames.Tiktok,
            {
                "url": f"https://www.tiktok.com/@test/video/this_doesnt_matter",
                "origin": "channel",
                "query": query,
                "video_id": "12345678912345",
            },
        )
        mock_video_2: Path = create_mock_video(
            getattr(tiktok_record_2, TiktokCollectionInfo.Fields.VideoId)
        )
        video_record_2: VideoCollectionRecord = create_video_record(
            tiktok_record_2, mock_video_2
        )

        # Now actually test stuff
        result = VideoCollection.find_unsed_videos_by_query(query)

        self.assertEqual(len(result), 1)

        delete_mock_video(mock_video_1)
        delete_video_record(video_record_1)
        delete_tiktok_record(tiktok_record_1)
        delete_mock_video(mock_video_2)
        delete_video_record(video_record_2)
        delete_tiktok_record(tiktok_record_2)


class CompilationCollectionModel(unittest.TestCase):
    @typechecked
    def test_01_validate_record(self):
        """
        Test the Compilation.validate_record method.
        """
        mock_video: Path = create_mock_video()
        compilation_video: Path = create_mock_video()
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        video_record: VideoCollectionRecord = create_video_record(
            tiktok_record, mock_video
        )
        compilation_record: CompilationRecord = create_compilation_record(
            compilation_video, [video_record]
        )

        try:
            Compilation.validate_record(compilation_record.title, exists=True)
        except Exception as error:
            delete_mock_video(mock_video)
            delete_mock_video(compilation_video)
            delete_video_record(video_record)
            delete_tiktok_record(tiktok_record)
            delete_compilation_record(compilation_record)
            raise error

        try:
            with self.assertRaises(ValueError):
                Compilation.validate_record(compilation_record.title, exists=False)
        except Exception as error:
            delete_mock_video(mock_video)
            delete_mock_video(compilation_video)
            delete_video_record(video_record)
            delete_tiktok_record(tiktok_record)
            delete_compilation_record(compilation_record)
            raise error

        delete_mock_video(mock_video)
        delete_mock_video(compilation_video)
        delete_video_record(video_record)
        delete_tiktok_record(tiktok_record)
        delete_compilation_record(compilation_record)

        Compilation.validate_record("Doesn't exist", exists=False)

    def test_02_create_record(self):
        """
        Tests the Compilation.create_record static method.
        """
        mock_video: Path = create_mock_video()
        compilation_video: Path = create_mock_video()
        tiktok_record: TiktokCollectionRecord = create_tiktok_record()
        video_record: VideoCollectionCollectionModel = create_video_record(
            tiktok_record, mock_video
        )

        title: str = f"Random title {randint(1, 1_000_000)}"

        compilation: VideoCollection = VideoCompilation(
            title,
            [Path(getattr(video_record, VideosCollectionInfo.Fields.VideoPath))],
            [tiktok_record.video_id],
            compilation_video,
            {},
        )
        record: CompilationRecord = Compilation.create_record(compilation)

        self.assertEqual(title, record.title)

        delete_mock_video(mock_video)
        delete_mock_video(compilation_video)
        delete_video_record(video_record)
        delete_tiktok_record(tiktok_record)
        delete_compilation_record(record)


if __name__ == "__main__":
    unittest.main(failfast=True)
