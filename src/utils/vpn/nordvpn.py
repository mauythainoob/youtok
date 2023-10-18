"""
Module for NordVPN connections.

# TODO: Tests these funcs.
"""

from subprocess import run
from random import choice
from time import sleep

import requests
from typeguard import typechecked


from ...logger import SingletonLogger

logger = SingletonLogger()


class NordvpnCountryOptions:
    """
    Current country options for nordvpn.

    Why:
    A bug may occur when connection to a country because you've spelt it wrong
    or nordvpn have changeg its value. Plus, I like dot notation... makes
    things easier to read IMO.
    """

    UK = "United Kingdom"
    Germany = "Germany"
    France = "France"
    Sweden = "Sweden"
    Norway = "Norway"


@typechecked
def establish_random_nordvpn_connection() -> None:
    """
    Exactly what is says on the tin.
    """
    logger.info("Establishing random NordVPN connection.")

    # Some good ol Python magic. Looks weird but this will grab a random property's value
    random_country = eval(
        "NordvpnCountryOptions"
        f".{choice([country for country in dir(NordvpnCountryOptions) if not country.startswith('__')])}"
    )

    return establish_nordvpn_connection(random_country)


@typechecked
def establish_nordvpn_connection(
    country: str, system_sleep: int = 10, request_timeout: int = 10
) -> None:
    """
    Establishes nordvpn connection to a country.


    Why this exist:
    Reseting our VPN connection allows us dodge services like CloudFlare. Since we use
    3rd party software to download videos for us, this is required.

    Args:
        country (str): The country you wish to connect to.
        system_sleep (int): How long we should let the system.run timeout and how long we
                            we let the system sleep to update the nordvpn connection.
                            (Default 10).
        request_timeout (int): How long our request should live until timeout. (Default 10).

    Raises:
        Exception: When nordvpn doesn't establish a connect (for whatever reason).

    """
    logger.info(f"Establishing VPN connection to {country}")
    # We set check as False as, even though it works, it still returns an error
    # so ignore this.
    run(["nordvpn", "-c", "-g", country], check=False, timeout=system_sleep)
    # Since we've had to ignore the check, we give Nord some time to connect
    sleep(system_sleep)

    # Now let's check if it's actually worked
    respone: requests.models.Response = requests.get(
        "https://api.myip.com/", timeout=request_timeout
    )
    respone.raise_for_status()

    assert respone.json()["country"] == country
    logger.info(f"Successfully connected to NordVPN in {country}")
