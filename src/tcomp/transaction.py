"""Transactions module.

This module contains classes and functions related with transactions.

Classes:
    Transaction: Basic class that represents single transaction.

Functions:
    transactions_from_csv: Create a list of transactions from csv file.
    transactions_from_json: Create a list of transactions from json file.
"""

import csv
import json
from abc import ABC, abstractmethod
from dataclasses import field
from datetime import datetime, timedelta
from io import TextIOWrapper
from pathlib import Path
from typing import Type
from uuid import UUID

from pydantic.dataclasses import dataclass
from uynab.model.transaction import NewTransaction

from tcomp.error import UnsupportedBankError

TIMEDELTA = timedelta(days=3)
"""Default timedelta - used for equality operator in Transaction class"""


class classproperty:
    """A helper class for creating class properties
    See: https://stackoverflow.com/questions/76249636/class-properties-in-python-3-11
    """

    def __init__(self, func):
        self.fget = func

    def __get__(self, instance, owner):
        return self.fget(owner)


class BankManager:
    SUPPORTED_BANKS: list[str] = []
    CREATORS: dict[str, Type["TransactionCreator"]] = {}

    @classmethod
    def add_to_supported(
        cls, creator: Type["TransactionCreator"]
    ) -> Type["TransactionCreator"]:
        if not isinstance(creator.bank, str):
            raise ValueError(
                f"{creator.__name__}.bank must return string. "
                "Use @classproperty decorator from tcomp.transaction module. "
                "Or use class attribute 'bank' instead."
            )

        cls.SUPPORTED_BANKS.append(creator.bank)
        cls.CREATORS[creator.bank] = creator

        return creator


@dataclass(slots=True, frozen=True)
class Transaction:
    """Class representing a single transaction.

    Attributes:
        date (str | datetime): The date when the transaction was issued.
        amount (int | float): The amount involved in the transaction.
        description (str): A brief description of the transaction.

    Raises:
        TypeError: If equality operator is used on a different type than Transaction.
    """

    date: datetime
    amount: int | float
    description: str = ""
    _delta: timedelta = field(default=TIMEDELTA, init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, "amount", int(self.amount * 1000))

    def __eq__(self, other: object) -> bool:
        """Check equality between two Transaction instances.

        Transactions are equal if their amount are the same and the difference
        between dates is smaller or equal to _delta.

        Args:
            other (object): The other transaction to compare against.

        Returns:
            bool: True if transactions are equivalent, False otherwise.
        """
        if not isinstance(other, type(self)):
            return False

        return (
            self.amount == other.amount and abs(self.date - other.date) <= self._delta
        )

    def __hash__(self) -> int:
        """Return Transaction hash

        Each transaction has its own unique hash which is equal its memory address.
        In practice it means equal Transaction instances are never identical.
        """
        return id(self)


class TransactionCreator(ABC):
    """Abstract Transaction creator class."""

    @staticmethod
    @abstractmethod
    def create_transaction(row: dict) -> Transaction: ...

    @classproperty
    @abstractmethod
    def bank(cls) -> str: ...

    @staticmethod
    def get_reader(fd: TextIOWrapper) -> csv.DictReader:
        return csv.DictReader(fd)


@BankManager.add_to_supported
class MillenniumTransactionCreator(TransactionCreator):
    @classproperty
    def bank(cls):
        return "millennium"

    @staticmethod
    def create_transaction(row: dict) -> Transaction:
        """Create transactions from Millennium bank CSV file.

        Args:
            row: Dict representing a row from csv.DictReader.

        Returns:
            Transaction object
        """
        return Transaction(
            date=row["Data transakcji"],
            amount=float(row["Obciążenia"] or row["Uznania"]),
            description=row["Opis"],
        )


@BankManager.add_to_supported
class PkoBpTransactionCreator(TransactionCreator):
    @classproperty
    def bank(cls):
        return "pkobp"

    @staticmethod
    def create_transaction(row: dict) -> Transaction:
        """Create transaction from PKO BP bank CSV file.

        Args:
            row: Dict representing a row from csv.DictReader.

        Returns:
            Transaction object.
        """
        return Transaction(
            date=row["Data waluty"],
            amount=float(row["Kwota"]),
            description=row["Opis transakcji"],
        )


@BankManager.add_to_supported
class SantanderTransactionCreator(TransactionCreator):
    SANTANDER_FIELDS = ["_", "date", "place", "_", "_", "amount"]

    @classproperty
    def bank(cls):
        return "santander"

    @staticmethod
    def create_transaction(row: dict) -> Transaction:
        """Create a Transaction object from a row in a Santander PL bank CSV file.

        Args:
            row (dict): A dictionary representing a row from csv.DictReader.

        Returns:
            A Transaction object populated with the data from the provided row.
        """
        date = datetime.strptime(row["date"], "%d-%m-%Y")
        return Transaction(
            date=date,
            amount=float(row["amount"].replace(",", ".")),
            description=row["place"],
        )

    @staticmethod
    def get_reader(fd: TextIOWrapper) -> csv.DictReader:
        next(fd)
        return csv.DictReader(
            fd, fieldnames=SantanderTransactionCreator.SANTANDER_FIELDS
        )


@BankManager.add_to_supported
class RevolutTransactionCreator(TransactionCreator):
    @classproperty
    def bank(cls):
        return "revolut"

    @staticmethod
    def create_transaction(row: dict) -> Transaction:
        """Create a Transaction object from a row in a Revolut PL bank CSV file.

        Args:
            row (dict): A dictionary representing a row from csv.DictReader.

        Returns:
            A Transaction object populated with the data from the provided row.
        """
        return Transaction(
            date=row["Started Date"],
            amount=float(row["Amount"]),
            description=row["Description"],
        )


class TransactionManager:
    DEFAULT_CREATOR: type[TransactionCreator] = MillenniumTransactionCreator

    def __init__(self, creator: type[TransactionCreator] | str | None = None):
        if creator is None:
            self.creator = TransactionManager.DEFAULT_CREATOR
        else:
            self.set_creator(creator)

    def transactions_from_json(self, file: Path) -> list[Transaction]:
        """Create a list of transactions from json file.

        Args:
            file: Path to json file.

        Returns:
            List of transactions
        """
        with open(file, "r") as fd:
            transactions = json.load(fd)["data"]["transactions"]

        return [
            Transaction(
                date=transaction["date"],
                amount=transaction["amount"],
                description=f"{transaction['payee_name']} {transaction['memo'] or ''}",
            )
            for transaction in transactions
        ]

    def transactions_from_csv(self, file: Path) -> list[Transaction]:
        """Create a list of transactions from csv file.

        Args:
            file: Path to csv file.

        Returns:
            List of transactions.
        """

        with open(file, "r", newline="", encoding="utf-8", errors="replace") as fd:
            reader = self.creator.get_reader(fd)

            return [self.creator.create_transaction(row) for row in reader]

    def set_creator(self, bank: Type[TransactionCreator] | str) -> None:
        """
        Sets the transaction creator for the bank.

        Args:
            bank (Type[TransactionCreator] | str): The bank's transaction creator class or a string representing the bank.

        Raises:
            UnsupportedBankError: If the bank is not supported.

        Returns:
            None
        """
        if isinstance(bank, type) and issubclass(bank, TransactionCreator):
            self.creator = bank
            return

        creator: Type[TransactionCreator] | None = BankManager.CREATORS.get(bank)

        if creator is None:
            raise UnsupportedBankError(f"Bank not supported: '{bank}'")

        self.creator = creator
