from typeguard import typechecked
from typing import Optional
from random import randint
from pathlib import Path
from typeguard import typechecked


from src.utils.pb.collections import (
    TiktokCollection,
    MetadataCollection,
    VideoCollection,
    Compilation,
)
from src.utils.pb.typehints import *
from src.utils.pb.classes import SingletonPocketBase
from src.compilation.models import VideoCompilation


pb = SingletonPocketBase()


class CollectionNames:
    Tiktok = "tiktok"
    Metadata = "metadata"
    Videos = "videos"
    Compilation = "compilations"


test_collection_name = "test"


@typechecked
def create_tiktok_record() -> TiktokCollectionRecord:
    """
    Creates a random tiktok record id.

    Returns:
        TiktokCollectionRecord
    """
    video_id = randint(1_000_000, 10_000_000)
    return pb.create(
        CollectionNames.Tiktok,
        {
            "url": f"https://www.tiktok.com/@test/video/{video_id}",
            "origin": "channel",
            "query": f"test_{video_id}",
            "video_id": str(video_id),
        },
    )


@typechecked
def delete_tiktok_record(record: TiktokCollectionRecord):
    """
    Deletes a tiktok record.

    Args:
        record (TiktokCollectionRecord)
    """
    pb.delete(CollectionNames.Tiktok, record.id)


@typechecked
def create_metadata_record(
    tiktok_record: TiktokCollectionRecord,
) -> MetadataCollectionRecord:
    """
    Creates a metadata record.

    Args:
        tiktok_record (TiktokCollectionRecord)

    Returns:
        MetadataCollectionRecord
    """
    return pb.create(
        CollectionNames.Metadata,
        {
            "tiktok": tiktok_record.id,
            "views": randint(1_000_000, 5_000_000),
            "likes": randint(1_000_000, 5_000_000),
            "everything": {},
        },
    )


@typechecked
def delete_metadata_record(record: MetadataCollectionRecord):
    """
    Deletes a metadata record.

    Args:
        record (MetadataCollectionRecord): _description_
    """
    pb.delete(CollectionNames.Metadata, record.id)


@typechecked
def create_mock_video(filename: Optional[str] = None) -> Path:
    """
    Creates a new path object and a new file with said object.

    Returns:
        Path: The newly created video
    """
    video: Path = Path(__file__).parent.joinpath(
        f"{filename if filename else randint(1_000_000, 10_000_000)}.mp4"
    )
    video.touch()
    return video


@typechecked
def delete_mock_video(video: Path):
    """
    Deletes a mock video.
    """
    if video.exists():
        video.unlink()


@typechecked
def create_video_record(
    tiktok_record: TiktokCollectionRecord, video: Path
) -> VideoCollectionRecord:
    """
    Creates a video record.

    Args:
        tiktok_record (TiktokCollectionRecord)
        mock_video (Path)

    Returns:
        VideoCollectionRecord
    """
    return pb.create(
        CollectionNames.Videos,
        {
            "tiktok": tiktok_record.id,
            "path": str(video),
            "deleted": False,
            "used": False,
        },
    )


@typechecked
def delete_video_record(record: VideoCollectionRecord):
    """
    Deletes a video record.

    Args:
        record (VideoCollectionRecord)
    """
    pb.delete(CollectionNames.Videos, record.id)


@typechecked
def create_compilation_record(
    compilation_video: Path,
    used_videos: list[VideoCollectionRecord],
    metadata: Optional[dict] = {},
) -> CompilationRecord:
    """
    Creates a compilation record.

    Args:
        compilation_video (Path): Video that is the "compilation"
        used_videos (list[str]): Videos used.
        metadata (Optional[dict], optional): Defaults to {}.

    Returns:
        CompilationRecord
    """
    return pb.create(
        CollectionNames.Compilation,
        {
            "title": f"Random title {randint(1_000_000, 5_000_000)}",
            "video_path": str(compilation_video),
            "used_videos": [video.id for video in used_videos],
            "metadata": metadata,
        },
    )


@typechecked
def delete_compilation_record(record: CompilationRecord):
    """
    Deletes a compilation record.

    Args:
        record (CompilationRecord)
    """
    pb.delete(CollectionNames.Compilation, record.id)
