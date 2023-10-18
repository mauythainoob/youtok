"""
Models to be used in the compilation process.
"""
from typing import TypeAlias, Union
from pathlib import Path
from dataclasses import dataclass

#
# Typehints
#
CompilationVideo: TypeAlias = Path


@dataclass
class CompilationMeatadata:
    """
    Class representating metadata of a video in a compilation.
    """

    video: str
    video_record_id: str
    start_time_in_seconds: float
    start_time: float
    finish_time_in_seconds: float
    finish_time: float

    def as_dict(self) -> dict[str, Union[str, float]]:
        """
        These object instance represented... as a dict.
        """
        return {
            "video": self.video,
            "video_record_id": self.video_record_id,
            "start_time_in_seconds": self.start_time_in_seconds,
            "start_time": self.start_time,
            "finish_time_in_seconds": self.finish_time_in_seconds,
            "finish_time": self.finish_time,
        }


@dataclass
class VideoCompilation:
    """
    Class representing the metadata of a compilation.
    """

    title: str
    videos: list[Path]
    tiktok_record_ids: list[str]
    video_path: CompilationVideo
    metadata: dict

    def as_dict(
        self,
    ) -> dict[str, Union[list[str], list[Path], CompilationVideo, dict]]:
        """
        These object instance represented... as a dict.
        """
        return {
            "title": self.title,
            "videos": self.videos,
            "tiktok_record_ids": self.tiktok_record_ids,
            "video_path": self.video_path,
            "metadata": self.metadata,
        }
