"""TCOMP Module.

This module contains main TCOMP functions and classes.

Classes:
    Transaction: Class representing single transaction.
    Diff: Class encapsulating transactions that differes.

Functions:
    compare: Compares 2 list of transactions.
    transactions_from_csv: Create a list of transactions from csv file.
    transactions_from_json: Create a list of transactions from json file.
"""

from typing import NamedTuple

from tcomp.transactions import (
    Transaction,
    transactions_from_csv,
    transactions_from_json,
)

__version__ = "0.0.1"
__author__ = "Adam Walkiewicz"


class Diff(NamedTuple):
    atob: list[Transaction]
    btoa: list[Transaction]


def compare(
    transactions_a: list[Transaction], transactions_b: list[Transaction]
) -> Diff:
    """Compare to list of transactions and return a dictionary with
    differences between them.

    Args:
        transactions_a: First list of transactions to compare.
        transactions_b: Second list of transactions to compare.

    Returns:
        Object with differances between transactions.
    """
    atob = []
    btoa = transactions_b

    for transaction in transactions_a:
        if transaction in transactions_b:
            transactions_b.remove(transaction)
        else:
            atob.append(transaction)

    return Diff(atob, btoa)
