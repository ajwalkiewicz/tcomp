from typing import NamedTuple

from tcomp.transaction import Transaction


class Diff(NamedTuple):
    """Represents the differences between two lists of transactions."""

    only_in_a: list[Transaction]
    only_in_b: list[Transaction]


def compare(
    transactions_a: list[Transaction], transactions_b: list[Transaction]
) -> Diff:
    """
    Compare two lists of transactions and return their differences.

    Args:
        transactions_a: First list of transactions to compare.
        transactions_b: Second list of transactions to compare.

    Returns:
        A Diff object containing transactions unique to each list.
    """
    only_in_a = []
    only_in_b = [*transactions_b]

    for transaction in transactions_a:
        if transaction in only_in_b:
            only_in_b.remove(transaction)
        else:
            only_in_a.append(transaction)

    return Diff(only_in_a, only_in_b)
