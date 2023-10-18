"""
Tests for Pocketbase classes.

NOTE: In the SinglePocketBase class we have methods
such as update, delete, create, but we don't test this. We simply
have these methods to exist as they class uses authentication, so
it's pointless testing as you'll be testing the module, not our implmentation.
"""
import unittest

from . import test_collection_name

from src.config import Config
from src.utils.pb.classes import SingletonPocketBase

from pocketbase import PocketBase


class TestSingletonPocketBase(unittest.TestCase):
    """
    Tests for Pocketbase classes.
    """

    def setUp(self) -> None:
        self.pb = PocketBase(Config.PocketBase.URL)
        self.pb.admins.auth_with_password(
            Config.PocketBase.AdminUsername, Config.PocketBase.AdminPassword
        )

        self.record_one: dict = {"first_name": "Danny", "second_name": "Goob"}
        self.record_two: dict = {"first_name": "Becky", "second_name": "Goob"}

        self.records: list[str] = [
            self.pb.collection(test_collection_name).create(record)
            for record in [self.record_one, self.record_two]
        ]

    def tearDown(self) -> None:
        for record in self.records:
            self.pb.collection(test_collection_name).delete(record.id)

    def test_singleton_instance(self):
        """
        Tests the SingletonPocketBase class.
        """
        instance_1 = SingletonPocketBase()
        instance_2 = SingletonPocketBase()

        self.assertEqual(instance_1, instance_2)

    def test_search_single_record(self):
        pb = SingletonPocketBase()

        query = {"filter": "second_name = 'Goob'"}

        # By using per_page=1 we ensure that our recursion is working
        results = pb.search(test_collection_name, query, per_page=1)

        self.assertEqual(len(results), len(self.records))

    def test_search_single_record(self):
        pb = SingletonPocketBase()

        empty_result = pb.search_single_record(
            test_collection_name, "first_name", "john"
        )
        self.assertEqual(empty_result, None)

        valid_result = pb.search_single_record(
            test_collection_name, "first_name", "Danny"
        )
        self.assertEqual(valid_result.first_name, "Danny")

        # As 'Goob' occurs more than once, if we try to search this, it should
        # throw an error
        with self.assertRaises(ValueError):
            pb.search_single_record(test_collection_name, "second_name", "Goob")

    def test_search_multiple_records(self):
        pb = SingletonPocketBase()

        results = pb.search_multiple_records(
            test_collection_name, "second_name", "Goob"
        )

        self.assertEqual(len(results), len(self.records))

    def test_serialize_value(self):
        # Ints and floats should remain untouched
        self.assertEqual(1, SingletonPocketBase.serialize_value(1))
        self.assertEqual(1.5, SingletonPocketBase.serialize_value(1.5))
        # NOTE: The reason we wrap quote around the string is bause the return value
        # will have quotes around them. So to get unittest to ensure this is actually working,
        # we must wrap quotes around string.
        self.assertEqual("'danny'", SingletonPocketBase.serialize_value("danny"))
        self.assertEqual('"Don\'t"', SingletonPocketBase.serialize_value("Don't"))
        self.assertEqual(
            "'The cat in the hat'",
            SingletonPocketBase.serialize_value("The cat in the hat"),
        )


if __name__ == "__main__":
    unittest.main(failfast=True)
