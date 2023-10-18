"""
Tests for the thumbmails file.
"""
import unittest
from pathlib import Path

from src.compilation.models import CompilationMeatadata, VideoCompilation


# pb = SingletonPocketBase()


class TestHelpers(unittest.TestCase):
    """
    Tests for the thumbmails file.
    """

    def test_compilation_metadata__as_dict_method(self):
        """
        Tests the CompilationMeatadata class as_dict method.
        """
        video = "video.mp4"
        video_record_id = "1"
        start_time_in_seconds = 0.0
        start_time = 0.0
        finish_time_in_seconds = 5.0
        finish_time = 5.0

        instance = CompilationMeatadata(
            video,
            video_record_id,
            start_time_in_seconds,
            start_time,
            finish_time_in_seconds,
            finish_time,
        )
        self.assertDictEqual(
            instance.as_dict(),
            {
                "video": video,
                "video_record_id": video_record_id,
                "start_time_in_seconds": start_time_in_seconds,
                "start_time": start_time,
                "finish_time_in_seconds": finish_time_in_seconds,
                "finish_time": finish_time,
            },
        )

    def test_video_compilation__as_dict_method(self):
        """
        Tests the VideoCompilation class as_dict method.
        """
        # The mock data doesn't matter.
        title = "doesn't matter"
        videos = [Path(__file__)]
        tiktok_record_ids = ["1"]
        video_path = [Path(__file__)]
        metadata = "{}"

        isinstance = VideoCompilation(
            title, videos, tiktok_record_ids, video_path, metadata
        )

        self.assertDictEqual(
            isinstance.as_dict(),
            {
                "title": title,
                "videos": videos,
                "tiktok_record_ids": tiktok_record_ids,
                "video_path": video_path,
                "metadata": metadata,
            },
        )


if __name__ == "__main__":
    unittest.main()
