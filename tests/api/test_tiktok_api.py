"""`
Tests for the Tiktok API. 
"""
import unittest


from src.apis.tiktok.api import TiktokAPI, ChannelDetailsAPI
from src.config import TestConfig


class TestUserDetailsApi(unittest.TestCase):
    def setUp(self) -> None:
        self.api = ChannelDetailsAPI("mrbeast", TestConfig.Apis.Tiktok.Cookie)

    def test_fetch_user_details(self):
        self.assertEqual(
            self.api.fetch_user_details()["userInfo"]["user"]["uniqueId"], "mrbeast"
        )

    def test_secuid(self):
        self.assertEqual(
            self.api.get_secuid(),
            "MS4wLjABAAAABKjQkOz_IIzXXzEAl_9LGsWhvK-gBnlczwRPXK8EmxAp6K3X0qiaP5_OEqmm0XwG",
        )


class TestTiktokApi(unittest.IsolatedAsyncioTestCase):
    """
    Tests for the classes file.
    """

    async def test_get_video_info_method(self):
        video_id: str = "7270973626050972974"
        result = await TiktokAPI().get_video_info(
            f"https://www.tiktok.com/@therock/video/{video_id}?lang=en"
        )

        self.assertTrue(video_id in result.keys())

    async def test_get_all_video_ids_from_channel(self):
        api = TiktokAPI()
        result = [
            item
            async for item in api.get_all_video_from_channel(
                ChannelDetailsAPI(
                    "kingoftiktokcompilations", TestConfig.Apis.Tiktok.Cookie
                )
            )
        ]
        # NOTE: For these tests to work we rely on this user existing. If this account is later deleted,
        # then change the account name. The reason this account is used is because is has few videos
        # which makes testing faster.
        self.assertTrue(len(result) > 0)

        # NOTE: To definetly confirm it works, it should include a video we KNOW to exist!
        video_discovered = False
        for item in result:
            if item["id"] == "7257173046899903771":
                video_discovered = True
                break

        self.assertTrue(video_discovered)

    async def test_valid_get_tiktok_metadata(self):
        """
        Tests the concurrently_get_tiktok_metadata function.
        """

        url = (
            "https://www.tiktok.com/@kingoftiktokcompilations/video/7257173046899903771"
        )
        result = await TiktokAPI().fetch_video_metadata_stats(url)
        # We test the len as we expect the following keys:
        # collectCount, commentCount, diggCount, playCount, and shareCount
        self.assertEqual(len(result), 5)

    async def test_invalid_get_tiktok_metadata(self):
        """
        Tests the concurrently_get_tiktok_metadata function.
        """

        url = "https://www.tiktok.com/@kingoftiktokcompilations/video/00000000000"
        result = await TiktokAPI().fetch_video_metadata_stats(url)
        # We test the len as we expect the following keys:
        # collectCount, commentCount, diggCount, playCount, and shareCount
        self.assertEqual(result, None)

    async def test_fetch_multiple_video_metadata_stats(self):
        api = TiktokAPI()
        urls = [
            "https://www.tiktok.com/@kingoftiktokcompilations/video/7257173046899903771",
            "https://www.tiktok.com/@kingoftiktokcompilations/video/7257526806092188954",
            "https://www.tiktok.com/@kingoftiktokcompilations/video/7249132203832118555"
            "https://www.tiktok.com/@kingoftiktokcompilations/video/7249116225958202651",
        ]
        data = {}
        async for url, metadata in api.fetch_multiple_video_metadata_stats(urls):
            data[url] = metadata
        self.assertEqual(len(data), len(urls))


if __name__ == "__main__":
    unittest.main()
