import unittest
from pathlib import Path

from src.utils.vpn.nordvpn import (
    NordvpnCountryOptions,
    establish_nordvpn_connection,
    establish_random_nordvpn_connection,
)


class TestValidateFileExists(unittest.TestCase):
    def test_establish_nordvpn_connection(self):
        """
        Tests the establish_nordvpn_connection func.
        """
        # There's an assert in this function that checks if the country
        # matches the requested connection.

        # NOTE: I test germany as it's not my home country.
        establish_nordvpn_connection(NordvpnCountryOptions.Germany)

    def test_establish_random_nordvpn_connection(self):
        """
        Tests the establish_random_nordvpn_connection func.
        """
        # There's an assert in this function that checks if the country
        # matches the requested connection.

        establish_random_nordvpn_connection()


if __name__ == "__main__":
    unittest.main()
