import unittest
from pathlib import Path
from uuid import uuid4

from src.utils.pb.queries import (
    most_viewed_tiktoks_from_channel,
    all_pb_records_of_channel,
)
from src.utils.pb.classes import SingletonPocketBase
from src.utils.pb.collections import CollectionNames

pb = SingletonPocketBase()


class TestPocketbaseQueries(unittest.TestCase):
    def setUp(self) -> None:
        """
        We need to create Tiktok and Metadata records.
        """
        self.channel_name = f"testing_{str(uuid4())}"
        self.tiktok_record_one = pb.create(
            CollectionNames.tiktok,
            {
                "url": "https://www.tiktok.com/@test/video/12345",
                "origin": "channel",
                "query": self.channel_name,
                "video_id": 12345,
            },
        )
        self.tiktok_record_two = pb.create(
            CollectionNames.tiktok,
            {
                "url": "https://www.tiktok.com/@test/video/67890",
                "origin": "channel",
                "query": self.channel_name,
                "video_id": 67890,
            },
        )
        self.metadata_record_one = pb.create(
            CollectionNames.metadata,
            {
                "tiktok": self.tiktok_record_one.id,
                "views": 100,
                "likes": 200,
                "everything": {},
            },
        )
        self.metadata_record_two = pb.create(
            CollectionNames.metadata,
            {
                "tiktok": self.tiktok_record_two.id,
                "views": 300,
                "likes": 400,
                "everything": {},
            },
        )

    def tearDown(self) -> None:
        """
        Delete the created records in the setup method. We must first delete the
        metadata records THEN the tiktok records.
        """
        pb.delete(CollectionNames.metadata, self.metadata_record_one.id)
        pb.delete(CollectionNames.metadata, self.metadata_record_two.id)
        pb.delete(CollectionNames.tiktok, self.tiktok_record_two.id)
        pb.delete(CollectionNames.tiktok, self.tiktok_record_one.id)

    def test_most_viewed_tiktoks_from_channel(self):
        """
        Tests most_viewed_tiktoks_from_channel.
        """
        result = most_viewed_tiktoks_from_channel(self.channel_name, 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.tiktok_record_two.id)

    def test_all_pb_records_of_channel(self):
        result = all_pb_records_of_channel(self.channel_name)
        self.assertEqual(len(result["tiktoks"]), 2)
        self.assertEqual(len(result["metadata"]), 2)
        self.assertEqual(len(result["videos"]), 0)
        self.assertEqual(len(result["compilations"]), 0)


if __name__ == "__main__":
    unittest.main()
