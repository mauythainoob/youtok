"""
Helpers for the Compilation process.
"""
import math
from typing import Union
from pathlib import Path

from datetime import timedelta
from time import sleep

import moviepy.editor as mp

from typeguard import typechecked
from PIL import Image, ImageDraw

from .models import CompilationMeatadata
from ..utils.pb.typehints import VideoCollectionRecord
from ..utils.pb.collections import VideosCollectionInfo
from ..utils.helpers import validate_path_exists
from ..logger import SingletonLogger
from ..utils.pb.classes import SingletonPocketBase
from ..utils.pb.collections import VideoCollection
from ..config import Config


pb = SingletonPocketBase()
logger = SingletonLogger()


#
# Typehints
#
_IncludeViews = tuple[bool, int]
_IncludeLikes = tuple[bool, int]

_ViewsLikesOrChannelImageClip = mp.ImageClip
TextBackgroundImageClip = mp.ImageClip


# TODO: Somehow write tests for this.
@typechecked
def add_likes_views_or_channel_name_to_video(
    video: mp.VideoFileClip,
    views_details: _IncludeViews = (False, 0),
    likes_details: _IncludeLikes = (False, 0),
    details_duration: int = 5,
) -> mp.CompositeVideoClip:
    """
    Adds likes, views, and channel name to a clip.

    Args:
        video (Union[mp.VideoClip, mp.VideoFileClip]): The video/clip.
        views_details (_IncludeViews, optional):
            If views should be added and it's value. Defaults to (False, 0).
        likes_details (_IncludeLikes, optional):
            If likes should be added and it's value. Defaults to (False, 0).

    Raises:
        ValueError: Views or likes not included
        ValueError: Views included but no value added
        ValueError: Likes included but no value added

    Returns:
        mp.CompositeVideoClip: Video/clip with the added text.
    """
    include_views: bool
    views: int
    include_views, views = views_details

    include_likes: bool
    likes: int
    include_likes, likes = likes_details

    if not include_views and not include_likes:
        message: str = "Neither views or likes are specified."
        logger.error(message)
        raise ValueError(message)

    if views == 0 and include_views:
        message: str = "Views are set to be included, but no value is passed."
        logger.error(message)
        raise ValueError()

    if likes == 0 and include_likes:
        message: str = "Likes are set to be included, but no value is passed."
        logger.error(message)
        raise ValueError(message)

    logger.info("Looping over included details")
    # See what text we've included
    text_clips_to_include: list[
        tuple[_ViewsLikesOrChannelImageClip, TextBackgroundImageClip]
    ] = []

    # Make the fontsize proportionate to the size of the video
    clip_width: float | int = video.w
    fontsize: int = int(((clip_width / 100) * 50) / 10)

    for include, value, literal in [
        (include_views, views, "views"),
        (include_likes, likes, "likes")
        # (include_channel_name, channel_name, "channel"),
    ]:
        if not include:
            continue
        logger.info(f"Adding {literal} with value {value} to {video.filename}")

        text: _ViewsLikesOrChannelImageClip = create_likes_views_or_channel_text_clip(
            literal, value, fontsize=fontsize
        )
        background: TextBackgroundImageClip = create_background_for_text(text)
        text_clips_to_include.append((text, background))

    crossfade_in: float = 0.0
    crossfade_out: float = 0.2
    final_background_clips: list[TextBackgroundImageClip] = []
    final_text_clips: list[_ViewsLikesOrChannelImageClip] = []
    # NOTE: Can't remember why we need to do this...
    clip_number: int = 0

    logger.info("Adding position and crossfade details")
    for text_clip, text_background_iamge in text_clips_to_include:
        clip_number += 1

        final_text_clips.append(
            text_clip.set_duration(details_duration)
            .set_position((32, text_clip.h * clip_number))
            .crossfadein(crossfade_in)
            .crossfadeout(crossfade_out)
        )
        final_background_clips.append(
            text_background_iamge.set_duration(details_duration)
            .set_position((15, (text_clip.h * clip_number) - (text_clip.h / 4)))
            .crossfadein(crossfade_in)
            .crossfadeout(crossfade_out)
        )

    args: list[mp.VideoFileClip] = [video]
    args.extend(final_background_clips)
    args.extend(final_text_clips)
    return mp.CompositeVideoClip(args)


# TODO: Somehow write tests for this.
@typechecked
def create_likes_views_or_channel_text_clip(
    prefix: str,
    value: Union[str, int],
    font: str = Config.Compilation.ImageClipFont,
    fontsize: int = Config.Compilation.ImageClipFontSize,
    kerning: int = Config.Compilation.ImageClipKerningSize,
) -> _ViewsLikesOrChannelImageClip:
    """
    Creates a standardized TextClip with a prefix and value.

    Args:
        prefix (str): The text displayed before the value.
            The prefix value must either be 'views', 'likes', or 'channel.
        value (Union[str, int]):
        font (str, optional): The font of the text.
            Defaults to Config.Compilation.ImageClipFont.
        fontsize (int, optional): Defaults to Config.Compilation.ImageClipFontSize.
        kerning (int, optional): The "spacing" between letters..
            Defaults to Config.Compilation.ImageClipKerningSize.

    Raises:
        ValueError: Invalid prefix.
        ValueError: Used a non-str value with the 'channel' prefix.

    Returns:
        _ViewsLikesOrChannelImageClip: _description_
    """
    if prefix not in ["views", "likes", "channel"]:
        message: str = f"Provided prefix {prefix} is not an accepted argument"
        logger.error(message)
        raise ValueError(message)

    if prefix == "channel":
        if isinstance(value, str):
            message: str = "You've used the 'channel' prefix with a non-str value. This isn't allowed."
            logger.error(message)
            raise ValueError(message)

        text: str = "{}: {}"
    else:
        # The ;, syntax allows use to get "120,000" from "120000".
        # Otherwise, the "120000" is kinda hard to read.
        text: str = "{}: {:,}"
    logger.info(f"Using value {value} with the prfix {prefix}")

    return mp.TextClip(
        txt=text.format(prefix, value),
        fontsize=fontsize,
        kerning=kerning,
        font=font,
    )


# TODO: Somehow write tests for this.
@typechecked
def create_background_for_text(
    text: mp.ImageClip,
    background_padding_width: int = 50,
    background_padding_height: int = 50,
    background_color: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> TextBackgroundImageClip:
    """
    Creates a background that is equal size to the height and length of the text.
    Padding can be applied to the background.

    Args:
        text (mp.ImageClip)
        background_padding_width (int, optional. Defaults to 40.
        background_padding_height (int, optional): Defaults to 20.
        background_color (tuple[int, int, int, int], optional): Defaults to (255, 255, 255, 255).

    Returns:
        TextBackgroundImageClip
    """
    logger.info(
        "Creating background with paddings"
        f" (w: {background_padding_width}, h: {background_padding_height})"
        f" and background color {background_color}"
    )
    # Specify the size of the image (which equals the text width and height)
    # and add the padding. Also,make the background transparent so it doesn't
    # affect any other operations below.
    logger.info("Creating new image")
    image: Image.Image = Image.new(
        "RGBA",
        size=(text.w + background_padding_width, text.h + background_padding_height),
        color=(0, 0, 0, 0),
    )

    logger.info("Creating draw object")
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

    #
    # Define the rectangle coordinates.
    #
    # Where the text starts. Why 10, 10? Because it works.
    logger.info("Defining positions")
    top_left: tuple[int, int] = (10, 10)
    # Where the bottom right text ends
    bottom_right: tuple[float, float] = (
        text.w + background_padding_width / 2,
        text.h + background_padding_height / 2,
    )

    # Draw the rectangle with rounded corners
    logger.info("Drawing rounded rectangle")
    draw.rounded_rectangle(
        [top_left, bottom_right], radius=5, fill=background_color, outline=None, width=0
    )

    # TODO: Perhaps leter we can just get the np.array and load it in directly

    # Now output the image so we can later load it from the filepath
    image_path: Path = (
        Path(__file__)
        .parent.joinpath(Config.Compilation.StaticFolderName)
        .joinpath("random.png")
    )
    logger.info(f"Saving draw obj to image to {str(image_path)}")
    image.save(str(image_path))
    logger.info("Imae saved")

    # Wait until the image is created
    while not image_path.exists():
        sleep(0.1)

    # Now we have it loaded it, delete the image
    background_image: mp.ImageClip = mp.ImageClip((str(image_path)))
    image_path.unlink()
    logger.info(f"Successfully deleted image {image_path}")

    return background_image


@typechecked
def construct_metadata_from_videos(
    videos: Union[list[mp.VideoFileClip], list[mp.CompositeVideoClip]],
    clip_number: int = 0,
    last_clip_time: float = 0,
    metadata: dict = {},
) -> dict:
    """
    Generates metadata from videos. This involves the video, video id, and timings.

    Args:
        videos (list[mp.VideoFileClip]): The videos to generate the metadata from.

        # NOTE: These aren't required, this is just for recursion.
        clip_number (int, optional): Defaults to 0.
        last_clip_time (int, optional): Defaults to 0.
        metadata (Optional[dict], optional): Defaults to None.

    Raises:
        ValueError: If the video file path is not found in Pocketbase.

    Returns:
        dict: The metadata...
    """
    if not videos:
        return metadata

    video: Union[mp.VideoFileClip, mp.CompositeVideoClip] = videos[0]
    if isinstance(video, mp.CompositeVideoClip):
        video = [clip for clip in video.clips if isinstance(clip, mp.VideoFileClip)][0]

    logger.info(f"Generating metadata for file {video.filename}")

    record: VideoCollectionRecord = VideoCollection.validate_record(
        VideosCollectionInfo.Fields.VideoPath, video.filename, True
    )

    metadata[clip_number]: CompilationMeatadata = CompilationMeatadata(
        video=video.filename,
        video_record_id=getattr(record, VideosCollectionInfo.Fields.Id),
        start_time_in_seconds=last_clip_time,
        start_time=str(timedelta(seconds=last_clip_time)),
        finish_time_in_seconds=last_clip_time + video.duration,
        finish_time=str(timedelta(seconds=last_clip_time + video.duration)),
    )

    return construct_metadata_from_videos(
        videos[1:], clip_number + 1, last_clip_time + video.duration, metadata
    )


def total_number_of_frames_in_a_video(video: Path) -> int:
    """
    What is says on the tin...

    Args:
        video (Path)

    Returns:
        int
    """
    validate_path_exists(video)
    clip = mp.VideoFileClip(video)
    return math.trunc(clip.duration)
