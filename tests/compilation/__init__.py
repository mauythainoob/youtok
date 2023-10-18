from pathlib import Path

files_path: Path = Path(__file__).parent.joinpath("files")

# We create a list due to the glob being a generator. This means other
# tests could be affected (when trying to use these videos)
mock_videos: Path = list(files_path.glob("*.mp4"))
