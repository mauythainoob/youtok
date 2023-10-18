"""`
Tests for the actions.py module.
"""
import unittest


from src.apis.tiktok.api import ChannelDetailsAPI
from src.utils.pb.actions import fetch_and_insert_videos_from_tiktok_channel
from src.utils.pb.collections import TiktokCollectionInfo, MetadataCollectionInfo
from src.utils.pb.classes import SingletonPocketBase
from src.config import TestConfig

pb: SingletonPocketBase = SingletonPocketBase()


class TestTiktokApi(unittest.IsolatedAsyncioTestCase):
    """
    Tests for the classes file.
    """

    def setUp(self) -> None:
        self.channel = "kingoftiktokcompilations"

    def tearDown(self) -> None:
        # We have to delete the metadata first
        records = pb.search_multiple_records(
            MetadataCollectionInfo.CollectionName,
            f"{MetadataCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.Query}",
            self.channel,
        )
        for record in records:
            pb.delete(
                MetadataCollectionInfo.CollectionName,
                getattr(record, MetadataCollectionInfo.Fields.Id),
            )

        records = pb.search_multiple_records(
            TiktokCollectionInfo.CollectionName,
            TiktokCollectionInfo.Fields.Query,
            self.channel,
        )
        for record in records:
            pb.delete(
                TiktokCollectionInfo.CollectionName,
                getattr(record, TiktokCollectionInfo.Fields.Id),
            )

    async def test_fetch_and_insert_videos_from_tiktok_channel(self):
        channel_details = ChannelDetailsAPI(self.channel, TestConfig.Apis.Tiktok.Cookie)

        # Make sure we have no results in here first
        records = pb.search_multiple_records(
            TiktokCollectionInfo.CollectionName,
            TiktokCollectionInfo.Fields.Query,
            self.channel,
        )
        self.assertTrue(len(records) == 0)

        await fetch_and_insert_videos_from_tiktok_channel(self.channel, channel_details)

        records = pb.search_multiple_records(
            TiktokCollectionInfo.CollectionName,
            TiktokCollectionInfo.Fields.Query,
            self.channel,
        )

        # We should have some results in here...
        self.assertTrue(len(records) > 0)

        records = pb.search_multiple_records(
            MetadataCollectionInfo.CollectionName,
            f"{MetadataCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.Query}",
            self.channel,
        )
        self.assertTrue(len(records) > 0)


if __name__ == "__main__":
    unittest.main()
