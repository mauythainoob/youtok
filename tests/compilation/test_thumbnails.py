"""
Tests for the thumbmails file.
"""
import unittest
from uuid import uuid4

from . import mock_videos

from src.config import TestConfig
from src.compilation.thumbnails import generate_thumbnails, save_thumbnails_to_path


class TestHelpers(unittest.TestCase):
    """
    Tests for the thumbmails file.
    """

    def setUp(self) -> None:
        self.temp_dir = TestConfig.Temp.Directory.joinpath(str(uuid4()))
        self.temp_dir.mkdir()

    def test_generate_thumbnails_process(self):
        """
        Tests if we can generate thumbnails and save them to a directory.
        """
        video = mock_videos[1]
        number_of_thumbnails = 10

        thumbnails = generate_thumbnails(
            "Testing this compilation", video, number_of_thumbnails
        )
        save_thumbnails_to_path(thumbnails, self.temp_dir)

        # Save thumbnails should create this path
        self.assertTrue(self.temp_dir.joinpath("thumbnails").exists())
        self.assertEqual(
            len(list(self.temp_dir.joinpath("thumbnails").glob("*.jpg"))),
            number_of_thumbnails,
        )


if __name__ == "__main__":
    unittest.main()
