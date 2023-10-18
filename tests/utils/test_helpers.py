import unittest
from pathlib import Path

from src.utils.helpers import validate_path_exists


class TestValidateFileExists(unittest.TestCase):
    def setUp(self) -> None:
        self.file: Path = Path(__file__).parent.joinpath("file.txt")

    def tearDown(self) -> None:
        if self.file.exists():
            self.file.unlink()

    def test_validate_path_exists(self):
        """
        Tests the validate_path_exists func.
        """
        with self.assertRaises(FileNotFoundError):
            validate_path_exists(self.file)

        self.file.touch()
        validate_path_exists(self.file)
        self.file.unlink()


if __name__ == "__main__":
    unittest.main()
