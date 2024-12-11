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

from pydantic.dataclasses import dataclass

from tcomp.error import UnsupportedBankError

TIMEDELTA = timedelta(days=3)
"""Default timedelat - used for equility operator in Transaction class"""


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

    date: str | datetime
    amount: int | float
    description: str = ""
    _delta: timedelta = field(default=TIMEDELTA, init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.date, str):
            object.__setattr__(self, "date", datetime.fromisoformat(self.date))

        if isinstance(self.amount, float):
            object.__setattr__(self, "amount", int(self.amount * 1000))

    def __eq__(self, other: "Transaction") -> bool:
        """Check equality between two Transaction instances.

        Transactions are equal if their ammount are the same and the difference
        between dates is smaller or equal to _delta.

        Args:
            other (Transaction): The other transaction to compare against.

        Returns:
            bool: True if transactions are equivalent, False otherwise.

        Raises:
            TypeError: If 'other' is not an instance of Transaction.
        """
        if not isinstance(other, Transaction):
            raise TypeError(
                f"Cannot compare '{type(self).__name__}' to '{type(other).__name__}'"
            )

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
    """Absctract Transaction creator class."""

    @staticmethod
    @abstractmethod
    def create_transaction(row: dict) -> Transaction: ...


class MilleniumTransactionCreator(TransactionCreator):
    @staticmethod
    def create_transaction(row: dict) -> Transaction:
        """Create transactions from Millenium bank CSV file.

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


class PkoBpTransactionCreator(TransactionCreator):
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


class SantanderTransactionCreator(TransactionCreator):
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
            date=date.isoformat(),
            amount=float(row["amount"].replace(",", ".")),
            description=row["place"],
        )


def transactions_from_json(file: str) -> list[Transaction]:
    """Create a list of transactions from json file.

    Args:
        file: Path to json file.

    Returns:
        List of transactions
    """
    with open(file, "r") as f:
        transactions = json.load(f)["data"]["transactions"]

    return [
        Transaction(
            date=transaction["date"],
            amount=transaction["amount"],
            description=f"{transaction['payee_name']} {transaction['memo'] or ''}",
        )
        for transaction in transactions
    ]


def transactions_from_csv(file: str, bank: str = "millenium") -> list[Transaction]:
    """Create a list of transactions from csv file.

    Args:
        file: Path to csv file.
        bank: From what ban csv was generated.

    Returns:
        List of transactions.
    """
    creator: TransactionCreator = {
        "millenium": MilleniumTransactionCreator,
        "pkobp": PkoBpTransactionCreator,
        "santander": SantanderTransactionCreator,
    }.get(bank)

    if creator is None:
        raise UnsupportedBankError(f"Bank not supported: '{bank}'")

    SANTANDER_FIELDS = ["_", "date", "place", "_", "_", "amount"]

    with open(file, "r", newline="", encoding="utf-8", errors="replace") as fd:
        if bank == "santander":
            next(fd)
            reader = csv.DictReader(fd, fieldnames=SANTANDER_FIELDS)
        else:
            reader = csv.DictReader(fd)

        return [creator.create_transaction(row) for row in reader]
