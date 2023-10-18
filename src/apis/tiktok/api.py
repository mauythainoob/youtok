from turtle import Turtle
import requests
import json
import base64
import time
import re, traceback
import urllib.parse
import pickle
from urllib.parse import urlencode, quote
from .browser import Browser
from .ultis import set_url, get_param_url
from .encryption import get_tt_param

from functools import lru_cache
from typing import Generator

from typeguard import typechecked

import aiohttp

from ...logger import SingletonLogger
from ...utils.vpn.nordvpn import establish_nordvpn_connection
from ...utils.pb.helpers import get_video_id_from_url

logger = SingletonLogger()


class ChannelDetailsAPI:
    """
    API wrapper for the https://t.tiktok.com/api/user/detail/?aid=1988&uniqueId={...} endpoint.
    """

    def __init__(self, username: str, cookie: str) -> None:
        self.username: str = username
        self.cookie: str = cookie
        logger.info(f"Creating instance with {self.username}")

        # Property used to save the API response
        self.response: dict = None

    # TODO: Potentially cache this
    def fetch_user_details(self) -> dict:
        """
        Fetches the user's details from Tiktok.  The response will be saved
        to the instance's response property. If this method is call again (directly
        or using another method which relies on this method) it will return
        that property.

        Returns:
            dict: The response (or instance response property, which is the response)
        """
        if self.response is not None:
            return self.response

        response = requests.get(
            f"https://t.tiktok.com/api/user/detail/?aid=1988&uniqueId={self.username}",
            headers={"Cookie": self.cookie},
        )
        response.raise_for_status()

        self.response = response.json()
        return self.response

    def get_secuid(self) -> str:
        """
        Returns the secUid from a user.

        Returns:
            str: _description_
        """
        logger.info(f"Returning secUid for {self.username}")
        return self.fetch_user_details()["userInfo"]["user"]["secUid"]


class TiktokAPI:
    def __init__(self):
        self.BASE_URL = "https://www.tiktok.com/node/"

        self.user_info = None

    def openBrowser(self, url="https://tiktok.com/", show_br=False):
        self.browser = Browser(url, show_br)
        self.browser.launch_borwser()
        self.default_params = self.browser.get_defaut_params()

    def closeBrowser(self):
        self.browser.close_browser()

    # def getTrendingFeed(self, count: int = 100, first=True):
    #     if first == True:
    #         return self.browser.first_data()
    #     try:
    #         params = {"count": f"{count}"}
    #         params.update(self.default_params)
    #         params = dict(sorted(params.items(), key=lambda item: item[1]))
    #         api_url = set_url("/api/recommend/item_list", params)
    #         data = self.browser.fetch_browser(api_url)
    #         return data
    #     except Exception:
    #         import traceback

    #         print(traceback.format_exc())
    #         return False

    # def getUserFeed(self, secUid="", cursor=0, first=True):
    #     if first == True:
    #         return self.browser.first_data()
    #     try:
    #         params = {
    #             "secUid": secUid,
    #             "count": "30",
    #             "cursor": cursor,
    #             "userId": "undefined",
    #         }
    #         params.update(self.default_params)
    #         params = dict(sorted(params.items(), key=lambda item: item[1]))
    #         api_url = set_url("/api/post/item_list/", params)
    #         tt_params = get_tt_param(get_param_url(params))
    #         data = self.browser.fetch_browser(api_url, tt_params)
    #         return data
    #     except Exception:
    #         import traceback

    #         print(traceback.format_exc())
    #         return False

    def getChallengeFeed(self, ch_id="", cursor=0, first=True):
        if first == True:
            return self.browser.first_data()
        try:
            params = {
                "challengeID": ch_id,
                "count": "30",
                "cursor": cursor,
            }
            params.update(self.default_params)
            params = dict(sorted(params.items(), key=lambda item: item[1]))
            api_url = set_url("/api/challenge/item_list/", params)
            tt_params = get_tt_param(get_param_url(params))
            data = self.browser.fetch_browser(api_url, tt_params)
            return data
        except Exception:
            import traceback

            print(traceback.format_exc())
            return False

    def getMusicFeed(self, music="", max_cursor=0):
        if music == "":
            return "Challenge or Ch_id is required"
        param = {
            "type": 4,
            "secUid": "",
            "id": "",
            "count": 30,
            "minCursor": 0,
            "maxCursor": max_cursor,
            "shareUid": "",
            "lang": "",
            "verifyFp": "",
        }

        # ch = self.getInfoMusic(music)
        if music:
            param["id"] = music
        else:
            return False
        try:
            url = self.BASE_URL + "video/feed"
            res = requests.get(
                url,
                params=param,
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "authority": "www.tiktok.com",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Host": "www.tiktok.com",
                    "User-Agent": "Mozilla/5.0  (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/86.0.170 Chrome/80.0.3987.170 Safari/537.36",
                },
            )
            resp = res.json()
            return resp["body"], res.cookies.get_dict()
        except Exception:
            print(traceback.format_exc())
            return False

    def getInfoChallenge(self, challenge):
        if challenge == "":
            return "Challenge is required"
        try:
            res = requests.get(
                "https://www.tiktok.com/tag/{}".format(quote(challenge)),
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "authority": "www.tiktok.com",
                    "path": "/tag/{}".format(quote(challenge)),
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Host": "www.tiktok.com",
                    "User-Agent": "Mozilla/5.0  (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/86.0.170 Chrome/80.0.3987.170 Safari/537.36",
                },
            )
            resp = self.__get_data_from_html_text(res.text)
            return json.loads(resp)["ChallengePage"]
        except Exception:
            print(traceback.format_exc())
            return False

    def getInfoMusic(self, music_url):
        if music_url == "":
            return "Challenge is required"
        try:
            res = requests.get(
                music_url,
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "authority": "www.tiktok.com",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Host": "www.tiktok.com",
                    "User-Agent": "Mozilla/5.0  (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/86.0.170 Chrome/80.0.3987.170 Safari/537.36",
                },
            )
            resp = self.__get_data_from_html_text(res.text)
            return json.loads(resp)["props"]["pageProps"]
        except Exception:
            print(traceback.format_exc())
            return False

    @typechecked
    async def get_video_info(self, url: str) -> None | dict:
        """
        Get's the information about a video.

        Args:
            url (str): URL to the video.

        Returns:
            None | dict: None if nothing returned else the response.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=self.__get_common_request_headers(),
            ) as response:
                if response.status != 200:
                    return None

                video_info_key: str = "ItemModule"
                data = json.loads(self.__get_data_from_html_text(await response.text()))
                if video_info_key not in data:
                    return None

                logger.info(f"Successfully returning data for {url}")
                return data[video_info_key]

    @typechecked
    async def get_all_video_from_channel(
        self, channel_details: ChannelDetailsAPI
    ) -> Generator:
        """
        Returns all videos [urls] from a channel.

        Args:
            channel_details (ChannelDetailsAPI):

        Yields:
            Generator: The results can get pretty large so let's prevent any memory issues
        """
        # TODO: Make explicit the exception raised here
        # Sometimes, the response fails... maybe due to span, othertime just because
        # we we no response... if that's the case, we just return what we get.
        # TODO: In the future, improve what we have here. Dunno how, but something to consider.
        # We use this as the initial value just to kick things off...
        cursor: int = 99_999_999_999_999_999_999_999
        sec_uid = channel_details.get_secuid()
        url_template: str = "https://www.tiktok.com/api/creator/item_list/?aid=1998&type=1&count=15&cursor={cursor}&secUid={sec_uid}&verifyF=verify_"

        attempts = 3

        while True:
            url: str = url_template.format(cursor=cursor, sec_uid=sec_uid)
            logger.info(
                f"Discovering {channel_details.username}'s videos. Cursor: {cursor}"
            )

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=15) as response:
                        response.raise_for_status()
                        data: dict = await response.json()
            except Exception:
                if attempts == 0:
                    break

                attempts -= 1
                # TODO: Change this in the future as some peeps may not live here
                await establish_nordvpn_connection("United Kingdom")
                continue

            if not data["itemList"]:
                break

            for item in data["itemList"]:
                yield item

            if not data["hasMorePrevious"]:
                break

            cursor = data["itemList"][-1]["createTime"] * 1000

    async def fetch_video_metadata_stats(self, url: str) -> dict | None:
        """
        The function actually used to download metadata.

        Args:
            url (str): _description_

        Returns:
            tuple[str, Optional[dict]]: _description_
        """
        response: dict | None = await TiktokAPI().get_video_info(url)
        video_id: str = str(get_video_id_from_url(url))

        if response is None:
            return None

        data = response[video_id]
        if not "stats" in data:
            return None

        return data["stats"]

    async def fetch_multiple_video_metadata_stats(self, urls: list[str]) -> Generator:
        for url in urls:
            yield url, await self.fetch_video_metadata_stats(url)

    def __get_data_from_html_text(self, html):
        resp = self.r1(
            r"window\[\'SIGI_STATE\'\]=(.*?);window\[\'SIGI_RETRY\'\]", html
        ) or self.r1(
            r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', html
        )
        return resp

    def __get_common_request_headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "authority": "www.tiktok.com",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Host": "www.tiktok.com",
            "User-Agent": "Mozilla/5.0  (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/86.0.170 Chrome/80.0.3987.170 Safari/537.36",
        }

    def r1(self, pattern, text):
        m = re.search(pattern, text)
        if m:
            return m.group(1)
