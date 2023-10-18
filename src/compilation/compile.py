"""
Module responsible for create Compilations.
"""

# from shutil import rmtree # NOTE: Doesn't seem to work in Jupyter...
from pathlib import Path
from typing import Union


from typeguard import typechecked

import moviepy.editor as mp

from .models import CompilationVideo
from ..config import Config
from ..logger import SingletonLogger
from ..utils.pb.collections import Compilation


logger = SingletonLogger()


# @typechecked
def create_compilation(
    title: str,
    videos: Union[list[Path], list[mp.CompositeVideoClip]],
    output_filename: str = "output.mp4",
    output_target_resolution: tuple[int, int] = Config.Compilation.VideoResolution,
    fps: int = Config.Compilation.FPS,
) -> CompilationVideo:
    """
    Creates a compilation/stiched videos. Saves the video to the folder of the title in the
    config's directory

    Args:
        title (str): Name of the config (this will be the folder name as well)
        videos (list[Path]):
        output_target_resolution (tuple[ int, int ], optional):
        Defaults to Config.Compilation.VideoResolution.
        fps (int, optional): Config.Compilation.FPS.

    Raises:
        FileExistsError

    Returns:
        CompilationVideo
    """
    logger.info(f"Creating compilation {title} using videos {str(videos)}")
    Compilation.validate_record(title, False)

    compilation_directory: Path = Path(Config.Compilation.Directory).joinpath(title)
    if compilation_directory.exists():
        message: str = (
            f"Compilation with the title {title} does not exist in Pocketbase"
            " but exists in the in the compilation directory. "
            " Either something has gone horribly wrong or it is mock/test"
            " data/attempted before and failed"
        )
        logger.warning(message)
        raise FileExistsError(message)
    compilation_directory.mkdir()

    # Increase the resolution using Moviepy
    if isinstance(videos[0], Path):
        video_file_clips: list[mp.VideoFileClip] = [
            mp.VideoFileClip(video, target_resolution=output_target_resolution)
            for video in videos
        ]
    else:
        video_file_clips = videos

    output_file: Path = compilation_directory.joinpath(output_filename)

    mp.concatenate_videoclips(
        video_file_clips,
        method="compose",
    ).write_videofile(output_file, fps=fps)

    # rmtree(tmp_dir) # NOTE: Doesn't seem to work in Jupyter...
    return output_file
