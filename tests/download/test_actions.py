import unittest
from uuid import uuid4

from src.download.actions import download_tiktok_videos_from_same_channel_and_update_pb
from src.utils.pb.classes import SingletonPocketBase
from src.utils.pb.collections import (
    TiktokCollection,
    VideoCollection,
    TiktokCollectionInfo,
    VideosCollectionInfo,
)
from src.config import TestConfig


class TestTikFail(unittest.TestCase):
    def setUp(self) -> None:
        """ """
        uuid = str(uuid4())
        self.download_dir = TestConfig.Downloads.Directory.joinpath(f"mrbeast_{uuid}")
        self.download_dir.mkdir()

        self.url = "https://www.tiktok.com/@jzuqiai/video/7290247208543276321"
        self.tiktok_record = TiktokCollection.create_record(
            self.url, TiktokCollectionInfo.OriginOoptions.Channel, f"test_{uuid}"
        )

    def tearDown(self) -> None:
        """ """
        pb = SingletonPocketBase()
        try:
            video_record = VideoCollection.validate_record(
                f"{VideosCollectionInfo.Fields.TiktokForeignKey}.{TiktokCollectionInfo.Fields.Id}",
                getattr(self.tiktok_record, TiktokCollectionInfo.Fields.Id),
                True,
            )
            pb.delete(
                VideosCollectionInfo.CollectionName,
                getattr(video_record, VideosCollectionInfo.Fields.Id),
            )
        except Exception:
            pass

        pb.delete(
            TiktokCollectionInfo.CollectionName,
            getattr(self.tiktok_record, TiktokCollectionInfo.Fields.Id),
        )

        for file in self.download_dir.glob("*"):
            file.unlink()
        self.download_dir.rmdir()

    def test_download_tiktok_videos_from_same_channel_and_update_pb(self) -> None:
        # NOTE: This URL should be random and is not probably already in PB are it could
        # result in a failure.
        # TODO: Seperate the tests pb with it's duplicate server or something.
        successes, failures = download_tiktok_videos_from_same_channel_and_update_pb(
            [self.tiktok_record], self.download_dir
        )

        # We shouldn't get any errors
        self.assertEqual(len(failures), 0)

        # There should be 1 item in the download file
        self.assertEqual(len(list(self.download_dir.glob("*"))), 1)


if __name__ == "__main__":
    unittest.main()
