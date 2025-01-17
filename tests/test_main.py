import re
import sys
import unittest
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from tcomp.__main__ import main
from tcomp.transaction import BankManager, Transaction, TransactionManager


def get_supported_banks_choice():
    """
    Helper function to get a string with supported banks choice
    that argparse will return on the console when incorrect
    bank is passed.

    In python 3.12.8 argparse parse differently the choices
    See this PR: https://github.com/python/cpython/pull/117766
    """
    if sys.version_info < (3, 12, 8):
        return ", ".join(f"'{bank}'" for bank in BankManager.SUPPORTED_BANKS)
    else:
        return ", ".join(f"{bank}" for bank in BankManager.SUPPORTED_BANKS)


class TestMainFunction(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    @patch("tcomp.transaction.TransactionManager.transactions_from_json")
    @patch("tcomp.transaction.TransactionManager.transactions_from_csv")
    def test_main_function_positive(
        self,
        mock_transactions_from_csv: Mock,
        mock_transactions_from_json: Mock,
        mock_stdout: Mock,
    ):
        self.maxDiff = None
        # Mock the transactions
        mock_transactions_from_json.return_value = [
            Transaction(
                date=datetime.fromisoformat("2023-01-01"),
                amount=2000,
                description="Test Transaction A",
            ),
            Transaction(
                date=datetime.fromisoformat("2023-01-02"),
                amount=3000,
                description="Test Transaction B",
            ),
        ]
        mock_transactions_from_csv.return_value = [
            Transaction(
                date=datetime.fromisoformat("2023-01-01"),
                amount=2000,
                description="Test Transaction A",
            ),
            Transaction(
                date=datetime.fromisoformat("2023-01-03"),
                amount=4000,
                description="Test Transaction C",
            ),
        ]

        # Call the main function
        main(["file_a.json", "file_b.csv", "--bank=millennium"])

        # Assertions
        mock_transactions_from_json.assert_called_once_with("file_a.json")
        mock_transactions_from_csv.assert_called_once_with(
            "file_b.csv", bank="millennium"
        )

        self.assertEqual(
            """\
# In file_a.json but not in file_b.csv:
| Date                |   Amount | Description        |
|---------------------|----------|--------------------|
| 2023-01-02 00:00:00 |     3000 | Test Transaction B |

# In file_b.csv but not in file_a.json:
| Date                |   Amount | Description        |
|---------------------|----------|--------------------|
| 2023-01-03 00:00:00 |     4000 | Test Transaction C |
""",
            mock_stdout.getvalue(),
        )

    @patch("sys.stdout", new_callable=StringIO)
    @patch("tcomp.transaction.TransactionManager.transactions_from_json")
    @patch("tcomp.transaction.TransactionManager.transactions_from_csv")
    def test_main_function_no_transactions(
        self,
        mock_transactions_from_csv: Mock,
        mock_transactions_from_json: Mock,
        mock_stdout: Mock,
    ):
        # Mock no transactions
        mock_transactions_from_json.return_value = []
        mock_transactions_from_csv.return_value = []

        # Call the main function
        main(["file_a.json", "file_b.csv", "--bank=millennium"])

        # Assertions
        mock_transactions_from_json.assert_called_once_with("file_a.json")
        mock_transactions_from_csv.assert_called_once_with(
            "file_b.csv", bank="millennium"
        )
        self.assertEqual(
            """\
# In file_a.json but not in file_b.csv:
| Date   | Amount   | Description   |
|--------|----------|---------------|

# In file_b.csv but not in file_a.json:
| Date   | Amount   | Description   |
|--------|----------|---------------|
""",
            mock_stdout.getvalue(),
        )

    @patch("tcomp.transaction.TransactionManager.transactions_from_json")
    @patch("tcomp.transaction.TransactionManager.transactions_from_csv")
    def test_main_function_invalid_file(
        self,
        mock_transactions_from_csv: Mock,
        mock_transactions_from_json: Mock,
    ):
        # Simulate an error when reading JSON
        mock_transactions_from_json.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            main(["invalid_file_a.json", "file_b.csv", "--bank=millennium"])

    @patch("tcomp.transaction.TransactionManager.transactions_from_json")
    @patch("tcomp.transaction.TransactionManager.transactions_from_csv")
    def test_main_function_invalid_csv(
        self, mock_transactions_from_csv, mock_transactions_from_json
    ):
        # Mock valid JSON but simulate an error when reading CSV
        mock_transactions_from_json.return_value = [
            Mock(date="2023-01-01", amount=2000, description="Test Transaction A")
        ]
        mock_transactions_from_csv.side_effect = ValueError("Invalid CSV format")

        with self.assertRaises(ValueError):
            main(["file_a.json", "invalid_file_b.csv", "--bank=millennium"])

    @patch("sys.stderr", new_callable=StringIO)
    def test_main_function_unsupported_bank(
        self,
        mock_stdout: Mock,
    ):
        script_name = Path(sys.argv[0]).name

        self.maxDiff = None
        with self.assertRaises(SystemExit):
            main(["file_a.json", "file_b.csv", "--bank=invalid_bank"])

        supported_bank_options = r"{" + ",".join(BankManager.SUPPORTED_BANKS) + r"}"
        supported_banks_choice = get_supported_banks_choice()

        expected_output = (
            f"usage: {script_name} [-h] [--bank {supported_bank_options}] file_a file_b\n"
            f"{script_name}: error: argument --bank: invalid choice: 'invalid_bank' (choose from {supported_banks_choice})\n"
        )

        actual_output_normalized = re.sub(r"\s+", " ", mock_stdout.getvalue().strip())
        expected_output_normalized = re.sub(r"\s+", " ", expected_output.strip())

        self.assertEqual(actual_output_normalized, expected_output_normalized)
