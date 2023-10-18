import unittest
from uuid import uuid4

from src.download.video import download_video
from src.config import TestConfig


class TestTikFail(unittest.TestCase):
    def setUp(self) -> None:
        """
        Creates dirs and files for tests.
        """
        self.dir = TestConfig.Temp.Directory.joinpath(
            f"test_download_video_{str(uuid4())}"
        )
        self.dir.mkdir()

        self.file = self.dir.joinpath(f"{uuid4()}.mp4")

    def tearDown(self) -> None:
        """
        Deletes everything from setUp.
        """
        self.file.unlink()
        self.dir.rmdir()

    def test_download_video(self):
        """
        Tests the get_tiktok_video_download_link.

        As the return value is a URL of the download link, we should
        check the content-type.
        """
        self.assertFalse(self.file.exists())

        download_video(
            "https://www.tiktok.com/@kingoftiktokcompilations/video/7257173046899903771",
            self.file,
        )

        self.assertTrue(self.file.exists())


if __name__ == "__main__":
    unittest.main()
