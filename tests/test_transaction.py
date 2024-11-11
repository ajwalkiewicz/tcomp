"""Tests for Transaction module

Tests generated with Bito AI: https://bito.ai/
Reviewd by human and sourcery.ai: https://sourcery.ai/
"""
import unittest
from datetime import datetime
from tcomp.transactions import SantanderTransaction, Transaction

class TestSantanderTransaction(unittest.TestCase):

    def test_create_transaction_valid_data(self):
        row = {
            "date": "15-03-2023",
            "amount": "100,50",
            "place": "Supermarket"
        }
        transaction = SantanderTransaction.create_transaction(row)
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.date, datetime.fromisoformat("2023-03-15"))
        self.assertEqual(transaction.amount, 100500)
        self.assertEqual(transaction.description, "Supermarket")

    def test_create_transaction_invalid_date_format(self):
        row = {
            "date": "03-15-2023",  # Invalid format
            "amount": "100,50",
            "place": "Supermarket"
        }
        with self.assertRaises(ValueError):
            SantanderTransaction.create_transaction(row)

    def test_create_transaction_invalid_amount(self):
        row = {
            "date": "15-03-2023",
            "amount": "invalid_amount",  # Invalid amount
            "place": "Supermarket"
        }
        with self.assertRaises(ValueError):
            SantanderTransaction.create_transaction(row)

    def test_create_transaction_empty_place(self):
        row = {
            "date": "15-03-2023",
            "amount": "100,50",
            "place": ""  # Empty place
        }
        transaction = SantanderTransaction.create_transaction(row)
        self.assertEqual(transaction.description, "")  # Should handle empty place

    def test_create_transaction_large_amount(self):
        row = {
            "date": "15-03-2023",
            "amount": "1000000,50",  # Large amount
            "place": "Bank Deposit"
        }
        transaction = SantanderTransaction.create_transaction(row)
        self.assertEqual(transaction.amount, 1000000500)

    def test_create_transaction_negative_amount(self):
        row = {
            "date": "15-03-2023",
            "amount": "-100,50",  # Negative amount
            "place": "Refund"
        }
        transaction = SantanderTransaction.create_transaction(row)
        self.assertEqual(transaction.amount, -100500)

    def test_create_transaction_boundary_date(self):
        row = {
            "date": "29-02-2020",  # Leap year
            "amount": "50,00",
            "place": "Leap Year Test"
        }
        transaction = SantanderTransaction.create_transaction(row)
        self.assertEqual(transaction.date, datetime.fromisoformat("2020-02-29"))

    def test_create_transaction_nonexistent_date(self):
        row = {
            "date": "31-04-2023",  # Invalid date (April has 30 days)
            "amount": "100,50",
            "place": "Invalid Date Test"
        }
        with self.assertRaises(ValueError):
            SantanderTransaction.create_transaction(row)

if __name__ == '__main__':
    unittest.main()