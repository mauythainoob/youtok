"""
Module to generate thumbnails for a Compilation (or any video of that matter).
"""
from pathlib import Path
from typing import Optional
from random import randint, shuffle
from PIL import Image


import moviepy.editor as mp
from typeguard import typechecked
import numpy as np

from .helpers import (
    total_number_of_frames_in_a_video,
    create_background_for_text,
    TextBackgroundImageClip,
)
from ..config import Config
from ..logger import SingletonLogger
from ..utils.helpers import validate_path_exists

logger: SingletonLogger = SingletonLogger()


@typechecked
def generate_thumbnails(
    title: str, video: Path, number_of_thumbnails: Optional[int] = None
) -> list[Image.Image]:
    """
    Generates a list of thumbnails with frames from a video and overlaid text.
    This functions will create a thumbnail that has three random images evenly spaced
    across the thumbnail.

    Args:
        title (str): The text to be overlaid on the thumbnails.
        video (Path): The target video file.
        number_of_thumbnails (int): Number of thumbnails to generate. Default is 50.

    Returns:
        list[Image.Image]: A list of generated thumbnails.
    """
    logger.info(f"Generating thumbnail for {str(video)} with title {title}")
    validate_path_exists(video)

    # Get frames from the video
    frames: list[Image.Image] = _get_frames_from_video(video)
    shuffle(frames)

    thumbnails: list[Image.Image] = _construct_thumbnail_images(
        frames, number_of_thumbnails=number_of_thumbnails
    )

    text = mp.TextClip(title, fontsize=50, font=Config.Compilation.ImageClipFont)
    text_background: TextBackgroundImageClip = create_background_for_text(text)

    # Move this to a function
    final_thumbnails: list[Image.Image] = []
    for thumbnail in thumbnails:
        thumbnail = mp.ImageClip(np.array(thumbnail))
        clips = [
            thumbnail,
            text_background.set_position("center"),
            text.set_position("center"),
        ]
        vid = mp.CompositeVideoClip(clips)
        final_thumbnails.append(Image.fromarray(vid.get_frame(0)))

    return final_thumbnails


@typechecked
def save_thumbnails_to_path(
    thumbnails: list[Image.Image], directory: Path
) -> list[Path]:
    """
    # NOTE: This function has  side affects
    Saves thumbmails to a path. This will create a 'thumbnails' directory where the
    thumbnails will be saved.

    Args:
        thumbnails (list[Image.Image]):
        directory (Path): Must be a directory.

    Raises:
        Exception: If the passed Path object is not a dir.
        Exception: If a "thumbnails" dir exists in the Path object dir.

    Returns:
        list[Path]: The newly created thumbnails
    """
    logger.info(f"Checking is {str(directory)} is a directory.")
    if not directory.is_dir():
        message: str = f"Path {str(directory)} is not a directory. Can't write thumbnails to this location."
        logger.error(message)
        raise Exception(message)
    validate_path_exists(directory)

    logger.info(f"Checking if 'thumbnails' dir doesn't exist in {str(directory)})")
    thumbnail_dir = directory.joinpath("thumbnails")
    if thumbnail_dir.exists():
        message: str = f"Thumbanils directory in {str(directory)} already exists. Can't write thumbnails to this location."
        logger.error(message)
        raise Exception(message)
    thumbnail_dir.mkdir()

    logger.info(f"Saving {len(thumbnails)} thumbnails to {str(thumbnail_dir)}")
    thumbnail_files: list[Path] = []
    for index, thumbnail in enumerate(thumbnails):
        dir: Path = thumbnail_dir.joinpath(f"{index}.jpg")
        thumbnail.save(dir)
        thumbnail_files.append(dir)

    return thumbnail_files


@typechecked
def _get_frames_from_video(video: Path) -> list[Image.Image]:
    """
    Grabs a collection of frames from a video.

    Args:
        video (Path): The target video.

    Returns:
        list[Image.Image]: A list of PIL Image objects representing the extracted frames.
    """
    video_filepath: str = str(video)
    logger.info(f"Fetching frames from {video_filepath}")

    validate_path_exists(video)

    logger.info(f"Opening {video_filepath} using MoviePy VideoFileClip")
    video_clip: mp.VideoFileClip = mp.VideoFileClip(video_filepath)

    frames = [
        Image.fromarray(video_clip.get_frame(frame))
        for frame in range(0, total_number_of_frames_in_a_video(video))
    ]

    logger.info(f"Closing {video_filepath}")
    video_clip.close()

    logger.info(f"Returning {len(frames)} from {video_filepath}")
    return frames


@typechecked
def _get_random_frame(frames: list[Image.Image]) -> Image.Image:
    """
    Selects a random frames from an array of frames.

    Args:
        frames (list[Image.Image]): The frames to select from.

    Returns:
        Image.Image: The randomly selected frame
    """
    index = randint(0, len(frames) - 1)
    logger.info(f"Selecting frame number {index} out of {len(frames)}")
    return frames[index]


def _construct_thumbnail_images(
    frames: list[Image.Image],
    thumbnail_width: int = 1560,
    thumbnail_height: int = 920,
    number_of_thumbnails: Optional[int] = None,
) -> list[Image.Image]:
    """
    Constructs a number of thumbnails which have three (potentially) different images
    side-to-side (horizontal) to fill up the desired width and hieght of the thumbnail.

    # NOTE:
    The word "potentially" is used as we grab random frames but dont check if the same frame
    has been returned before.

    Args:
        frames (list[Image.Image]): Essentially the video [frames] you want the images from.
        thumbnail_width (int, optional): Defaults to 1560.
        thumbnail_height (int, optional): Defaults to 920.
        number_of_thumbnails (Optional[int], optional): How many thumbnails we should return.
            Defaults to None. If nothing is passed, it'll use the number of frames passed as
            this value.

    Returns:
        list[Image.Image]: The thumbnails...
    """
    if not number_of_thumbnails:
        number_of_thumbnails = len(frames)

    logger.info(
        f"Generating {number_of_thumbnails} thumbnails ({thumbnail_width} x {thumbnail_height})."
    )

    thumbnails: list[Image.Image] = []
    for _ in range(0, number_of_thumbnails):
        logger.info("Finding three random frames to use for the thumbnail")
        three_random_frames: list[Image.Image] = [
            _get_random_frame(frames).resize(
                (int(thumbnail_width / 3), thumbnail_height)
            )
            for _ in range(0, 3)
        ]
        left_image, middle_image, right_image = three_random_frames

        thumbnail: Image.Image = Image.new(
            "RGB", (thumbnail_width, thumbnail_height), (250, 250, 250)
        )

        # Let's put each frame next to eachother. We simply "push" the images
        # next to eachother based of their size.
        thumbnail.paste(left_image, (0, 0))
        thumbnail.paste(middle_image, (left_image.size[0], 0))
        thumbnail.paste(right_image, (2 * middle_image.size[0], 0))

        thumbnails.append(thumbnail)
        logger.info("Thumbnail generated")

    return thumbnails


# @typechecked
# def _get_font_location(
#     font: str = Config.Compilation.DefaultThumbnailFont,
# ) -> Path:
#     """
#     Get the file location of a font.

#     Args:
#         font (str): Name of the font file. Default is 'AovelSansRounded-rdDL'.

#     Returns:
#         str: File location of the font.
#     """
#     logger.info(f"Look for font {font}")
#     font_path: Path = Path(__file__).parent.joinpath("fonts").joinpath(f"{font}.ttf")
#     validate_path_exists(font_path)

#     return font_path
