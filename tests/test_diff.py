from datetime import datetime, timedelta

from tcomp import Diff, Transaction, compare


def test_diff_initialization():
    transaction_a1 = Transaction(
        date="2023-01-01", amount=100, description="Transaction A1"
    )
    transaction_b2 = Transaction(
        date="2023-01-02", amount=200, description="Transaction B2"
    )

    result = Diff(only_in_a=[transaction_a1], only_in_b=[transaction_b2])

    assert result.only_in_a == [transaction_a1]
    assert result.only_in_b == [transaction_b2]


def test_diff_only_in_a():
    """Test when there are transactions only in list A."""
    transactions_a = [
        Transaction(date="2023-01-01", amount=100, description="Transaction A1"),
        Transaction(date="2023-01-02", amount=200, description="Transaction A2"),
    ]
    transactions_b = [
        Transaction(date="2023-01-02", amount=200, description="Transaction B2")
    ]

    result = compare(transactions_a, transactions_b)

    assert result.only_in_a == [transactions_a[0]]
    assert result.only_in_b == []


def test_diff_only_in_b():
    """Test when there are transactions only in list B."""
    transaction_a2 = Transaction(
        date="2023-01-02", amount=200, description="Transaction A2"
    )
    transaction_b1 = Transaction(
        date="2023-01-03", amount=300, description="Transaction B1"
    )

    result = Diff(only_in_a=[transaction_a2], only_in_b=[transaction_b1])

    assert result.only_in_a == [transaction_a2]
    assert result.only_in_b == [transaction_b1]


def test_diff_both_lists_empty():
    """Test when both lists are empty."""
    result = compare([], [])

    assert result.only_in_a == []
    assert result.only_in_b == []


def test_diff_identical_transactions():
    """Test when both lists contain identical transactions."""
    transactions_a = [
        Transaction(date="2023-01-01", amount=100, description="Transaction A1")
    ]
    transactions_b = [
        Transaction(date="2023-01-02", amount=100, description="Transaction A2")
    ]

    result = compare(transactions_a, transactions_b)

    assert result.only_in_a == []
    assert result.only_in_b == []


def test_diff_no_common_transactions():
    """Test when there are no common transactions."""
    transactions_a = [
        Transaction(date="2023-01-01", amount=100, description="Transaction A1")
    ]
    transactions_b = [
        Transaction(date="2023-01-02", amount=200, description="Transaction B1")
    ]

    result = compare(transactions_a, transactions_b)

    assert result.only_in_a == transactions_a
    assert result.only_in_b == transactions_b


def test_diff_with_edge_cases():
    """Test with edge cases like large input."""
    transactions_a = [
        Transaction(date=datetime(2023, 1, 1) + timedelta(days=i), amount=i * 10)
        for i in range(1000)
    ]
    transactions_b = [
        Transaction(date=datetime(2023, 1, 1) + timedelta(days=i), amount=i * 10)
        for i in range(5, 995)
    ]

    result = compare(transactions_a, transactions_b)

    assert len(result.only_in_a) == 10  # All transactions in A
    assert len(result.only_in_b) == 0  # All transactions in B
