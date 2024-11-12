"""Tests for Transaction module

Tests generated with Bito AI: https://bito.ai/
Reviewd by human and sourcery.ai: https://sourcery.ai/
"""
import unittest
from datetime import datetime
from tcomp.transactions import SantanderTransaction, Transaction


class TestTransaction(unittest.TestCase):

    def setUp(self):
        """Set up a valid Transaction instance for testing."""
        self.transaction1 = Transaction(date='2023-10-01T12:00:00', amount=100.50, description='Test Transaction 1')
        self.transaction2 = Transaction(date='2023-10-02T12:00:00', amount=100.50, description='Test Transaction 2')
        self.transaction3 = Transaction(date='2023-10-01T12:00:00', amount=200.00, description='Test Transaction 3')

    def test_transaction_initialization(self):
        """Test if Transaction is initialized correctly."""
        self.assertEqual(self.transaction1.date, datetime.fromisoformat('2023-10-01T12:00:00'))
        self.assertEqual(self.transaction1.amount, 100500)  # Amount converted to int
        self.assertEqual(self.transaction1.description, 'Test Transaction 1')

    def test_transaction_equality_within_delta(self):
        """Test equality of transactions within the defined time delta."""
        self.assertEqual(self.transaction1, self.transaction2)

    def test_transaction_equality_outside_delta(self):
        """Test equality of transactions outside the defined time delta."""
        self.transaction4 = Transaction(date='2023-10-05T12:00:00', amount=100.50, description='Test Transaction 4')
        self.assertNotEqual(self.transaction1, self.transaction4)

    def test_transaction_equality_different_amounts(self):
        """Test equality of transactions with different amounts."""
        self.assertNotEqual(self.transaction1, self.transaction3)

    def test_transaction_invalid_date_format(self):
        """Test initialization with an invalid date format."""
        with self.assertRaises(ValueError):
            Transaction(date='invalid-date', amount=100.50, description='Invalid Date Transaction')

    def test_transaction_invalid_comparison(self):
        """Test comparison with a non-Transaction instance."""
        with self.assertRaises(TypeError):
            self.transaction1 == "Not a Transaction"

    def test_transaction_amount_as_float(self):
        """Test if the amount can be initialized as a float and converted correctly."""
        transaction = Transaction(date='2023-10-01T12:00:00', amount=150.75, description='Float Amount Transaction')
        self.assertEqual(transaction.amount, 150750)

    def test_transaction_date_conversion(self):
        """Test if a datetime object is converted to ISO format."""
        transaction = Transaction(date=datetime(2023, 10, 1, 12, 0, 0), amount=100.50, description='Datetime Transaction')
        self.assertEqual(transaction.date, datetime.fromisoformat('2023-10-01T12:00:00'))

    def test_transaction_edge_case(self):
        """Test edge case with a date exactly on the boundary of the delta."""
        transaction = Transaction(date='2023-10-04T12:00:00', amount=100.50, description='Boundary Transaction')
        self.assertEqual(self.transaction1, transaction)

    def test_transaction_remove_fourth_decimal_digit(self):
        """
        Test case to verify that two transactions are considered identical
        when the fourth decimal digit of the amount is removed during 
        conversion to an integer.
        """
        
        transaction1 = Transaction(
            date='2023-10-04T12:00:00',
            amount=100.1238,
            description='Floating point number removal 1'
        )
        
        transaction2 = Transaction(
            date='2023-10-04T12:00:00',
            amount=100.1239,
            description='Floating point number removal 2'
        )
        
        self.assertEqual(transaction1, transaction2)



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