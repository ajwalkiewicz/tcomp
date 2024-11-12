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
from dataclasses import dataclass, field
from datetime import datetime, timedelta

TIMEDELTA = timedelta(days=3)
"""Default timedelat - used for equility operator in Transaction class"""


@dataclass(slots=True)
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
    description: str
    _delta: timedelta = field(default=TIMEDELTA, init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.fromisoformat(self.date)

        if isinstance(self.amount, float):
            self.amount = int(self.amount * 1000)

    def __eq__(self, other: "Transaction") -> bool:
        """Check equality between two Transaction instances.

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
        
        return self.amount == other.amount and abs(self.date - other.date) <= self._delta

class TransactionCreator(ABC):
    """Absctract Transaction creator class."""

    @staticmethod
    @abstractmethod
    def create_transaction(row: dict) -> Transaction: ...


class MilleniumTransaction(TransactionCreator):
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


class PkoBpTransaction(TransactionCreator):
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


class SantanderTransaction(TransactionCreator):
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
        "millenium": MilleniumTransaction,
        "pkobp": PkoBpTransaction,
        "santander": SantanderTransaction,
    }.get(bank, MilleniumTransaction)

    SANTANDER_FIELDS = ["_", "date", "place", "_", "_", "amount"]

    with open(file, "r", newline="", encoding="utf-8", errors="replace") as fd:
        if bank == "santander":
            next(fd)
            reader = csv.DictReader(fd, fieldnames=SANTANDER_FIELDS)
        else:
            reader = csv.DictReader(fd)

        return [creator.create_transaction(row) for row in reader]
