"""TCOMP Module.

This module contains main TCOMP functions and classes.

Classes:
    Transaction: Class representing single transaction.
    Diff: Class encapsulating transactions that differs.

Functions:
    compare: Compares 2 list of transactions.
    transactions_from_csv: Create a list of transactions from csv file.
    transactions_from_json: Create a list of transactions from json file.
"""

from importlib.metadata import version

from tcomp.diff import Diff, compare
from tcomp.transaction import (
    BankManager,
    Transaction,
    TransactionManager,
)

__version__ = version("tcomp")
__author__ = "Adam Walkiewicz"

__all__ = [
    "BankManager",
    "Diff",
    "Transaction",
    "TransactionManager",
    "compare",
]
