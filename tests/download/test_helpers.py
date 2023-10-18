import unittest

import requests

from src.download.helpers import get_tiktok_video_download_link


class TestTikFail(unittest.TestCase):
    def test_get_tiktok_video_download_link(self):
        """
        Tests the get_tiktok_video_download_link.

        As the return value is a URL of the download link, we should
        check the content-type.
        """
        result = get_tiktok_video_download_link(
            "https://www.tiktok.com/@kingoftiktokcompilations/video/7257173046899903771"
        )

        response = requests.get(result)
        self.assertEqual(response.headers["Content-Type"], "video/mp4")


if __name__ == "__main__":
    unittest.main()
