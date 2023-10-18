"""
Config file intended to be used across the codebase.
"""
from os import environ
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

# The BASE_PATH makes everything absolute.
# TODO: Figure out why we have this otherwise remove
BASE_PATH: Path = Path(__file__).parent

# This must be an absolute path.
VIDEO_DIRECTORY: Path = None
TEST_DIRECTORY: Path = VIDEO_DIRECTORY.joinpath("tiktoks_test")

TiktokCookie: str = environ.get("TIKTOK_COOKIE")


class Config:
    class Apis:
        class Tiktok:
            Cookie = TiktokCookie

    class Concurrency:
        """
        Default config for concurrency used in this project.
        """

        NumberOfWorkers = 4

    class Download:
        """
        Default config for anything related to 'downloads'
        """

        Directory: Path = VIDEO_DIRECTORY.joinpath("downloads")

    class Compilation:
        """
        Default config for the 'compilation' process
        """

        Directory = VIDEO_DIRECTORY.joinpath("compilations")
        TempDirectory = VIDEO_DIRECTORY.joinpath("compilations_tmp")
        ImageClipFont = "Agency-FB"
        ImageClipFontSize = 26
        ImageClipKerningSize = 1
        StaticFolderName = "static"

        # Fonts specific
        FontDirectoryName: str = "fonts"
        DefaultThumbnailFont: str = "AovelSansRounded-rdDL"

        WriteVideoClipsNumberOfThreads = 8

        VideoFileExtension = "mp4"
        MoviePyWriteAlgorithm = "libx264"
        VideoResolution = (1280, 720)
        FPS = 30

    class PocketBase:
        """
        Config for Pocketbase.
        """

        URL = environ.get("POCKETBASE_URL")
        AdminUsername = environ.get("POCKETBASE_ADMIN_USERNAME")
        AdminPassword = environ.get("POCKETBASE_ADMIN_PASSWORD")


class TestConfig:
    """
    Config for tests.
    """

    class Apis:
        class Tiktok:
            Cookie = TiktokCookie

    class Compilation:
        """
        Default config for 'Compilation'
        """

        Directory: Path = TEST_DIRECTORY.joinpath("compilations")

    class Downloads:
        Directory: Path = TEST_DIRECTORY.joinpath("downloads")

    class Temp:
        Directory: Path = TEST_DIRECTORY.joinpath("tmp")
