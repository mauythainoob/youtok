"""`
Tests for the helpers file.
"""
import unittest
from datetime import timedelta
from pathlib import Path

import moviepy.editor as mp
import numpy as np

from . import mock_videos

from src.config import TestConfig
from src.utils.pb.classes import SingletonPocketBase
from src.utils.pb.helpers import TiktokCollectionInfo, VideosCollectionInfo
from src.utils.pb.collections import TiktokCollection, VideoCollection
from src.compilation.helpers import (
    construct_metadata_from_videos,
    total_number_of_frames_in_a_video,
)

pb = SingletonPocketBase()


class TestHelpers(unittest.TestCase):
    """
    Tests for the helpers file.
    """

    def setUp(self) -> None:
        """
        Create 'video' and 'tiktok' records.

        # TODO: We have to use actual videos to make this work test work, which requires additional
        setup. Therefore, we just need to create a file which has n number of seconds.
        """
        self.maxDiff = None

        self.tiktok_record_1 = TiktokCollection.create_record(
            "https://tiktok.com/@testing/video/12345", "channel", "test"
        )
        self.tiktok_record_2 = TiktokCollection.create_record(
            "https://tiktok.com/@testing/video/56780", "channel", "test2"
        )

        self.mock_video_1 = mock_videos[0]
        self.video_record_1 = VideoCollection.create_record(
            "https://tiktok.com/@testing/video/12345", self.mock_video_1
        )

        self.mock_video_2 = mock_videos[1]
        self.video_record_2 = VideoCollection.create_record(
            "https://tiktok.com/@testing/video/56780", self.mock_video_2
        )

    def tearDown(self) -> None:
        """
        Deletes the created records in setUp().
        """
        # We have to delete the video records before the tiktok records
        pb.delete(VideosCollectionInfo.CollectionName, self.video_record_1.id)
        pb.delete(VideosCollectionInfo.CollectionName, self.video_record_2.id)
        pb.delete(TiktokCollectionInfo.CollectionName, self.tiktok_record_1.id)
        pb.delete(TiktokCollectionInfo.CollectionName, self.tiktok_record_2.id)

    def test_construct_metadata_from_videos__as_dict_method(self):
        """
        Testing the construct_metadata_from_videos function. Whilst the function results
        a dict whos values are CompilationMeatadata - this class has a as_dict method.
        This is all we care about.
        """
        video_1 = mp.VideoFileClip(self.mock_video_1)
        video_2 = mp.VideoFileClip(self.mock_video_2)

        result = {
            key: value.as_dict()
            for (key, value) in construct_metadata_from_videos(
                [video_1, video_2]
            ).items()
        }
        expected = {
            0: {
                "video": video_1.filename,
                "video_record_id": self.video_record_1.id,
                "start_time_in_seconds": 0,
                "start_time": "0:00:00",
                "finish_time_in_seconds": video_1.duration,
                "finish_time": str(timedelta(seconds=video_1.duration)),
            },
            1: {
                "video": video_2.filename,
                "video_record_id": self.video_record_2.id,
                "start_time_in_seconds": video_1.duration,
                "start_time": str(timedelta(seconds=video_1.duration)),
                "finish_time_in_seconds": video_1.duration + video_2.duration,
                "finish_time": str(
                    timedelta(seconds=video_1.duration + video_2.duration)
                ),
            },
        }

        self.assertEqual(result, expected)

    def test_total_number_of_frames_in_a_video(self):
        """
        Tests the total_number_of_frames_in_a_video function.
        """
        video = Path(mock_videos[0])
        video_duration_rounded_down = 12
        self.assertEqual(
            total_number_of_frames_in_a_video(video), video_duration_rounded_down
        )


if __name__ == "__main__":
    unittest.main()
