"""`
Tests for the classes file.

# TODO: Check if a Compilation record is created. I'm being lazy ATM but you need to setup
example TiktokCollection and DownloadedVdeo examples records IOT get the Compilation to reference
everything. 
"""
import unittest

from . import mock_videos

from src.config import Config
from src.compilation.compile import create_compilation


class TestCompileTikTokVideos(unittest.TestCase):
    """
    Tests for the classes file.
    """

    def test_create_compilation(self) -> None:
        title = "Test"
        result = create_compilation(title, mock_videos)
        self.assertTrue(result.exists())
        result.unlink()
        Config.Compilation.Directory.joinpath(title).rmdir()


if __name__ == "__main__":
    unittest.main()
