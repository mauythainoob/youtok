"""
Tests for project's config.
"""
from pathlib import Path
import unittest

from src.config import BASE_PATH


class TestConfig(unittest.TestCase):
    """
    Tests for project's config.
    """

    def test_base_path(self):
        """
        Tests for _BASE_PATH var.
        """
        self.assertIsInstance(BASE_PATH, Path)


if __name__ == "__main__":
    unittest.main()
