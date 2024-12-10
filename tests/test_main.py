import unittest
from io import StringIO
from unittest.mock import Mock, patch

from tcomp.__main__ import main
from tcomp.transaction import Transaction


class TestMainFunction(unittest.TestCase):

    @patch("sys.stdout", new_callable=StringIO)
    @patch("tcomp.transaction.transactions_from_json")
    @patch("tcomp.transaction.transactions_from_csv")
    def test_main_function_positive(
        self,
        mock_transactions_from_csv: Mock,
        mock_transactions_from_json: Mock,
        mock_stdout: Mock,
    ):
        # Mock the transactions
        mock_transactions_from_json.return_value = [
            Transaction(
                date="2023-01-01", amount=2000, description="Test Transaction A"
            ),
            Transaction(
                date="2023-01-02", amount=3000, description="Test Transaction B"
            ),
        ]
        mock_transactions_from_csv.return_value = [
            Transaction(
                date="2023-01-01", amount=2000, description="Test Transaction A"
            ),
            Transaction(
                date="2023-01-03", amount=4000, description="Test Transaction C"
            ),
        ]

        # Call the main function
        main(["file_a.json", "file_b.csv", "--bank=millenium"])

        # Assertions
        mock_transactions_from_json.assert_called_once_with("file_a.json")
        mock_transactions_from_csv.assert_called_once_with(
            "file_b.csv", bank="millenium"
        )

        self.assertEqual(
            """\
# In file_a.json but not in file_b.csv:
| Date                |   Amount | Description        |
|---------------------|----------|--------------------|
| 2023-01-02 00:00:00 |        3 | Test Transaction B |

# In file_b.csv but not in file_a.json:
| Date                |   Amount | Description        |
|---------------------|----------|--------------------|
| 2023-01-03 00:00:00 |        4 | Test Transaction C |
""",
            mock_stdout.getvalue(),
        )

    @patch("sys.stdout", new_callable=StringIO)
    @patch("tcomp.transaction.transactions_from_json")
    @patch("tcomp.transaction.transactions_from_csv")
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
        main(["file_a.json", "file_b.csv", "--bank=millenium"])

        # Assertions
        mock_transactions_from_json.assert_called_once_with("file_a.json")
        mock_transactions_from_csv.assert_called_once_with(
            "file_b.csv", bank="millenium"
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

    @patch("tcomp.transaction.transactions_from_json")
    @patch("tcomp.transaction.transactions_from_csv")
    def test_main_function_invalid_file(
        self,
        mock_transactions_from_csv: Mock,
        mock_transactions_from_json: Mock,
    ):
        # Simulate an error when reading JSON
        mock_transactions_from_json.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            main(["invalid_file_a.json", "file_b.csv", "--bank=millenium"])

    @patch("tcomp.transaction.transactions_from_json")
    @patch("tcomp.transaction.transactions_from_csv")
    def test_main_function_invalid_csv(
        self, mock_transactions_from_csv, mock_transactions_from_json
    ):
        # Mock valid JSON but simulate an error when reading CSV
        mock_transactions_from_json.return_value = [
            Mock(date="2023-01-01", amount=2000, description="Test Transaction A")
        ]
        mock_transactions_from_csv.side_effect = ValueError("Invalid CSV format")

        with self.assertRaises(ValueError):
            main(["file_a.json", "invalid_file_b.csv", "--bank=millenium"])
