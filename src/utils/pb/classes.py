from typing import Union, Optional
from abc import ABC, abstractstaticmethod

from pocketbase import PocketBase
from pocketbase.models import Record

from typeguard import typechecked


from .typehints import *
from ...config import Config
from ...logger import SingletonLogger

logger = SingletonLogger()


class CollectionBaseClass(ABC):
    @staticmethod
    @abstractstaticmethod
    def create_record():
        pass

    @staticmethod
    @abstractstaticmethod
    def validate_record():
        pass


class SingletonPocketBase:
    """
    This class is a Singleton implementation of PocketBase which provides
    access to all the PocketBase functionalities.
    """

    _instance = None

    def __new__(cls):
        """
        Where the singleton magic happens!
        """
        if cls._instance is None:
            logger.info("Instantiating SingletonPocketBase")

            cls._instance = super().__new__(cls)  # TODO: Figure out if this is required
            cls._instance.instance: PocketBase = PocketBase(Config.PocketBase.URL)
            cls._instance.__authenticate_admin(
                Config.PocketBase.AdminUsername,
                Config.PocketBase.AdminPassword,
            )
        return cls._instance

    def __authenticate_admin(self, email: str, password: str) -> None:
        """
        Admin authenticate.

        Args:
            email (str): The admin's email.
            password (str): The admin's password.
        """
        self.instance.admins.auth_with_password(email, password)
        logger.info("Admin authenticated with PocketBase")

    @typechecked
    def search(
        self,
        collection: str,
        query: dict[str, str],
        records: Optional[list[Record]] = None,
        page: int = 1,
        per_page: int = 500,
    ) -> list[Record]:
        """
        Returns all the records from a search query.

        Args:
            collection (str): The target collection.
            page (int): The page number.
            query (dict[str, str]): What you're searching.
            records (list[Record]): The discovered records from the query.
            per_page (int, optional): How many items to return from a search. Defaults to 500 (max).

        Returns:
            list[Record]: All discovered records from the query
        """
        logger.info(f"Searching {collection} for {query}. Page {page}")
        if not records:
            records: list[Record] = []

        response = self.instance.collection(collection).get_list(page, per_page, query)

        accumulated_records = records + response.items

        if len(accumulated_records) == response.total_items:
            return accumulated_records

        return self.search(collection, query, accumulated_records, page + 1, per_page)

    @typechecked
    def search_single_record(
        self, collection: str, field: str, value: PocketBaseValueOptions
    ) -> Optional[Record]:
        """
        Returns a single record from a query. The intent of this mention is to return
        a value we expect to be unique (such as a Tiktok URL) or to check if the record
        does exist.

        Args:
            collection (str): The target collection.
            field (str): The field to search against.
            value (PocketBaseValueOptions): The value...

        Raises:
            ValueError: If we return more than 1 result.

        Returns:
            Optional[Record]
        """
        query = {"filter": f"{field} = {SingletonPocketBase.serialize_value(value)}"}
        results = self.search(collection, query)

        if len(results) == 0:
            return None
        if len(results) > 1:
            raise ValueError("Returned too many results!")

        return results[0]

    @typechecked
    def search_multiple_records(
        self, collection: str, field: str, value: PocketBaseValueOptions
    ) -> list[Record]:
        """
        Returns multiple records that match the query.

        Args:
            collection (str): _description_
            field (str): _description_
            value (PocketBaseValueOptions): _description_

        Returns:
            list[Record]
        """
        query = {"filter": f"{field} = {SingletonPocketBase.serialize_value(value)}"}
        return self.search(collection, query)

    @typechecked
    def create(self, collection: str, data: dict) -> Record:
        """
        Inserts a record into a collection.

        Args:
            collection (str): The target collection.
            data (Data[str, Any]): the record to insert.

        Returns:
            dict: The result of the create query.
        """
        logger.info(f"Creating record {collection}. Data: {data}")
        return self.instance.collection(collection).create(data)

    @typechecked
    def update(self, collection: str, record_id: str, data: dict):
        """
        Update an existing record.

        Args:
            collection (str): The target collection.
            data (dict): The field that we want to change and the new value.

        """
        logger.info(
            f"Updating record {record_id} from collection {collection}. Data: {data}"
        )
        self.instance.collection(collection).update(record_id, data)

    @typechecked
    def delete(self, collection: str, record_id: str) -> None:
        """
        Deletes a record from a collection.

        Args:
            collection (str): The target collection.
            record_id (str): The id of the record to delete.
        """
        logger.warning(f"Deleting record {record_id} from {collection}.")
        self.instance.collection(collection).delete(record_id)

    @typechecked
    @staticmethod
    def serialize_value(value: PocketBaseValueOptions) -> PocketBaseValueOptions:
        """
        Serializes a value.

        Args:
            value (PocketBaseValueOptions)

        Returns:
            PocketBaseValueOptions
        """
        logger.info(f"Serializing value {value}")
        if isinstance(value, (int, float, bool)):
            return value

        # If a single quote is in the str, wrap it in double quotes
        if "'" in value:
            return f'"{value}"'

        return f"'{value}'"
