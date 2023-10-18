from pathlib import Path
from src.config import VIDEO_DIRECTORY, TEST_DIRECTORY, Config, TestConfig

if VIDEO_DIRECTORY is None:
    raise ValueError("You must first defined the video directory in the config file")


for directory in [
    # Top level folders go first
    VIDEO_DIRECTORY,
    TEST_DIRECTORY,
    Config.Download.Directory,
    Config.Compilation.Directory, 
    Config.Compilation.TempDirectory,
    TestConfig.Compilation.Directory,
    TestConfig.Downloads.Directory, 
    TestConfig.Temp.Directory

]:
    if not isinstance(directory, Path):
        directory = Path(directory)
        
    if not directory.exists():
        print("Creating directory", str(directory))
        directory.mkdir()
