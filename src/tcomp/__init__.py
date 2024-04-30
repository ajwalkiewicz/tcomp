"""
TCOMP Module

This module contains main TCOMP functions and classes

Classes:
    Transaction: class representing single transaction
    Diff: class encapsulating transactions that differes

Functions:
    compare: compares 2 list of transactions
    transactions_from_csv: create a list of transactions from csv file
    transactions_from_json; create a list of transactions from json file
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
    differences between them

    Args:
        transactions_a (list[Transaction]): first list of transactions to compare
        transactions_b (list[Transaction]): second list of transactions to compare

    Returns:
        Diff: object with differance between transactions
    """
    atob = []
    btoa = transactions_b

    for transaction in transactions_a:
        if transaction in transactions_b:
            transactions_b.remove(transaction)
        else:
            atob.append(transaction)

    return Diff(atob, btoa)
