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

from tcomp.diff import Diff, compare
from tcomp.transaction import Transaction, transactions_from_csv, transactions_from_json

__version__ = "0.0.1"
__author__ = "Adam Walkiewicz"

__all__ = [
    "Diff", 
    "compare",
    "Transaction",
    "transactions_from_csv",
    "transactions_from_json",
]

SUPPORTED_BANKS = ("millennium", "pkobp", "santander", "revolut")
