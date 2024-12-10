"""Tests for Transaction module

Tests generated with Bito AI: https://bito.ai/
Reviewd by human and sourcery.ai: https://sourcery.ai/
"""

import dataclasses
import json
import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

import pydantic
import pydantic.error_wrappers

import tcomp
import tcomp.error
from tcomp.transaction import (
    SantanderTransactionCreator,
    Transaction,
    transactions_from_json,
)


class TestTransaction(unittest.TestCase):

    def setUp(self):
        """Set up a valid Transaction instance for testing."""
        self.transaction1 = Transaction(
            date="2023-10-01T12:00:00", amount=100.50, description="Test Transaction 1"
        )
        self.transaction2 = Transaction(
            date="2023-10-02T12:00:00", amount=100.50, description="Test Transaction 2"
        )
        self.transaction3 = Transaction(
            date="2023-10-01T12:00:00", amount=200.00, description="Test Transaction 3"
        )

    def test_transaction_initialization(self):
        """Test if Transaction is initialized correctly."""
        self.assertEqual(
            self.transaction1.date, datetime.fromisoformat("2023-10-01T12:00:00")
        )
        self.assertEqual(self.transaction1.amount, 100500)
        self.assertEqual(self.transaction1.description, "Test Transaction 1")
        negative_transaction = Transaction(
            date="2023-10-01T12:00:00",
            amount=-50.75,
            description="Negative Transaction",
        )
        self.assertEqual(negative_transaction.amount, -50750)

    def test_transaction_equality_within_delta(self):
        """Test equality of transactions within the defined time delta."""
        self.assertEqual(self.transaction1, self.transaction2)

    def test_transaction_equality_outside_delta(self):
        """Test equality of transactions outside the defined time delta."""
        self.transaction4 = Transaction(
            date="2023-10-05T12:00:00", amount=100.50, description="Test Transaction 4"
        )
        self.assertNotEqual(self.transaction1, self.transaction4)

    def test_transaction_equality_different_amounts(self):
        """Test equality of transactions with different amounts."""
        self.assertNotEqual(self.transaction1, self.transaction3)

    def test_transaction_invalid_date_format(self):
        """Test initialization with an invalid date format."""
        with self.assertRaises(ValueError):
            Transaction(
                date="invalid-date",
                amount=100.50,
                description="Invalid Date Transaction",
            )

    def test_transaction_invalid_comparison(self):
        """Test comparison with a non-Transaction instance."""
        with self.assertRaises(TypeError):
            self.transaction1 == "Not a Transaction"

    def test_transaction_amount_as_float(self):
        """Test if the amount can be initialized as a float and converted correctly."""
        transaction = Transaction(
            date="2023-10-01T12:00:00",
            amount=150.75,
            description="Float Amount Transaction",
        )
        self.assertEqual(transaction.amount, 150750)

    def test_transaction_date_conversion(self):
        """Test if a datetime object is converted to ISO format."""
        transaction = Transaction(
            date=datetime(2023, 10, 1, 12, 0, 0),
            amount=100.50,
            description="Datetime Transaction",
        )
        self.assertEqual(
            transaction.date, datetime.fromisoformat("2023-10-01T12:00:00")
        )

    def test_transaction_edge_case(self):
        """Test edge case with a date exactly on the boundary of the delta."""
        transaction_on_boundary = Transaction(
            date="2023-10-04T12:00:00",
            amount=100.50,
            description="Boundary Transaction",
        )
        transaction_outside_boundary = Transaction(
            date="2023-10-04T12:00:01", amount=100.50, description="Outside Boundary"
        )
        self.assertEqual(self.transaction1, transaction_on_boundary)
        self.assertNotEqual(self.transaction1, transaction_outside_boundary)

    def test_transaction_remove_fourth_decimal_digit(self):
        """
        Test case to verify that two transactions are considered identical
        when the fourth decimal digit of the amount is removed during
        conversion to an integer.
        """

        transaction1 = Transaction(
            date="2023-10-04T12:00:00",
            amount=100.1238,
            description="Floating point number removal 1",
        )

        transaction2 = Transaction(
            date="2023-10-04T12:00:00",
            amount=100.1239,
            description="Floating point number removal 2",
        )

        self.assertEqual(transaction1, transaction2)

    def test_transactions_are_equal_but_not_identical(self):
        """Test that Transactions are equal but not identical"""
        transaction1 = Transaction(
            date="2023-10-01T12:00:00", amount=100.50, description="Hash Test 1"
        )
        transaction2 = Transaction(
            date="2023-10-01T12:00:00", amount=100.50, description="Hash Test 1"
        )

        # Transactions are equal
        self.assertTrue(transaction1 == transaction2)

        # But not identical
        self.assertFalse(transaction1 is transaction2)

    def test_transactions_are_hashable(self):
        """Test that Transaction is hashable"""
        transaction = Transaction(
            date="2023-10-01T12:00:00", amount=100.50, description="Hash Test"
        )
        self.assertTrue(hash(transaction) == id(transaction))
        {transaction: "test hash"}

    def test_that_transaction_is_frozen(self):
        """Test that Transaction attributes cannot be changed after initialization"""
        transaction = Transaction(
            date="2023-10-01T12:00:00", amount=100.50, description="Frozen Test"
        )
        with self.assertRaises(dataclasses.FrozenInstanceError):
            transaction.amount = 1005000
        with self.assertRaises(dataclasses.FrozenInstanceError):
            transaction.date = "2023-10-02T12:00:00"
        with self.assertRaises(dataclasses.FrozenInstanceError):
            transaction.description = "New description"


class TestSantanderTransaction(unittest.TestCase):

    def test_create_transaction_valid_data(self):
        row = {"date": "15-03-2023", "amount": "100,50", "place": "Supermarket"}
        transaction = SantanderTransactionCreator.create_transaction(row)
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.date, datetime.fromisoformat("2023-03-15"))
        self.assertEqual(transaction.amount, 100500)
        self.assertEqual(transaction.description, "Supermarket")

    def test_create_transaction_invalid_date_format(self):
        row = {
            "date": "03-15-2023",  # Invalid format
            "amount": "100,50",
            "place": "Supermarket",
        }
        with self.assertRaises(ValueError):
            SantanderTransactionCreator.create_transaction(row)

    def test_create_transaction_invalid_amount(self):
        row = {
            "date": "15-03-2023",
            "amount": "invalid_amount",  # Invalid amount
            "place": "Supermarket",
        }
        with self.assertRaises(ValueError):
            SantanderTransactionCreator.create_transaction(row)

    def test_create_transaction_empty_place(self):
        row = {"date": "15-03-2023", "amount": "100,50", "place": ""}  # Empty place
        transaction = SantanderTransactionCreator.create_transaction(row)
        self.assertEqual(transaction.description, "")  # Should handle empty place

    def test_create_transaction_large_amount(self):
        row = {
            "date": "15-03-2023",
            "amount": "1000000,50",  # Large amount
            "place": "Bank Deposit",
        }
        transaction = SantanderTransactionCreator.create_transaction(row)
        self.assertEqual(transaction.amount, 1000000500)

    def test_create_transaction_negative_amount(self):
        row = {
            "date": "15-03-2023",
            "amount": "-100,50",  # Negative amount
            "place": "Refund",
        }
        transaction = SantanderTransactionCreator.create_transaction(row)
        self.assertEqual(transaction.amount, -100500)

    def test_create_transaction_boundary_date(self):
        row = {
            "date": "29-02-2020",  # Leap year
            "amount": "50,00",
            "place": "Leap Year Test",
        }
        transaction = SantanderTransactionCreator.create_transaction(row)
        self.assertEqual(transaction.date, datetime.fromisoformat("2020-02-29"))

    def test_create_transaction_nonexistent_date(self):
        row = {
            "date": "31-04-2023",  # Invalid date (April has 30 days)
            "amount": "100,50",
            "place": "Invalid Date Test",
        }
        with self.assertRaises(ValueError):
            SantanderTransactionCreator.create_transaction(row)


class TestTransactionsFromJson(unittest.TestCase):

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"data": {"transactions": [{"date": "2023-01-01", "amount": 100, "payee_name": "Payee1", "memo": "Test memo"}]}}',
    )
    def test_transactions_from_json_positive(self, mock_file):
        # Given a valid JSON file, we expect a list of Transaction objects
        expected_transaction = Transaction(
            date="2023-01-01", amount=100, description="Payee1 Test memo"
        )

        result = transactions_from_json("fake_path.json")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].date, expected_transaction.date)
        self.assertEqual(result[0].amount, expected_transaction.amount)
        self.assertEqual(result[0].description, expected_transaction.description)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"data": {"transactions": []}}',
    )
    def test_transactions_from_json_empty(self, mock_file):
        # Given an empty transactions list, we expect an empty list
        result = transactions_from_json("fake_path.json")

        self.assertEqual(result, [])

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"data": {"transactions": [{"date": "2023-01-01", "amount": 100, "payee_name": "Payee1", "memo": null}]}}',
    )
    def test_transactions_from_json_no_memo(self, mock_file):
        # Test handling of null memo
        expected_transaction = Transaction(
            date="2023-01-01", amount=100, description="Payee1 "
        )

        result = transactions_from_json("fake_path.json")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].description, expected_transaction.description)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"data": {"transactions": [{"date": "2023-01-01", "amount": "invalid", "payee_name": "Payee1", "memo": "Test memo"}]}}',
    )
    def test_transactions_from_json_invalid_amount(self, mock_file):
        # Given an invalid amount type, we expect a ValueError
        with self.assertRaises(ValueError):
            transactions_from_json("fake_path.json")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_transactions_from_json_file_not_found(self, mock_file):
        # Test handling of file not found error
        with self.assertRaises(FileNotFoundError):
            transactions_from_json("non_existent_file.json")
