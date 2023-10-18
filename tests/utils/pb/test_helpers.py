"""
Tests the helper functions.
"""
import unittest

from . import (
    create_tiktok_record,
    delete_tiktok_record,
    create_metadata_record,
    delete_metadata_record,
)

from src.utils.pb.helpers import *


class TestHelperFunctions(unittest.TestCase):
    """
    Tests the helper functions.
    """

    def setUp(self) -> None:
        self.mock_video_file = Path(__file__).parent.joinpath("12345.mp4")
        self.mock_video_file.touch()

        self.tiktok_record = create_tiktok_record()
        self.metadata_record = create_metadata_record(self.tiktok_record)

    def tearDown(self) -> None:
        if self.mock_video_file.exists():
            self.mock_video_file.unlink()

        delete_metadata_record(self.metadata_record)
        delete_tiktok_record(self.tiktok_record)

    def test_get_video_id_from_video_file(self):
        result = get_video_id_from_video_file(self.mock_video_file)
        self.assertEqual(result, 12345)

    def test_get_video_id_functions(self):
        id = 7252525161415691525

        result = get_video_id_from_url(
            f"https://www.tiktok.com/@spicy_karate/video/{id}"
        )
        self.assertEqual(result, id)

        # If the username contains numbers
        result = get_video_id_from_url(f"https://www.tiktok.com/@123123123/video/{id}")
        self.assertEqual(result, id)

    def test_transform_record_to_dict(self):
        self.assertEqual(
            transform_record_to_dict(self.tiktok_record, TiktokCollectionInfo),
            {
                "id": self.tiktok_record.id,
                "url": self.tiktok_record.url,
                "origin": self.tiktok_record.origin,
                "query": self.tiktok_record.query,
                "video_id": self.tiktok_record.video_id,
            },
        )

        self.assertEqual(
            transform_record_to_dict(self.metadata_record, MetadataCollectionInfo),
            {
                "id": self.metadata_record.id,
                "tiktok": self.tiktok_record.id,
                "views": self.metadata_record.views,
                "likes": self.metadata_record.likes,
                "everything": self.metadata_record.everything,
            },
        )


if __name__ == "__main__":
    unittest.main(failfast=True)
